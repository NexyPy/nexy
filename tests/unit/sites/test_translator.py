"""A page keeps its skeleton when it travels through a translator."""

from __future__ import annotations

from sites.shared import translator

PAGE = """# Choose a router

A route is a file, and `link()` builds a URL.

```python
def GET() -> str:
    return "hello"
```

| Router | Fits |
|---|---|
| FBR | a folder of files |

See [Core concepts](../getting-started/core-concepts.md) and https://nexy.ai.
"""


class TestProtect:
    def test_a_fence_never_reaches_the_translator(self):
        template, kept = translator.protect(PAGE)
        assert "def GET()" not in template and any("def GET()" in part for part in kept)

    def test_an_inline_code_stays_with_its_sentence(self):
        template, _kept = translator.protect(PAGE)
        assert "A route is a file, and [[1]] builds a URL." in template

    def test_a_link_keeps_its_target(self):
        _template, kept = translator.protect(PAGE)
        assert "](../getting-started/core-concepts.md)" in kept

    def test_a_table_keeps_its_pipes(self):
        template, kept = translator.protect(PAGE)
        assert " Router " in template and " Fits " in template
        assert kept.count("|") == 6

    def test_a_heading_keeps_its_marker(self):
        _template, kept = translator.protect(PAGE)
        assert kept[0] == "# "


class TestChunks:
    def test_a_chunk_never_cuts_a_paragraph(self):
        text = "\n\n".join(["word " * 40] * 4)
        assert all("word word" in chunk for chunk in translator.chunks(text, limit=250))

    def test_the_paragraphs_come_back_in_order(self):
        text = "one\n\ntwo\n\nthree"
        assert "\n\n".join(translator.chunks(text, limit=5)) == text


class TestSplit:
    def test_a_piece_cuts_at_the_space_nearest_the_middle(self):
        assert translator.split("one two three four") == ("one two", " ", "three four")

    def test_a_named_place_is_cut_on_its_left(self):
        assert translator.split("one two three four", near=12) == ("one two", " ", "three four")

    def test_a_place_on_a_space_keeps_that_space_apart(self):
        assert translator.split("one two three four", near=13) == ("one two three", " ", "four")

    def test_a_piece_without_a_space_is_not_split(self):
        assert translator.split("abcdefghij") is None


class TestHealOpening:
    def test_a_placeholder_that_opens_a_piece_gets_its_bracket_back(self):
        assert translator.heal_opening("[80]]Routing") == "[[80]]Routing"

    def test_a_placeholder_in_the_middle_is_left_alone(self):
        assert translator.heal_opening("a [80]] b") == "a [80]] b"

    def test_a_whole_placeholder_that_opens_a_piece_stays_as_it_is(self):
        assert translator.heal_opening("[[80]]Routing") == "[[80]]Routing"


class TestRestore:
    def test_every_kept_part_comes_back(self):
        template, kept = translator.protect(PAGE)
        assert translator.restore([template], kept) == PAGE

    def test_a_lost_placeholder_is_refused(self):
        template, kept = translator.protect(PAGE)
        lost = template.replace("[[1]]", "")
        assert translator.missing(lost, kept) == [1]

    def test_a_repeated_placeholder_is_refused(self):
        template, kept = translator.protect(PAGE)
        twice = template.replace("[[1]]", "[[1]] [[1]]")
        assert translator.missing(twice, kept) == [1]

    def test_a_restored_page_holds_no_placeholder(self):
        template, kept = translator.protect(PAGE)
        assert "[[" not in translator.restore([template], kept)


class TestUnwrap:
    def test_a_wrapped_paragraph_becomes_one_line(self):
        assert (
            translator.unwrap("Two servers, two\nbuild systems.\n")
            == "Two servers, two build systems.\n"
        )

    def test_a_list_item_keeps_its_continuation(self):
        text = "- **Python.** A page needs\n  no framework.\n- Next item\n"
        assert translator.unwrap(text) == "- **Python.** A page needs no framework.\n- Next item\n"

    def test_a_fence_keeps_its_lines(self):
        text = "```python\na = 1\nb = 2\n```\n"
        assert translator.unwrap(text) == text

    def test_table_rows_stay_apart(self):
        text = "| A | B |\n|---|---|\n| 1 | 2 |\n"
        assert translator.unwrap(text) == text

    def test_a_heading_keeps_the_next_line_apart(self):
        text = "# Title\nFirst line.\n"
        assert translator.unwrap(text) == text

    def test_an_alert_marker_keeps_its_own_line(self):
        text = "> [!NOTE]\n> One line\n> and the next.\n"
        assert translator.unwrap(text) == "> [!NOTE]\n> One line and the next.\n"

    def test_a_hard_break_is_kept(self):
        text = "First line\\\nsecond line\n"
        assert translator.unwrap(text) == text

    def test_a_comment_line_stays_apart(self):
        text = "<!-- router:fbr -->\nSome text\n<!-- /router -->\n"
        assert translator.unwrap(text) == text
