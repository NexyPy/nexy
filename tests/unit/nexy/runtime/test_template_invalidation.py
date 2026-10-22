from nexy.helpers.fs.vfs import VFS
from nexy.template import Template


def _clean():
    VFS().clear()
    from nexy.template import _SHARED_ENV

    if _SHARED_ENV is not None:
        _SHARED_ENV.cache.clear()


def test_render_uses_vfs_source():
    _clean()
    VFS().write("__nexy__/src/routes/page.html", "Hello {{ name }}")
    result = Template().render("__nexy__/src/routes/page.html", {"name": "World"})
    assert result == "Hello World"


def test_render_invalidates_after_source_change():
    _clean()
    VFS().write("__nexy__/src/routes/page.html", "OLD {{ name }}")
    tpl = Template()
    assert tpl.render("__nexy__/src/routes/page.html", {"name": "X"}) == "OLD X"

    VFS().write("__nexy__/src/routes/page.html", "NEW {{ name }}")
    assert tpl.render("__nexy__/src/routes/page.html", {"name": "X"}) == "NEW X"
