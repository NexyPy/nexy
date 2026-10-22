"""Generates the client bootstrap files under __nexy__/ (entry, deps, keys, runtime)."""

import hashlib
from pathlib import Path
from typing import Any

from nexy.frontend.constants import FRAMEWORK_DEPS, NAVIGABLE_EXTS, navigable_glob
from nexy.utils.fs.path import PathUtil


def generate_vite_entry(use_ff: Any) -> None:
    """Emit framework islands, deps, keys, runtime, main.ts and the Link component."""
    ff_list = normalize_ff(use_ff)
    dest_dir = Path("__nexy__")
    src_dir = dest_dir / "src"
    dest_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    write_framework_clients(ff_list, src_dir)
    write_deps_file(ff_list, src_dir)
    write_keys_file(src_dir)
    write_runtime_file(src_dir)
    write_main_file(dest_dir, frameworks_of(ff_list))
    write_client_link(src_dir)


def normalize_ff(use_ff: Any) -> list[Any]:
    """Normalize the useFF config value into a list of non-null frameworks."""
    ff_list = [use_ff] if not isinstance(use_ff, list) else (use_ff or [])
    return [ff for ff in ff_list if ff is not None]


def frameworks_of(ff_list: list[Any]) -> set[str]:
    """Lowercased names of the frameworks in *ff_list*."""
    return {getattr(ff, "name", "").lower() for ff in ff_list if hasattr(ff, "name")}


def write_framework_clients(ff_list: list[Any], src_dir: Path) -> None:
    """Emit one {name}.nexy.ts client module per framework plus ff.auto.ts."""
    imports: list[str] = []
    invocations: list[str] = []
    for ff in ff_list:
        name = getattr(ff, "name", None)
        render = getattr(ff, "render", None)
        if not name or not render:
            continue
        target = src_dir / f"{name}.nexy.ts"
        content = f"const run = () => {{\n{render}\n}};\nexport default run;\n"
        PathUtil.write_if_changed(target, content)
        imports.append(f"import init_{name} from './{target.name}';")
        invocations.append(f"init_{name}();")

    ff_lines = [*imports, *invocations, "export {};"]
    PathUtil.write_if_changed(src_dir / "ff.auto.ts", "\n".join(ff_lines) + "\n")


def write_deps_file(ff_list: list[Any], src_dir: Path) -> None:
    """Write deps.auto.ts: Vite optimizeDeps.include derived from used frameworks."""
    used_names = [getattr(ff, "name", "").lower() for ff in ff_list if hasattr(ff, "name")]
    deps_list: list[str] = []
    for name in used_names:
        deps_list.extend(FRAMEWORK_DEPS.get(name, [name]))
    content = "export const __NEXY_DEPS: string[] = " + repr(deps_list) + "\n"
    PathUtil.write_if_changed(src_dir / "deps.auto.ts", content)


def write_keys_file(src_dir: Path) -> None:
    """Write keys.auto.ts: mapping hash(md5(path)) -> path (navigable components only)."""
    mapping: dict[str, str] = {}
    src_root = Path("src")
    if src_root.is_dir():
        for ext in NAVIGABLE_EXTS:
            for p in src_root.glob(f"**/*{ext}"):
                rel = "/" + p.as_posix().lstrip("/")
                mapping[hashlib.md5(rel.encode("utf-8"), usedforsecurity=False).hexdigest()] = rel

    lines = ["export const __NEXY_KEYS: Record<string,string> = {"]
    lines.extend(f'  "{key}": "{value}",' for key, value in mapping.items())
    lines.append("};")
    PathUtil.write_if_changed(src_dir / "keys.auto.ts", "\n".join(lines) + "\n")


def write_runtime_file(src_dir: Path) -> None:
    """Write runtime.ts: client router (match, render, navigate) wired to the manifests."""
    content = "\n".join(_runtime_lines()) + "\n"
    PathUtil.write_if_changed(src_dir / "runtime.ts", content)


