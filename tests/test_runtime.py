"""Owned offline fixtures, unittest admission checks and HTML smoke writer.

Run interactive evidence separately in a browser: static tests do not execute JS.
"""
import copy
from html.parser import HTMLParser
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import unittest

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from runtime import (RuntimeSpecError, merge_inputs, numeric_shape, parse_compute,
                     render, validate_inputs, validate_spec)


def entropy_spec():
    return {
        "version": 1, "title": "Entropy of a discrete distribution", "audience": "Engineering students",
        "plan": "Normalize weights, inspect contributions, compare certainty and equal outcomes.",
        "starting_point": {"idea": "Entropy measures uncertainty.", "why": "Uncertain outcomes need more information.",
                           "explanation": "H = −sum p log2 p. Zero probabilities contribute zero. All-zero active weights use a uniform distribution."},
        "symbols": [{"symbol": "p", "meaning": "Outcome probability", "units": "dimensionless"},
                    {"symbol": "H", "meaning": "Entropy", "units": "bits"}],
        "controls": [
            {"id": "weights", "label": "Outcome weights", "help": "Nonnegative weights; only the active prefix is used.", "units": "dimensionless", "kind": "vector", "shape": [4], "default": [1, 1, 1, 1], "min": 0, "max": 10, "step": 0.1},
            {"id": "count", "label": "Active outcomes", "help": "Count is rounded down to a whole number.", "units": "outcomes", "kind": "number", "default": 4, "min": 1, "max": 4, "step": 1}],
        "outputs": [{"id": "probabilities", "label": "Normalized probabilities", "units": "dimensionless", "role": "intermediate"},
                    {"id": "contributions", "label": "Information contributions", "units": "bits", "role": "intermediate"},
                    {"id": "entropy", "label": "Total entropy", "units": "bits", "role": "result"}],
        "visuals": [{"id": "contribution_chart", "kind": "bar", "title": "Contributions to entropy", "output": "contributions", "x_label": "Outcome", "y_label": "Contribution", "labels": ["A", "B", "C", "D"]}],
        "explorations": [
            {"title": "Certainty", "instruction": "Put all weight on A.", "observe": "Entropy becomes zero.", "why": "The outcome is known.", "preset": {"weights": [1, 0, 0, 0]}},
            {"title": "Equal outcomes", "instruction": "Use four equal weights.", "observe": "Each contributes half a bit; total is two bits.", "why": "Four equally likely outcomes maximize entropy.", "preset": {"weights": [1, 1, 1, 1], "count": 4}}],
        "limitation": "A finite discrete distribution; no estimate of continuous entropy.",
        "grounding": [{"paper": "Shannon, A Mathematical Theory of Communication", "locator": "Section 6", "support": "example", "claim": "This teaching example illustrates discrete entropy."}],
        "tests": [
            {"name": "Certainty is zero bits", "inputs": {"weights": [1, 0, 0, 0]}, "expected": {"entropy": 0}, "atol": 1e-10, "rtol": 1e-10},
            {"name": "Four equal outcomes are two bits", "inputs": {}, "expected": {"entropy": 2, "contributions": [0.5, 0.5, 0.5, 0.5]}, "atol": 1e-10, "rtol": 1e-10},
            {"name": "All-zero weights use uniform policy", "inputs": {"weights": [0, 0, 0, 0], "count": 2}, "expected": {"entropy": 1, "probabilities": [0.5, 0.5]}, "atol": 1e-10, "rtol": 1e-10}],
        "invariants": [{"name": "Probabilities sum to one", "output": "probabilities", "kind": "sum", "expected": 1, "atol": 1e-10, "rtol": 1e-10},
                       {"name": "Entropy is finite", "output": "entropy", "kind": "finite", "atol": 0, "rtol": 0}],
        "compute_js": """function compute(inputs) {
          const n = Math.floor(inputs.count);
          const weights = inputs.weights.slice(0, n);
          const total = weights.reduce((s, w) => s + w, 0);
          const probabilities = weights.map(w => total > 0 ? w / total : 1 / n);
          const contributions = probabilities.map(p => p === 0 ? 0 : -p * Math.log2(p));
          const entropy = contributions.reduce((s, x) => s + x, 0);
          return {probabilities, contributions, entropy};
        }"""}


def all_kinds_spec():
    spec = entropy_spec()
    spec["controls"] += [
        {"id": "amplitude", "label": "Amplitude", "help": "Scale the field.", "units": "V", "kind": "slider", "default": 1, "min": -2, "max": 2, "step": 0.1},
        {"id": "negate", "label": "Negate", "help": "Reverse sign.", "units": "", "kind": "toggle", "default": False},
        {"id": "mode", "label": "Mode", "help": "Select gain.", "units": "", "kind": "select", "default": "single", "options": [{"value": "single", "label": "Single"}, {"value": "double", "label": "Double"}]},
        {"id": "field", "label": "Field", "help": "Edit a two by two field.", "units": "V", "kind": "matrix", "shape": [2, 2], "default": [[1, 0], [0, -1]], "min": -10, "max": 10, "step": 0.1}]
    spec["outputs"] += [
        {"id": "energy", "label": "Squared amplitude", "units": "V²", "role": "result"},
        {"id": "scaled_field", "label": "Scaled field", "units": "V", "role": "intermediate"}]
    spec["visuals"] += [
        {"id": "energy_line", "kind": "line", "title": "Squared amplitude sweep", "output": "energy", "x_label": "Amplitude", "y_label": "Squared amplitude", "sweep": {"control": "amplitude", "min": -2, "max": 2, "points": 41}},
        {"id": "field_heatmap", "kind": "heatmap", "title": "Signed field", "output": "scaled_field", "x_label": "Column", "y_label": "Row", "labels": ["A", "B"]},
        {"id": "readouts", "kind": "values", "title": "Field values", "output": "scaled_field", "x_label": "Column", "y_label": "Row"}]
    spec["compute_js"] = spec["compute_js"].replace("return {probabilities, contributions, entropy};", """
        const gain = inputs.mode === 'double' ? 2 : 1;
        const direction = inputs.negate ? -1 : 1;
        const energy = inputs.amplitude * inputs.amplitude;
        const scaled_field = inputs.field.map(row => row.map(x => x * inputs.amplitude * gain * direction));
        return {probabilities, contributions, entropy, energy, scaled_field};""")
    return spec


