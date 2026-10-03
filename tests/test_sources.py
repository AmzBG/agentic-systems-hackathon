from paper_playground.sources import select_relevant_excerpt


def test_excerpt_selection_keeps_relevant_passage() -> None:
    filler = "Background material without the target phrase. " * 40
    target = "Scaled dot-product attention divides similarity by the square root dimension."
    text = "\n\n".join([filler, filler, target, filler, filler])
    excerpt = select_relevant_excerpt(text, "scaled dot-product attention", max_chars=1_200)
    assert "Scaled dot-product attention" in excerpt
    assert len(excerpt) <= 1_200