def _runtime_lines() -> list[str]:
    return [
        "type CompMod = { default: unknown }",
        "type Importer = () => Promise<CompMod>",
        "type Importers = Record<string, Importer>",
        "import { __NEXY_KEYS } from '@nexy/keys.auto.ts';",
        "import { NEXY_ROUTES, type NexyRoute } from '@nexy/routes.client.auto.ts';",
        "const importers: Importers = import.meta.glob(",
        f"  '/src/**/*.{navigable_glob()}', {{ eager: false }}",
        ") as Record<string, Importer>",
        "const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p",
        "const w: any = window as any;",
        "w.__nexy_import = (p: string) => {",
        "  let key = p;",
        "  if (!key.startsWith('/')) {",
        "    const mapped = (__NEXY_KEYS as any)[key];",
        "    if (mapped) key = mapped;",
        "  }",
        "  const k1 = norm(key);",
        "  const k2 = k1.startsWith('/') ? k1.slice(1) : k1;",
        "  const imp = (importers as any)[k1] || (importers as any)[k2];",
        "  if (!imp) return Promise.reject(new Error('Component not found: ' + p));",
        "  return imp();",
        "}",
        "const toSegments = (p: string) => p.split('/').filter(Boolean);",
        "const NAVIGABLE_EXTS = ['.tsx', '.jsx', '.vue', '.svelte', '.solid', '.preact'];",
        "const isNavigable = (route: NexyRoute) => NAVIGABLE_EXTS.some("
        "ext => route.file.endsWith(ext));",
        "const matchRoute = (pathname: string): "
        "{ route: NexyRoute | null; params: Record<string, string> } => {",
        "  const parts = toSegments(pathname);",
        "  for (const route of NEXY_ROUTES) {",
        "    if (!isNavigable(route)) continue;",
        "    const segs = toSegments(route.path);",
        "    if (segs.length !== parts.length) continue;",
        "    const params: Record<string, string> = {};",
        "    let ok = true;",
        "    for (let i = 0; i < segs.length; i++) {",
        "      const pat = segs[i];",
        "      if (pat.startsWith('{...')) { params[pat.slice(4, -1)] = "
        "parts.slice(i).join('/'); break; }",
        "      if (pat.startsWith('{')) { params[pat.slice(1, -1)] = parts[i]; continue; }",
        "      if (pat !== parts[i]) { ok = false; break; }",
        "    }",
        "    if (ok) return { route, params };",
        "  }",
        "  return { route: null, params: {} };",
        "};",
        "const mainContainer = () => document.querySelector('main') || document.body;",
        "async function renderRoute(file: string, params: Record<string, string>) {",
        "  const mod: any = await w.__nexy_import(file);",
        "  const Comp = (mod && mod.default) || mod;",
        "  const container = mainContainer();",
        "  if (w.__nexy_render) return w.__nexy_render(Comp, container, params);",
        "  if (Comp && typeof Comp === 'function') {",
        "    container.innerHTML = '<div class=\\\"nexy-client-route\\\"></div>';",
        "  }",
        "}",
        "const navigate = async (href: string, push: boolean) => {",
        "  if (href.startsWith('http') || href.startsWith('#') "
        "|| href.startsWith('mailto:')) return;",
        "  const url = new URL(href, location.origin);",
        "  const { route, params } = matchRoute(url.pathname);",
        "  if (!route) { if (push) window.location.href = href; return; }",
        "  try {",
        "    await renderRoute(route.file, params);",
        "    if (push) window.history.pushState({ nexy: true }, '', href);",
        "    document.dispatchEvent(new CustomEvent('nexy:navigated', "
        "{ detail: { pathname: url.pathname, params } }));",
        "  } catch (err) {",
        "    console.error('[Nexy] Client navigation failed:', err);",
        "    if (push) window.location.href = href;",
        "  }",
        "};",
        "document.addEventListener('click', (e: MouseEvent) => {",
        "  const target = e.target as HTMLElement;",
        "  const a = target.closest('a[data-nexy-link]');",
        "  if (!a) return;",
        "  const href = a.getAttribute('href');",
        "  if (!href || a.getAttribute('target') === '_blank') return;",
        "  if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;",
        "  const { route } = matchRoute(new URL(href, location.origin).pathname);",
        "  if (!route) return;",
        "  e.preventDefault();",
        "  navigate(href, true);",
        "});",
        "window.addEventListener('popstate', (e: PopStateEvent) => {",
        "  if (e.state && (e.state as any).nexy) { navigate(location.href, false); return; }",
        "  window.location.reload();",
        "});",
        "export {};",
    ]


def write_main_file(dest_dir: Path, frameworks: set[str]) -> None:
    """Write the minimal main.ts: react preamble (top), styles, runtime and islands."""
    preamble = _react_preamble(frameworks)
    minimal = (
        f"{preamble}\n"
        'import "/src/globale.css";\n'
        'import "@nexy/runtime.ts";\n'
        'import "@nexy/ff.auto.ts";\n'
        "export {};\n"
    )
    PathUtil.write_if_changed(dest_dir / "main.ts", minimal)


def _react_preamble(frameworks: set[str]) -> str:
    if "react" not in frameworks:
        return ""
    return (
        "// Nexy: Synchronous Preamble Injection\n"
        "if (import.meta.env.DEV) {\n"
        "  (window as any).$RefreshReg$ = () => {};\n"
        "  (window as any).$RefreshSig$ = () => (type: any) => type;\n"
        "  (window as any).__vite_plugin_react_preamble_installed__ = true;\n"
        "  import('/@react-refresh').then(m => m.default.injectIntoGlobalHook(window));\n"
        "}\n"
    )


def write_client_link(src_dir: Path) -> None:
    """Generate a typed client Link component (Next.js API, href: Route)."""
    target = src_dir / "Link.tsx"
    content = (
        "import type { ReactNode } from 'react';\n"
        "import { type Route } from '@nexy/routes.auto.ts';\n"
        "\n"
        "const w = window as any;\n"
        "\n"
        "export function Link({\n"
        "  href,\n"
        "  children,\n"
        "  className,\n"
        "  prefetch = true,\n"
        "  ...rest\n"
        "}: {\n"
        "  href: Route;\n"
        "  children?: ReactNode;\n"
        "  className?: string;\n"
        "  prefetch?: boolean;\n"
        "}) {\n"
        "  const resolved = href;\n"
        "  const preload = () => {\n"
        "    if (w.__nexy_prefetch) w.__nexy_prefetch(resolved);\n"
        "  };\n"
        "  return (\n"
        "    <a\n"
        "      href={resolved}\n"
        '      data-nexy-link="true"\n'
        "      className={className}\n"
        "      onMouseEnter={prefetch ? preload : undefined}\n"
        "      onTouchStart={prefetch ? preload : undefined}\n"
        "      {...rest}\n"
        "    >\n"
        "      {children}\n"
        "    </a>\n"
        "  );\n"
        "}\n"
        "\n"
    )
    PathUtil.write_if_changed(target, content)
