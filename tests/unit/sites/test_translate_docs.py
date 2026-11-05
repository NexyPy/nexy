"""A page reaches a service in pieces it can carry, and comes back whole."""

from __future__ import annotations

from scripts.translate_docs import translate_chunk, translate_markdown


def service(text: str, target: str) -> str:
    """A translator that keeps every placeholder but the one a piece opens on its own word."""
    head, _, rest = text.partition("]]")
    if head.startswith("[[") and rest and not rest[0].isspace():
        return rest
    return f"{target}:{text}"


class TestTranslateChunk:
    def test_a_marker_glued_to_its_word_keeps_the_marker(self):
        assert translate_chunk("[[7]]Routing", "bn", service) == "[[7]]bn:Routing"

    def test_a_marker_glued_after_its_word_keeps_the_marker(self):
        assert translate_chunk("React.[[8]]", "bn", service) == "bn:React.[[8]]"

    def test_a_word_between_two_markers_keeps_both(self):
        assert translate_chunk("[[7]]Routing[[8]]", "bn", service) == "[[7]]bn:Routing[[8]]"

    def test_a_marker_inside_a_sentence_stays_with_it(self):
        assert translate_chunk("[[7]] Routing", "bn", service) == "[[7]] bn:Routing"

    def test_a_piece_the_service_keeps_whole_is_asked_once(self):
        assert translate_chunk("a [[1]] b", "bn", service) == "bn:a [[1]] b"


class TestTranslateMarkdown:
    def test_a_wrapped_paragraph_reaches_the_service_whole(self):
        asked: list[str] = []
        translate_markdown(
            "Two servers, two\nbuild systems.\n", "fr", lambda t, _: asked.append(t) or t
        )
        assert asked == ["Two servers, two build systems."]


def drops_line_starts(text: str, target: str) -> str:
    """A translator that loses every placeholder opening a line, as Urdu does with a heading."""
    lines = [
        line.split("]] ", 1)[1] if line.startswith("[[") else line for line in text.split("\n")
    ]
    return "\n".join(f"{target}:{line}" if line else line for line in lines)


class TestLineStarts:
    def test_a_marker_opening_a_line_never_reaches_the_service(self):
        chunk = "Intro [[1]] here\n\n[[2]] Reference\n\n[[3]] Commands"
        answer = translate_chunk(chunk, "ur", drops_line_starts)
        assert answer == "ur:Intro [[1]] here\n\n[[2]] ur:Reference\n\n[[3]] ur:Commands"


def trims(text: str, target: str) -> str:
    """A translator that drops the blank lines around a piece, as the public one does."""
    return f"{target}:{text.strip()}" if text.strip() else ""


class TestBlankEdges:
    def test_the_blank_lines_around_a_piece_come_back(self):
        assert translate_chunk("\n[[1]] Reference\n", "ur", trims) == "\n[[1]] ur:Reference\n"

    def test_a_piece_of_markers_only_is_never_sent(self):
        assert translate_chunk("\n[[1]]\n", "ur", trims) == "\n[[1]]\n"


class TestOpeningWords:
    def test_a_name_opening_a_line_travels_with_its_sentence(self):
        asked: list[str] = []
        translate_chunk("[[0]] [[1]] first", "fr", lambda t, _: asked.append(t) or t, opening={0})
        assert asked == ["[[1]] first"]
