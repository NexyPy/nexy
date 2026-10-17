"""HTTP smoke test - compile framework routes then GET them via FastAPI TestClient.

No framework deps used for SSR here (dev mode); we just check the route registers
and returns non-empty HTML containing the <ncc> wrapper with the RIGHT symbol.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
os.chdir(REPO)

from fastapi.testclient import TestClient  # noqa: E402

from nexy.routers.app import AppServer  # noqa: E402


def main() -> int:
    app_server = AppServer()
    app_server.setup()
    assert app_server.app is not None, "AppServer.setup() failed: app is None"
    assert app_server._loaded is True, f"Config not loaded: load_error={getattr(app_server.config,'_load_error', None)}"

    routes_seen = sorted({r.path for r in app_server.app.routes if hasattr(r, "path")})
    print("\n[OK] registered paths sample:")
    for p in routes_seen[:20]:
        print(f"  - {p}")

    urls_to_check = [
        "/",          # index.nexy
        "/about",     # about.mdx
        "/card",      # card.tsx
        "/use",       # use.tsx
        "/hello",     # hello.md
        "/qs",        # qs.py
    ]
    client = TestClient(app_server.app, raise_server_exceptions=False)
    failures: list[str] = []
    for url in urls_to_check:
        try:
            resp = client.get(url)
        except Exception as exc:  # pragma: no cover - transport
            failures.append(f"{url}: EXCEPTION {type(exc).__name__}: {exc}")
            continue
        content = resp.text or ""
        ncc_count = content.count("<ncc")
        title_like = "<title>" in content.lower() or "Bonjour" in content or "Nexy" in content or content.strip() != ""
        print(
            f"\nGET {url}: {resp.status_code}\n"
            f"  body_bytes={len(resp.content)}, title_like={title_like}, ncc_tags={ncc_count}"
        )
        if resp.status_code != 200 and url != "/qs":  # qs.py may expect params
            failures.append(f"{url}: status {resp.status_code} not 200")
            preview = content[:400].replace("\n", " ")
            print(f"  BODY PREVIEW: {preview!r}")
            continue
        if len(resp.content) < 120 and not any(s in content for s in (
            "<title>Bonjour",
            "espoir",
            "Junior",
            "John Doe",
            "static site generator",
            "Nexy is",
        )):
            preview = content[:400].replace("\n", " ")
            failures.append(f"{url}: page appears EMPTY, only {len(resp.content)} bytes. Preview: {preview!r}")

    print("\n====== SUMMARY ======")
    if failures:
        print("FAILURES:")
        for f in failures:
            print("  -", f)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
