"""Paper to Playground agent: case.json -> offline index.html + trace.jsonl.

python agent.py --input case.json --output out --model MODEL_ID

Flow: read_input -> fetch -> [plan] -> generate -> parse -> render -> check ->
up to two targeted revisions -> final. The best safe candidate is written
atomically after every improvement; a known required failure exits nonzero.
"""

from __future__ import annotations

import argparse
import html as html_lib
import io
import json
import os
import re
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from budget import Budget, BudgetExceeded
from model_client import ModelCallError, OpenRouterClient
from prompts import (MAX_SOURCE_CHARS, build_generation_messages, build_plan_messages,
                     build_repair_messages, expand_requested)
from spec_parser import SPEC_KEYS, REVISABLE_KEYS, SpecError, error_targets, merge_revision, parse_spec

REQUIRED_FIELDS = ("source_url", "focus", "audience")
MAX_FIELD_CHARS = 16_000  # per brief field; longer text keeps its focus-relevant passages
# Reasoning models spend most completion tokens before visible text; caps leave room for it.
# Worst case with unverified usage (16k + 7k) stays under the 24k soft cap.
# OpenRouter unified reasoning settings; "model" sends no reasoning field at all.
REASONING_MODES = {"model": None, "low": {"effort": "low"}, "off": {"enabled": False},
                   "high": {"effort": "high"}}  # high: experimental only
DEFAULT_REASONING = "auto"
# Model-specific defaults apply only to recognised models; any other model gets the generic path.
# Evidence (U1 stage 1+2, 3 Oct): throughput routing 11/11 runs succeeded with 0 cut-offs vs 8/9 and 2 cut-offs
# on default routing; same served model; mean wall time lower on 5 of 6 cases.
MODEL_PROFILES = {"deepseek/deepseek-v4.1-flash": {"reasoning": "low", "provider_sort": "throughput"}}


def model_profile(model: str) -> dict:
    return MODEL_PROFILES.get(model.split(":", 1)[0].strip().lower(), {})


def resolve_reasoning(model: str, mode: str) -> dict | None:
    """Explicit modes win; 'auto' uses the model profile, else sends no reasoning field."""
    if mode != "auto":
        return REASONING_MODES[mode]
    profile = model_profile(model)
    return REASONING_MODES[profile["reasoning"]] if profile else None


def resolve_sort(model: str, choice: str) -> str | None:
    """'auto' uses the model profile (generic models: OpenRouter default routing); 'none' disables sorting."""
    if choice == "auto":
        return model_profile(model).get("provider_sort")
    return None if choice == "none" else choice


def provider_preferences(reasoning: dict | None, sort: str | None) -> dict | None:
    """Require providers to honour the reasoning setting; optional dev-only routing sort."""
    preferences: dict = {}
    if reasoning is not None:
        preferences["require_parameters"] = True
    if sort:
        preferences["sort"] = sort
    return preferences or None
GENERATION_MAX_TOKENS = 16_000
REPAIR_MAX_TOKENS = 7_000
PLAN_MAX_TOKENS = 3_000  # reasoning precedes the visible plan; 3k + 16k generation < 24k soft cap
MAX_REPAIRS = 2
MAX_RETRIES_PER_CALL = 1
MIN_RETRY_TOKENS = 2_000
MIN_REGENERATION_TOKENS = 8_000
TRUNCATED_NOTE = ("the previous response was cut off at the completion-token limit before END_COMPUTE; "
                  "reason briefly and write compact JSON without indentation")
PAGE_PROBE_SECONDS = 2.0
PAGE_OUTPUT_LEAVES = 128  # templates/runtime.js caps numeric leaves across all outputs combined


def _leaves(value: Any) -> int:
    return sum(_leaves(v) for v in value) if isinstance(value, list) else 1
FETCH_SECONDS = 3.0
FETCH_MAX_BYTES = 6 * 1024 * 1024
EXTRACT_MAX_CHARS = 400_000
COLLABORATOR_SECONDS = 60.0
FINISH_MARGIN_SECONDS = 5.0

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 2


class InputError(ValueError):
    pass


# ------------------------------------------------------------------ helpers

