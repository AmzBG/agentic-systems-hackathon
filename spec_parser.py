"""Parse and validate the v1 wire response into a Spec dictionary.

Wire format (delimiter lines, surrounding whitespace ignored):

    BEGIN_SPEC
    {metadata JSON without compute_js}
    END_SPEC
    BEGIN_COMPUTE
    function compute(inputs) { ... }
    END_COMPUTE

Outside the blocks only whitespace and one optional Markdown fence pair around
the whole response are allowed. One fence pair directly inside a block is
removed. Error messages name paths and reasons only, never echo model text.
"""

from __future__ import annotations

import copy
import json
import math
import re
from typing import Any

BEGIN_SPEC, END_SPEC = "BEGIN_SPEC", "END_SPEC"
BEGIN_COMPUTE, END_COMPUTE = "BEGIN_COMPUTE", "END_COMPUTE"
DELIMITERS = (BEGIN_SPEC, END_SPEC, BEGIN_COMPUTE, END_COMPUTE)

SPEC_KEYS = (
    "version", "plan", "title", "audience", "starting_point", "symbols", "controls",
    "outputs", "visuals", "explorations", "limitation", "grounding", "tests",
    "invariants", "compute_js",
)
REVISABLE_KEYS = frozenset(SPEC_KEYS) - {"version"}

CONTROL_KINDS = {"slider", "number", "toggle", "select", "vector", "matrix"}
VISUAL_KINDS = {"bar", "line", "heatmap", "values"}
OUTPUT_ROLES = {"intermediate", "result"}
SUPPORT_KINDS = {"excerpt", "example", "simplification", "unverified"}
INVARIANT_KINDS = {"finite", "range", "sum", "row_sum", "nondecreasing"}
MAX_AXIS = 8
MAX_LEAVES = 128
MAX_SWEEP_POINTS = 41
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
FENCE_RE = re.compile(r"^```[A-Za-z0-9_-]*$")
COMPUTE_HEAD_RE = re.compile(r"^function\s+compute\s*\(\s*inputs\s*\)\s*\{")
# Static deny-list; U3's checks remain the authoritative safety review.
FORBIDDEN_JS = re.compile(
    r"\b(?:eval|Function|import|require|fetch|XMLHttpRequest|WebSocket|EventSource|"
    r"document|window|globalThis|navigator|localStorage|sessionStorage|indexedDB|"
    r"Date|crypto|setTimeout|setInterval|setImmediate|queueMicrotask|Worker|"
    r"postMessage|constructor|__proto__|Reflect|Proxy)\b"
    r"|Math\s*\.\s*random|<\s*/\s*script"
)


