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

    def test_a_marker_leaves_its_space_to_the_text(self):
        template, kept = translator.protect("### Modes\n")
        assert template == "[[0]] Modes\n" and kept == ["###"]

    def test_a_heading_keeps_its_marker(self):
        _template, kept = translator.protect(PAGE)
        assert kept[0] == "#" and _template.startswith("[[0]] Choose")


class TestNames:
    def test_a_product_name_never_reaches_the_translator(self):
        template, kept = translator.protect("Python serves, Vite builds.")
        assert "Python" not in template and "Python" in kept and "Vite" in kept

    def test_a_longer_name_wins_over_its_prefix(self):
        _template, kept = translator.protect("Read Jinja2 and Next.js docs.")
        assert kept == ["Jinja2", "Next.js"]

    def test_a_name_inside_a_word_is_left_alone(self):
        _template, kept = translator.protect("A reactive view.")
        assert kept == []

    def test_a_marker_is_structure_and_a_name_is_not(self):
        _template, kept = translator.protect("## Python\n")
        assert translator.structural(kept) == frozenset({0})


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


class TestRespace:
    def test_a_space_the_service_ate_after_a_name_comes_back(self):
        assert translator.respace("[[1]]documentation", "[[1]] docs") == "[[1]] documentation"

    def test_a_space_the_service_ate_before_a_name_comes_back(self):
        assert translator.respace("un[[1]] ici", "a [[1]] here") == "un [[1]] ici"

    def test_a_name_glued_in_the_source_stays_glued(self):
        assert translator.respace("[[1]]docs", "[[1]]docs") == "[[1]]docs"


class TestTidyEmphasis:
    def test_the_spaces_inside_bold_are_dropped(self):
        assert translator.tidy("- ** A frontend **  text\n") == "- **A frontend**  text\n"

    def test_bold_in_a_fence_is_left_alone(self):
        text = "```python\nf(** kw )\n```\n"
        assert translator.tidy(text) == text

    def test_a_line_with_bold_in_code_is_left_alone(self):
        text = "Use `** kw` and ** this **\n"
        assert translator.tidy(text) == text


class TestHeal:
    def test_zero_width_spaces_inside_a_placeholder_are_dropped(self):
        assert translator.heal("a [[183]\u200b\u200b] b") == "a [[183]] b"

    def test_a_zero_width_joiner_in_the_text_is_kept(self):
        assert translator.heal("ক্‍ষ [[1]]") == "ক্‍ষ [[1]]"

    def test_the_bracket_dropped_at_the_opening_comes_back(self):
        assert translator.heal("[1]] text") == "[[1]] text"


class TestHealInside:
    def test_a_placeholder_that_lost_a_bracket_inside_a_link_comes_back(self):
        assert translator.heal("دیکھیں [لے آؤٹس[153]]۔") == "دیکھیں [لے آؤٹس[[153]]۔"

    def test_a_whole_placeholder_is_left_alone(self):
        assert translator.heal("a [[1]] b") == "a [[1]] b"


class TestAlerts:
    def test_an_alert_marker_never_reaches_the_translator(self):
        template, kept = translator.protect("> [!NOTE]\n> Read this.\n")
        assert "NOTE" not in template and "[!NOTE]" in kept

    def test_an_alert_marker_is_layout(self):
        _template, kept = translator.protect("> [!TIP]\n")
        assert kept.index("[!TIP]") in translator.structural(kept)


class TestRelabel:
    def test_a_link_left_in_english_takes_the_word_of_the_glossary(self):
        assert translator.relabel("voir les [views](a.md)", "fr") == "voir les [vues](a.md)"

    def test_a_translated_link_stays_as_it_is(self):
        assert translator.relabel("voir [Dépannage](a.md)", "fr") == "voir [Dépannage](a.md)"

    def test_an_image_keeps_its_text(self):
        assert translator.relabel("![views](a.png)", "fr") == "![views](a.png)"

    def test_a_link_inside_a_code_fence_is_code(self):
        fence = "```md\n[views](a.md)\n```\n"
        assert translator.relabel(fence, "fr") == fence

    def test_an_english_page_is_left_alone(self):
        assert translator.relabel("[views](a.md)", "en") == "[views](a.md)"


