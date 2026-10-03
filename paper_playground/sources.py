"""Retrieve PDF or HTML papers and select a focus-relevant excerpt."""

from __future__ import annotations

import io
import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from .case_input import CaseInput
from .config import SOURCE_EXCERPT_CHARS, SOURCE_MAX_BYTES
from .trace import TraceWriter


class SourceError(RuntimeError):
    """Raised when the requested source cannot be retrieved or parsed."""


@dataclass(frozen=True)
class SourceDocument:
    url: str
    title: str
    media_type: str
    full_text: str
    excerpt: str


_STOPWORDS = {
    "about",
    "after",
    "also",
    "audience",
    "change",
    "concept",
    "explain",
    "from",
    "have",
    "into",
    "learner",
    "learning",
    "mechanism",
    "outcome",
    "paper",
    "should",
    "show",
    "that",
    "their",
    "these",
    "this",
    "through",
    "using",
    "what",
    "when",
    "with",
}


def load_source(case: CaseInput, trace: TraceWriter) -> SourceDocument:
    supplied = case.supplied_source_text()
    if supplied:
        title = case.extra.get("title", "Supplied paper excerpt").strip()
        excerpt = select_relevant_excerpt(supplied, case.focus)
        trace.emit(
            "source",
            "load_supplied_excerpt",
            "ok",
            characters=len(supplied),
            excerpt_characters=len(excerpt),
        )
        return SourceDocument(case.source_url, title, "text/plain", supplied, excerpt)

    trace.emit("source", "download", "started", url=case.source_url)
    try:
        response = requests.get(
            case.source_url,
            headers={"User-Agent": "PaperToPlayground/0.1 (educational hackathon agent)"},
            timeout=(10, 45),
            stream=True,
        )
        response.raise_for_status()
        chunks: list[bytes] = []
        total = 0
        for chunk in response.iter_content(chunk_size=64 * 1024):
            total += len(chunk)
            if total > SOURCE_MAX_BYTES:
                raise SourceError(
                    f"Source exceeds the {SOURCE_MAX_BYTES // (1024 * 1024)} MiB limit."
                )
            chunks.append(chunk)
        content = b"".join(chunks)
    except requests.RequestException as exc:
        trace.emit(
            "source",
            "download",
            "failed",
            url=case.source_url,
            error=type(exc).__name__,
        )
        raise SourceError(
            "Could not download source_url. If assessment networking blocks paper URLs, "
            "the case must provide an excerpt field."
        ) from exc

    content_type = response.headers.get("Content-Type", "").split(";", 1)[0].lower()
    is_pdf = content.startswith(b"%PDF-") or content_type == "application/pdf"
    if is_pdf:
        title, text = _extract_pdf(content)
        media_type = "application/pdf"
    else:
        title, text = _extract_html(content, response.encoding)
        media_type = content_type or "text/html"
    if len(text.strip()) < 500:
        raise SourceError("The downloaded source did not contain enough extractable text.")

    excerpt = select_relevant_excerpt(text, case.focus)
    trace.emit(
        "source",
        "download_and_extract",
        "ok",
        url=case.source_url,
        media_type=media_type,
        bytes=len(content),
        characters=len(text),
        excerpt_characters=len(excerpt),
    )
    return SourceDocument(case.source_url, title, media_type, text, excerpt)


def _extract_pdf(content: bytes) -> tuple[str, str]:
    try:
        reader = PdfReader(io.BytesIO(content))
        metadata = reader.metadata
        title = str(metadata.title).strip() if metadata and metadata.title else "PDF paper"
        pages = []
        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append(f"[Page {page_number}]\n{text.strip()}")
    except Exception as exc:
        raise SourceError(f"Could not parse the downloaded PDF: {type(exc).__name__}") from exc
    return title, "\n\n".join(pages)


def _extract_html(content: bytes, declared_encoding: str | None) -> tuple[str, str]:
    encoding = declared_encoding or "utf-8"
    markup = content.decode(encoding, errors="replace")
    soup = BeautifulSoup(markup, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else "HTML paper"
    for unwanted in soup(["script", "style", "noscript", "nav", "footer", "form"]):
        unwanted.decompose()
    blocks: list[str] = []
    for element in soup.select("h1,h2,h3,h4,h5,h6,p,li,figcaption,pre"):
        text = " ".join(element.get_text(" ", strip=True).split())
        if text and (not blocks or blocks[-1] != text):
            blocks.append(text)
    return title, "\n\n".join(blocks)


def select_relevant_excerpt(
    text: str,
    focus: str,
    max_chars: int = SOURCE_EXCERPT_CHARS,
) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if len(normalized) <= max_chars:
        return normalized.strip()

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    if not paragraphs:
        return normalized[:max_chars].strip()

    keywords = {
        word.lower()
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", focus)
        if word.lower() not in _STOPWORDS
    }
    scored: list[tuple[int, int]] = []
    score_by_index: dict[int, int] = {}
    for index, paragraph in enumerate(paragraphs):
        lower = paragraph.lower()
        score = sum(1 + min(lower.count(keyword), 3) for keyword in keywords if keyword in lower)
        if re.search(r"\b(section|equation|algorithm|definition|theorem)\b", lower):
            score += 1
        scored.append((score, index))
        score_by_index[index] = score

    selected = set(range(min(4, len(paragraphs))))
    for score, index in sorted(scored, reverse=True):
        if score <= 0:
            break
        selected.update(range(max(0, index - 2), min(len(paragraphs), index + 3)))
        current_length = sum(len(paragraphs[item]) + 2 for item in selected)
        if current_length >= max_chars:
            break

    ordered: list[str] = []
    used = 0
    previous = -2
    for index in sorted(selected):
        paragraph = paragraphs[index]
        separator = "\n\n" if index == previous + 1 else "\n\n[... omitted ...]\n\n"
        addition = ("" if not ordered else separator) + paragraph
        if used + len(addition) > max_chars:
            remaining = max_chars - used
            if score_by_index[index] <= 0 or remaining <= 200:
                continue
            focus_positions = [
                paragraph.lower().find(keyword)
                for keyword in keywords
                if keyword in paragraph.lower()
            ]
            anchor = min((position for position in focus_positions if position >= 0), default=0)
            content_budget = max(1, remaining - len(separator))
            start = max(0, anchor - content_budget // 3)
            clipped = paragraph[start : start + content_budget]
            if start > 0:
                clipped = "... " + clipped[4:]
            ordered.append(("" if not ordered else separator) + clipped)
            used = max_chars
            previous = index
            continue
        ordered.append(addition)
        used += len(addition)
        previous = index
    return "".join(ordered).strip()

