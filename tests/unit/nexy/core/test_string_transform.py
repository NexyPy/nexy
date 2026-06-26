from nexy.core.string import Pathname, StringTransform


class TestPathname:
    def test_simple_path(self) -> None:
        assert Pathname("/blog/post").process() == "/blog/post"

    def test_index_normalized(self) -> None:
        assert Pathname("/blog/index").process() == "/blog"

    def test_root_index(self) -> None:
        assert Pathname("/index").process() == "/"

    def test_group_removed(self) -> None:
        assert Pathname("/(auth)/login").process() == "/login"

    def test_dynamic_param(self) -> None:
        assert Pathname("/blog/[slug]").process() == "/blog/{slug}"

    def test_catch_all(self) -> None:
        assert Pathname("/docs/[...slug]").process() == "/docs/{slug:path}"


class TestStringTransform:
    def setup_method(self) -> None:
        self.st = StringTransform()

    def test_resolve_pathname(self) -> None:
        assert StringTransform.resolve_pathname("/foo/bar") == "foobar"

    def test_normalize_dynamic_param(self) -> None:
        result = StringTransform._normalize_dynamic_segment("[slug]")
        assert result == "slug_dynamic_param"

    def test_normalize_catch_all_param(self) -> None:
        result = StringTransform._normalize_dynamic_segment("[...slug]")
        assert result == "slug_dynamic_param"

    def test_normalize_group_param(self) -> None:
        result = StringTransform._normalize_dynamic_segment("(auth)")
        assert result == "auth_group"

    def test_normalize_plain_segment(self) -> None:
        result = StringTransform._normalize_dynamic_segment("blog")
        assert result == "blog"

    def test_get_component_name_simple(self) -> None:
        assert self.st.get_component_name("blog") == "Blog"

    def test_get_component_name_dynamic(self) -> None:
        name = self.st.get_component_name("/blog/[slug]")
        assert name.endswith("_catch_all")

    def test_get_component_name_dynamic_file(self) -> None:
        name = self.st.get_component_name("src/routes/[slug].nexy")
        assert name.endswith("_catch_all")

    def test_normalize_route_path(self) -> None:
        result = StringTransform.normalize_route_path_for_namespace(
            "src/routes/blog/post.nexy"
        )
        assert result == "src/routes/blog/post.nexy"