class SpecError(ValueError):
    """Wire or schema violation; errors are 'path: reason' strings."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors[:12]) + (" ..." if len(errors) > 12 else ""))


# ---------------------------------------------------------------- wire layer

def _strip_fence_pair(lines: list[str]) -> list[str]:
    body = [line for line in lines]
    while body and not body[0].strip():
        body.pop(0)
    while body and not body[-1].strip():
        body.pop()
    if len(body) >= 2 and FENCE_RE.match(body[0].strip()) and body[-1].strip() == "```":
        return body[1:-1]
    return body


def split_wire(text: str, *, compute: str) -> tuple[str, str | None]:
    """Return (metadata_text, compute_text). compute: 'required'|'optional'|'forbidden'."""
    if not isinstance(text, str):
        raise SpecError(["response: not text"])
    lines = _strip_fence_pair(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
    marks: dict[str, list[int]] = {name: [] for name in DELIMITERS}
    for index, line in enumerate(lines):
        if line.strip() in marks:
            marks[line.strip()].append(index)
    errors = [f"wire: duplicate {name}" for name, at in marks.items() if len(at) > 1]
    for name in (BEGIN_SPEC, END_SPEC):
        if not marks[name]:
            errors.append(f"wire: missing {name}")
    has_begin, has_end = bool(marks[BEGIN_COMPUTE]), bool(marks[END_COMPUTE])
    if has_begin != has_end:
        errors.append("wire: unpaired compute delimiters")
    if compute == "required" and not (has_begin or has_end):
        errors.append("wire: missing compute block")
    if compute == "forbidden" and (has_begin or has_end):
        errors.append("wire: compute block was not requested")
    if errors:
        raise SpecError(errors)

    spec_start, spec_end = marks[BEGIN_SPEC][0], marks[END_SPEC][0]
    if spec_end < spec_start:
        raise SpecError(["wire: END_SPEC precedes BEGIN_SPEC"])
    spans = [(spec_start, spec_end)]
    if has_begin:
        compute_start, compute_end = marks[BEGIN_COMPUTE][0], marks[END_COMPUTE][0]
        if not spec_end < compute_start < compute_end:
            raise SpecError(["wire: compute block must follow the spec block"])
        spans.append((compute_start, compute_end))

    inside = {i for start, end in spans for i in range(start, end + 1)}
    if any(line.strip() for i, line in enumerate(lines) if i not in inside):
        raise SpecError(["wire: content outside the delimited blocks"])

    metadata = "\n".join(_strip_fence_pair(lines[spec_start + 1:spec_end]))
    compute_text = None
    if has_begin:
        compute_text = "\n".join(_strip_fence_pair(lines[spans[1][0] + 1:spans[1][1]])).strip()
    return metadata, compute_text


def _reject_constant(name: str) -> Any:
    raise ValueError("non-finite JSON constant")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def load_metadata(metadata: str) -> dict:
    try:
        data = json.loads(metadata, object_pairs_hook=_no_duplicate_keys, parse_constant=_reject_constant)
    except (ValueError, RecursionError) as exc:
        reason = str(exc).split(":")[0] if not isinstance(exc, json.JSONDecodeError) else exc.msg
        raise SpecError([f"metadata: invalid JSON ({reason})"]) from None
    if not isinstance(data, dict):
        raise SpecError(["metadata: must be a JSON object"])
    if "compute_js" in data:
        raise SpecError(["metadata.compute_js: code belongs in the compute block"])
    return data


# ---------------------------------------------------------------- public API

def parse_spec(text: str) -> dict:
    """Parse a complete wire response into a validated Spec dictionary."""
    metadata, compute_text = split_wire(text, compute="required")
    spec = load_metadata(metadata)
    spec["compute_js"] = compute_text
    validate_spec(spec)
    return spec


def merge_revision(base: dict, text: str, requested: list[str]) -> dict:
    """Apply a targeted revision on a copy of base and validate the result.

    Metadata may contain only requested top-level keys plus version; the
    compute block is allowed only when compute_js was requested. Each value
    replaces the base value wholesale; omitted requested keys keep the base.
    """
    wanted = set(requested)
    unknown = sorted(wanted - REVISABLE_KEYS)
    if not wanted or unknown:
        raise SpecError([f"revision: unsupported requested keys {unknown or '[]'}"])
    metadata, compute_text = split_wire(
        text, compute="optional" if "compute_js" in wanted else "forbidden")
    patch = load_metadata(metadata)
    errors = []
    if patch.get("version") != 1 or isinstance(patch.get("version"), bool):
        errors.append("revision.version: must be 1")
    extra = sorted(key for key in patch if key != "version" and key not in wanted)
    if extra:
        errors.append(f"revision: keys not requested {extra}")
    if errors:
        raise SpecError(errors)
    merged = copy.deepcopy(base)
    for key, value in patch.items():
        merged[key] = copy.deepcopy(value)
    if compute_text is not None:
        merged["compute_js"] = compute_text
    validate_spec(merged)
    return merged


# ---------------------------------------------------------------- validation

def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _leaf_count(value: Any) -> int:
    return sum(_leaf_count(item) for item in value) if isinstance(value, list) else 1


def _shape(value: Any) -> tuple[int, ...] | None:
    """Shape of a nonempty rectangular numeric tree, or None if invalid."""
    if _is_number(value):
        return ()
    if not isinstance(value, list) or not value or len(value) > MAX_AXIS:
        return None
    shapes = {_shape(item) for item in value}
    if len(shapes) != 1 or None in shapes:
        return None
    return (len(value),) + shapes.pop()


def check_numeric_tree(value: Any, path: str, errors: list[str]) -> None:
    if _shape(value) is None:
        errors.append(f"{path}: must be a finite number or nonempty rectangular numeric array (axis <= {MAX_AXIS})")
    elif _leaf_count(value) > MAX_LEAVES:
        errors.append(f"{path}: more than {MAX_LEAVES} values")


class _Validator:
    def __init__(self, spec: dict) -> None:
        self.spec = spec
        self.errors: list[str] = []
        self.controls: dict[str, dict] = {}
        self.outputs: dict[str, dict] = {}

    def err(self, path: str, reason: str) -> None:
        self.errors.append(f"{path}: {reason}")

    def text(self, obj: dict, key: str, path: str) -> None:
        if not _is_text(obj.get(key)):
            self.err(f"{path}.{key}" if path else key, "must be a nonblank string")

    def items(self, key: str, minimum: int, exact: int | None = None) -> list[dict]:
        value = self.spec.get(key)
        if not isinstance(value, list):
            self.err(key, "must be a list")
            return []
        if exact is not None and len(value) != exact:
            self.err(key, f"must contain exactly {exact} entries")
        elif len(value) < minimum:
            self.err(key, f"must contain at least {minimum} entries")
        good = []
        for index, item in enumerate(value):
            if isinstance(item, dict):
                good.append(item)
            else:
                self.err(f"{key}[{index}]", "must be an object")
        return good

    def tolerance(self, obj: dict, path: str) -> None:
        for key in ("atol", "rtol"):
            value = obj.get(key)
            if not _is_number(value) or value < 0:
                self.err(f"{path}.{key}", "must be a finite nonnegative number")

    def run(self) -> list[str]:
        spec = self.spec
        if spec.get("version") != 1 or isinstance(spec.get("version"), bool):
            self.err("version", "must be 1")
        for key in ("plan", "title", "audience", "limitation"):
            self.text(spec, key, "")
        starting = spec.get("starting_point")
        if isinstance(starting, dict):
            for key in ("idea", "why", "explanation"):
                self.text(starting, key, "starting_point")
        else:
            self.err("starting_point", "must be an object")
        for index, symbol in enumerate(self.items("symbols", 1)):
            for key in ("symbol", "meaning", "units"):
                if not isinstance(symbol.get(key), str):
                    self.err(f"symbols[{index}].{key}", "must be a string")
        self.check_controls()
        self.check_outputs()
        self.check_unique_ids()
        self.check_visuals()
        self.check_explorations()
        supports = set()
        for index, item in enumerate(self.items("grounding", 1)):
            path = f"grounding[{index}]"
            for key in ("paper", "locator", "claim"):
                self.text(item, key, path)
            if item.get("support") not in SUPPORT_KINDS:
                self.err(f"{path}.support", "unsupported value")
            supports.add(item.get("support"))
        # The brief requires identifying the paper. Labelling toy values is requested by the prompt but not
        # enforced here, because a limitation can also state it and the frozen schema does not require it.
        if isinstance(spec.get("grounding"), list) and not supports & {"excerpt", "unverified"}:
            self.err("grounding", "needs an entry citing the paper with support excerpt or unverified")
        self.check_tests()
        self.check_invariants()
        self.check_compute()
        return self.errors

    def check_controls(self) -> None:
        for index, control in enumerate(self.items("controls", 2)):
            path = f"controls[{index}]"
            cid = control.get("id")
            if not isinstance(cid, str) or not ID_RE.match(cid):
                self.err(f"{path}.id", "must match [a-z][a-z0-9_]*")
                continue
            for key in ("label", "help", "units"):
                if not isinstance(control.get(key), str):
                    self.err(f"{path}.{key}", "must be a string")
            self.text(control, "label", path)
            kind = control.get("kind")
            if kind not in CONTROL_KINDS:
                self.err(f"{path}.kind", "unsupported control kind")
                continue
            if kind in {"slider", "number", "vector", "matrix"}:
                lo, hi, step = control.get("min"), control.get("max"), control.get("step")
                if not (_is_number(lo) and _is_number(hi) and lo < hi):
                    self.err(path, "needs finite min < max")
                if not (_is_number(step) and step > 0):
                    self.err(f"{path}.step", "must be a finite positive number")
            if kind in {"vector", "matrix"}:
                shape = control.get("shape")
                rank = 1 if kind == "vector" else 2
                if not (isinstance(shape, list) and len(shape) == rank and all(
                        isinstance(n, int) and not isinstance(n, bool) and 1 <= n <= MAX_AXIS for n in shape)):
                    self.err(f"{path}.shape", f"must be {rank} integer(s) in 1..{MAX_AXIS}")
            if kind == "select":
                options = control.get("options")
                values = [o.get("value") for o in options if isinstance(o, dict)] if isinstance(options, list) else []
                if not options or len(values) != len(options) or not all(
                        isinstance(o.get("value"), str) and isinstance(o.get("label"), str) for o in options):
                    self.err(f"{path}.options", "must be a nonempty list of {value, label} strings")
                elif len(set(values)) != len(values):
                    self.err(f"{path}.options", "values must be unique")
            self.controls[cid] = control
            self.check_input(control, control.get("default"), f"{path}.default")

    def check_input(self, control: dict, value: Any, path: str) -> None:
        kind = control.get("kind")
        lo, hi = control.get("min"), control.get("max")
        bounded = _is_number(lo) and _is_number(hi)

        def in_bounds(number: Any) -> bool:
            return _is_number(number) and (not bounded or lo <= number <= hi)

        if kind in {"slider", "number"}:
            if not in_bounds(value):
                self.err(path, "must be a finite number within [min, max]")
        elif kind == "toggle":
            if not isinstance(value, bool):
                self.err(path, "must be a boolean")
        elif kind == "select":
            options = control.get("options") if isinstance(control.get("options"), list) else []
            if not isinstance(value, str) or value not in [o.get("value") for o in options if isinstance(o, dict)]:
                self.err(path, "must be one of the option values")
        elif kind in {"vector", "matrix"}:
            shape = control.get("shape")
            actual = _shape(value)
            if not isinstance(shape, list) or actual != tuple(shape):
                self.err(path, "must match the control shape exactly")
            elif not all(in_bounds(x) for x in (value if kind == "vector" else [c for row in value for c in row])):
                self.err(path, "every entry must be within [min, max]")

    def check_inputs_map(self, mapping: Any, path: str) -> None:
        if not isinstance(mapping, dict):
            self.err(path, "must be an object of control values")
            return
        for cid, value in mapping.items():
            if cid not in self.controls:
                self.err(f"{path}", "references an unknown control")
            else:
                self.check_input(self.controls[cid], value, f"{path}.{cid}")

    def check_outputs(self) -> None:
        roles = set()
        for index, output in enumerate(self.items("outputs", 2)):
            path = f"outputs[{index}]"
            oid = output.get("id")
            if not isinstance(oid, str) or not ID_RE.match(oid):
                self.err(f"{path}.id", "must match [a-z][a-z0-9_]*")
                continue
            self.text(output, "label", path)
            if not isinstance(output.get("units"), str):
                self.err(f"{path}.units", "must be a string")
            if output.get("role") not in OUTPUT_ROLES:
                self.err(f"{path}.role", "must be intermediate or result")
            roles.add(output.get("role"))
            self.outputs[oid] = output
        if not OUTPUT_ROLES <= roles:
            self.err("outputs", "need at least one intermediate and one result")

    def check_unique_ids(self) -> None:
        seen: set[str] = set()
        for key in ("controls", "outputs", "visuals"):
            entries = self.spec.get(key) if isinstance(self.spec.get(key), list) else []
            for index, item in enumerate(entries):
                ident = item.get("id") if isinstance(item, dict) else None
                if isinstance(ident, str):
                    if ident in seen:
                        self.err(f"{key}[{index}].id", "duplicates another control/output/visual ID")
                    seen.add(ident)

    def check_visuals(self) -> None:
        for index, visual in enumerate(self.items("visuals", 1)):
            path = f"visuals[{index}]"
            if not isinstance(visual.get("id"), str) or not ID_RE.match(visual["id"]):
                self.err(f"{path}.id", "must match [a-z][a-z0-9_]*")
            kind = visual.get("kind")
            if kind not in VISUAL_KINDS:
                self.err(f"{path}.kind", "unsupported visual kind")
            for key in ("title", "x_label", "y_label"):
                self.text(visual, key, path)
            if visual.get("output") not in self.outputs:
                self.err(f"{path}.output", "references an unknown output")
            labels = visual.get("labels")
            if labels is not None and not (isinstance(labels, list) and all(isinstance(x, str) for x in labels)):
                self.err(f"{path}.labels", "must be a list of strings")
            sweep = visual.get("sweep")
            if kind == "line":
                self.check_sweep(sweep, f"{path}.sweep")
            elif sweep is not None:
                self.err(f"{path}.sweep", "only line visuals sweep a control")

    def check_sweep(self, sweep: Any, path: str) -> None:
        if not isinstance(sweep, dict):
            self.err(path, "line visuals need a sweep")
            return
        control = self.controls.get(sweep.get("control"))
        if not control or control.get("kind") not in {"slider", "number"}:
            self.err(f"{path}.control", "must reference a slider or number control")
            return
        lo, hi, points = sweep.get("min"), sweep.get("max"), sweep.get("points")
        if not (_is_number(lo) and _is_number(hi) and lo < hi):
            self.err(path, "needs finite min < max")
        elif _is_number(control.get("min")) and _is_number(control.get("max")) and not (
                control["min"] <= lo and hi <= control["max"]):
            self.err(path, "range must lie within the control bounds")
        if not (isinstance(points, int) and not isinstance(points, bool) and 2 <= points <= MAX_SWEEP_POINTS):
            self.err(f"{path}.points", f"must be an integer in 2..{MAX_SWEEP_POINTS}")

    def check_explorations(self) -> None:
        for index, item in enumerate(self.items("explorations", 2, exact=2)):
            path = f"explorations[{index}]"
            for key in ("title", "instruction", "observe", "why"):
                self.text(item, key, path)
            self.check_inputs_map(item.get("preset"), f"{path}.preset")

    def check_tests(self) -> None:
        for index, test in enumerate(self.items("tests", 2)):
            path = f"tests[{index}]"
            self.text(test, "name", path)
            self.check_inputs_map(test.get("inputs"), f"{path}.inputs")
            expected = test.get("expected")
            if not isinstance(expected, dict) or not expected:
                self.err(f"{path}.expected", "must be a nonempty object of output values")
            else:
                for oid, value in expected.items():
                    if oid not in self.outputs:
                        self.err(f"{path}.expected", "references an unknown output")
                    else:
                        check_numeric_tree(value, f"{path}.expected.{oid}", self.errors)
            self.tolerance(test, path)

    def check_invariants(self) -> None:
        for index, item in enumerate(self.items("invariants", 1)):
            path = f"invariants[{index}]"
            self.text(item, "name", path)
            if item.get("output") not in self.outputs:
                self.err(f"{path}.output", "references an unknown output")
            kind = item.get("kind")
            if kind not in INVARIANT_KINDS:
                self.err(f"{path}.kind", "unsupported invariant kind")
            for key in ("min", "max", "expected"):
                if key in item and not _is_number(item[key]):
                    self.err(f"{path}.{key}", "must be a finite number")
            if kind == "range" and ("min" not in item or "max" not in item):
                self.err(path, "range needs both min and max")
            if kind == "range" and _is_number(item.get("min")) and _is_number(item.get("max")) and item["min"] > item["max"]:
                self.err(path, "min must not exceed max")
            if kind in {"sum", "row_sum"} and "expected" not in item:
                self.err(path, f"{kind} needs expected")
            self.tolerance(item, path)

    def check_compute(self) -> None:
        code = self.spec.get("compute_js")
        if not isinstance(code, str) or not code.strip():
            self.err("compute_js", "missing compute function")
            return
        if not COMPUTE_HEAD_RE.match(code) or not code.rstrip().endswith("}"):
            self.err("compute_js", "must be a single declaration 'function compute(inputs) { ... }'")
        if FORBIDDEN_JS.search(code):
            self.err("compute_js", "uses a forbidden global, API or construct")
        if len(code) > 20_000:
            self.err("compute_js", "longer than 20000 characters")


def validate_spec(spec: Any) -> None:
    """Raise SpecError listing every schema violation found."""
    if not isinstance(spec, dict):
        raise SpecError(["spec: must be an object"])
    errors = _Validator(spec).run()
    if errors:
        raise SpecError(errors)


def error_targets(errors: list[str]) -> list[str]:
    """Top-level Spec keys named by validation error paths (for targeted repair)."""
    targets = []
    for error in errors:
        head = re.split(r"[.\[:]", error, maxsplit=1)[0]
        if head in REVISABLE_KEYS and head not in targets:
            targets.append(head)
    return targets