def attention_spec():
    spec = entropy_spec()
    spec.update(title="Scaled dot-product attention", plan="Inspect scores, softmax weights, and weighted values.")
    spec["starting_point"] = {"idea": "Queries compare with keys to choose values.", "why": "Weighted combinations let a representation select context.", "explanation": "Scores are QKᵀ divided by sqrt(d), then stable row softmax produces weights. Weighted output is weights × V."}
    spec["symbols"] = [{"symbol": "Q, K, V", "meaning": "Query, key, and value matrices", "units": "dimensionless"}]
    def matrix(id, label):
        return {"id": id, "label": label, "help": "Two rows, two features.", "units": "dimensionless", "kind": "matrix", "shape": [2, 2], "default": [[1, 0], [0, 1]], "min": -10, "max": 10, "step": 0.1}
    spec["controls"] = [matrix("queries", "Queries"), matrix("keys", "Keys"), matrix("values", "Values"),
                        {"id": "scaled", "label": "Scale scores", "help": "Divide by sqrt(2).", "units": "", "kind": "toggle", "default": True},
                        {"id": "temperature", "label": "Temperature", "help": "Positive softmax temperature.", "units": "dimensionless", "kind": "slider", "default": 1, "min": 0.1, "max": 3, "step": 0.1},
                        {"id": "mode", "label": "Weight rule", "help": "Compare softmax with uniform averaging.", "units": "", "kind": "select", "default": "softmax", "options": [{"value": "softmax", "label": "Softmax"}, {"value": "uniform", "label": "Uniform"}]}]
    spec["outputs"] = [{"id": "scores", "label": "Similarity scores", "units": "dimensionless", "role": "intermediate"},
                       {"id": "weights", "label": "Attention weights", "units": "dimensionless", "role": "intermediate"},
                       {"id": "attended", "label": "Weighted output", "units": "dimensionless", "role": "result"}]
    spec["visuals"] = [{"id": "weight_heatmap", "kind": "heatmap", "title": "Attention weights by query and key", "output": "weights", "x_label": "Key", "y_label": "Query", "labels": ["1", "2"]},
                       {"id": "score_values", "kind": "values", "title": "Scores", "output": "scores", "x_label": "Key", "y_label": "Query"}]
    spec["explorations"] = [{"title": "Equal scores", "instruction": "Set all queries to zero.", "observe": "Each key receives half the weight.", "why": "Equal scores produce equal softmax weights.", "preset": {"queries": [[0, 0], [0, 0]]}},
                            {"title": "Dominant first key", "instruction": "Align queries strongly with the first key.", "observe": "Weight concentrates on the first key.", "why": "Exponentiation favors larger scores.", "preset": {"queries": [[8, 0], [8, 0]]}}]
    spec["grounding"] = [{"paper": "Attention Is All You Need", "locator": "Section 3.2.1", "support": "example", "claim": "A two-feature example of scaled dot-product attention."}]
    spec["limitation"] = "Toy matrices illustrate one attention operation; no training, masking, or multi-head model."
    spec["tests"] = [{"name": "Equal scores average values", "inputs": {"queries": [[0, 0], [0, 0]]}, "expected": {"weights": [[0.5, 0.5], [0.5, 0.5]], "attended": [[0.5, 0.5], [0.5, 0.5]]}, "atol": 1e-10, "rtol": 1e-10},
                     {"name": "Unscaled identity scores", "inputs": {"scaled": False}, "expected": {"scores": [[1, 0], [0, 1]]}, "atol": 1e-10, "rtol": 1e-10}]
    spec["invariants"] = [{"name": "Rows sum to one", "output": "weights", "kind": "row_sum", "expected": 1, "atol": 1e-10, "rtol": 1e-10},
                          {"name": "Probabilities in range", "output": "weights", "kind": "range", "min": 0, "max": 1, "atol": 1e-10, "rtol": 1e-10}]
    spec["compute_js"] = """function compute(inputs) {
      function dot(a, b) { return a.reduce((sum, x, i) => sum + x * b[i], 0); }
      const scale = inputs.scaled ? Math.sqrt(2) : 1;
      const scores = inputs.queries.map(q => inputs.keys.map(k => dot(q, k) / scale));
      const weights = scores.map(row => {
        const maximum = Math.max(...row);
        const exponentials = row.map(x => Math.exp((x - maximum) / inputs.temperature));
        const total = exponentials.reduce((sum, x) => sum + x, 0);
        return exponentials.map(x => inputs.mode === 'uniform' ? 0.5 : x / total);
      });
      const attended = weights.map(row => inputs.values[0].map((unused, col) => row.reduce((sum, w, i) => sum + w * inputs.values[i][col], 0)));
      return {scores, weights, attended};
    }"""
    return spec


def _engine_child():
    """Optional Windows JSRT test engine: bounded process, no browser/network."""
    import ctypes as ct
    lib = ct.WinDLL("chakra.dll")
    pointer = ct.c_void_p
    def api(name, args):
        fn = getattr(lib, name)
        fn.argtypes = args
        fn.restype = ct.c_uint
        return fn
    create = api("JsCreateRuntime", [ct.c_uint, pointer, ct.POINTER(pointer)])
    memory = api("JsSetRuntimeMemoryLimit", [pointer, ct.c_size_t])
    context = api("JsCreateContext", [pointer, ct.POINTER(pointer)])
    current = api("JsSetCurrentContext", [pointer])
    run = api("JsRunScript", [ct.c_wchar_p, ct.c_size_t, ct.c_wchar_p, ct.POINTER(pointer)])
    exception = api("JsGetAndClearException", [ct.POINTER(pointer)])
    convert = api("JsConvertValueToString", [pointer, ct.POINTER(pointer)])
    string = api("JsStringToPointer", [pointer, ct.POINTER(ct.c_wchar_p), ct.POINTER(ct.c_size_t)])
    dispose = api("JsDisposeRuntime", [pointer])
    add_ref = api("JsAddRef", [pointer, ct.POINTER(ct.c_uint)])
    runtime, ctx, value = pointer(), pointer(), pointer()
    def check(code):
        if code:
            raise RuntimeError(f"JSRT error {code:#x}")
    def stringify(value):
        text_value, raw, length = pointer(), ct.c_wchar_p(), ct.c_size_t()
        refs = ct.c_uint()
        check(add_ref(value, ct.byref(refs)))
        check(convert(value, ct.byref(text_value)))
        check(add_ref(text_value, ct.byref(refs)))
        check(string(text_value, ct.byref(raw), ct.byref(length)))
        return ct.wstring_at(raw, length.value)
    # Disable background work, permit interruption, disable native generation
    # and eval. Parent subprocess timeout enforces the hard wall-clock limit.
    check(create(1 | 2 | 8 | 16, None, ct.byref(runtime)))
    try:
        check(memory(runtime, 128 * 1024 * 1024))
        check(context(runtime, ct.byref(ctx)))
        check(current(ctx))
        source = ct.create_unicode_buffer(sys.stdin.read())
        code = run(source, 0, "owned-test", ct.byref(value))
        if code:
            check(exception(ct.byref(value)))
            print(json.dumps({"engine_error": stringify(value)}, ensure_ascii=True))
            return
        print(json.dumps(json.loads(stringify(value)), ensure_ascii=True))
    finally:
        current(None)
        dispose(runtime)


