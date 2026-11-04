"""A page reaches a service in pieces it can carry, and comes back whole."""

from __future__ import annotations

from scripts.translate_docs import translate_chunk


def service(text: str, target: str) -> str:
    """A translator that keeps every placeholder but the one a piece opens on its own word."""
    head, _, rest = text.partition("]]")
    if head.startswith("[[") and rest and not rest[0].isspace():
        return rest
    return f"{target}:{text}"


class TestTranslateChunk:
    def test_a_marker_glued_to_its_word_keeps_the_marker(self):
        assert translate_chunk("[[7]]Routing", "bn", service) == "[[7]]bn:Routing"

    def test_a_marker_inside_a_sentence_stays_with_it(self):
        assert translate_chunk("[[7]] Routing", "bn", service) == "bn:[[7]] Routing"

    def test_a_piece_the_service_keeps_whole_is_asked_once(self):
        assert translate_chunk("a [[1]] b", "bn", service) == "bn:a [[1]] b"
