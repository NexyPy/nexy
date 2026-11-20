from src.services.markdown import excerpt, to_html


def test_a_heading_becomes_html():
    assert to_html("# Groceries") == "<h1>Groceries</h1>\n"


def test_a_table_is_rendered():
    assert "<table>" in to_html("| a | b |\n|---|---|\n| 1 | 2 |")


def test_html_typed_in_a_note_is_shown_as_text():
    assert "<script>" not in to_html("<script>alert(1)</script>")


def test_a_javascript_link_is_not_made_a_link():
    assert "href" not in to_html("[click](javascript:alert(1))")


def test_the_excerpt_is_the_first_line_with_words():
    assert excerpt("\n\n# Groceries\n- milk") == "Groceries"


def test_the_excerpt_drops_the_signs_of_markdown():
    assert excerpt("- **Milk** and `eggs`") == "Milk and eggs"


def test_the_excerpt_keeps_the_text_of_a_link():
    assert excerpt("See [the docs](https://example.com) first") == "See the docs first"


def test_a_long_excerpt_ends_with_three_dots():
    assert excerpt("word " * 60).endswith("...")


def test_a_long_excerpt_is_at_most_140_long():
    assert len(excerpt("word " * 60)) <= 140


def test_an_empty_note_has_no_excerpt():
    assert excerpt("  \n ") == ""
