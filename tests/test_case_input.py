import json
from pathlib import Path

import pytest

from paper_playground.case_input import CaseInputError, load_case


def write_case(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_case_accepts_extra_string_fields(tmp_path: Path) -> None:
    path = tmp_path / "case.json"
    write_case(
        path,
        {
            "source_url": "https://example.com/paper.pdf",
            "focus": "Explain the mechanism.",
            "audience": "Engineering undergraduate",
            "excerpt": "A supplied excerpt",
            "title": "Example paper",
        },
    )
    case = load_case(path)
    assert case.supplied_source_text() == "A supplied excerpt"
    assert case.extra["title"] == "Example paper"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"source_url": "file:///paper.pdf", "focus": "x", "audience": "y"},
        {"source_url": "https://example.com", "focus": "x", "audience": 3},
    ],
)
def test_load_case_rejects_invalid_contract(tmp_path: Path, payload: object) -> None:
    path = tmp_path / "case.json"
    write_case(path, payload)
    with pytest.raises(CaseInputError):
        load_case(path)

