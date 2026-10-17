"""Rendering final check : appel direct handlers framework /card et /use (sans httpx)."""
from __future__ import annotations

import sys, io, os, asyncio, inspect
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
os.chdir(REPO))

_wrapped = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
try:
    sys.stdout = _wrapped
except Exception:
    pass

from nexy.routers.app import AppServer
app = AppServer().run()

wanted = {"/card", "/use", "/about", "/hello"}

# Find APIRoute endpoints for wanted routes
found_handlers: dict[str, tuple[inspect.Signature] = {}
for r in app.routes:
    p = getattr(r, "path", None)
    if p in wanted:
        ep = getattr(r, "endpoint", None)
        if ep is not None:
            found_handlers[p] = (ep, r.methods if hasattr(r, "methods") else None)

print(f"\nHandlers trouves: {list(found_handlers.keys())}\n")

# Mock scope minimal pour FakeRequest pour appeler async handlers StreamingResponse
class FakeHeaders(list):
    pass

def _fake_request(path: str):
    from starlette.requests import Request as R
    state_obj = type("State", (), {"locale": "en"})()
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [],
        "server": ("test", 80),
        "client": ("127.0.0.1", 10000),
        "scheme": "http",
        "http_version": "1.1",
        "path_params": {},
        "app": app,
        "route": None,
        "session": None,
        "auth": None,
        "extensions": {},
    }
    req = R(scope)
    req._state = state_obj
    return req

async def call_endpoint(url: str):
    handler, methods = found_handlers[url]
    print(f"\n{'='*60}\nGET {url}  methods={methods}\n{'='*60}")
    sig = inspect.signature(handler)
    print(f"  handler sig: {sig}")
    # Determine args
    try:
        if "request" in sig.parameters:
            result = handler(_fake_request(url))
        else:
            result = handler()
        if inspect.isawaitable(result):
            result = await result
        # If StreamingResponse, read body chunks
        from starlette.responses import StreamingResponse, HTMLResponse
        if isinstance(result, StreamingResponse):
            body_bytes = b"".join([c if isinstance(c, bytes) else c.encode() for c in result.body_iterator])
            html = body_bytes.decode("utf-8", errors="replace")
        elif isinstance(result, HTMLResponse):
            html = result.body.decode("utf-8", errors="replace") if isinstance(result.body, (bytes, bytearray)) else str(result.body)
        elif isinstance(result, str):
            html = result
        else:
            html = str(result)
        # Check markers
        markers = ["<ncc", "data-nexy-fw", "data-nexy-key", "data-nexy-path", "espoir", "force", "Junior", "Card", "User", "<script"]
        hits = [m for m in markers if m in html]
        print(f"  status={getattr(result, 'status_code', 'N/A')} len={len(html)} chars, markers={hits}")
        print(f"  HTML PREVIEW (800 chars):\n{html[:800]}\n")
        return html
    except Exception as e:
        import traceback
        print(f"  ERREUR: {type(e).__name__}: {e}")
        traceback.print_exc(limit=6)
        return None


async def main():
    for url in ["/card", "/use", "/about", "/hello", "/"]:
        if url in found_handlers:
            await call_endpoint(url)
        else:
            # Fallback: call the full ASGI layer via app() manually - find match
            print(f"\n{'='*60}\nGET {url}: PAS de handler APIRoute - appel via asgi direct\n{'='*60}")
            # Try to hit app() and do a synthetic ASGI loop and collect body.
            body_collected: list[bytes] = []
            sent_started = None
            async def receive():
                return {"type": "http.request", "body": b"", "more_body": False}
            async def send(ev):
                nonlocal sent_started, body_collected
                if ev["type"] == "http.response.start":
                    sent_started = ev
                elif ev["type"] == "http.response.body":
                    body_collected.append(ev.get("body", b""))
            p = url
            scope = {
                "type": "http", "method": "GET",
                "path": p, "raw_path": p.encode(),
                "query_string": b"", "headers": [],
                "server": None, "client": None,
                "scheme": "http", "http_version": "1.1",
                "extensions": {}
            }
            try:
                await app(scope, receive, send)
                body_bytes = b"".join(body_collected)
                html = body_bytes.decode("utf-8", errors="replace")
                status = sent_started["status"] if sent_started else "N/A"
                markers = ["<ncc", "data-nexy-fw", "espoir", "Junior", "Hello", "about", "nexy"]
                hits = [m for m in markers if m in html]
                print(f"  ASGI status={status} len={len(html)} chars, markers={hits}")
                print(f"  HTML PREVIEW 800 chars:\n{html[:800]}\n")
            except Exception as e:
                import traceback
                print(f"  ASGI ERREUR: {type(e).__name__}: {e}")
                traceback.print_exc(limit=6)


asyncio.run(main())
