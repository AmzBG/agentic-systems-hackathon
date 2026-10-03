"""Pure structural and numerical checks for a generated teaching page.

Generated JavaScript is executed only in a bounded QuickJS child process. The
checker has no network calls or file writes and always reports skipped checks.
"""

from __future__ import annotations

import json
import math
import multiprocessing
import queue
import re
from html.parser import HTMLParser
from typing import Any


KINDS = {"slider", "number", "toggle", "select", "vector", "matrix"}
VISUALS = {"bar", "line", "heatmap", "values"}
INVARIANTS = {"finite", "range", "sum", "row_sum", "nondecreasing"}
ID = re.compile(r"^[a-z][a-z0-9_]*$")
FORBIDDEN = re.compile(
    r"\b(?:eval|Function|globalThis|window|document|self|fetch|XMLHttpRequest|"
    r"WebSocket|Worker|import|require|process|navigator|localStorage|"
    r"sessionStorage|constructor|prototype|__proto__|Date|setTimeout|"
    r"setInterval|while|with|this)\b|\bMath\s*\.\s*random\b|\bfor\s*\(\s*;\s*;"
)


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _shape(value: Any, depth: int = 0) -> tuple[int, ...] | None:
    if _number(value):
        return ()
    if depth >= 3 or not isinstance(value, list) or not 1 <= len(value) <= 128:
        return None
    first = _shape(value[0], depth + 1)
    if first is None or any(_shape(item, depth + 1) != first for item in value[1:]):
        return None
    result = (len(value), *first)
    return result if math.prod(result) <= 128 else None


def _leaves(value: Any) -> list[float]:
    return [number for item in value for number in _leaves(item)] if isinstance(value, list) else [float(value)]


def _valid_value(control: dict, value: Any) -> bool:
    kind = control.get("kind")
    if kind == "toggle":
        return isinstance(value, bool)
    if kind == "select":
        options = control.get("options")
        if not isinstance(options, list):
            return False
        return isinstance(value, str) and value in {
            option.get("value") for option in options if isinstance(option, dict)
        }
    if kind not in {"slider", "number", "vector", "matrix"}:
        return False
    low, high = control.get("min"), control.get("max")
    if not (_number(low) and _number(high) and low <= high):
        return False
    if kind in {"slider", "number"}:
        return _number(value) and low <= value <= high
    dimensions = control.get("shape")
    if not isinstance(dimensions, list) or len(dimensions) != (1 if kind == "vector" else 2):
        return False
    if any(not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 8 for n in dimensions):
        return False
    return _shape(value) == tuple(dimensions) and all(low <= n <= high for n in _leaves(value))


