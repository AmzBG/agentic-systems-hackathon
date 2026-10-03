from paper_playground.validation import failed_checks, validate_html


SOURCE = "https://example.com/paper"


def valid_html() -> str:
    padding = "Scientifically grounded explanation. " * 100
    return f"""<!doctype html>
<html><head><style>body {{ color: #123; }}</style></head><body>
<main><h1>Mechanism</h1><p>{padding}</p>
<svg aria-label="A labeled relationship"><text>output</text></svg>
<label>A <input id="a" type="range"></label>
<label>B <select id="b"><option>1</option></select></label>
<h2>Guided exploration 1</h2><p>Change A and observe the output because the term grows.</p>
<h2>Guided exploration 2</h2><p>Change B and observe the visual because weights shift.</p>
<h2>Limitation</h2><p>This toy assumption simplifies the paper.</p>
<p>Source paper, Section 2: <a href="{SOURCE}">{SOURCE}</a></p>
</main><script>
document.querySelector('#a').addEventListener('input', () => {{}});
</script></body></html>"""


def test_valid_artifact_passes() -> None:
    assert failed_checks(validate_html(valid_html(), SOURCE)) == []


def test_remote_script_is_rejected() -> None:
    html = valid_html().replace("<script>", '<script src="https://cdn.example/x.js"></script><script>')
    failures = failed_checks(validate_html(html, SOURCE))
    assert "offline_assets" in {item["name"] for item in failures}

