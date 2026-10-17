"""Post-fix framework diagnostic: /card + /use registered + HTML output check."""
from __future__ import annotations

import sys, os, io
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
os.chdir(REPO)

# UTF-8 stdout Windows
import io as _io
_wrapped = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
try:
    sys.stdout = _wrapped
except Exception:
    pass

def section(t: str):
    print(f"\n{'='*70}\n## {t}\n{'='*70}")


# -------------------------------------------------------------------
section("1. AppServer.routes APRES fix: /card et /use existent-ils ?")
from nexy.routers.app import AppServer

app = AppServer().run()
route_paths = sorted({r.path for r in app.routes if hasattr(r, "path")})
print(f"Nombre total de routes: {len(route_paths)}")

wanted = {"/card", "/use"}
found = wanted & set(route_paths)
missing = wanted - found
if missing:
    print(f"[ERROR] Routes framework toujours MANQUANTES: {missing}")
else:
    print(f"[OK] Toutes les routes framework React sont ENREGISTREES: {wanted}")
print(f"\nListe complete:")
for p in route_paths:
    mark = "  <-- FRAMEWORK TSX" if p in wanted else ""
    print(f"  - {p}{mark}")


# -------------------------------------------------------------------
section("2. Test direct GET /card via TestClient (si httpx est installe)")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    for url in ["/card", "/use"]:
        try:
            r = client.get(url, follow_redirects=True)
            content_len = len(r.content)
            ok_markers = []
            # Ces markers indiquent que la balise framework est présente
            for m in ["data-nexy-fw", "<ncc", "Card", "User", "Junior", "espoir", "force"]:
                if m.encode() in r.content or m in r.text:
                    ok_markers.append(m)
            print(f"[GET {url}] status={r.status_code} bytes={content_len}, markers={ok_markers}")
            if r.status_code != 200:
                # Afficher 500 chars de l'erreur
                print(f"   PREVIEW ERREUR: {r.text[:500]}")
            else:
                # Montre les 500 premiers chars
                print(f"   PREVIEW HTML: {r.text[:600]!r}")
        except Exception as e:
            print(f"[GET {url}] ERREUR: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc(limit=3)
except ImportError as httpx_missing:
    print(f"(skip) TestClient indisponible - {httpx_missing}")
    # Fallback: appeler directement la fonction de route FastAPI si on la trouve
    for r in app.routes:
        if getattr(r, "path", None) in wanted:
            fn = getattr(r, "endpoint", None)
            if callable(fn) and "locale" in fn.__name__:
                print(f"  Appel direct handler {r.path} (async fallback via asyncio)")
                try:
                    import asyncio
                    from starlette.requests import Request as _R
                    scope = {"type": "http", "method": "GET", "path": r.path, "query_string": b"", "headers": [], "state": type("S",(),{"locale":"en"})(), "route":r, "path_params":{}}
                    async def _run():
                        from fastapi import Request
                        fake = Request(scope)
                        # Simuler request.state.locale
                        return await fn(fake)
                    out = asyncio.run(_run())
                    print(f"  -> {type(out).__name__}, len chars={len(str(out))}")
                    print(f"  -> PREVIEW: {str(out)[:500]}")
                except Exception as e2:
                    import traceback
                    print(f"  -> ECHEC appel handler: {type(e2).__name__}: {e2}")
                    traceback.print_exc(limit=5)

# -------------------------------------------------------------------
section("3. FrontendRouteCompiler compile('card.tsx') output direct VFS")
from nexy.compiler.frontend_route import FrontendRouteCompiler
from nexy.utils.fs.vfs import VFS

compiler = FrontendRouteCompiler()
vfs = VFS()
card_src = str(REPO / "src" / "routes" / "card.tsx")
use_src = str(REPO / "src" / "routes" / "use.tsx")

for label, src in [("card.tsx", card_src), ("use.tsx", use_src)]:
    if not Path(src).exists():
        print(f"  (skip) {label} absent")
        continue
    try:
        compiler.compile(input=src)
        # Trouver le module généré
        for key in list(vfs._store.keys())[-5:]:
            if "__routes__" in key and key.endswith(".py"):
                # Chercher le contenu
                code = vfs.read(key)
                print(f"\n  [{label}] VFS module: {key}")
                print(f"     len(code)={len(code)} chars")
                # Est-ce qu'il contient des marqueurs SSR React ?
                markers_in = [m for m in ["data-nexy-fw", "<ncc", "return \"", 'data-nexy-path=', 'data-nexy-symbol='] if m in code]
                print(f"     Contient markers HTML: {markers_in}")
                print(f"     PREVIEW: {code[:600]!r}")
                break
    except Exception as e:
        import traceback
        print(f"\n  [{label}] compile() a plante: {type(e).__name__}: {e}")
        traceback.print_exc(limit=5)


print("\n" + "="*70)
print("DIAGNOSTIC POST-FIX TERMINE")