def _schema_errors(spec: Any) -> list[str]:
    if not isinstance(spec, dict):
        return ["spec must be an object"]
    errors: list[str] = []
    if spec.get("version") != 1:
        errors.append("version must be 1")
    for field in ("plan", "title", "audience", "limitation"):
        if not _text(spec.get(field)):
            errors.append(f"{field} is empty")
    starting = spec.get("starting_point")
    if not isinstance(starting, dict) or any(not _text(starting.get(k)) for k in ("idea", "why", "explanation")):
        errors.append("starting_point needs idea, why, explanation")
    symbols = spec.get("symbols")
    if not isinstance(symbols, list) or not symbols or any(
        not isinstance(s, dict) or any(not _text(s.get(k)) for k in ("symbol", "meaning", "units"))
        for s in symbols
    ):
        errors.append("symbols need text, meaning, and units")
    controls, outputs, visuals = (spec.get(k) for k in ("controls", "outputs", "visuals"))
    if not isinstance(controls, list) or len(controls) < 2:
        errors.append("at least two controls required")
        controls = []
    if not isinstance(outputs, list) or len(outputs) < 2:
        errors.append("intermediate and result outputs required")
        outputs = []
    if not isinstance(visuals, list) or not visuals:
        errors.append("at least one visual required")
        visuals = []
    seen: set[str] = set()
    for group, items in (("control", controls), ("output", outputs), ("visual", visuals)):
        for item in items:
            if not isinstance(item, dict):
                errors.append(f"{group} is not an object")
                continue
            name = item.get("id")
            if not isinstance(name, str) or not ID.fullmatch(name) or name in seen:
                errors.append(f"invalid or duplicated {group} id {name!r}")
            else:
                seen.add(name)
    control_map = {x["id"]: x for x in controls if isinstance(x, dict) and isinstance(x.get("id"), str)}
    output_map = {x["id"]: x for x in outputs if isinstance(x, dict) and isinstance(x.get("id"), str)}
    for control in controls:
        if not isinstance(control, dict):
            continue
        kind = control.get("kind")
        if kind not in KINDS:
            errors.append(f"unsupported control kind {kind!r}")
            continue
        if any(not _text(control.get(k)) for k in ("label", "help", "units")):
            errors.append(f"control {control.get('id')} lacks label, help, or units")
        if kind in {"slider", "number", "vector", "matrix"} and (
            not _number(control.get("step")) or control["step"] <= 0
        ):
            errors.append(f"control {control.get('id')} needs positive step")
        if kind == "select":
            options = control.get("options")
            if not isinstance(options, list) or len(options) < 2 or any(
                not isinstance(option, dict) or not _text(option.get("value")) or not _text(option.get("label"))
                for option in options
            ):
                errors.append(f"control {control.get('id')} needs two labeled options")
        if not _valid_value(control, control.get("default")):
            errors.append(f"control {control.get('id')} has invalid default or bounds")
    roles = {item.get("role") for item in outputs if isinstance(item, dict)}
    if not {"intermediate", "result"}.issubset(roles):
        errors.append("outputs need intermediate and result roles")
    for output in outputs:
        if isinstance(output, dict) and (
            output.get("role") not in {"intermediate", "result"}
            or not _text(output.get("label")) or not _text(output.get("units"))
        ):
            errors.append(f"invalid output metadata {output.get('id')}")
    for visual in visuals:
        if not isinstance(visual, dict):
            continue
        if visual.get("kind") not in VISUALS or visual.get("output") not in output_map:
            errors.append(f"invalid visual kind/output {visual.get('id')}")
        if any(not _text(visual.get(k)) for k in ("title", "x_label", "y_label")):
            errors.append(f"visual {visual.get('id')} needs title and axes")
        if visual.get("kind") == "line":
            sweep = visual.get("sweep")
            control = control_map.get(sweep.get("control")) if isinstance(sweep, dict) else None
            if not control or control.get("kind") not in {"slider", "number"} or not (
                _number(sweep.get("min")) and _number(sweep.get("max"))
                and control["min"] <= sweep["min"] < sweep["max"] <= control["max"]
                and isinstance(sweep.get("points"), int) and not isinstance(sweep.get("points"), bool)
                and 2 <= sweep["points"] <= 41
            ):
                errors.append(f"line visual {visual.get('id')} has invalid sweep")
    explorations = spec.get("explorations")
    if not isinstance(explorations, list) or len(explorations) != 2:
        errors.append("exactly two explorations required")
    else:
        for index, item in enumerate(explorations, 1):
            if not isinstance(item, dict) or any(not _text(item.get(k)) for k in ("title", "instruction", "observe", "why")):
                errors.append(f"exploration {index} lacks guidance")
                continue
            preset = item.get("preset")
            if not isinstance(preset, dict) or not preset or any(
                k not in control_map or not _valid_value(control_map[k], v) for k, v in preset.items()
            ):
                errors.append(f"exploration {index} has invalid preset")
    grounding = spec.get("grounding")
    if not isinstance(grounding, list) or not grounding or any(
        not isinstance(item, dict)
        or any(not _text(item.get(k)) for k in ("paper", "locator", "claim"))
        or item.get("support") not in {"excerpt", "example", "simplification", "unverified"}
        for item in grounding
    ):
        errors.append("grounding needs a paper, locator, supported claim")
    tests = spec.get("tests")
    if not isinstance(tests, list) or len(tests) < 2:
        errors.append("at least two numerical tests required")
    else:
        for index, test in enumerate(tests, 1):
            if not isinstance(test, dict):
                errors.append(f"test {index} is not an object")
                continue
            inputs, expected = test.get("inputs"), test.get("expected")
            if not _text(test.get("name")) or not isinstance(inputs, dict) or not isinstance(expected, dict) or not expected:
                errors.append(f"test {index} needs name, inputs, expected")
                continue
            if any(k not in control_map or not _valid_value(control_map[k], v) for k, v in inputs.items()):
                errors.append(f"test {index} has invalid inputs")
            if any(k not in output_map or _shape(v) is None for k, v in expected.items()):
                errors.append(f"test {index} has invalid expected outputs")
            if any(not _number(test.get(k)) or test[k] < 0 for k in ("atol", "rtol")):
                errors.append(f"test {index} has invalid tolerance")
    invariants = spec.get("invariants")
    if not isinstance(invariants, list) or not invariants:
        errors.append("at least one invariant required")
    else:
        for index, item in enumerate(invariants, 1):
            if not isinstance(item, dict) or not _text(item.get("name")) or item.get("output") not in output_map or item.get("kind") not in INVARIANTS:
                errors.append(f"invariant {index} has invalid metadata")
                continue
            if any(not _number(item.get(k)) or item[k] < 0 for k in ("atol", "rtol")):
                errors.append(f"invariant {index} has invalid tolerance")
            if item["kind"] in {"sum", "row_sum"} and not _number(item.get("expected")):
                errors.append(f"invariant {index} needs expected sum")
            if item["kind"] == "range" and not (
                _number(item.get("min")) and _number(item.get("max")) and item["min"] <= item["max"]
            ):
                errors.append(f"invariant {index} needs finite bounds")
    if not _text(spec.get("compute_js")):
        errors.append("compute_js is missing")
    return errors[:25]