def js_result(script):
    if os.name != "nt" or not Path("C:/Windows/System32/chakra.dll").is_file():
        raise unittest.SkipTest("Bounded Windows JSRT engine unavailable; numerical JS execution unverified")
    # Root the returned string in the engine's global environment before the
    # JSRT call returns; Python's stack is not a JS GC root.
    last = script.rfind("JSON.stringify(")
    if last < 0:
        raise AssertionError("Engine test must finish with JSON.stringify")
    script = script[:last] + "var ownedTestResult = " + script[last:] + "\nownedTestResult;"
    # Parent pipe encoding and child standard streams must agree even when
    # Windows locale mode and inherited PYTHONIOENCODING differ.
    child_env = dict(os.environ, PYTHONIOENCODING="utf-8")
    child = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--js-engine"], input=script,
                           encoding="utf-8", env=child_env, capture_output=True, timeout=20)
    if child.returncode:
        raise AssertionError(child.stderr or child.stdout)
    result = json.loads(child.stdout)
    if isinstance(result, dict) and "engine_error" in result:
        raise AssertionError(result["engine_error"])
    return result


@unittest.skipUnless(os.name == "nt" and Path("C:/Windows/System32/chakra.dll").is_file(),
                     "Bounded Windows JSRT engine unavailable; Unicode transport unverified")
class EngineTransportTests(unittest.TestCase):
    def test_unicode_roundtrip(self):
        value = "caf\u00e9 \u2212 \u03c0 \u0627\u0644\u0639\u0631\u0628\u064a\u0629 \U0001f600"
        self.assertEqual(js_result("JSON.stringify(" + json.dumps(value, ensure_ascii=False) + ");"), value)

    def test_unicode_roundtrip_in_fresh_process_environments(self):
        value = "caf\u00e9 \u2212 \u03c0 \u0627\u0644\u0639\u0631\u0628\u064a\u0629 \U0001f600"
        source = ("import json; from tests.test_runtime import js_result; "
                  "value = " + ascii(value) + "; "
                  "result = js_result('JSON.stringify(' + json.dumps(value, ensure_ascii=False) + ');'); "
                  "print(json.dumps(result, ensure_ascii=True))")
        for settings in ({}, {"PYTHONUTF8": "0", "PYTHONIOENCODING": "utf-8"},
                         {"PYTHONUTF8": "1", "PYTHONIOENCODING": "ascii"}):
            with self.subTest(settings=settings):
                environment = os.environ.copy()
                environment.pop("PYTHONUTF8", None)
                environment.pop("PYTHONIOENCODING", None)
                environment.update(settings)
                child = subprocess.run([sys.executable, "-c", source],
                                       cwd=Path(__file__).resolve().parents[1], env=environment,
                                       encoding="utf-8", capture_output=True, timeout=30)
                self.assertEqual(child.returncode, 0, child.stderr or child.stdout)
                self.assertEqual(json.loads(child.stdout), value)


def calculate(spec, patch=None):
    tree = parse_compute(spec["compute_js"])
    inputs = merge_inputs(spec["controls"], patch or {})
    source = (Path(__file__).resolve().parents[1] / "templates/interpreter.js").read_text(encoding="utf-8")
    return js_result(source + "\nJSON.stringify(NumericRuntime.run(" + json.dumps(tree) + "," + json.dumps(inputs) + "));")


