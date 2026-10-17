"""Framework rendering diagnostic script - trace TSX/VUE/SVELTE route compilation + HTML output."""
from __future__ import annotations

import sys, os
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))
os.chdir(REPO)

# Force UTF-8 on Windows console (avoid charmap errors for emoji)
import io
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
_ok_replace = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
_err_replace = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
try:
    sys.stdout = _ok_replace
    sys.stderr = _err_replace
except Exception:
    pass


def print_hdr(title: str):
    print(f"\n{'=' * 70}\n## {title}\n{'=' * 70}")


# -------------------------------------------------------------------
# 1. CONFIG - vérifier que React/Frameworks sont BIEN déclarés dans useFF
# -------------------------------------------------------------------
print_hdr("1. Config.useFF et Config.useVite")
from nexy.core.config import Config

c = Config()
print(f"   useVite      : {c.useVite!r} (type={type(c.useVite).__name__})")
print(f"   useFF        : {c.useFF!r} (type={type(c.useFF).__name__})")
print(f"   FRAMEWORK_ROUTE_EXTENSIONS : {c.FRAMEWORK_ROUTE_EXTENSIONS}")
print(f"   FRONTEND_EXTENSIONS map    : {c.FRONTEND_EXTENSIONS}")
print(f"   ROUTE_FILE_EXTENSIONS      : {c.ROUTE_FILE_EXTENSIONS}")
print(f"   ALWAYS_ACTIVE_EXTENSIONS   : {c.ALWAYS_ACTIVE_EXTENSIONS}")

if not c.useVite:
    print("   ⚠️  useVite=False → Les composants React/Vue/etc. NE PEUVENT PAS être SSR'd")
    print("   → Il faut passer useVite=True et déclarer le framework dans useFF=[...] dans nexyconfig.py")

# -------------------------------------------------------------------
# 2. nexyconfig.py utilisateur - vérifier le contenu
# -------------------------------------------------------------------
print_hdr("2. nexyconfig.py racine")
cfg_path = REPO / "nexyconfig.py"
if cfg_path.exists():
    content = cfg_path.read_text(encoding="utf-8")
    print(content)
else:
    print("   ❌ nexyconfig.py n'existe pas à la racine !")

# -------------------------------------------------------------------
# 3. AppServer.routes() - voir si les routes TSX sont DÉTECTÉES
# -------------------------------------------------------------------
print_hdr("3. AppServer.run() - routes enregistrées qui commencent par TSX/VUE")
from nexy.routers.app import AppServer

app = AppServer().run()
routes_detected: list[str] = []
for r in app.routes:
    p = getattr(r, "path", None)
    if p is None:
        continue
    routes_detected.append(p)

# Quelles routes TSX devraient exister ?
tsx_routes_on_disk: list[tuple[str, str]] = []
router_path = Path(c.ROUTER_PATH)
if router_path.exists():
    for f in sorted(router_path.rglob("*")):
        if not f.is_file():
            continue
        ext = f.suffix.lower()
        if ext in {".tsx", ".vue", ".svelte", ".jsx"}:
            rel = f.relative_to(router_path).with_suffix("")
            # convert (group)/... ; [param] ; etc. to url path
            url = "/" + "/".join(
                seg for seg in rel.as_posix().split("/")
                if not (seg.startswith("(") and seg.endswith(")"))
            ).replace("index", "").rstrip("/") or "/"
            tsx_routes_on_disk.append((url, str(f)))

print(f"\n   [.tsx/.vue/.svelte/.jsx] Fichiers sur disque : {len(tsx_routes_on_disk)}")
for url, fp in tsx_routes_on_disk:
    present = any(url == p for p in routes_detected)
    mark = "✅" if present else "❌"
    print(f"   {mark} GET {url:30s} ← {fp}")

print(f"\n   Toutes les routes enregistrées count={len(routes_detected)}:")
for p in sorted(routes_detected):
    is_framework = any(p in u for u, _ in tsx_routes_on_disk)
    tag = " [FW?]" if is_framework else ""
    print(f"      - {p}{tag}")

# -------------------------------------------------------------------
# 4. FrontendRoute - compile card.tsx et regarde l'HTML généré
# -------------------------------------------------------------------
print_hdr("4. FrontendRoute.compile() - test sur src/routes/card.tsx")
from nexy.compiler.frontend_route import FrontendRoute