def load_dotenv(path: Path = Path(".env")) -> None:
    """Load KEY=VALUE lines without overriding the real environment."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def read_case(path: Path) -> tuple[dict[str, str], list[str]]:
    """Return every string field (all forwarded) and the names of ignored fields."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        raise InputError("input file does not exist") from None
    except (OSError, UnicodeDecodeError, ValueError):
        raise InputError("input is not readable UTF-8 JSON") from None
    if not isinstance(payload, dict):
        raise InputError("input JSON must be an object")
    case = {str(k): v for k, v in payload.items() if isinstance(v, str)}
    ignored = sorted(str(k) for k, v in payload.items() if not isinstance(v, str))
    missing = [name for name in REQUIRED_FIELDS if not case.get(name, "").strip()]
    if missing:
        raise InputError("missing required string fields: " + ", ".join(missing))
    return case, ignored


def guarded_call(fn: Callable, *args: Any, timeout: float) -> Any:
    """Run fn in a daemon thread; raise TimeoutError if it outlives timeout."""
    box: dict = {}

    def target() -> None:
        try:
            box["value"] = fn(*args)
        except BaseException as exc:  # re-raised in the caller's thread
            box["error"] = exc

    worker = threading.Thread(target=target, daemon=True)
    worker.start()
    worker.join(max(0.0, timeout))
    if worker.is_alive():
        raise TimeoutError(f"exceeded {timeout:.0f}s")
    if "error" in box:
        raise box["error"]
    return box.get("value")


def write_atomic(path: Path, text: str) -> None:
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(temp, path)


def fallback_page(reason: str) -> str:
    safe = html_lib.escape(reason)
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            "<title>Generation incomplete</title></head><body style=\"font-family:sans-serif;"
            "max-width:40rem;margin:2rem auto;padding:0 1rem\"><h1>Generation incomplete</h1>"
            f"<p>The interactive explanation could not be produced: {safe}</p>"
            "<p>No scientific content is shown because none was verified.</p></body></html>")


# ------------------------------------------------------------------ source fetch

class FetchFailure(ValueError):
    """A specific, safe-to-trace reason the source text could not be used."""


