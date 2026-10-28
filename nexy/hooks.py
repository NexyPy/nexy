import html as _html
import importlib
import json
import traceback
from contextvars import ContextVar
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse
from starlette.datastructures import URL

from nexy.core.config import Config
from nexy.core.string import StringTransform
from nexy.vite import Vite

string_transform = StringTransform()


class View(HTMLResponse):
    """An HTML response that also renders as its markup.

    A layout receives a nested view as ``children``; ``str(view)`` and
    ``{{ children | safe }}`` must give the markup, not the object's repr.
    """

    def __init__(self, markup: str, *, client: str = "", **kwargs: Any) -> None:
        super().__init__(client + markup, **kwargs)
        self.markup = markup

    def __str__(self) -> str:
        return self.markup

    def __html__(self) -> str:
        return self.markup


def _is_document(markup: str) -> bool:
    return markup.lstrip()[:15].lower().startswith(("<!doctype", "<html"))


def _get_req() -> Request:
    from .modules.routers.context import current_request

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


def useParams() -> dict[str, Any]:
    """Read the dynamic path parameters of the current request.

    The twin of `useParams()` on the client: `/blog/[slug]` gives `{"slug": "post-1"}`.

    Returns:
        The path parameters, empty for a route without a dynamic segment.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req().path_params


def useQuery() -> dict[str, Any]:
    """Read dynamic path parameters of the current request.

    The original name of `useParams()`, kept so existing pages keep working. Despite its name it
    does not read the query string: that is `useSearchParams()`.

    Returns:
        The same dict as `useParams()`.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return useParams()


def useRequest() -> Request:
    """Read the current request, for what the other hooks do not cover.

    Returns:
        The Starlette request.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req()


def useHeaders() -> dict[str, str]:
    """Read the headers of the current request.

    Returns:
        Header names, in lower case, mapped to their values.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return dict(_get_req().headers)


def useUrl() -> URL:
    """Read the full URL of the current request.

    Returns:
        A Starlette `URL`: `.scheme`, `.hostname`, `.port`, `.path`, `.query`.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    return _get_req().url


def _path_of(href: str) -> str:
    """The path of an href without query, fragment or trailing slash ("/" stays "/")."""
    path = href.split("#")[0].split("?")[0]
    return path.rstrip("/") or "/"


def useIsActive(href: str, exact: bool = False) -> bool:
    """Tell whether *href* points at the current page, or at one of its parents.

    The twin of `useIsActive()` on the client, for the active link of a navigation bar. The
    query string, the fragment and a trailing slash are ignored.

    Args:
        href: The link target, such as `/blog`.
        exact: Match the page itself only. `/` is only ever active on `/`.

    Returns:
        True when the current path is *href*, or is below it unless *exact* is set.

    Raises:
        RuntimeError: If called outside an HTTP request context.
    """
    current, target = _path_of(_get_req().url.path), _path_of(href)
    if current == target:
        return True
    return not exact and target != "/" and current.startswith(target + "/")


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
    from nexy.modules.runtime.markdown import build_toc_html as _build_toc_html

    html = _toc_storage.get()
    if not html:
        return ""
    return _build_toc_html(html, depth_range)


PYTHON_VIEWS = (".nexy",)
FRONTEND_VIEWS = (".tsx", ".vue", ".svelte", ".jsx", ".mdx")


def _python_view(path: str, ctx: dict[str, Any]) -> HTMLResponse:
    """Render a compiled .nexy/.md view: import its module and call its component."""
    mapped = string_transform.normalize_route_path_for_namespace(path)
    import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
    try:
        module = importlib.import_module(import_path)
        file_name = path.split("/")[-1].split(".", 1)[0]
        component = getattr(module, string_transform.get_component_name(file_name))
        markup = str(component(**ctx))
    except (ImportError, AttributeError) as error:
        traceback.print_exc()
        raise ValueError(f"Failed to load module or function for path: {path}") from error
    # A full document injects <Vite /> itself, in its <head>; a fragment has none.
    return View(markup, client="" if _is_document(markup) else Vite())


def _client_container(path: str, ctx: dict[str, Any]) -> str:
    """The element the browser hydrates: the framework, the file and the escaped props."""
    framework = Config.FRONTEND_EXTENSIONS.get(f".{path.split('.')[-1]}", "react")
    props = _html.escape(json.dumps(ctx, default=str), quote=True)
    return (
        f'<div data-nexy-fw="{_html.escape(framework, quote=True)}" '
        f'data-nexy-path="{_html.escape(path, quote=True)}" '
        f'data-nexy-props="{props}">'
        f"</div>"
    )


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
        return _python_view(path, ctx)
    if any(ext in path for ext in FRONTEND_VIEWS):
        return View(_client_container(path, ctx), client=Vite())
    raise ValueError(f"Unsupported view type for path: {path}")
