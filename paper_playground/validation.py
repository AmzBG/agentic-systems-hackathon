"""Fast, deterministic checks for generated artifact requirements."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


class _ArtifactParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str, dict[str, str]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags.append((tag.lower(), {key.lower(): value or "" for key, value in attrs}))


def validate_html(html: str, source_url: str) -> list[dict[str, str | bool]]:
    parser = _ArtifactParser()
    try:
        parser.feed(html)
        parse_ok = True
    except Exception:
        parse_ok = False

    lower = html.lower()
    tags = parser.tags
    controls = [tag for tag, _ in tags if tag in {"input", "select", "button"}]
    external_assets: list[str] = []
    for tag, attrs in tags:
        candidate = ""
        if tag in {"script", "img", "iframe", "source", "video", "audio"}:
            candidate = attrs.get("src", "")
        elif tag == "link":
            candidate = attrs.get("href", "")
        if candidate.lower().startswith(("http://", "https://", "//")):
            external_assets.append(f"{tag}:{candidate[:100]}")
    external_assets.extend(
        match[:100]
        for match in re.findall(r"url\(\s*['\"]?https?://[^)]+", html, flags=re.I)
    )

    guided_terms = len(
        re.findall(r"guided exploration|try this|experiment\s+[12]|exploration\s+[12]", lower)
    )
    checks = [
        Check("parseable_html", parse_ok and "<html" in lower and "</html>" in lower, "Complete HTML document"),
        Check("substantial_content", len(html) >= 2_500, f"{len(html)} characters"),
        Check("embedded_style", "<style" in lower, "Embedded CSS present"),
        Check("executable_javascript", "<script" in lower, "Embedded JavaScript present"),
        Check("meaningful_visual", "<svg" in lower or "<canvas" in lower, "Inline SVG or canvas present"),
        Check("two_controls", len(controls) >= 2, f"Found {len(controls)} control elements"),
        Check(
            "interactive_updates",
            any(term in lower for term in ("addeventlistener", "oninput", "onchange")),
            "Control event handling present",
        ),
        Check(
            "two_guided_explorations",
            guided_terms >= 2 and "observe" in lower,
            f"Found {guided_terms} explicit exploration markers",
        ),
        Check(
            "limitation_or_assumption",
            any(term in lower for term in ("limitation", "assumption", "misconception")),
            "Limitation, assumption, or misconception is stated",
        ),
        Check(
            "source_grounding",
            source_url.rstrip("/") in html.rstrip("/")
            and any(term in lower for term in ("section", "equation", "source", "paper")),
            "Paper URL and grounding language present",
        ),
        Check(
            "offline_assets",
            not external_assets,
            "No remote runtime assets" if not external_assets else "; ".join(external_assets),
        ),
        Check(
            "no_secret_reference",
            "openrouter_api_key" not in lower and "bearer " not in lower,
            "No credential names or authorization values in artifact",
        ),
        Check("no_markdown_fence", "```" not in html, "No Markdown code fences"),
    ]
    return [asdict(check) for check in checks]


def failed_checks(checks: list[dict[str, str | bool]]) -> list[dict[str, str | bool]]:
    return [check for check in checks if not check["passed"]]