def _safe_compute(code: str) -> str | None:
    if len(code) > 30_000 or "`" in code or "/*" in code or "//" in code:
        return "compute has excessive length, comments, or template strings"
    if FORBIDDEN.search(code):
        return "compute refers to ambient APIs, dynamic evaluation, or unbounded loops"
    start = re.match(r"\s*function\s+compute\s*\(\s*inputs\s*\)\s*\{", code)
    if not start:
        return "compute must be one function compute(inputs) declaration"
    quote, escaped, depth = None, False, 1
    for index in range(start.end(), len(code)):
        char = code[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char in {"'", '"'}:
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return None if not code[index + 1 :].strip(" \t\r\n;") else "executable text follows compute"
    return "compute has unmatched braces"


class _HTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag.lower(), {k.lower(): v or "" for k, v in attrs}))


def _html_errors(html: Any) -> list[str]:
    if not isinstance(html, str) or len(html) < 200:
        return ["page is missing or too short"]
    errors: list[str] = []
    lower = html.lower()
    if "<html" not in lower or "</html>" not in lower:
        errors.append("page is not complete HTML")
    if "<style" not in lower or "<script" not in lower:
        errors.append("page lacks embedded CSS or JavaScript")
    if not any(x in lower for x in ("<svg", "<canvas", "createelementns", "getcontext")):
        errors.append("page has no inline visual drawing")
    if "addeventlistener" not in lower:
        errors.append("page has no addEventListener control wiring")
    if re.search(r"\b(?:fetch|XMLHttpRequest|WebSocket)\s*\(", html):
        errors.append("page contains a runtime network request")
    if re.search(r"@import\s+|url\(\s*['\"]?https?://", html, re.I):
        errors.append("page loads remote styles or images")
    if "openrouter_api_key" in lower or re.search(r"\bsk-or-[A-Za-z0-9_-]+\b", html):
        errors.append("page appears to contain a credential")
    parser = _HTML()
    try:
        parser.feed(html)
    except Exception:
        errors.append("HTML parsing failed")
    for tag, attrs in parser.tags:
        for key in attrs:
            if key.startswith("on"):
                errors.append(f"inline event handler: {key}")
        url = attrs.get("src", "") if tag in {"script", "img", "iframe", "source", "video", "audio", "embed"} else attrs.get("href", "") if tag == "link" else ""
        if url.lower().startswith(("https://", "http://", "//")):
            errors.append(f"remote asset in {tag}")
    return errors[:20]


def _probes(spec: dict) -> list[tuple[str, dict, str | None, dict | None]]:
    defaults = {c["id"]: c["default"] for c in spec["controls"]}
    result: list[tuple[str, dict, str | None, dict | None]] = [("default", defaults, None, None)]
    for index, item in enumerate(spec["explorations"], 1):
        result.append((f"exploration_{index}", {**defaults, **item["preset"]}, None, None))
    for index, item in enumerate(spec["tests"], 1):
        result.append((f"test_{index}", {**defaults, **item["inputs"]}, None, item))
    for control in spec["controls"]:
        kind, name = control["kind"], control["id"]
        if kind in {"slider", "number"}:
            values = [control["min"], (control["min"] + control["max"]) / 2, control["max"]]
        elif kind == "toggle":
            values = [False, True]
        elif kind == "select":
            values = [item["value"] for item in control["options"]]
        elif kind == "vector":
            count, low, high = control["shape"][0], control["min"], control["max"]
            values = [[low] * count, [high] * count]
            for index in range(count):
                changed = [low] * count
                changed[index] = high
                values.append(changed)
        else:
            rows, columns = control["shape"]
            low, high = control["min"], control["max"]
            values = [[[n] * columns for _ in range(rows)] for n in (low, high)]
            for row in range(rows):
                for column in range(columns):
                    changed = [[low] * columns for _ in range(rows)]
                    changed[row][column] = high
                    values.append(changed)
        for index, value in enumerate(values):
            result.append((f"control_{name}_{index}", {**defaults, name: value}, name, None))
            if len(result) >= 80:
                return result
    for visual in spec["visuals"]:
        if visual["kind"] == "line" and len(result) + 3 <= 80:
            sweep = visual["sweep"]
            for index, value in enumerate((sweep["min"], (sweep["min"] + sweep["max"]) / 2, sweep["max"])):
                result.append((f"line_{visual['id']}_{index}", {**defaults, sweep["control"]: value}, None, None))
    return result


