"""The root layout owns the document, so its <!DOCTYPE html> must survive parsing."""

from nexy.modules.compiler.parser.html_parser import NexyHTMLParser


def _text(nodes) -> str:
    return "".join(getattr(n, "content", "") for n in nodes)


class TestDoctype:
    def test_doctype_is_kept(self):
        nodes = NexyHTMLParser().parse("<!DOCTYPE html><html><body></body></html>")
        assert _text(nodes) == "<!DOCTYPE html>"

    def test_doctype_comes_before_the_root_element(self):
        nodes = NexyHTMLParser().parse("<!DOCTYPE html>\n<html></html>")
        assert getattr(nodes[0], "content", "") == "<!DOCTYPE html>"
        assert nodes[-1].tag_name == "html"
