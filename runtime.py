"""Offline v1 teaching renderer. Compute source is parsed, never executed.

The deliberately small JavaScript language supports numeric teaching models;
unsupported syntax produces a readable degraded page rather than unsafe code.
Only standard-library Python and embedded, trusted browser code are used.
"""

import base64
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import re


class RuntimeSpecError(ValueError):
    """An unsafe or unsupported renderer input."""


_ID = re.compile(r"[a-z][a-z0-9_]*\Z")
_FORBIDDEN = frozenset("""__proto__ prototype constructor window document globalThis
    self parent top frames location navigator fetch XMLHttpRequest WebSocket
    import export eval Function Date performance crypto random setTimeout
    setInterval Worker SharedWorker WebAssembly Atomics Proxy Reflect
    process require module this new class async await yield with debugger
    try catch finally delete typeof instanceof in while do switch""".split())
_TOKEN = re.compile(
    r"\s+|//[^\n]*|/\*[\s\S]*?\*/|"
    r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|"
    r"\"(?:\\.|[^\"\\\r\n])*\"|'(?:\\.|[^'\\\r\n])*'|"
    r"[A-Za-z_$][A-Za-z0-9_$]*|===|!==|=>|\*\*|<=|>=|==|!=|&&|\|\||"
    r"\+\+|--|\+=|-=|\*=|/=|\.\.\.|[{}\[\]().,;:?+*/%<>=!\-]"
)