class PageInspection(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.scripts = []
        self.tags = []
        self.active = None
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == "script":
            self.active = [dict(attrs), ""]
            self.scripts.append(self.active)

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = None

    def handle_data(self, data):
        if self.active is not None:
            self.active[1] += data


# Minimal DOM contract double. This executes the exact shipped page scripts,
# including handlers/SVG creation, but is not evidence of actual browser layout.
_DOM = r"""
const nodes=[];
class TestNode {
  constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.style={};this.events={};this.dataset={};this.validity={badInput:false};this._text='';this.value='';nodes.push(this);}
  set textContent(v){this._text=String(v);this.children=[];}
  get textContent(){return this._text+this.children.map(x=>x.textContent).join(' ');}
  append(n){this.children.push(n);}
  replaceChildren(...ns){this._text='';this.children=ns;}
  setAttribute(k,v){this.attrs[k]=String(v);}
  removeAttribute(k){delete this.attrs[k];}
  addEventListener(k,fn){this.events[k]=fn;}
}
const document={
  createElement:t=>new TestNode(t),createElementNS:(ns,t)=>new TestNode(t),
  getElementById:id=>nodes.find(n=>n.id===id),
  querySelectorAll:selector=>selector==='.preset'?nodes.filter(n=>n.className==='preset'):[]
};
for(const id of ['runtime-data','controls','outputs','visuals','status','result-status','check-status','checks','principal-result','preset-result-0','preset-result-1','feedback-0','feedback-1']){const n=new TestNode('div');n.id=id;}
for(let i=0;i<2;i++){const b=new TestNode('button');b.className='preset';b.dataset.preset=String(i);}
const text=id=>document.getElementById(id).textContent;
const change=(id,value)=>{const n=document.getElementById(id);n.value=value;n.events.change();};
const preset=i=>document.querySelectorAll('.preset')[i].events.click();
"""


def page_result(spec, actions="", inspection=None):
    page = PageInspection(render(spec))
    payload = page.scripts[0][1]
    script = page.scripts[1][1]
    if inspection is None:
        inspection = "{status:text('status'),resultStatus:text('result-status'),outputs:text('outputs'),visuals:text('visuals'),checks:text('checks'),checkStatus:text('check-status')}"
    return js_result(_DOM + "\ndocument.getElementById('runtime-data').textContent=" + json.dumps(payload) + ";\n" + script + "\n" + actions + "\nJSON.stringify(" + inspection + ");")


class ContractTests(unittest.TestCase):
    def test_workbench_groups_controls_and_feedback_before_supporting_sections(self):
        page = render(entropy_spec())
        parsed = PageInspection(page)
        classes = [attrs.get("class") for _, attrs in parsed.tags]
        self.assertIn("workbench-grid", classes)
        self.assertIn("control-panel", classes)
        self.assertIn("live-panel", classes)
        self.assertLess(page.index('id="controls"'), page.index('id="principal-result"'))
        self.assertLess(page.index('id="principal-result"'), page.index('id="outputs"'))
        self.assertLess(page.index('class="verification"'), page.index('class="limitation"'))
        self.assertLess(page.index('class="limitation"'), page.index('<h2>Grounding'))
        feedback = [attrs for tag, attrs in parsed.tags if tag == "details" and attrs.get("class") == "exploration-feedback"]
        self.assertEqual(len(feedback), 2)
        self.assertTrue(all("open" not in attrs for attrs in feedback))

    def test_teaching_sequence_and_prediction_reveal(self):
        page = render(entropy_spec())
        self.assertLess(page.index('id="calculate"'), page.index('id="results"'))
        self.assertLess(page.index('id="results"'), page.index('id="explorations"'))
        self.assertLess(page.index('id="explorations"'), page.index('<h2>Grounding'))
        self.assertEqual(page.count('<summary>Compare your prediction</summary>'), 2)
        self.assertEqual(page.count('href="#results"'), 2)
        self.assertIn('they do not verify every claim', page)

    def test_exploration_order_predict_apply_observe_explain(self):
        page = render(entropy_spec())
        self.assertLess(page.index('<strong>Predict:'), page.index('data-preset="0"'))
        self.assertLess(page.index('data-preset="0"'), page.index('<strong>Observe:'))
        self.assertLess(page.index('<strong>Observe:'), page.index('<strong>Explain:'))

    def test_standalone_teaching_page_and_presets(self):
        spec = entropy_spec()
        page = render(spec)
        self.assertTrue(page.startswith("<!doctype html>"))
        for text in (spec["title"], spec["audience"], spec["plan"], "Symbols and units", "Section 6", "Limitation", "bits"):
            self.assertIn(text, page)
        self.assertEqual(page.count('class="preset"'), 2)
        self.assertIn('type="application/json"', page)
        self.assertNotIn('"compute_js":', page)
        self.assertNotIn("Runtime stub", page)
        self.assertIn("TOY EXAMPLE", page)
        provenance_spec = copy.deepcopy(spec)
        provenance_spec["grounding"] = [dict(spec["grounding"][0], support=kind)
                                        for kind in ("excerpt", "example", "simplification", "unverified")]
        provenance_page = render(provenance_spec)
        for label in ("FROM PAPER", "TOY EXAMPLE", "SIMPLIFICATION", "UNVERIFIED"):
            self.assertIn(label, provenance_page)

    def test_frozen_signature_and_no_collaborator_imports(self):
        import inspect
        self.assertEqual(str(inspect.signature(render)), "(spec: dict) -> str")
        source = inspect.getsource(sys.modules["runtime"])
        for name in ("model_client", "spec_parser", "checks", "paper_playground", "budget", "openrouter"):
            self.assertNotRegex(source, r"(?:from|import)\s+" + name + r"\b")

    def test_render_is_pure_and_admits_entropy_compute(self):
        spec = entropy_spec()
        before = copy.deepcopy(spec)
        validate_spec(spec)
        tree = parse_compute(spec["compute_js"])
        self.assertEqual(tree[:2], ["fn", ["inputs"]])
        render(spec)
        self.assertEqual(spec, before)

    def test_compute_failure_preserves_explanation(self):
        spec = entropy_spec()
        spec["compute_js"] = "function compute(inputs) { return document.body; }"
        page = render(spec)
        self.assertIn("Degraded:", page)
        self.assertIn(spec["starting_point"]["explanation"], page)
        self.assertIn("Skipped: compute was not admitted", page)


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.spec = all_kinds_spec()
        self.controls = self.spec["controls"]

    def test_all_six_control_kinds_are_admitted(self):
        validate_spec(self.spec)
        self.assertEqual({c["kind"] for c in self.controls}, {"slider", "number", "toggle", "select", "vector", "matrix"})
        page = render(self.spec)
        self.assertNotIn('"error":"Invalid', page)
        self.assertIn('"ast":["fn"', page)

    def test_partial_presets_merge_over_defaults_not_current_state(self):
        inputs = merge_inputs(self.controls, {"count": 2})
        self.assertEqual(inputs["count"], 2)
        self.assertEqual(inputs["field"], [[1, 0], [0, -1]])
        inputs["weights"][0] = 9
        self.assertEqual(merge_inputs(self.controls, {})["weights"], [1, 1, 1, 1])

    def test_arrays_replace_atomically(self):
        with self.assertRaises(RuntimeSpecError):
            merge_inputs(self.controls, {"weights": [2]})
        with self.assertRaises(RuntimeSpecError):
            merge_inputs(self.controls, {"field": [[2, 3]]})

    def test_invalid_values_do_not_mutate_defaults(self):
        before = copy.deepcopy(self.controls)
        for patch in ({"negate": 1}, {"mode": "missing"}, {"count": "2"}, {"count": float("nan")}, {"weights": [1, 1, 1, float("inf")]}, {"field": [[1, 2], [3]]}):
            with self.subTest(patch=patch), self.assertRaises(RuntimeSpecError):
                merge_inputs(self.controls, patch)
        self.assertEqual(before, self.controls)

    def test_finite_ui_values_clamp_and_presets_reject_bounds(self):
        values = merge_inputs(self.controls, {})
        values["amplitude"] = 100
        values["field"] = [[-100, 0], [0, 100]]
        clamped = validate_inputs(self.controls, values, clamp=True)
        self.assertEqual(clamped["amplitude"], 2)
        self.assertEqual(clamped["field"], [[-10, 0], [0, 10]])
        with self.assertRaises(RuntimeSpecError):
            merge_inputs(self.controls, {"amplitude": 100})

    def test_unknown_and_missing_controls_rejected(self):
        with self.assertRaises(RuntimeSpecError):
            merge_inputs(self.controls, {"__proto__": 1})
        values = merge_inputs(self.controls, {})
        del values["count"]
        with self.assertRaises(RuntimeSpecError):
            validate_inputs(self.controls, values)

    def test_dimension_and_aggregate_input_limits(self):
        spec = entropy_spec()
        spec["controls"][0]["shape"] = [9]
        spec["controls"][0]["default"] = [1] * 9
        with self.assertRaises(RuntimeSpecError):
            validate_spec(spec)
        base = {"kind": "matrix", "shape": [8, 8], "label": "Matrix", "units": "", "help": "", "default": [[0] * 8 for _ in range(8)], "min": 0, "max": 1, "step": 1}
        controls = [dict(base, id="a"), dict(base, id="b")]
        self.assertEqual(len(merge_inputs(controls, {})["a"]), 8)
        controls.append({"id": "extra", "kind": "number", "default": 0, "min": 0, "max": 1, "step": 1})
        with self.assertRaises(RuntimeSpecError):
            merge_inputs(controls, {})

    def test_invalid_step_and_select_options(self):
        for step in (0, -1, float("inf"), True):
            spec = entropy_spec()
            spec["controls"][0]["step"] = step
            with self.subTest(step=step), self.assertRaises(RuntimeSpecError):
                validate_spec(spec)
        self.spec["controls"][-2]["options"].append({"value": "single", "label": "Duplicate"})
        with self.assertRaises(RuntimeSpecError):
            validate_spec(self.spec)


class VisualTests(unittest.TestCase):
    def test_all_visual_kinds_and_output_metadata(self):
        spec = all_kinds_spec()
        validate_spec(spec)
        self.assertEqual({v["kind"] for v in spec["visuals"]}, {"bar", "line", "heatmap", "values"})
        for output in spec["outputs"]:
            self.assertIn(output["label"], render(spec))

    def test_sweep_limits_numeric_control_and_bounds(self):
        for patch in ({"points": 1}, {"points": 42}, {"points": 2.5}, {"points": True}, {"min": -3}, {"max": float("inf")}, {"control": "negate"}, {"control": "absent"}, {"min": 2, "max": 1}):
            spec = all_kinds_spec()
            spec["visuals"][1]["sweep"].update(patch)
            with self.subTest(patch=patch), self.assertRaises(RuntimeSpecError):
                validate_spec(spec)

    def test_missing_output_reference_and_duplicate_ids(self):
        for change in ("missing", "duplicate"):
            spec = entropy_spec()
            if change == "missing":
                spec["visuals"][0]["output"] = "absent"
            else:
                spec["visuals"][0]["id"] = "weights"
            with self.assertRaises(RuntimeSpecError):
                validate_spec(spec)

    def test_numeric_tree_validation(self):
        self.assertEqual(numeric_shape([[1, 2], [3, 4]]), ((2, 2), 4))
        self.assertEqual(numeric_shape(0), ((), 1))
        for value in ([], [1, [2]], [[1, 2], [3]], [True], float("nan"), float("inf"), [0]*9, [[[0]*8]*8]*3):
            with self.subTest(value=value), self.assertRaises(RuntimeSpecError):
                numeric_shape(value)


class CalculationTests(unittest.TestCase):
    def test_compound_assignment_reads_before_rhs_side_effects(self):
        spec = entropy_spec()
        spec["compute_js"] = """function compute(inputs) {
          let x=1; x += (x=2);
          return {probabilities:[1], contributions:[0], entropy:x};
        }"""
        self.assertEqual(calculate(spec)["entropy"], 3)

    def test_missing_arguments_do_not_turn_into_invented_null_values(self):
        spec = entropy_spec()
        spec["compute_js"] = """function compute(inputs) {
          function f(x) { return x === null ? 9 : 3; }
          return {probabilities:[1], contributions:[0], entropy:f()};
        }"""
        self.assertIn("Missing function argument", page_result(spec)["status"])

    def test_entropy_identities_and_zero_weight_policy(self):
        self.assertAlmostEqual(calculate(entropy_spec())["entropy"], 2)
        self.assertEqual(calculate(entropy_spec(), {"weights": [1, 0, 0, 0]})["entropy"], 0)
        result = calculate(entropy_spec(), {"weights": [0, 0, 0, 0], "count": 2})
        self.assertEqual(result["probabilities"], [0.5, 0.5])
        self.assertEqual(result["entropy"], 1)

    def test_attention_against_scalar_reference(self):
        spec = attention_spec()
        validate_spec(spec)
        result = calculate(spec)
        weight = math.exp(1 / math.sqrt(2)) / (math.exp(1 / math.sqrt(2)) + 1)
        self.assertAlmostEqual(result["weights"][0][0], weight)
        self.assertAlmostEqual(result["attended"][1][1], weight)
        for row in result["weights"]:
            self.assertAlmostEqual(sum(row), 1)
        equal = calculate(spec, {"queries": [[0, 0], [0, 0]]})
        self.assertEqual(equal["attended"], [[0.5, 0.5], [0.5, 0.5]])
        dominant = calculate(spec, {"queries": [[8, 0], [8, 0]], "temperature": 0.1})
        self.assertGreater(dominant["weights"][0][0], 0.999999)

    def test_all_control_values_reach_real_compute_outputs(self):
        result = calculate(all_kinds_spec(), {"amplitude": -2, "negate": True, "mode": "double", "field": [[1, 2], [3, 4]], "count": 2})
        self.assertEqual(result["energy"], 4)
        self.assertEqual(result["scaled_field"], [[4, 8], [12, 16]])
        self.assertEqual(result["entropy"], 1)

    def test_loops_helpers_and_array_mutation(self):
        spec = entropy_spec()
        spec["compute_js"] = """function compute(inputs) {
          function square(x) { return x * x; }
          const probabilities = Array(4).fill(0);
          let entropy = 0;
          for (let i = 0; i < inputs.weights.length; i++) { probabilities[i] = square(inputs.weights[i]); }
          for (const p of probabilities) { if (p === 0) continue; entropy += p; }
          return {probabilities, contributions: probabilities.slice(), entropy};
        }"""
        self.assertEqual(calculate(spec)["entropy"], 4)


class InteractionTests(unittest.TestCase):
    def test_invalid_edit_has_local_accessible_feedback_and_clears_on_correction(self):
        result = page_result(entropy_spec(), "change('input-count-scalar','');const message=text('error-count');const input=document.getElementById('input-count-scalar');const invalid=input.attrs['aria-invalid'];change('input-count-scalar','2');", "{message,invalid,describedBy:input.attrs['aria-describedby'],corrected:text('error-count'),value:input.value}")
        self.assertIn("previous value restored", result["message"])
        self.assertEqual(result["invalid"], "true")
        self.assertEqual(result["describedBy"], "help-count error-count")
        self.assertEqual(result["corrected"], "")
        self.assertEqual(result["value"], "2")

    def test_result_readout_and_preset_snapshot_are_calculated_and_retained(self):
        result = page_result(entropy_spec(), "preset(0);const snapshot=text('preset-result-0');change('input-count-scalar','2');", "{snapshot,retained:text('preset-result-0'),current:text('principal-result'),open:document.getElementById('feedback-0').open}")
        self.assertIn("Total entropy 0 bits", result["snapshot"])
        self.assertEqual(result["snapshot"], result["retained"])
        self.assertFalse(result["open"])
        self.assertIn("Current result", result["current"])
        failure = entropy_spec()
        failure["compute_js"] = failure["compute_js"].replace("const n =", "if (inputs.count === 2) throw 'failure'; const n =")
        stale = page_result(failure, "const before=text('principal-result');change('input-count-scalar','2');", "{before,after:text('principal-result'),stale:document.getElementById('principal-result').attrs['data-stale']}")
        self.assertEqual(stale["before"], stale["after"])
        self.assertEqual(stale["stale"], "true")

    def test_synced_public_fixtures_and_measured_expected_details(self):
        root = Path(__file__).resolve().parents[1]
        for name, count in (("entropy", 12), ("attention", 10)):
            path = root / "practice/specs" / (name + ".json")
            if not path.is_file():
                self.skipTest("Collaborator reference fixture absent: " + str(path))
            with self.subTest(name=name):
                spec = json.loads(path.read_text(encoding="utf-8"))
                result = page_result(spec)
                self.assertEqual(result["status"], "Inputs and calculation valid.")
                self.assertEqual(result["checkStatus"], f"{count} passed; 0 failed; 0 skipped.")
                self.assertIn("Measured", result["checks"])
                self.assertIn("expected", result["checks"])
                self.assertIn("atol", result["checks"])
                self.assertIn("rtol", result["checks"])

    def test_maximum_matrix_and_vector_with_full_sweep(self):
        spec = all_kinds_spec()
        spec["controls"][0].update(shape=[8], default=[1]*8)
        spec["controls"][1].update(default=8, max=8)
        spec["controls"][-1].update(shape=[8, 8], default=[[0]*8 for _ in range(8)])
        spec["tests"] = [
            {"name": "Eight equal outcomes", "inputs": {}, "expected": {"entropy": 3}, "atol": 1e-10, "rtol": 1e-10},
            {"name": "Eight zero weights", "inputs": {"weights": [0]*8}, "expected": {"entropy": 3}, "atol": 1e-10, "rtol": 1e-10}]
        spec["explorations"][0]["preset"] = {"weights": [1]+[0]*7}
        spec["explorations"][1]["preset"] = {"weights": [1]*8, "count": 8}
        result = page_result(spec, "change('input-field-7-7','2');", "{status:text('status'),visuals:text('visuals'),layout:nodes.find(n=>n.style.gridTemplateColumns).style.gridTemplateColumns}")
        self.assertEqual(result["status"], "Inputs and calculation valid.")
        self.assertIn("repeat(8", result["layout"])
        self.assertNotIn("unavailable", result["visuals"])

    def test_all_five_invariant_kinds_are_evaluated(self):
        spec = entropy_spec()
        spec["invariants"] = [{"name": "Ordered contributions", "output": "contributions", "kind": "nondecreasing", "atol": 0, "rtol": 0},
                              {"name": "Bounded probabilities", "output": "probabilities", "kind": "range", "min": 0, "max": 1, "atol": 0, "rtol": 0}]
        result = page_result(spec)
        self.assertIn("9 passed; 0 failed", result["checkStatus"])
        # Other tests execute finite, sum, and row_sum; incompatible shape fails.
        spec["invariants"][0]["kind"] = "row_sum"
        spec["invariants"][0]["expected"] = 1
        self.assertIn("requires matrix", page_result(spec)["checks"])

    def test_sweep_failure_is_contained_and_never_plots_invented_points(self):
        spec = all_kinds_spec()
        spec["compute_js"] = spec["compute_js"].replace("const n =", "if (inputs.amplitude === 0) throw 'undefined at zero'; const n =")
        result = page_result(spec)
        self.assertIn("1 visual(s) unavailable", result["status"])
        self.assertIn("undefined at zero", result["visuals"])
        self.assertIn("Current valid result", result["resultStatus"])

    def test_negative_bar_and_constant_heatmap_have_finite_geometry(self):
        spec = all_kinds_spec()
        spec["visuals"][0]["output"] = "scaled_field"
        result = page_result(spec)
        self.assertIn("Bar chart requires a vector", result["visuals"])
        spec["visuals"][0]["output"] = "contributions"
        spec["compute_js"] = spec["compute_js"].replace("return {probabilities, contributions, entropy, energy, scaled_field};", "return {probabilities, contributions: [-2,0,1,3], entropy, energy, scaled_field};")
        result = page_result(spec, inspection="{status:text('status'),attrs:nodes.filter(n=>n.tag==='rect').map(n=>n.attrs)}")
        # Negative sample bars deliberately contradict the entropy identity;
        # chart geometry remains valid while the scientific failure is visible.
        self.assertEqual(result["status"], "Calculation completed; 1 scientific check(s) failed.")
        for attrs in result["attrs"]:
            for key in ("x", "y", "width", "height"):
                self.assertTrue(math.isfinite(float(attrs[key])))
        self.assertTrue(all(float(a["height"]) >= 0 for a in result["attrs"]))

    def test_initial_entropy_and_two_preset_handlers(self):
        result = page_result(entropy_spec())
        self.assertEqual(result["status"], "Inputs and calculation valid.")
        self.assertIn("Total entropy", result["outputs"])
        self.assertIn("2", result["outputs"])
        self.assertEqual(result["checkStatus"], "9 passed; 0 failed; 0 skipped.")
        result = page_result(entropy_spec(), "preset(0);const first=text('outputs');preset(1);", "{first,second:text('outputs')}")
        self.assertIn("Total entropy — result (bits) 0", result["first"])
        self.assertIn("Total entropy — result (bits) 2", result["second"])

    def test_invalid_edit_retains_previous_inputs_and_result(self):
        result = page_result(entropy_spec(), "const before=text('outputs');change('input-count-scalar','');", "{before,after:text('outputs'),value:document.getElementById('input-count-scalar').value,status:text('status')}")
        self.assertEqual(result["before"], result["after"])
        self.assertEqual(result["value"], "4")
        self.assertIn("Invalid edit; last valid inputs retained", result["status"])

    def test_swept_line_heatmap_values_and_labels_execute(self):
        result = page_result(all_kinds_spec())
        self.assertEqual(result["status"], "Inputs and calculation valid.")
        self.assertIn("Squared amplitude sweep", result["visuals"])
        self.assertIn("Signed field", result["visuals"])
        self.assertIn("Field values", result["visuals"])
        self.assertNotIn("unavailable", result["visuals"])

    def test_attention_checks_execute_and_matrix_edits_recalculate(self):
        result = page_result(attention_spec(), "change('input-queries-0-0','0');preset(0);")
        self.assertEqual(result["status"], "Inputs and calculation valid.")
        self.assertIn("8 passed; 0 failed", result["checkStatus"])
        self.assertIn("0.5", result["outputs"])

    def test_wrong_expectations_and_invariants_are_not_green(self):
        spec = entropy_spec()
        spec["tests"][0]["expected"]["entropy"] = 999
        spec["invariants"][0]["expected"] = 999
        result = page_result(spec)
        self.assertIn("4 failed", result["checkStatus"])
        self.assertIn("expectation not met", result["checks"])
        self.assertIn("scientific check(s) failed", result["status"])
        self.assertEqual(page_result(spec, inspection="document.getElementById('status').className"), "caution")

    def test_visuals_follow_their_outputs_and_tables_keep_semantic_axes(self):
        spec = attention_spec()
        spec["visuals"][0].update(x_label="Key columns", y_label="Query rows")
        result = page_result(spec, inspection="{cards:document.getElementById('outputs').children.map(n=>n.textContent),headers:nodes.filter(n=>n.tag==='th').map(n=>n.textContent)}")
        self.assertEqual(len(result["cards"]), len(spec["outputs"]))
        for output, card in zip(spec["outputs"], result["cards"]):
            self.assertIn(output["label"], card)
            for visual in spec["visuals"]:
                if visual["output"] == output["id"]:
                    self.assertIn(visual["title"], card)
        self.assertIn("Query rows", result["headers"])
        self.assertIn("Key columns 1", result["headers"])
        swept_spec = all_kinds_spec()
        sweep = page_result(swept_spec, inspection="nodes.filter(n=>n.tag==='th').map(n=>n.textContent)")
        visual = next(v for v in swept_spec["visuals"] if v["kind"] == "line")
        control = next(c for c in swept_spec["controls"] if c["id"] == visual["sweep"]["control"])
        output = next(o for o in swept_spec["outputs"] if o["id"] == visual["output"])
        self.assertIn(f"{visual['x_label']} ({control['units']})", sweep)
        self.assertIn(f"{output['label']} ({output['units']})", sweep)

    def test_later_calculation_failure_labels_retained_result(self):
        spec = entropy_spec()
        spec["compute_js"] = spec["compute_js"].replace("const n =", "if (inputs.count === 2) throw 'demonstration failure'; const n =")
        result = page_result(spec, "const before=text('outputs');change('input-count-scalar','2');", "{before,after:text('outputs'),status:text('status'),resultStatus:text('result-status'),checkStatus:text('check-status')}")
        self.assertEqual(result["before"], result["after"])
        self.assertIn("Calculation failed", result["status"])
        self.assertIn("stale", result["resultStatus"])
        self.assertIn("Degraded", result["checkStatus"])


class SafetyTests(unittest.TestCase):
    def test_compound_thrown_values_cannot_expand_error_messages(self):
        for body in (
            "let a=[0];for(let i=0;i<25;i++){a=[a,a];}throw a;",
            "const a=[0];a[0]=a;throw a;",
            "throw {message:[1,2]};",
        ):
            spec = entropy_spec()
            spec["compute_js"] = "function compute(inputs){" + body + "}"
            result = page_result(spec)
            self.assertIn("non-scalar error value", result["status"])
            self.assertLess(len(result["status"]), 200)
            self.assertEqual(result["outputs"], "")

    def test_var_is_rejected_and_const_binding_is_enforced(self):
        with self.assertRaisesRegex(RuntimeSpecError, "var is unsupported"):
            parse_compute("function compute(inputs){var x=1;if(true){var x=7;}return x;}")
        for body in ("const x=1;x=7;", "for(const x of [1,2]){x=7;}"):
            spec = entropy_spec()
            spec["compute_js"] = "function compute(inputs){" + body + "return {probabilities:[1],contributions:[1],entropy:1};}"
            self.assertIn("Cannot reassign const", page_result(spec)["status"])

    def test_counted_loop_closures_keep_each_iterations_binding(self):
        spec = entropy_spec()
        spec["compute_js"] = """function compute(inputs){
          const callbacks=[];
          for(let i=0;i<3;i++){callbacks.push(()=>i);}
          const contributions=callbacks.map(f=>f());
          return {probabilities:[1],contributions,entropy:contributions[0]};
        }"""
        self.assertEqual(calculate(spec)["contributions"], [0, 1, 2])

    def test_coercive_equality_is_rejected_instead_of_changing_js_semantics(self):
        with self.assertRaises(RuntimeSpecError):
            parse_compute("function compute(inputs) { return inputs.count == '4'; }")

    def test_csp_allows_only_exact_trusted_script_hash(self):
        import base64
        import hashlib
        parsed = PageInspection(render(entropy_spec()))
        csp = next(attrs["content"] for tag, attrs in parsed.tags if tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy")
        script = parsed.scripts[1][1]
        digest = base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
        self.assertIn("script-src 'sha256-" + digest + "'", csp)
        self.assertNotIn("script-src 'unsafe-inline'", csp)

    def test_script_breakout_and_all_text_is_inert(self):
        spec = entropy_spec()
        attack = '</script><script>document.title="owned"</script><img src=x onerror="owned()"> & " \' \u2028\u2029'
        spec["title"] = attack
        spec["audience"] = attack
        spec["plan"] = attack
        spec["starting_point"]["idea"] = attack
        spec["symbols"][0]["meaning"] = attack
        spec["grounding"][0]["claim"] = attack
        spec["explorations"][0]["title"] = attack
        spec["controls"][0]["label"] = attack
        spec["outputs"][0]["label"] = attack
        spec["visuals"][0]["labels"][0] = attack
        page = render(spec)
        parsed = PageInspection(page)
        self.assertEqual(len(parsed.scripts), 2)
        self.assertNotIn("</script>", parsed.scripts[0][1])
        self.assertIn("\\u003c/script\\u003e", parsed.scripts[0][1])
        self.assertIn("\\u2028\\u2029", parsed.scripts[0][1])
        self.assertFalse(any(tag == "img" for tag, _ in parsed.tags))
        self.assertFalse(any(any(k.startswith("on") for k in attrs) for _, attrs in parsed.tags))
        self.assertEqual(json.loads(parsed.scripts[0][1])["spec"]["controls"][0]["label"], attack)
        result = page_result(spec)
        self.assertIn(attack, result["outputs"])
        self.assertEqual(result["status"], "Inputs and calculation valid.")

    def test_unsafe_compute_rejected_before_interpretation(self):
        bodies = ["return document.body;", "return fetch('https://example.com');", "return Math.random();",
                  "return Math['random']();", "return inputs['constructor'];", "return inputs['\\u0063onstructor'];",
                  "return Date.now();", "return Function('return 1')();", "return eval('1');",
                  "return globalThis;", "return window;", "while(true) {}", "return import('x');",
                  "return ({}).__proto__;", "return inputs.constructor.constructor('return 1')();"]
        for body in bodies:
            with self.subTest(body=body), self.assertRaises(RuntimeSpecError):
                parse_compute("function compute(inputs) {" + body + "}")
        with self.assertRaises(RuntimeSpecError):
            parse_compute("function compute(inputs) {return {};} malicious();")

    def test_dynamic_properties_cannot_reach_host_objects(self):
        spec = all_kinds_spec()
        spec["controls"][-2]["options"] = [{"value": "constructor", "label": "Test"}]
        spec["controls"][-2]["default"] = "constructor"
        spec["compute_js"] = "function compute(inputs) { return inputs.weights[inputs.mode](); }"
        result = page_result(spec)
        self.assertIn("Unsafe property access", result["status"])
        self.assertIn("No valid result", result["resultStatus"])

    def test_nonfinite_malformed_missing_and_extra_outputs_fail(self):
        bodies = ["return {entropy: 1};", "return 1;", "return {probabilities:[1],contributions:[1],entropy:1,extra:2};",
                  "return {probabilities:[],contributions:[1],entropy:1};", "return {probabilities:[true],contributions:[1],entropy:1};",
                  "return {probabilities:[1],contributions:[1],entropy:1/0};", "return {probabilities:[1],contributions:[1],entropy:Math.sqrt(-1)};",
                  "return {probabilities:[[1,2],[3]],contributions:[1],entropy:1};", "return {probabilities:[1],contributions:[1],entropy:'missing'};"]
        for body in bodies:
            spec = entropy_spec()
            spec["compute_js"] = "function compute(inputs) {" + body + "}"
            with self.subTest(body=body):
                result = page_result(spec)
                self.assertIn("Calculation failed", result["status"])
                self.assertEqual(result["outputs"], "")
                self.assertIn("Degraded", result["checkStatus"])

    def test_bounded_loop_recursion_allocation_and_cyclic_outputs(self):
        bodies = ["for (let i=0; true; i++) {} return {};",
                  "function recurse(x) { return recurse(x); } return recurse(1);",
                  "const a = Array(129); return a;",
                  "const a=[0]; a[0]=a; return {probabilities:a,contributions:[1],entropy:1};",
                  "let a=Array(128).fill(0); for (let i=0; i<256; i++) { a=a.map(x=>x); } return {};",
                  "for(let i=0;i<256;i++){for(let j=0;j<256;j++){let a=1+1;}} return {};"
                  ]
        for body in bodies:
            spec = entropy_spec()
            spec["compute_js"] = "function compute(inputs) {" + body + "}"
            with self.subTest(body=body):
                result = page_result(spec)
                self.assertIn("Calculation failed", result["status"])
                self.assertTrue(any(word in result["status"] for word in ("limit", "depth", "cyclic")), result)

    def test_source_ast_and_literal_limits(self):
        sources = [" " * 65537, "function compute(inputs){return " + "("*60 + "1" + ")"*60 + ";}",
                   "function compute(inputs){return 1e999;}", "function compute(inputs){return '" + "x"*1025 + "';}"]
        for source in sources:
            with self.subTest(length=len(source)), self.assertRaises(RuntimeSpecError):
                parse_compute(source)
        with self.assertRaises(RuntimeSpecError):
            numeric_shape(10**400)

    def test_no_remote_assets_dynamic_execution_or_network(self):
        parsed = PageInspection(render(entropy_spec()))
        for tag, attrs in parsed.tags:
            self.assertNotIn("src", attrs)
            if "href" in attrs:
                self.assertTrue(attrs["href"].startswith("#"), attrs)
            self.assertNotIn("action", attrs)
        script = parsed.scripts[1][1]
        for forbidden in (r"\beval\s*\(", r"\bnew\s+Function\b", r"\bfetch\s*\(", r"\bDate\b", r"Math\.random", r"\.innerHTML\b", r"insertAdjacentHTML", r"XMLHttpRequest", r"WebSocket"):
            self.assertNotRegex(script, forbidden)
        self.assertIn("connect-src 'none'", render(entropy_spec()))

    def test_nonfinite_schema_and_bad_tolerances_degrade(self):
        for tolerance in (-1, True, float("inf"), float("nan")):
            spec = entropy_spec()
            spec["tests"][0]["atol"] = tolerance
            with self.subTest(tolerance=tolerance):
                self.assertIn("Degraded:", render(spec))
        spec = entropy_spec()
        spec["controls"][0]["default"][0] = float("nan")
        result = page_result(spec)
        self.assertIn("Degraded:", result["status"])

    def test_input_copy_isolation_and_output_leaf_cap(self):
        spec = entropy_spec()
        spec["compute_js"] = """function compute(inputs) {
          inputs.weights[0] = 9;
          return {probabilities:[1],contributions:[1],entropy:1};
        }"""
        result = page_result(spec, "preset(1);", "{weight:document.getElementById('input-weights-0').value}")
        self.assertEqual(result["weight"], "1")
        spec["compute_js"] = """function compute(inputs) {
          const a=Array(8).fill(0).map(x=>Array(8).fill(0));
          return {probabilities:a, contributions:a, entropy:1};
        }"""
        result = page_result(spec)
        self.assertIn("Total output numeric leaf limit", result["status"])


if __name__ == "__main__":
    if "--js-engine" in sys.argv:
        _engine_child()
    elif "--smoke" in sys.argv:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--smoke", choices=["entropy", "attention", "all-kinds"])
        parser.add_argument("--output", required=True)
        args = parser.parse_args()
        path = Path(args.output) / "index.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        fixture = {"entropy": entropy_spec, "attention": attention_spec, "all-kinds": all_kinds_spec}[args.smoke]
        path.write_text(render(fixture()), encoding="utf-8")
        print(f"Wrote {path.resolve()}; browser calculation NOT verified by this command")
    else:
        unittest.main()
