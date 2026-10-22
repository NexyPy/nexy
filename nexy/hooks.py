import importlib
import json
import traceback
from contextvars import ContextVar
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.vite import Vite

string_transform = StringTransform()


def _get_req() -> Request:
    from .routers.context import current_request

    req = current_request.get()
    if not req:
        raise RuntimeError(
            "Navigation hooks can only be called within the context of an HTTP request."
        )
    return req


def usePathname() -> str:
    """Read the request path of the current HTTP request.

    Returns:
        The URL path (e.g. "/blog/post-1").

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req().url.path


def useSearchParams() -> dict[str, str]:
    """Read the query string of the current request.

    Returns:
        Query parameters as a plain dict (first value per key).

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return dict(_get_req().query_params)


def useRouter() -> dict[str, Any]:
    """Read routing info of the current request.

    Returns:
        A dict with "path", "base_url" and "url_for" keys.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    req = _get_req()
    return {
        "path": req.url.path,
        "base_url": str(req.base_url),
        "url_for": req.app.url_for if req.app else None,
    }


def useQuery() -> dict[str, Any]:
    """Read dynamic path parameters of the current request.

    Returns:
        The FastAPI path params dict (e.g. {"slug": "post-1"}).

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req().path_params


def useSession() -> dict[str, Any]:
    """Read the session store of the current request.

    Returns:
        The session dict, empty when sessions are not enabled.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return getattr(_get_req(), "session", {})


def useCookies() -> dict[str, str]:
    """Read the cookies of the current request.

    Returns:
        Cookie names mapped to their values.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req().cookies


_toc_storage: ContextVar[str] = ContextVar("_toc_storage", default="")


def useToc(depth_range: str = "2-6") -> str:
    """Read the table of contents generated for the current page.

    Args:
        depth_range: Heading depth selector (e.g. "2-4"), default "2-6".

    Returns:
        Rendered TOC HTML, or an empty string when the page has none.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    from nexy.runtime.markdown import build_toc_html as _build_toc_html

    html = _toc_storage.get()
    if not html:
        return ""
    return _build_toc_html(html, depth_range)


PYTHON_VIEWS = (".nexy",)
FRONTEND_VIEWS = (".tsx", ".vue", ".svelte", ".jsx", ".mdx")


def useViews(path: str, context: dict[str, Any] | None = None) -> HTMLResponse:
    """Render a server view for the given route path.

    Args:
        path: Route path carrying the view extension (e.g. "index.nexy",
            "about.tsx"). Python paths delegate to the VFS importer, frontend
            extensions are rendered as client-side containers.
        context: Props passed to the component; defaults to an empty dict.

    Returns:
        The HTML response for the view, with the Vite dev/prod client prepended.

    Raises:
        ValueError: If the path extension is not a supported view, or if the
            compiled module or its component function cannot be loaded.
    """
    ctx = context or {}

    if path.endswith(PYTHON_VIEWS):
        mapped = string_transform.normalize_route_path_for_namespace(path)
        import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]

        try:
            module = importlib.import_module(import_path)

            file_name = path.split("/")[-1].split(".", 1)[0]
            func_name = string_transform.get_component_name(file_name)
            component_func = getattr(module, func_name)
            return HTMLResponse(Vite() + component_func(**ctx))

        except (ImportError, AttributeError) as e:
            traceback.print_exc()
            raise ValueError(f"Failed to load module or function for path: {path}") from e

    elif any(ext in path for ext in FRONTEND_VIEWS):
        ext = f".{path.split('.')[-1]}"
        framework = Config.FRONTEND_EXTENSIONS.get(ext, "react")

        props_json = json.dumps(ctx)

        container = (
            f'<div data-nexy-fw="{framework}" '
            f'data-nexy-path="{path}" '
            f"data-nexy-props='{props_json}'>"
            f"</div>"
        )

        return HTMLResponse(Vite() + container)

    else:
        raise ValueError(f"Unsupported view type for path: {path}")