class _Parser:
    """Recursive-descent statements and Pratt expressions into inert JSON AST."""

    def __init__(self, source):
        if not isinstance(source, str) or len(source) > 65536:
            raise RuntimeSpecError("Compute source must be text, at most 65536 characters")
        self.tokens = []
        pos = 0
        while pos < len(source):
            match = _TOKEN.match(source, pos)
            if not match:
                raise RuntimeSpecError(f"Unsupported compute token at character {pos}")
            token = match.group()
            pos = match.end()
            if token.isspace() or token.startswith(("//", "/*")):
                continue
            if token in _FORBIDDEN:
                raise RuntimeSpecError(f"Unsafe or unsupported compute name: {token}")
            if token in ("==", "!="):
                raise RuntimeSpecError("Coercive equality is unsupported; use === or !==")
            if token == "var":
                raise RuntimeSpecError("Function-scoped var is unsupported; use let or const")
            self.tokens.append(token)
        if len(self.tokens) > 8192:
            raise RuntimeSpecError("Compute token limit exceeded")
        self.tokens.append("<end>")
        self.i = 0
        self.depth = 0

    def peek(self):
        return self.tokens[self.i]

    def take(self, token=None):
        value = self.peek()
        if token is not None and value != token:
            raise RuntimeSpecError(f"Expected {token!r}, found {value!r}")
        self.i += 1
        return value

    def accept(self, token):
        if self.peek() == token:
            self.take()
            return True
        return False

    def name(self):
        value = self.take()
        if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", value):
            raise RuntimeSpecError("Expected a local identifier")
        if value in _FORBIDDEN or value in {"Math", "Array", "Number"}:
            raise RuntimeSpecError(f"Reserved compute name: {value}")
        return value

    def params(self):
        self.take("(")
        params = []
        if self.peek() != ")":
            params.append(self.name())
            while self.accept(","):
                params.append(self.name())
        self.take(")")
        if len(params) != len(set(params)) or len(params) > 8:
            raise RuntimeSpecError("Duplicate or excessive function parameters")
        return params

    def block(self):
        self.take("{")
        body = []
        while self.peek() != "}":
            if self.peek() == "<end>":
                raise RuntimeSpecError("Unterminated compute block")
            body.append(self.statement())
        self.take("}")
        return ["block", body]

    def statement(self):
        self.depth += 1
        if self.depth > 48:
            raise RuntimeSpecError("Compute nesting limit exceeded")
        try:
            token = self.peek()
            if token == "{":
                return self.block()
            if token in ("let", "const", "var"):
                node = self.declaration()
                self.accept(";")
                return node
            if self.accept("function"):
                name = self.name()
                return ["decl", [[name, ["fn", self.params(), self.block()]]]]
            if self.accept("return"):
                node = ["return", self.expression()]
                self.accept(";")
                return node
            if self.accept("if"):
                self.take("(")
                cond = self.expression()
                self.take(")")
                yes = self.statement()
                no = self.statement() if self.accept("else") else ["block", []]
                return ["if", cond, yes, no]
            if self.accept("for"):
                self.take("(")
                if self.peek() not in ("let", "const", "var"):
                    raise RuntimeSpecError("For loops require a local loop variable")
                init = self.declaration()
                if self.accept("of"):
                    if len(init[1]) != 1 or init[1][0][1] != ["lit", None]:
                        raise RuntimeSpecError("Unsupported for-of declaration")
                    seq = self.expression()
                    self.take(")")
                    return ["each", init[1][0][0], seq, self.statement(), init[2]]
                self.take(";")
                cond = self.expression()
                self.take(";")
                step = self.expression()
                self.take(")")
                return ["for", init, cond, step, self.statement()]
            if token in ("break", "continue"):
                self.take()
                self.accept(";")
                return [token]
            if self.accept("throw"):
                node = ["throw", self.expression()]
                self.accept(";")
                return node
            if self.accept(";"):
                return ["block", []]
            node = ["expr", self.expression()]
            self.accept(";")
            return node
        finally:
            self.depth -= 1

    def declaration(self):
        kind = self.take()
        pairs = []
        while True:
            name = self.name()
            pairs.append([name, self.expression() if self.accept("=") else ["lit", None]])
            if not self.accept(","):
                break
        return ["decl", pairs, kind]

    _PRECEDENCE = {"=": 1, "+=": 1, "-=": 1, "*=": 1, "/=": 1,
                   "||": 3, "&&": 4, "==": 5, "!=": 5, "===": 5, "!==": 5,
                   "<": 6, ">": 6, "<=": 6, ">=": 6,
                   "+": 7, "-": 7, "*": 8, "/": 8, "%": 8, "**": 9}

    def expression(self, minimum=1):
        self.depth += 1
        if self.depth > 48:
            raise RuntimeSpecError("Compute nesting limit exceeded")
        try:
            left = self.primary()
            while True:
                op = self.peek()
                if op == "?" and minimum <= 2:
                    self.take()
                    yes = self.expression()
                    self.take(":")
                    left = ["cond", left, yes, self.expression(2)]
                    continue
                precedence = self._PRECEDENCE.get(op, 0)
                if precedence < minimum:
                    break
                self.take()
                right = self.expression(precedence if precedence == 1 or op == "**" else precedence + 1)
                if precedence == 1 and left[0] not in ("id", "get"):
                    raise RuntimeSpecError("Invalid assignment target")
                left = ["assign" if precedence == 1 else "bin", op, left, right]
            return left
        finally:
            self.depth -= 1

    def primary(self):
        token = self.take()
        if token in ("!", "-", "+"):
            return ["un", token, self.expression(10)]
        if token == "function":
            if self.peek() != "(":
                raise RuntimeSpecError("Function expressions must be anonymous")
            node = ["fn", self.params(), self.block()]
        elif token == "(":
            saved = self.i
            try:
                params = []
                if self.peek() != ")":
                    params.append(self.name())
                    while self.accept(","):
                        params.append(self.name())
                self.take(")")
                self.take("=>")
                if len(params) != len(set(params)) or len(params) > 8:
                    raise RuntimeSpecError("Invalid arrow parameters")
                node = ["fn", params, self.arrow_body()]
            except RuntimeSpecError:
                self.i = saved
                node = self.expression()
                self.take(")")
        elif token == "[":
            items = []
            while self.peek() != "]":
                items.append(self.expression())
                if not self.accept(","):
                    break
            self.take("]")
            node = ["array", items]
        elif token == "{":
            pairs = []
            while self.peek() != "}":
                key = self.take()
                if key.startswith(("'", '"')):
                    key = self.string(key)
                elif not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", key):
                    raise RuntimeSpecError("Unsupported object key")
                if key in _FORBIDDEN:
                    raise RuntimeSpecError("Unsafe object key")
                value = self.expression() if self.accept(":") else ["id", key]
                pairs.append([key, value])
                if not self.accept(","):
                    break
            self.take("}")
            if len({p[0] for p in pairs}) != len(pairs):
                raise RuntimeSpecError("Duplicate compute object key")
            node = ["object", pairs]
        elif token.startswith(("'", '"')):
            node = ["lit", self.string(token)]
        elif token in ("true", "false", "null"):
            node = ["lit", {"true": True, "false": False, "null": None}[token]]
        elif re.fullmatch(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", token):
            value = float(token)
            if not math.isfinite(value):
                raise RuntimeSpecError("Nonfinite compute literal")
            node = ["lit", value]
        elif re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", token):
            if self.accept("=>"):
                if token in {"Math", "Array", "Number"}:
                    raise RuntimeSpecError("Reserved arrow parameter")
                node = ["fn", [token], self.arrow_body()]
            else:
                node = ["id", token]
        else:
            raise RuntimeSpecError(f"Unsupported compute expression: {token}")
        while True:
            if self.accept("."):
                key = self.take()
                if not re.fullmatch(r"[A-Za-z_$][A-Za-z0-9_$]*", key) or key in _FORBIDDEN:
                    raise RuntimeSpecError("Unsafe compute property")
                node = ["get", node, ["lit", key]]
            elif self.accept("["):
                node = ["get", node, self.expression()]
                self.take("]")
            elif self.accept("("):
                args = []
                while self.peek() != ")":
                    args.append(["spread", self.expression()] if self.accept("...") else self.expression())
                    if not self.accept(","):
                        break
                self.take(")")
                node = ["call", node, args]
            elif self.peek() in ("++", "--"):
                if node[0] not in ("id", "get"):
                    raise RuntimeSpecError("Invalid update target")
                node = ["update", self.take(), node]
            else:
                break
        return node

    def arrow_body(self):
        return self.block() if self.peek() == "{" else ["return", self.expression(2)]

    @staticmethod
    def string(token):
        # Only JSON-like escapes are admitted; no host-language evaluation.
        value = token[1:-1]
        if token[0] == "'":
            value = value.replace('"', '\\"').replace("\\'", "'")
        try:
            result = json.loads('"' + value + '"')
        except ValueError as exc:
            raise RuntimeSpecError("Unsupported string escape") from exc
        if len(result) > 1024:
            raise RuntimeSpecError("Compute string limit exceeded")
        return result


def parse_compute(source: str) -> list:
    """Admit one pure declaration; produce inert AST with no executable source."""
    parser = _Parser(source)
    parser.take("function")
    parser.take("compute")
    if parser.params() != ["inputs"]:
        raise RuntimeSpecError("Compute must have exactly the inputs parameter")
    tree = ["fn", ["inputs"], parser.block()]
    parser.take("<end>")
    names = {"Math", "Array", "Number"}
    references = set()
    nodes = 0

    def walk(node, depth=0):
        nonlocal nodes
        nodes += 1
        if nodes > 4096 or depth > 64:
            raise RuntimeSpecError("Compute AST limit exceeded")
        kind = node[0]
        if kind == "id":
            references.add(node[1])
        elif kind == "get":
            if node[2][0] == "lit" and node[2][1] in _FORBIDDEN:
                raise RuntimeSpecError("Unsafe compute property")
            walk(node[1], depth + 1)
            walk(node[2], depth + 1)
        elif kind == "fn":
            names.update(node[1])
            walk(node[2], depth + 1)
        elif kind == "decl":
            for name, value in node[1]:
                names.add(name)
                walk(value, depth + 1)
        elif kind == "each":
            names.add(node[1])
            walk(node[2], depth + 1)
            walk(node[3], depth + 1)
        elif kind == "object":
            for _, value in node[1]:
                walk(value, depth + 1)
        elif kind in ("array", "block"):
            for child in node[1]:
                walk(child, depth + 1)
        elif kind == "call":
            walk(node[1], depth + 1)
            for child in node[2]:
                walk(child, depth + 1)
        elif kind not in ("lit", "break", "continue"):
            for child in node[1:]:
                if isinstance(child, list):
                    walk(child, depth + 1)
    walk(tree)
    if references - names:
        raise RuntimeSpecError("Unknown compute names: " + ", ".join(sorted(references - names)))
    return tree


def _finite(value):
    try:
        return type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        return False


def numeric_shape(value, depth=0):
    """Validate bounded finite rectangular numeric trees; return (shape, leaves)."""
    if _finite(value):
        return (), 1
    if not isinstance(value, list) or not 1 <= len(value) <= 8 or depth >= 8:
        raise RuntimeSpecError("Numeric values must be finite, nonempty and bounded")
    children = [numeric_shape(item, depth + 1) for item in value]
    if any(shape != children[0][0] for shape, _ in children):
        raise RuntimeSpecError("Numeric arrays must be rectangular")
    leaves = sum(count for _, count in children)
    if leaves > 128:
        raise RuntimeSpecError("Numeric leaf limit is 128")
    return (len(value),) + children[0][0], leaves


def validate_inputs(controls: list, values: dict, clamp=False) -> dict:
    """Return a fresh validated complete input dictionary."""
    if not isinstance(values, dict) or set(values) != {c["id"] for c in controls}:
        raise RuntimeSpecError("Inputs must contain exactly the declared controls")
    result = {}
    leaves = 0
    for control in controls:
        value = copy.deepcopy(values[control["id"]])
        kind = control["kind"]
        if kind == "toggle":
            if type(value) is not bool:
                raise RuntimeSpecError("Toggle requires a boolean")
        elif kind == "select":
            if not isinstance(value, str) or value not in [o["value"] for o in control["options"]]:
                raise RuntimeSpecError("Select value is not an available option")
        else:
            shape, count = numeric_shape(value)
            expected = tuple(control.get("shape", []))
            if shape != expected:
                raise RuntimeSpecError(f"Wrong shape for {control['id']}: expected {expected}")
            leaves += count
            def bounded(item):
                if isinstance(item, list):
                    return [bounded(x) for x in item]
                if clamp:
                    return min(control["max"], max(control["min"], item))
                if not control["min"] <= item <= control["max"]:
                    raise RuntimeSpecError(f"Out of bounds: {control['id']}")
                return item
            value = bounded(value)
        result[control["id"]] = value
    if leaves > 128:
        raise RuntimeSpecError("Total input numeric leaf limit is 128")
    return result


def merge_inputs(controls: list, preset: dict) -> dict:
    if not isinstance(preset, dict) or set(preset) - {c["id"] for c in controls}:
        raise RuntimeSpecError("Preset contains unknown controls")
    defaults = {c["id"]: copy.deepcopy(c["default"]) for c in controls}
    defaults.update(copy.deepcopy(preset))
    return validate_inputs(controls, defaults)


def validate_spec(spec: dict) -> None:
    """Renderer admission checks, independent of collaborator implementations."""
    def need(condition, message):
        if not condition:
            raise RuntimeSpecError(message)
    need(isinstance(spec, dict) and type(spec.get("version")) is int and spec["version"] == 1, "Expected v1 spec")
    for key in ("title", "audience", "plan", "limitation", "compute_js"):
        need(isinstance(spec.get(key), str), f"Missing text: {key}")
    start = spec.get("starting_point", {})
    need(isinstance(start, dict) and all(isinstance(start.get(k), str) for k in ("idea", "why", "explanation")), "Invalid starting point")
    for key in ("symbols", "grounding", "controls", "outputs", "visuals", "explorations", "tests", "invariants"):
        need(isinstance(spec.get(key), list) and len(spec[key]) <= 128, f"Invalid or excessive {key}")
    for key, fields in (("symbols", ("symbol", "meaning", "units")), ("grounding", ("paper", "locator", "support", "claim"))):
        for item in spec[key]:
            need(isinstance(item, dict) and all(isinstance(item.get(f), str) for f in fields), f"Invalid {key} entry")
    for item in spec["grounding"]:
        need(item["support"] in ("excerpt", "example", "simplification", "unverified"), "Invalid grounding support")
    need(len(spec["controls"]) >= 2 and len(spec["visuals"]) >= 1, "At least two controls and one visual required")
    ids = set()
    for key in ("controls", "outputs", "visuals"):
        for item in spec[key]:
            need(isinstance(item, dict) and isinstance(item.get("id"), str) and bool(_ID.fullmatch(item["id"])), "Invalid ID")
            need(item["id"] not in ids, "IDs must be globally unique")
            ids.add(item["id"])
    for c in spec["controls"]:
        need(all(isinstance(c.get(k), str) for k in ("label", "help", "units")), "Invalid control labels")
        need(c.get("kind") in ("slider", "number", "toggle", "select", "vector", "matrix"), "Unsupported control")
        if c["kind"] == "select":
            options = c.get("options")
            need(isinstance(options, list) and 1 <= len(options) <= 128, "Invalid select options")
            need(all(isinstance(o, dict) and isinstance(o.get("value"), str) and isinstance(o.get("label"), str) for o in options), "Invalid select option")
            need(len({o["value"] for o in options}) == len(options), "Duplicate select option")
        elif c["kind"] not in ("toggle",):
            need(all(_finite(c.get(k)) for k in ("min", "max", "step")) and c["min"] <= c["max"] and c["step"] > 0, "Invalid numeric bounds/step")
            if c["kind"] in ("vector", "matrix"):
                shape = c.get("shape")
                need(isinstance(shape, list) and len(shape) == (1 if c["kind"] == "vector" else 2) and all(type(d) is int and 1 <= d <= 8 for d in shape), "Invalid control shape")
            else:
                need("shape" not in c, "Scalar controls cannot have shape")
        need("default" in c, "Missing control default")
    merge_inputs(spec["controls"], {})
    outputs = {o["id"] for o in spec["outputs"]}
    roles = set()
    for o in spec["outputs"]:
        need(all(isinstance(o.get(k), str) for k in ("label", "units")), "Invalid output labels")
        need(o.get("role") in ("intermediate", "result"), "Invalid output role")
        roles.add(o["role"])
    need(roles == {"intermediate", "result"}, "Intermediate and result outputs required")
    controls = {c["id"]: c for c in spec["controls"]}
    for v in spec["visuals"]:
        need(v.get("kind") in ("bar", "line", "heatmap", "values") and v.get("output") in outputs, "Invalid visual/output reference")
        need(all(isinstance(v.get(k), str) for k in ("title", "x_label", "y_label")), "Invalid visual labels")
        if "labels" in v:
            need(isinstance(v["labels"], list) and len(v["labels"]) <= 8 and all(isinstance(x, str) for x in v["labels"]), "Invalid visual labels")
        if v["kind"] == "line":
            sweep = v.get("sweep", {})
            need(isinstance(sweep, dict) and sweep.get("control") in controls, "Missing sweep control")
            control = controls[sweep["control"]]
            need(control["kind"] in ("slider", "number"), "Sweep control must be numeric scalar")
            need(_finite(sweep.get("min")) and _finite(sweep.get("max")) and control["min"] <= sweep["min"] < sweep["max"] <= control["max"], "Invalid sweep bounds")
            need(type(sweep.get("points")) is int and 2 <= sweep["points"] <= 41, "Sweep points must be 2–41")
    need(len(spec["explorations"]) == 2, "Exactly two explorations required")
    for e in spec["explorations"]:
        need(isinstance(e, dict) and all(isinstance(e.get(k), str) for k in ("title", "instruction", "observe", "why")), "Invalid exploration text")
        merge_inputs(spec["controls"], e.get("preset"))
    need(len(spec["tests"]) >= 2 and len(spec["invariants"]) >= 1, "Declarative tests and invariants required")
    for t in spec["tests"] + spec["invariants"]:
        need(isinstance(t, dict) and isinstance(t.get("name"), str), "Invalid check name")
        need(all(_finite(t.get(k)) and t[k] >= 0 for k in ("atol", "rtol")), "Invalid check tolerances")
    for t in spec["tests"]:
        merge_inputs(spec["controls"], t.get("inputs"))
        expected = t.get("expected")
        need(isinstance(expected, dict) and bool(expected) and not set(expected) - outputs, "Invalid expected outputs")
        need(sum(numeric_shape(v)[1] for v in expected.values()) <= 128, "Expected output leaf limit exceeded")
    for t in spec["invariants"]:
        need(t.get("output") in outputs and t.get("kind") in ("finite", "range", "sum", "row_sum", "nondecreasing"), "Invalid invariant")
        if t["kind"] == "range":
            need(_finite(t.get("min")) and _finite(t.get("max")) and t["min"] <= t["max"], "Invalid invariant range")
        if t["kind"] in ("sum", "row_sum"):
            need(_finite(t.get("expected")), "Invalid invariant expected sum")


def _escape(value):
    return html.escape(str(value), quote=True)


def _serialize(value):
    text = json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _teaching(spec):
    """Static plain-text teaching content survives any compute failure."""
    esc = _escape
    start = spec.get("starting_point", {})
    parts = [f'<header><p class="eyebrow">Paper to Playground</p><h1>{esc(spec.get("title", "Teaching page"))}</h1>',
             f'<p class="lead">{esc(start.get("idea", ""))}</p>',
             f'<p class="why"><strong>Why it matters:</strong> {esc(start.get("why", ""))}</p>',
             '<details class="lesson-notes"><summary>About this lesson</summary>',
             f'<p><strong>Audience:</strong> {esc(spec.get("audience", ""))}</p>',
             f'<p><strong>Plan:</strong> {esc(spec.get("plan", ""))}</p></details></header>',
             '<section class="notation" aria-label="Symbols and units"><details open><summary>Symbols and units</summary><div class="scroll"><table><caption>Notation</caption><thead><tr><th scope="col">Symbol</th><th scope="col">Meaning</th><th scope="col">Units</th></tr></thead><tbody>']
    for s in spec.get("symbols", []):
        parts.append('<tr>' + ''.join(f'<td>{esc(s.get(k, ""))}</td>' for k in ("symbol", "meaning", "units")) + '</tr>')
    parts.append('</tbody></table></div></details></section>')
    introduction = ''.join(parts)
    parts = ['<section aria-labelledby="explorations"><h2 id="explorations">Experiments</h2>']
    for index, e in enumerate(spec.get("explorations", [])):
        parts.append(f'<article class="exploration"><h3>{index + 1}. {esc(e.get("title", ""))}</h3>')
        instruction = e.get("instruction", "").lstrip().removeprefix("Predict:").lstrip().removeprefix("Predict ")
        parts.append(f'<p class="prediction" id="prediction-{index}"><strong>Predict:</strong> {esc(instruction)}</p>')
        parts.append(f'<div class="exploration-actions"><button type="button" class="preset" data-preset="{index}" aria-describedby="prediction-{index}">Apply preset</button>')
        parts.append(' <a href="#results">View updated results</a></div>')
        parts.append(f'<div class="preset-result" id="preset-result-{index}" role="status" aria-live="polite"></div>')
        parts.append(f'<details class="exploration-feedback" id="feedback-{index}"><summary>Compare your prediction</summary>')
        for key, label in (("observe", "Observe"), ("why", "Explain")):
            parts.append(f'<p><strong>{label}:</strong> {esc(e.get(key, ""))}</p>')
        parts.append('</details></article>')
    parts.append('</section>')
    explorations = ''.join(parts)
    parts = [f'<section class="limitation"><h2>Limitation</h2><p>{esc(spec.get("limitation", ""))}</p></section>',
             '<section><h2>Source and grounding</h2><ul class="grounding-list">']
    support_labels = {"excerpt": "FROM PAPER", "example": "TOY EXAMPLE",
                      "simplification": "SIMPLIFICATION", "unverified": "UNVERIFIED"}
    for g in spec.get("grounding", []):
        support = g.get("support", "")
        label = support_labels.get(support, support)
        parts.append(f'<li><span class="badge" data-support="{esc(support)}">{esc(label)}</span> <strong>{esc(g.get("paper", ""))}</strong> — {esc(g.get("locator", ""))}<p>{esc(g.get("claim", ""))}</p></li>')
    parts.append('</ul></section>')
    return introduction, explorations, ''.join(parts)


def render(spec: dict) -> str:
    """Return one self-contained offline HTML page, including degraded states."""
    error = ""
    tree = None
    try:
        validate_spec(spec)
        tree = parse_compute(spec["compute_js"])
    except (RuntimeSpecError, KeyError, TypeError, ValueError, RecursionError) as exc:
        error = str(exc)
    # Retain plain teaching content on compute admission failure. Invalid schema
    # collections are not assumed safe enough to traverse.
    teaching_spec = spec if isinstance(spec, dict) else {}
    try:
        teaching, explorations, grounding = _teaching(teaching_spec)
    except (AttributeError, TypeError):
        teaching = '<h1>Teaching page</h1><p>Malformed teaching metadata.</p>'
        explorations = grounding = ''
    payload = {"spec": {k: v for k, v in teaching_spec.items() if k in (
        "controls", "outputs", "visuals", "explorations", "tests", "invariants")}, "ast": tree, "error": error}
    try:
        serialized = _serialize(payload)
    except (TypeError, ValueError, RecursionError):
        error = error or "Spec contains unserializable or nonfinite values"
        serialized = _serialize({"spec": {}, "ast": None, "error": error})
    base = Path(__file__).resolve().parent / "templates"
    css = (base / "runtime.css").read_text(encoding="utf-8")
    interpreter = (base / "interpreter.js").read_text(encoding="utf-8")
    browser = (base / "runtime.js").read_text(encoding="utf-8")
    script = '"use strict";\n' + interpreter + '\n' + browser + '\n'
    digest = base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
    status = "Degraded: " + error if error else "Calculation pending; JavaScript is required for interactive results."
    starting_point = teaching_spec.get("starting_point", {})
    mechanism = starting_point.get("explanation", "") if isinstance(starting_point, dict) else ""
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'sha256-{digest}\'; style-src \'unsafe-inline\'; img-src data:; connect-src \'none\'; object-src \'none\'; base-uri \'none\'; form-action \'none\'">'
            f'<title>{_escape(teaching_spec.get("title", "Teaching page"))}</title><style>{css}</style></head><body><main>{teaching}'
            f'<section class="workbench" aria-labelledby="calculate"><div class="workbench-heading"><h2 id="calculate">Try it</h2></div><p id="status" role="status" aria-live="polite">{_escape(status)}</p>'
            '<noscript>Degraded: JavaScript is disabled. Teaching content remains available; calculations and self-checks have not run.</noscript>'
            '<div class="workbench-grid"><section class="control-panel" aria-labelledby="input-heading"><h3 id="input-heading">Inputs</h3><a class="mobile-result-link" href="#principal-result">View current result</a><div id="controls"></div><a href="#explorations">Experiments</a></section><section class="live-panel" aria-labelledby="results"><h3 id="results" tabindex="-1">Calculation</h3><p id="result-status">No valid result yet.</p>'
            f'<p class="mechanism-note">{_escape(mechanism)}</p><div id="principal-result" tabindex="-1"></div>'
            '<div id="visuals"><div id="outputs"></div></div><p class="section-note">Plot labels are rounded; numeric tables show full precision.</p></section></div></section>'
            f'{explorations}'
            '<section class="verification"><h2>Self-check</h2><p id="check-status" role="status">Not run.</p><p>These checks test the specified examples and identities; they do not verify every claim in the explanation.</p><details><summary>Inspect measured values, expectations and tolerances</summary><ul id="checks"></ul></details></section>'
            f'{grounding}</main>'
            f'<script type="application/json" id="runtime-data">{serialized}</script><script>{script}</script></body></html>')
