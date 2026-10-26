import re


class Pathname:
    def __init__(self, pathname: str) -> None:
        self.pathname = "/" + pathname.strip("/")

    def _dynamic_pathname(self, path: str | None = None) -> str:
        """Convert [slug] to {slug}."""
        target = path or self.pathname
        return re.sub(r"\[(?!(\.\.\.))([^\]]+)\]", r"{\2}", target)

    def _catch_all(self, path: str | None = None) -> str:
        """Convert [...slug] to {slug:path}."""
        target = path or self.pathname
        return re.sub(r"\[\.\.\.([^\]]+)\]", r"{\1:path}", target)

    def _group_pathname(self, path: str | None = None) -> str:
        """Remove parenthesized segments like /(user)/."""
        target = path or self.pathname
        cleaned = re.sub(r"/\([^)]+\)", "", target)
        return cleaned if cleaned else "/"

    def _normalize_pathname(self, path: str | None = None) -> str:
        target = path or self.pathname
        if target.endswith("/index"):
            target = target[:-6]
        return target if target else "/"

    def process(self) -> str:
        """Execute all transformations in logical order."""
        res = self._group_pathname()
        res = self._normalize_pathname(res)
        res = self._catch_all(res)
        res = self._dynamic_pathname(res)

        res = re.sub(r"/+", "/", res)
        return res if (res == "/" or not res.endswith("/")) else res.rstrip("/")


class StringTransform:
    def __init__(self) -> None:
        pass

    @staticmethod
    def resolve_pathname(pathname: str) -> str:
        return pathname.replace("/", "")

    @staticmethod
    def _normalize_dynamic_segment(segment: str) -> str:
        if segment.startswith("[...") and segment.endswith("]"):
            return f"{segment[4:-1].replace('-', '_')}_dynamic_param"
        if segment.startswith("[") and segment.endswith("]"):
            return f"{segment[1:-1].replace('-', '_')}_dynamic_param"
        if segment.startswith("(") and segment.endswith(")"):
            return f"{segment[1:-1]}_group"
        return segment.replace("-", "_")

    @staticmethod
    def normalize_route_path_for_namespace(path: str) -> str:
        path = path.strip("/")
        if not path:
            return ""

        parts = path.split("/")

        if "." not in parts[-1]:
            return "/".join([StringTransform._normalize_dynamic_segment(p) for p in parts])

        *dirs, filename = parts
        normalized = [StringTransform._normalize_dynamic_segment(p) for p in dirs]
        return "/".join([*(p for p in normalized if p), StringTransform._normalize_file(filename)])

    @staticmethod
    def _normalize_file(filename: str) -> str:
        """A route file as a module name: ``[slug].tsx`` becomes ``slug_catch_all.tsx``."""
        stem, ext = filename.rsplit(".", 1)
        if "[" in stem and "]" in stem:
            stem = re.sub(r"\[\.\.\.([^\]]+)\]", r"\1", stem)
            stem = re.sub(r"\[([^\]]+)\]", r"\1", stem)
            stem = f"{stem}_catch_all"
        return f"{stem.replace('-', '_')}.{ext}"

    def get_component_name(self, pathname: str) -> str:
        segment = pathname.split("/")[-1]
        if "[" in segment and "]" in segment:
            cleaned = re.sub(r"\[\.\.\.([^\]]+)\]", r"\1", segment)
            cleaned = re.sub(r"\[([^\]]+)\]", r"\1", cleaned)
            cleaned = cleaned.replace("-", "_")
            if not cleaned:
                return ""
            first = cleaned[0].capitalize()
            return f"{first}{cleaned[1:]}_catch_all"
        if not segment:
            return ""
        segment = segment.replace("-", "_")
        first_letter = segment[0].capitalize()
        return first_letter + segment[1:]