def _worker(code: str, probes: list[tuple[str, dict, str | None, dict | None]], result_queue: Any) -> None:
    try:
        import quickjs

        results = []
        for name, inputs, _, _ in probes:
            # A fresh context makes each probe independent. Otherwise a function
            # property retained across calls can imitate control influence.
            ctx = quickjs.Context()
            ctx.set_memory_limit(16 * 1024 * 1024)
            ctx.set_max_stack_size(512 * 1024)
            ctx.set_time_limit(0.08)
            ctx.eval(code)
            source = """(() => {
              const reads=[];
              const data=INPUTS;
              const before=JSON.stringify(data);
              const tracked=new Proxy(data,{get(target,key){
                if(typeof key==='string' && Object.prototype.hasOwnProperty.call(target,key)) reads.push(key);
                return target[key];
              }});
              const value=compute(tracked);
              return JSON.stringify({value,reads:[...new Set(reads)],mutated:JSON.stringify(data)!==before});
            })()""".replace("INPUTS", json.dumps(inputs, ensure_ascii=True, allow_nan=False))
            raw = ctx.eval(source)
            if not isinstance(raw, str):
                raise ValueError("compute returned nonserializable output")
            results.append((name, json.loads(raw)))
        result_queue.put(("ok", results))
    except ImportError:
        result_queue.put(("unavailable", "quickjs is unavailable"))
    except Exception as exc:
        result_queue.put(("failed", f"{type(exc).__name__}: {str(exc)[:120]}"))


def _execute(code: str, probes: list[tuple[str, dict, str | None, dict | None]]) -> tuple[str, Any]:
    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue(maxsize=1)
    child = context.Process(target=_worker, args=(code, probes, result_queue), daemon=True)
    try:
        child.start()
        try:
            result = result_queue.get(timeout=5)
        except queue.Empty:
            return "failed", "compute exceeded five seconds or exited without a result"
        return result
    except Exception as exc:
        return "unavailable", f"JavaScript engine could not start: {type(exc).__name__}"
    finally:
        if child.is_alive():
            child.terminate()
        if child.pid is not None:
            child.join(timeout=1)
        result_queue.close()


def _close(actual: Any, expected: Any, atol: float, rtol: float) -> bool:
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(
            _close(a, e, atol, rtol) for a, e in zip(actual, expected)
        )
    return _number(actual) and _number(expected) and abs(actual - expected) <= atol + rtol * abs(expected)


def _invariant(item: dict, value: Any) -> bool:
    kind, shape = item["kind"], _shape(value)
    if shape is None:
        return False
    if kind == "finite":
        return True
    atol, rtol = item["atol"], item["rtol"]
    if kind == "range":
        tolerance = atol + rtol * max(abs(item["min"]), abs(item["max"]))
        return all(item["min"] - tolerance <= n <= item["max"] + tolerance for n in _leaves(value))
    if kind == "sum":
        return len(shape) == 1 and _close(sum(value), item["expected"], atol, rtol)
    if kind == "row_sum":
        return len(shape) == 2 and all(_close(sum(row), item["expected"], atol, rtol) for row in value)
    if kind == "nondecreasing":
        return len(shape) == 1 and all(
            left <= right + atol + rtol * abs(right) for left, right in zip(value, value[1:])
        )
    return False


def _invariant_evidence(item: dict, value: Any) -> str:
    kind = item["kind"]
    if kind == "range":
        leaves = _leaves(value) if _shape(value) is not None else []
        measured = [min(leaves), max(leaves)] if leaves else value
        expected: Any = [item["min"], item["max"]]
    elif kind == "sum":
        measured = sum(value) if _shape(value) and len(_shape(value)) == 1 else value
        expected = item["expected"]
    elif kind == "row_sum":
        measured = [sum(row) for row in value] if _shape(value) and len(_shape(value)) == 2 else value
        expected = item["expected"]
    else:
        measured = value
        expected = "finite" if kind == "finite" else "nondecreasing"
    return (
        f"measured={str(measured)[:160]} expected={str(expected)[:80]} "
        f"atol={item['atol']} rtol={item['rtol']}"
    )