card_path = REPO / "src" / "routes" / "card.tsx"
if card_path.exists():
    try:
        fr = FrontendRoute(path=str(card_path), url_path="/card")
        print(f"   FrontendRoute instantiated OK, framework={fr.framework!r}")
        # Tenter render_html (si SSR est supporté sans node)
        if hasattr(fr, "render_html"):
            try:
                html = fr.render_html(props={})
                print(f"   render_html() → {len(html)} chars")
                print(f"   PREVIEW: {html[:500]!r}")
            except Exception as e:
                print(f"   render_html() a échoué: {type(e).__name__}: {e}")
        else:
            print("   ⚠️  FrontendRoute n'a pas de méthode render_html()")
            print("   → Méthodes disponibles:", [m for m in dir(fr) if not m.startswith("_")])
    except Exception as e:
        import traceback
        print(f"   ❌ FrontendRoute(card.tsx) a échoué: {type(e).__name__}: {e}")
        traceback.print_exc(limit=4)
else:
    print(f"   ❌ {card_path} n'existe pas !")

# -------------------------------------------------------------------
# 5. SSR check - react.py render + node_modules existent ?
# -------------------------------------------------------------------
print_hdr("5. Check node_modules existent-ils ? Framework registry render output")
node_modules = REPO / "node_modules"
print(f"   node_modules/ existe : {node_modules.exists()}")
if not node_modules.exists():
    print("   ⚠️  node_modules MANQUANT → impossible de SSR React/Vue/etc.")
    print("   → Il faut lancer: pnpm install (ou npm i) à la racine")

# Le registry frontend renvoie quoi ?
from nexy.frontend import react, vue, svelte, solid, preact
from nexy.core.models import FrontendFramework
for fn, name in [(react, "react"), (vue, "vue"), (svelte, "svelte"), (solid, "solid"), (preact, "preact")]:
    ff: FrontendFramework = fn()
    # Est-ce que le script client mentionne bien l'import du package ?
    print(f"\n   Framework {name}:")
    print(f"      name={ff.name!r}")
    has_import = f"import(\"{name}\")" in ff.render or f"from '{name}'" in ff.render
    print(f"      Chargement {name} depuis render_script ? : {'✅' if has_import else '❌ (ou autre import)'}")
    print(f"      render_script length: {len(ff.render)} chars")
    # Cherche les erreurs possibles
    if "console.error" in ff.render:
        print(f"      ✅ contient fallback console.error si load échoue")
    # Extrait le premier fragment significatif
    lines = [ln for ln in ff.render.splitlines() if ln.strip() and not ln.strip().startswith("//")][:5]
    for l in lines:
        print(f"      {l.strip():100s}")

# -------------------------------------------------------------------
# 6. FBRouter - framework route files sont-ils skippés ?
# -------------------------------------------------------------------
print_hdr("6. FBRouter single framework validator - single_framework_active ?")
from nexy.routers.fbrouter.discovery import RouteDiscovery
from nexy.core.models import FrontendFramework

rd = RouteDiscovery()
try:
    files = rd.scan_routes()
    print(f"   scan_routes() → {len(files)} fichiers routes bruts détectés")
    for f in files[:30]:
        if hasattr(f, "file_path"):
            print(f"      • {getattr(f, 'file_path', str(f))}")
except Exception as e:
    import traceback
    print(f"   ❌ scan_routes a échoué: {type(e).__name__}: {e}")
    traceback.print_exc(limit=4)

# -------------------------------------------------------------------
# 7. Builder.compile - compile card.tsx et use.tsx
# -------------------------------------------------------------------
print_hdr("7. Builder.compile_single(card.tsx) et compile_single(use.tsx)")
from nexy.builder import Builder, BuildError

b = Builder()
for rel in ["src/routes/card.tsx", "src/routes/use.tsx", "src/components/count.tsx"]:
    fp = REPO / rel
    if not fp.exists():
        print(f"   ⏭  {rel} n'existe pas")
        continue
    print(f"\n   >>> compile_single({rel})")
    try:
        code, err, is_error_page = b.compile_file(str(fp))
        if err:
            print(f"      ❌ BuildError: path={err.path} line={err.line} col={err.col} type={err.type}")
            print(f"         msg preview: {str(err)[:300]}")
        else:
            print(f"      ✅ Compilé OK → {len(code)} chars, is_error={is_error_page}")
            print(f"      PREVIEW 400ch: {code[:400]!r}")
    except Exception as e:
        import traceback
        print(f"      💥 Exception: {type(e).__name__}: {e}")
        traceback.print_exc(limit=4)

print("\n" + "=" * 70)
print("DIAGNOSTIC TERMINÉ")
