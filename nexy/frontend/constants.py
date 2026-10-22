NAVIGABLE_EXTS: tuple[str, ...] = (".tsx", ".jsx", ".vue", ".svelte", ".solid", ".preact")

FRAMEWORK_DEPS: dict[str, list[str]] = {
    "react": ["react", "react-dom", "react/jsx-runtime"],
    "vue": ["vue"],
    "preact": ["preact", "preact/compat"],
    "solid": ["solid-js"],
    "svelte": ["svelte"],
}


def navigable_glob() -> str:
    """Brace glob covering every navigable extension (e.g. '{tsx,jsx,...}')."""
    return "{" + ",".join(ext.lstrip(".") for ext in NAVIGABLE_EXTS) + "}"