class TestCells:
    @staticmethod
    def _round_trip(markdown: str) -> str:
        template, kept = translator.protect(markdown)
        template, kept = translator.cells(template, kept)
        return translator.rows(translator.restore([template], kept))

    def test_a_row_puts_each_cell_on_its_own_line(self):
        template, kept = translator.cells(*translator.protect("| a | b |"))
        assert len(template.split("\n")) == 2

    def test_a_row_comes_back_as_it_was(self):
        assert self._round_trip("| a | b |") == "| a | b |"

    def test_an_empty_cell_comes_back_empty(self):
        assert self._round_trip("| a |  | c |") == "| a | | c |"

    def test_a_pipe_inside_code_is_not_a_cell(self):
        assert self._round_trip("| `a | b` | c |") == "| `a | b` | c |"

    def test_an_escaped_pipe_is_not_a_cell(self):
        assert self._round_trip("| a \\| b | c |") == "| a \\| b | c |"

    def test_a_table_separator_stays_on_its_line(self):
        table = "| a | b |\n| --- | --- |\n| c | d |"
        assert self._round_trip(table) == table

    def test_no_pipe_of_a_row_reaches_the_service(self):
        template, kept = translator.cells(*translator.protect("| a | b |"))
        body, _ = translator.leads(template, translator.structural(kept))
        assert body == "a\nb"

    def test_a_row_cut_between_two_chunks_is_joined_again(self):
        template, kept = translator.cells(*translator.protect("| a | b |"))
        first, second = template.split("\n")
        assert translator.rows(translator.restore([first, second], kept)) == "| a | b |"

    def test_an_empty_last_cell_comes_back_empty(self):
        assert self._round_trip("| a | |") == "| a | |"


class TestLinkOpenings:
    def test_a_link_opening_a_line_keeps_its_bracket_out_of_the_request(self):
        body, openings = translator.leads("[[1]] [Performance[[2]]", frozenset({1}))
        assert body == "Performance[[2]]"

    def test_the_bracket_of_a_link_opening_a_line_comes_back(self):
        _, openings = translator.leads("[[1]] [Performance[[2]]", frozenset({1}))
        assert translator.with_leads("کارکردگی [[2]]", openings) == "[[1]] [کارکردگی [[2]]"

    def test_a_placeholder_opening_a_line_is_not_a_link(self):
        body, _ = translator.leads("[[1]] text", frozenset())
        assert body == "[[1]] text"

    def test_a_link_whose_bracket_was_lost_names_its_placeholder(self):
        assert translator.unopened("voir Dépannage[[1]].", "See [Troubleshooting[[1]].") == 1

    def test_a_link_moved_after_its_text_names_its_placeholder(self):
        assert translator.unopened("a[[1]] dans [b", "the [b in a[[1]]") == 1

    def test_a_link_on_a_name_whose_bracket_was_lost_names_the_name(self):
        assert translator.unopened("et [[3]][[4]].", "and [[[3]][[4]].") == 3

    def test_a_link_with_its_bracket_names_nothing(self):
        assert translator.unopened("voir [Dépannage[[1]].", "See [Troubleshooting[[1]].") is None

    def test_a_task_box_opening_a_line_travels(self):
        body, _ = translator.leads("[[1]] [ ] ship it", frozenset({1}))
        assert body == "[ ] ship it"

    def test_a_ticked_task_box_opening_a_line_travels(self):
        body, _ = translator.leads("[[1]] [x] ship it", frozenset({1}))
        assert body == "[x] ship it"


class TestStrayed:
    def test_a_code_moved_to_the_next_cell_names_its_placeholder(self):
        assert translator.strayed("a\n[[1]] b", "a [[1]]\nb") == 1

    def test_a_code_on_its_own_line_names_nothing(self):
        assert translator.strayed("x [[1]]\ny", "a [[1]]\nb") is None

    def test_an_answer_with_other_lines_is_left_to_the_other_checks(self):
        assert translator.strayed("a [[1]] b", "a [[1]]\nb") is None
