_FRAMEWORK_BY_EXTENSION: dict[str, str] = {
    ".vue": "vue",
    ".svelte": "svelte",
    ".tsx": "react",
    ".jsx": "react",
    ".solid": "solid",
    ".preact": "preact",
    ".nexy": "nexy",
}


def framework_from_extension(suffix: str) -> str:
    """Map a component file extension to its client framework (default: react)."""
    return _FRAMEWORK_BY_EXTENSION.get(suffix.lower(), "react")


def wrap_component_script(content: str, framework: str) -> str:
    """Wrap *content* in a <script framework=...> block unless already a component."""
    if framework == "nexy" or content.strip().startswith("<script"):
        return content
    return f'<script framework="{framework}">\n{content}\n</script>'