def run_checks(spec: dict, html: str) -> dict:
    """Return the frozen CheckReport shape with genuine failures and skips."""
    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    def add(name: str, status: str, detail: str, target: str | None = None) -> None:
        checks.append({"id": name, "status": status, "detail": detail, "target": target})
        if status == "fail":
            failures.append(f"{name}: {detail}")

    try:
        schema_errors = _schema_errors(spec)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        schema_errors = [f"malformed spec metadata ({type(exc).__name__})"]
    add("spec_schema", "fail" if schema_errors else "pass", "; ".join(schema_errors) or "v1 schema valid", "spec")
    html_errors = _html_errors(html)
    add("offline_html", "fail" if html_errors else "pass", "; ".join(html_errors) or "self-contained page", "html")
    if schema_errors:
        add("numerical_execution", "skip", "schema failed; compute was not executed", "compute_js")
        return {"ok": False, "degraded": True, "checks": checks, "failures": failures, "revisions": []}
    code_error = _safe_compute(spec["compute_js"])
    add("compute_safety", "fail" if code_error else "pass", code_error or "pure function shape", "compute_js")
    if code_error:
        add("numerical_execution", "skip", "unsafe code was not executed", "compute_js")
        return {"ok": False, "degraded": True, "checks": checks, "failures": failures, "revisions": []}
    probes = _probes(spec)
    status, payload = _execute(spec["compute_js"], probes)
    if status == "unavailable":
        add("numerical_execution", "skip", str(payload), "compute_js")
        return {"ok": not failures, "degraded": True, "checks": checks, "failures": failures, "revisions": []}
    if status != "ok":
        add("numerical_execution", "fail", str(payload), "compute_js")
        return {"ok": False, "degraded": False, "checks": checks, "failures": failures, "revisions": []}
    result_map = dict(payload)
    default = result_map.get("default", {}).get("value")
    output_ids = {item["id"] for item in spec["outputs"]}
    watched = {item["id"] for item in spec["outputs"] if item["role"] == "result"}
    watched.update(item["output"] for item in spec["visuals"])
    meaningful: set[str] = set()
    probe_errors: list[str] = []
    for name, _, changed_control, test in probes:
        record = result_map.get(name)
        if not isinstance(record, dict) or not isinstance(record.get("value"), dict):
            probe_errors.append(f"{name}: compute did not return an object")
            continue
        values = record["value"]
        if record.get("mutated") is True:
            probe_errors.append(f"{name}: compute mutated its inputs")
        extra_outputs = set(values) - output_ids
        if extra_outputs:
            probe_errors.append(f"{name}: undeclared outputs {', '.join(sorted(extra_outputs))}")
        for output_id in output_ids:
            if output_id not in values or _shape(values[output_id]) is None:
                probe_errors.append(f"{name}: {output_id} missing or nonfinite")
        for visual in spec["visuals"]:
            value = values.get(visual["output"])
            shape = _shape(value)
            required = {"bar": 1, "line": 0, "heatmap": 2}.get(visual["kind"])
            if required is not None and (shape is None or len(shape) != required):
                probe_errors.append(f"{name}: visual {visual['id']} has wrong output shape")
        for invariant in spec["invariants"]:
            target = values.get(invariant["output"])
            if target is None or not _invariant(invariant, target):
                probe_errors.append(
                    f"{name}: invariant {invariant['name']} failed "
                    f"({_invariant_evidence(invariant, target)})"
                )
        if test:
            for output_id, expected in test["expected"].items():
                if output_id not in values or not _close(values[output_id], expected, test["atol"], test["rtol"]):
                    probe_errors.append(
                        f"{name}: expected {output_id} failed "
                        f"(measured={str(values.get(output_id))[:160]} expected={str(expected)[:160]} "
                        f"atol={test['atol']} rtol={test['rtol']})"
                    )
        if changed_control and changed_control in record.get("reads", []) and isinstance(default, dict):
            if any(
                output_id in values and output_id in default
                and not _close(values[output_id], default[output_id], 1e-9, 1e-9)
                for output_id in watched
            ):
                meaningful.add(changed_control)
    if len(probe_errors) > 10:
        probe_errors = probe_errors[:10] + ["additional probe failures omitted"]
    add("numerical_execution", "fail" if probe_errors else "pass", "; ".join(probe_errors) or f"{len(probes)} bounded probes passed", "compute_js")
    add("two_meaningful_controls", "pass" if len(meaningful) >= 2 else "fail", f"{len(meaningful)} distinct controls were read and changed a result or visual", "controls")
    return {"ok": not failures, "degraded": False, "checks": checks, "failures": failures, "revisions": []}
