"""useViews: nested views render as markup, props are escaped, Vite is injected once."""

import re

from nexy.hooks import View, _is_document, useViews


class TestView:
    def test_renders_as_its_markup_in_a_layout(self):
        assert str(View("<p>x</p>", client="<script></script>")) == "<p>x</p>"

    def test_jinja_safe_uses_the_markup(self):
        from markupsafe import Markup

        assert Markup(View("<p>x</p>", client="<i></i>")) == "<p>x</p>"

    def test_client_tags_only_reach_the_response_body(self):
        view = View("<p>x</p>", client="<script></script>")
        assert view.body == b"<script></script><p>x</p>"


class TestDocumentDetection:
    def test_doctype_is_a_document(self):
        assert _is_document("\n  <!DOCTYPE html><html></html>")

    def test_fragment_is_not(self):
        assert not _is_document("<section></section>")


class TestUseViewsClientComponent:
    def test_props_cannot_break_out_of_the_attribute(self, nexy_project):
        nexy_project("")
        response = useViews("page.tsx", context={"name": "'><img src=x onerror=alert(1)>\""})
        html = response.body.decode()
        tag = re.search(r"<div data-nexy-fw.*?</div>", html, re.S)
        assert tag and "<img" not in tag.group(0)
        assert "&lt;img" in tag.group(0)