class _TextExtractor(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "head", "nav", "footer"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self.SKIP:
            self._skip += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "section", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self.parts.append(data)


def _normalize(text: str) -> str:
    text = re.sub(r"[ \t\f\v]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def _extract_pdf(data: bytes, deadline: float, clock: Callable[[], float]) -> tuple[str, bool]:
    """Extract page text until the shared fetch deadline or the character cap."""
    from pypdf import PdfReader  # optional dependency owned by requirements.txt

    parts, size = [], 0
    reader = PdfReader(io.BytesIO(data))
    for page in reader.pages:
        if clock() > deadline or size > EXTRACT_MAX_CHARS:
            if not parts:
                raise FetchFailure("fetch deadline reached after download, before any PDF page was extracted")
            return "\n".join(parts), True
        text = page.extract_text() or ""
        parts.append(text)
        size += len(text)
    return "\n".join(parts), False


def select_passages(text: str, focus: str, limit: int = MAX_SOURCE_CHARS) -> str:
    """Keep the opening chunk plus the chunks sharing most words with the focus."""
    if len(text) <= limit:
        return text
    chunk = 1500
    chunks = [text[i:i + chunk] for i in range(0, len(text), chunk)]
    words = {w for w in re.findall(r"[a-z][a-z0-9-]{3,}", focus.lower())}
    scores = [sum(c.lower().count(w) for w in words) for c in chunks]
    order = [0] + sorted(range(1, len(chunks)), key=lambda i: -scores[i])
    keep: list[int] = []
    for index in order:
        if (len(keep) + 1) * chunk > limit:
            break
        keep.append(index)
    return "\n[...]\n".join(chunks[i] for i in sorted(keep))


def fetch_source(url: str, focus: str, *, opener: Callable = urllib.request.urlopen,
                 clock: Callable[[], float] = time.monotonic) -> dict:
    started = clock()
    result: dict = {"status": "failed", "kind": None, "text": "", "truncated": False, "bytes": 0}
    if urlparse(url).scheme not in {"http", "https"}:
        result.update(status="skipped", error="unsupported URL scheme")
        return result

    def download() -> tuple[bytes, str, bool]:
        request = urllib.request.Request(url, headers={"User-Agent": "paper-playground/1.0"})
        with opener(request, timeout=FETCH_SECONDS) as response:
            ctype = response.headers.get("Content-Type", "") if response.headers else ""
            data = response.read(FETCH_MAX_BYTES + 1)
        return data[:FETCH_MAX_BYTES], ctype, len(data) > FETCH_MAX_BYTES

    try:
        data, ctype, capped = guarded_call(download, timeout=FETCH_SECONDS)
        result["bytes"] = len(data)
        if data.lstrip()[:5] == b"%PDF-" or "pdf" in ctype.lower():
            result["kind"] = "pdf"
            if capped:
                raise FetchFailure("PDF exceeded the byte cap")
            text, truncated = _extract_pdf(data, started + FETCH_SECONDS, clock)
        else:
            decoded = data.decode("utf-8", errors="replace")
            if "html" in ctype.lower() or decoded.lstrip()[:1] == "<":
                result["kind"] = "html"
                parser = _TextExtractor()
                parser.feed(decoded)
                text = "".join(parser.parts)
            else:
                result["kind"] = "text"
                text = decoded
            truncated = capped
        text = _normalize(text)
        if not text:
            raise FetchFailure(f"no extractable text in the {result['kind']} source")
        selected = select_passages(text, focus)
        result.update(status="ok", text=selected, chars=len(text),
                      truncated=truncated or len(selected) < len(text))
    except ImportError:
        result["error"] = "PDF text extraction unavailable"
    except FetchFailure as exc:
        result["error"] = str(exc)
    except TimeoutError:
        result["error"] = f"download did not finish within {FETCH_SECONDS:g} s"
    except Exception as exc:  # any fetch failure is traced, then generation proceeds
        result["error"] = type(exc).__name__
    result["seconds"] = round(clock() - started, 3)
    return result


# ------------------------------------------------------------------ page interpreter probe

def page_compute_check(spec: dict, root: Path = Path(__file__).resolve().parent) -> dict | None:
    """Run compute through the page's own numeric interpreter (QuickJS) on defaults, presets and tests.

    Checks may execute compute as full JavaScript, but the page runs a smaller language; a compute that
    only the larger engine accepts would pass checks and still leave the page without numbers. Returns
    None when the renderer, interpreter or engine is unavailable (nothing is claimed in that case).
    """
    try:
        import quickjs
        from runtime import merge_inputs, numeric_shape, parse_compute
        interpreter = (root / "templates" / "interpreter.js").read_text(encoding="utf-8")
    except Exception:
        return None
    check = {"id": "page_interpreter", "status": "pass", "target": "compute_js", "tier": "numerical"}
    try:
        ast = json.dumps(parse_compute(spec["compute_js"]))
    except Exception as exc:
        return {**check, "status": "fail", "detail": f"page interpreter rejects compute: {exc}"[:300]}
    controls = spec.get("controls", [])
    probes = [("default", {})]
    probes += [(f"exploration_{i + 1}", e.get("preset", {})) for i, e in enumerate(spec.get("explorations", []))]
    probes += [(f"test_{i + 1}", t.get("inputs", {})) for i, t in enumerate(spec.get("tests", []))]
    declared = {o.get("id") for o in spec.get("outputs", [])}
    for name, preset in probes:
        try:
            inputs = json.dumps(merge_inputs(controls, preset))
            context = quickjs.Context()
            context.set_time_limit(PAGE_PROBE_SECONDS)
            context.set_memory_limit(64 * 1024 * 1024)
            call = f"JSON.stringify(NumericRuntime.run({ast}, {inputs}, NumericRuntime.budget()))"
            result = json.loads(context.eval(interpreter + "\n" + call))
            if set(result) != declared:
                return {**check, "status": "fail", "detail": f"{name}: page compute returns {sorted(result)}, "
                                                             f"declared outputs are {sorted(declared)}"}
            for key in sorted(declared):
                try:
                    numeric_shape(result[key])  # the page's own rule: finite, rectangular, each axis <= 8
                except Exception as exc:
                    return {**check, "status": "fail", "detail": f"{name}: output {key}: {exc}"}
            leaves = sum(_leaves(result[key]) for key in declared)
            if leaves > PAGE_OUTPUT_LEAVES:
                return {**check, "status": "fail",
                        "detail": f"{name}: outputs hold {leaves} numbers; the page shows at most {PAGE_OUTPUT_LEAVES} in total"}
        except Exception as exc:
            reason = str(exc).splitlines()[0] if str(exc) else type(exc).__name__
            return {**check, "status": "fail", "detail": f"{name}: page interpreter error: {reason}"[:300]}
    return {**check, "detail": f"{len(probes)} probes ran in the page interpreter"}


# ------------------------------------------------------------------ candidates

@dataclass
class Candidate:
    spec: dict
    html: str
    report: dict
    rank: tuple
    safe: bool
    label: str


def normalize_report(report: Any) -> dict:
    if not (isinstance(report, dict) and isinstance(report.get("checks"), list)
            and isinstance(report.get("ok"), bool)):
        return {"ok": False, "degraded": True, "checks": [],
                "failures": ["checks returned a malformed report"], "revisions": []}
    report.setdefault("degraded", False)
    report.setdefault("failures", [])
    report.setdefault("revisions", [])
    report["checks"] = [c for c in report["checks"] if isinstance(c, dict)]
    return report


def rank_report(report: dict) -> tuple[tuple, bool]:
    """Lower is better. Uses per-check tiers when checks provide them."""
    checks = report["checks"]
    failed = [c for c in checks if c.get("status") == "fail"]
    safe = not any(c.get("tier") == "safety" for c in failed)
    if any("tier" in c for c in checks):
        def count(tier: str, status: str = "fail") -> int:
            return sum(1 for c in checks if c.get("tier", "structural") == tier and c.get("status") == status)
        detail = (count("safety"), count("numerical"), count("structural"),
                  count("numerical", "skip"), count("advisory"))
    else:
        skipped = sum(1 for c in checks if c.get("status") == "skip")
        detail = (0, len(report["failures"]), len(failed), skipped, 0)
    return (int(not report["ok"]),) + detail, safe


# Words in check targets/details that name a top-level Spec key.
_KEY_WORDS = {key: key for key in REVISABLE_KEYS} | {
    "symbol": "symbols", "control": "controls", "output": "outputs", "visual": "visuals",
    "exploration": "explorations", "preset": "explorations", "test": "tests", "expected": "tests",
    "invariant": "invariants", "compute": "compute_js"}
# Failures in the rendered page are renderer defects; revising the spec cannot fix them.
PAGE_TARGETS = {"html", "page", "runtime", "render", "template"}


def repair_targets(report: dict) -> tuple[list[str], list[dict]]:
    """Spec keys to revise, and the failed checks a spec revision can address."""
    targets: list[str] = []
    fixable: list[dict] = []
    for check in report["checks"]:
        if check.get("status") != "fail":
            continue
        target = check.get("target") if isinstance(check.get("target"), str) else ""
        head = re.split(r"[.\[:/ ]", target.strip().lower(), maxsplit=1)[0]
        if head in PAGE_TARGETS:
            continue
        fixable.append(check)
        # A direct target may need reference-dependent keys too; keys named only in the detail text
        # (field-level schema findings) are revised alone to keep repairs small.
        keys = expand_requested([_KEY_WORDS[head]]) if head in _KEY_WORDS else []
        keys += [_KEY_WORDS[word] for word in re.findall(r"[a-z_]+", str(check.get("detail", "")).lower())
                 if word in _KEY_WORDS]
        for key in keys:
            if key not in targets:
                targets.append(key)
    return targets, fixable


def schema_targets(errors: list[str]) -> list[str]:
    """Spec keys named by schema error paths. A whole-list controls error (e.g. the 128-leaf input cap) is
    fixed by changing shapes or controls, so the keys that reference control IDs and shapes may change too."""
    keys = error_targets(errors)
    if any(error.startswith("controls:") for error in errors):
        keys += [key for key in expand_requested(["controls"]) if key not in keys]
    return keys


# ------------------------------------------------------------------ runner

class Runner:
    def __init__(self, args: argparse.Namespace, *, budget: Budget, environ: dict,
                 client_factory: Callable, fetcher: Callable, render: Callable | None,
                 run_checks: Callable | None, write_trace: Callable | None, clock: Callable) -> None:
        self.args = args
        self.budget = budget
        self.environ = environ
        self.client_factory = client_factory
        self.fetcher = fetcher
        self.render = render
        self.run_checks = run_checks
        self.write_trace = write_trace
        self.clock = clock
        self.out = Path(args.output)
        self.trace_path = self.out / "trace.jsonl"
        self.index_path = self.out / "index.html"
        self.trace_ok = write_trace is not None
        self.best: Candidate | None = None
        self.revisions: list[dict] = []
        self.identified = False
        self.calls_blocked = False
        self.usage_totals = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
                             "total_tokens": 0, "unverified_attempts": 0}
        self.rejected: Candidate | None = None
        self.repair_base: dict | None = None  # schema-invalid but parsed generation; base for targeted repair
        self.case: dict[str, str] = {}
        self._secret = ""

    # -- trace
    def _scrub(self, value: Any) -> Any:
        if isinstance(value, str):
            return value.replace(self._secret, "[redacted]") if self._secret else value
        if isinstance(value, list):
            return [self._scrub(v) for v in value]
        if isinstance(value, dict):
            return {k: self._scrub(v) for k, v in value.items()}
        return value

    def emit(self, stage: str, action: str, result: str, *, prompt_tokens: int | None = None,
             completion_tokens: int | None = None, checks: list | None = None,
             failures: list | None = None, revisions: list | None = None, details: dict | None = None) -> None:
        event = self._scrub({
            "stage": stage, "action": action, "result": result,
            "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
            "elapsed_seconds": round(self.budget.elapsed(), 3),
            "checks": checks or [], "failures": [str(f) for f in (failures or [])],
            "revisions": revisions or [], "details": details or {},
        })
        if self.write_trace is None:
            return
        try:
            self.write_trace(str(self.trace_path), event)
        except Exception as exc:
            self.trace_ok = False
            print(f"trace write failed: {type(exc).__name__}", file=sys.stderr)

    # -- model calls
    def tally(self, usage: dict) -> None:
        """Add one attempt's API-reported usage; unreported usage is counted, never guessed."""
        if not usage.get("verified"):
            self.usage_totals["unverified_attempts"] += 1
        for key in ("prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens"):
            if isinstance(usage.get(key), int):
                self.usage_totals[key] += usage[key]

    def call(self, client: OpenRouterClient, stage: str, action: str,
             messages: list[dict[str, str]], max_tokens: int) -> str | None:
        for attempt in range(1 + MAX_RETRIES_PER_CALL):
            if attempt:
                # A failed attempt keeps its whole reservation charged; retry within what the hard cap leaves.
                max_tokens = min(max_tokens, self.budget.completion_left())
                if max_tokens < MIN_RETRY_TOKENS:
                    self.emit(stage, action, "skip", details={"reason": "too few completion tokens left to retry",
                                                              **self.budget.snapshot()})
                    return None
            try:
                text, usage = client.call_model(messages, max_tokens)
            except BudgetExceeded as exc:
                self.emit(stage, action, "skip", details={"reason": str(exc), **self.budget.snapshot()})
                return None
            except ModelCallError as exc:
                usage = client.last_call.get("usage", {})
                self.tally(usage)
                self.emit(stage, action, "fail", prompt_tokens=usage.get("prompt_tokens"),
                          completion_tokens=usage.get("completion_tokens"), failures=[str(exc)],
                          details={**client.last_call, "retryable": exc.retryable, "attempt": attempt + 1})
                if not exc.retryable:
                    self.calls_blocked = True  # e.g. bad key or unknown model: further calls cannot help
                elif attempt < MAX_RETRIES_PER_CALL:
                    continue
                return None
            except Exception as exc:
                self.emit(stage, action, "fail", failures=[f"client error: {type(exc).__name__}"],
                          details=dict(client.last_call))
                return None
            self.tally(usage)
            self.emit(stage, action, "pass" if text.strip() else "fail",
                      prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"),
                      failures=[] if text.strip() else ["empty visible response"],
                      details={**client.last_call, "attempt": attempt + 1})
            return text if text.strip() else None
        return None

    # -- candidates
    def collaborator_timeout(self) -> float:
        return min(COLLABORATOR_SECONDS, self.budget.finish_seconds_left() - FINISH_MARGIN_SECONDS)

    def evaluate(self, spec: dict, label: str, stage: str) -> Candidate | None:
        if self.collaborator_timeout() <= 0:
            self.emit("check", f"{label}:skipped", "skip", failures=["finish deadline reached"])
            return None
        if self.render is None:
            self.emit(stage, f"{label}:render", "fail", failures=["renderer unavailable"])
            return None
        try:
            page = guarded_call(self.render, spec, timeout=self.collaborator_timeout())
            if not isinstance(page, str) or not page.strip():
                raise TypeError("render returned no HTML text")
        except Exception as exc:
            self.emit(stage, f"{label}:render", "fail", failures=[f"render failed: {type(exc).__name__}"])
            return None
        self.emit(stage, f"{label}:render", "pass", details={"html_chars": len(page)})
        if self.run_checks is None:
            report = normalize_report(None)
            report["failures"] = ["checks unavailable"]
        else:
            try:
                report = normalize_report(guarded_call(self.run_checks, spec, page,
                                                       timeout=self.collaborator_timeout()))
            except Exception as exc:
                report = normalize_report(None)
                report["failures"] = [f"checks failed to run: {type(exc).__name__}"]
        page_check = page_compute_check(spec)
        if page_check is not None:
            report["checks"].append(page_check)
            if page_check["status"] == "fail":
                report["ok"] = False
                report["failures"].append(f"page_interpreter: {page_check['detail']}")
        rank, safe = rank_report(report)
        result = "pass" if report["ok"] else "fail"
        self.emit("check", label, result, checks=report["checks"], failures=report["failures"],
                  details={"degraded": bool(report["degraded"]), "rank": list(rank), "safe": safe})
        return Candidate(spec, page, report, rank, safe, label)

    def consider(self, candidate: Candidate | None) -> bool:
        if candidate is None:
            return False
        if not candidate.safe:
            self.rejected = candidate  # never written; its failures drive the next repair
            return False
        if self.best is not None and candidate.rank >= self.best.rank:
            return False
        self.best = candidate
        write_atomic(self.index_path, candidate.html)
        return True

    def identify(self, spec: dict, plan_from_call: bool) -> None:
        if self.identified:
            return
        self.identified = True
        start = spec.get("starting_point", {})
        self.emit("identify", "from_spec", "info", details={
            "title": spec.get("title"), "idea": start.get("idea"), "audience": spec.get("audience")})
        if not plan_from_call:
            self.emit("plan", "from_spec", "info", details={"plan": str(spec.get("plan", ""))[:600]})

    # -- main flow
    def execute(self) -> int:
        try:
            self.case, ignored = read_case(Path(self.args.input))
        except InputError as exc:
            self.emit("read_input", "load_case", "fail", failures=[str(exc)])
            return self.finish(EXIT_USAGE, str(exc))
        bounded = {}
        for key, value in list(self.case.items()):
            if key != "source_url" and len(value) > MAX_FIELD_CHARS:
                self.case[key] = select_passages(value, self.case["focus"], MAX_FIELD_CHARS)
                bounded[key] = [len(value), len(self.case[key])]
        self.emit("read_input", "load_case", "pass", details={
            "fields": sorted(self.case), "ignored_non_string_fields": ignored,
            "chars": {k: len(v) for k, v in self.case.items()}, "bounded_fields": bounded})

        source = self.fetcher(self.case["source_url"], self.case["focus"])
        self.emit("fetch", "source_url", "pass" if source.get("status") == "ok" else "fail",
                  failures=[] if source.get("status") == "ok" else [str(source.get("error", source.get("status")))],
                  details={k: source.get(k) for k in ("status", "kind", "bytes", "chars", "truncated", "seconds")})

        api_key = self.environ.get("OPENROUTER_API_KEY", "").strip()
        if not api_key:
            self.emit("generate", "credentials", "fail", failures=["OPENROUTER_API_KEY is not set"])
            return self.finish(EXIT_FAILED, "the model API key was not configured")
        self._secret = api_key
        client = self.client_factory(self.args.model, api_key, self.budget)

        plan = None
        if self.args.flow == "planned" and self.budget.allows_optional_call(PLAN_MAX_TOKENS + GENERATION_MAX_TOKENS):
            text = self.call(client, "plan", "request", build_plan_messages(self.case, source), PLAN_MAX_TOKENS)
            if text:
                plan = text.strip()[:800]
                self.emit("plan", "teaching_plan", "info", details={"plan": plan})

        errors: list[str] = []
        text = self.call(client, "generate", "request",
                         build_generation_messages(self.case, source, plan), GENERATION_MAX_TOKENS)
        if text is None:
            errors = ["the generation call returned no usable response"]
        else:
            try:
                spec = parse_spec(text)
                self.emit("generate", "parse", "pass")
                self.identify(spec, plan is not None)
                self.consider(self.evaluate(spec, "generation", "generate"))
            except SpecError as exc:
                errors = exc.errors
                if exc.spec is not None and error_targets(errors):
                    self.repair_base = exc.spec
                if client.last_call.get("finish_reason") == "length":
                    errors = [TRUNCATED_NOTE] + errors
                self.emit("generate", "parse", "fail", failures=errors[:40])

        for number in range(1, MAX_REPAIRS + 1):
            if (self.best is not None and self.best.report["ok"]) or self.calls_blocked:
                break
            if not self.budget.allows_optional_call(REPAIR_MAX_TOKENS):
                self.emit("revision", f"revision_{number}", "skip", details={
                    "reason": "soft token, request or time budget", **self.budget.snapshot()})
                break
            if not self.repair(client, source, number, plan, errors):
                break
            last = self.revisions[-1]
            errors = last.get("errors", errors if last.get("call_failed") else [])

        if self.best is None:
            return self.finish(EXIT_FAILED, "no valid specification was produced within the limits")
        if not self.best.report["ok"]:
            return self.finish(EXIT_FAILED, "the best candidate still has required check failures")
        return self.finish(EXIT_OK, "")

    def repair(self, client: OpenRouterClient, source: dict, number: int,
               plan: str | None, errors: list[str]) -> bool:
        """One repair request. Returns False when no actionable failure exists."""
        record: dict = {"number": number, "accepted": False}
        base = self.best.spec if self.best is not None else self.repair_base
        if self.best is None and self.repair_base is not None and error_targets(errors):
            # The generation parsed but broke field-level schema rules: revise only those keys.
            requested = schema_targets(errors)
            record.update(mode="targeted", requested=requested)
            messages = build_repair_messages(self.case, self.repair_base, errors, requested)
            max_tokens = REPAIR_MAX_TOKENS
        elif self.best is None:
            if not errors and self.rejected is not None:
                errors = [f"{c.get('id')}: {c.get('detail')}" for c in self.rejected.report["checks"]
                          if c.get("status") == "fail"]
            if not errors:
                return False  # nothing parsed and nothing demonstrated; a blind retry is not a repair
            record.update(mode="full", requested=list(SPEC_KEYS))
            messages = build_generation_messages(self.case, source, plan, errors)
            # Nothing usable exists yet, so spend what the hard cap allows (the soft cap guards repairs only).
            max_tokens = min(GENERATION_MAX_TOKENS, self.budget.completion_left())
            if max_tokens < MIN_REGENERATION_TOKENS:
                self.emit("revision", f"revision_{number}", "skip", details={
                    "reason": "too few completion tokens left for a complete response", **self.budget.snapshot()})
                return False
        else:
            report = self.best.report
            targets, fixable = repair_targets(report)
            if not fixable and not errors:
                if any(c.get("status") == "fail" for c in report["checks"]):
                    self.emit("revision", f"revision_{number}", "skip", failures=report["failures"],
                              details={"reason": "remaining failures are in the rendered page, not the specification"})
                return False  # skips/degraded only, or renderer defects: no spec repair can help
            targets += [key for key in schema_targets(errors) if key not in targets]
            requested = targets or [k for k in SPEC_KEYS if k in REVISABLE_KEYS]
            failures = [f"{c.get('id')}: {c.get('detail')}" for c in fixable] + \
                       [f"previous revision rejected: {e}" for e in errors]
            record.update(mode="targeted", requested=requested)
            messages = build_repair_messages(self.case, self.best.spec, failures, requested)
            max_tokens = REPAIR_MAX_TOKENS
        self.emit("revision", f"revision_{number}:targets", "info", revisions=[dict(record)])
        text = self.call(client, "revision", f"revision_{number}", messages, max_tokens)
        if text is None:
            record["call_failed"] = True
            self.revisions.append(record)
            return True
        try:
            spec = parse_spec(text) if record["mode"] == "full" else merge_revision(base, text, record["requested"])
        except SpecError as exc:
            record["errors"] = exc.errors[:40]
            self.revisions.append(record)
            self.emit("revision", f"revision_{number}:parse", "fail", failures=exc.errors[:40],
                      revisions=[{k: v for k, v in record.items() if k != "errors"}])
            return True
        self.emit("revision", f"revision_{number}:parse", "pass")
        self.identify(spec, plan is not None)
        record["accepted"] = self.consider(self.evaluate(spec, f"revision_{number}", "revision"))
        self.revisions.append(record)
        self.emit("revision", f"revision_{number}:result", "pass" if record["accepted"] else "fail",
                  revisions=[record], failures=[] if record["accepted"] else ["candidate not better than retained page"])
        return True

    def finish(self, code: int, reason: str) -> int:
        if self.best is None:
            try:
                write_atomic(self.index_path, fallback_page(reason or "generation did not complete"))
            except OSError:
                code = EXIT_FAILED
        if not self.identified:
            self.emit("identify", "from_spec", "fail", failures=["no valid specification"])
        if code == EXIT_OK and not self.trace_ok:
            code, reason = EXIT_FAILED, "trace could not be written"
        best = self.best
        self.emit("final", "write_output", "pass" if code == EXIT_OK else "fail",
                  failures=[reason] if reason else [], revisions=self.revisions, details={
                      "exit_code": code, "candidate": best.label if best else None,
                      "degraded": bool(best and best.report.get("degraded")),
                      "checks_ok": bool(best and best.report["ok"]), **self.budget.snapshot(),
                      "usage_totals": dict(self.usage_totals),
                      "repairs": {"attempted": len(self.revisions),
                                  "accepted": sum(1 for r in self.revisions if r.get("accepted"))}})
        if code == EXIT_OK and best and best.report.get("degraded"):
            print("completed in degraded mode: execution checks were skipped", file=sys.stderr)
        elif code != EXIT_OK:
            print(f"failed: {reason}", file=sys.stderr)
        return code


# ------------------------------------------------------------------ entry point

def _resolve(module: str, name: str) -> Callable | None:
    try:
        return getattr(__import__(module), name, None)
    except Exception:
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate an offline interactive explanation from a case file.")
    parser.add_argument("--input", required=True, help="case JSON file")
    parser.add_argument("--output", required=True, help="output directory")
    parser.add_argument("--model", required=True, help="OpenRouter model ID used for every call")
    parser.add_argument("--flow", choices=("single", "planned"), default="single",
                        help="planned adds a planning call; kept only for development comparisons (rejected on evidence)")
    parser.add_argument("--provider-sort", choices=("auto", "throughput", "latency", "none"), default="auto",
                        help="OpenRouter provider routing order; auto uses the model profile")
    parser.add_argument("--reasoning", choices=sorted(REASONING_MODES) + ["auto"], default=DEFAULT_REASONING,
                        help="OpenRouter reasoning control for every call")
    return parser


_DEFAULT = object()


def run(argv: list[str] | None = None, *, environ: dict | None = None, client_factory: Callable | None = None,
        fetcher: Callable | None = None, render: Any = _DEFAULT, run_checks: Any = _DEFAULT,
        write_trace: Any = _DEFAULT, clock: Callable[[], float] = time.monotonic) -> int:
    budget = Budget(clock=clock)  # monotonic origin before any input is read
    args = build_parser().parse_args(argv)
    if environ is None:
        load_dotenv()
        environ = dict(os.environ)
    out = Path(args.output)
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "trace.jsonl").write_text("", encoding="utf-8")  # fresh trace per run
        write_atomic(out / "index.html", fallback_page("generation is still in progress or was interrupted"))
    except OSError as exc:
        print(f"cannot prepare output directory: {type(exc).__name__}", file=sys.stderr)
        return EXIT_FAILED
    runner = Runner(
        args, budget=budget, environ=environ,
        client_factory=client_factory or (lambda model, key, b: OpenRouterClient(
            model, key, b, reasoning=resolve_reasoning(model, args.reasoning),
            provider=provider_preferences(resolve_reasoning(model, args.reasoning),
                                          resolve_sort(model, args.provider_sort)))),
        fetcher=fetcher or fetch_source,
        render=_resolve("runtime", "render") if render is _DEFAULT else render,
        run_checks=_resolve("checks", "run_checks") if run_checks is _DEFAULT else run_checks,
        write_trace=_resolve("trace", "write_trace") if write_trace is _DEFAULT else write_trace,
        clock=clock,
    )
    try:
        return runner.execute()
    except Exception as exc:  # last resort: keep the retained page and report honestly
        return runner.finish(EXIT_FAILED, f"internal error: {type(exc).__name__}")


def main() -> int:
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
