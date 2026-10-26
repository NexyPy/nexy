type CompMod = { default: unknown }
type Importer = () => Promise<CompMod>
type Importers = Record<string, Importer>
import { __NEXY_KEYS } from '@nexy/keys.auto.ts';
import { NEXY_ROUTES, type NexyRoute } from '@nexy/routes.client.auto.ts';
import { createRouter } from '@nexy/router.ts';
const importers: Importers = import.meta.glob(
  '/src/**/*.__NAVIGABLE_GLOB__', { eager: false }
) as Record<string, Importer>
const norm = (p: string) => p && p.startsWith('/') ? p : '/' + p
const w: any = window as any;
w.__nexy_import = (p: string) => {
  let key = p;
  if (!key.startsWith('/')) {
    const mapped = (__NEXY_KEYS as any)[key];
    if (mapped) key = mapped;
  }
  const k1 = norm(key);
  const k2 = k1.startsWith('/') ? k1.slice(1) : k1;
  const imp = (importers as any)[k1] || (importers as any)[k2];
  if (!imp) return Promise.reject(new Error('Component not found: ' + p));
  return imp();
}
const toSegments = (p: string) => p.split('/').filter(Boolean);
const NAVIGABLE_EXTS = __NAVIGABLE_EXTS__;
const isNavigable = (route: NexyRoute) => NAVIGABLE_EXTS.some(ext => route.file.endsWith(ext));
const matchRoute = (pathname: string): { route: NexyRoute | null; params: Record<string, string> } => {
  const parts = toSegments(pathname);
  for (const route of NEXY_ROUTES) {
    if (!isNavigable(route)) continue;
    const segs = toSegments(route.path);
    const last = segs[segs.length - 1] || '';
    const isCatchAll = last.startsWith('{...');
    if (isCatchAll ? parts.length < segs.length : segs.length !== parts.length) continue;
    const params: Record<string, string> = {};
    let ok = true;
    for (let i = 0; i < segs.length; i++) {
      const pat = segs[i];
      if (pat.startsWith('{...')) { params[pat.slice(4, -1)] = parts.slice(i).join('/'); break; }
      if (pat.startsWith('{')) { params[pat.slice(1, -1)] = parts[i]; continue; }
      if (pat !== parts[i]) { ok = false; break; }
    }
    if (ok) return { route, params };
  }
  return { route: null, params: {} };
};
const mainContainer = () => document.querySelector('main') || document.body;
const JSX_FRAMEWORKS = ['react', 'preact', 'solid'];
const pickRenderer = (file: string) => {
  const renderers = w.__nexy_renderers || {};
  if (file.endsWith('.vue')) return renderers.vue;
  if (file.endsWith('.svelte')) return renderers.svelte;
  const name = JSX_FRAMEWORKS.find(n => renderers[n]);
  return (name && renderers[name]) || w.__nexy_render;
};
async function renderRoute(file: string, params: Record<string, string>, layouts: string[] = []) {
  const mod: any = await w.__nexy_import(file);
  const Comp = (mod && mod.default) || mod;
  const chain = await Promise.all(layouts.map(async (p) => {
    const lm: any = await w.__nexy_import(p);
    return (lm && lm.default) || lm;
  }));
  const container = mainContainer();
  const render = pickRenderer(file);
  if (render) return render(Comp, container, params, chain);
  if (Comp && typeof Comp === 'function') {
    container.innerHTML = '<div class=\"nexy-client-route\"></div>';
  }
}
const router = createRouter({
  match: (pathname: string) => {
    const { route, params } = matchRoute(pathname);
    return route ? { file: route.file, layouts: route.layouts || [], params } : null;
  },
  render: (m) => renderRoute(m.file, m.params, m.layouts),
  prefetch: (m) => Promise.all([m.file, ...m.layouts].map(f => w.__nexy_import(f))),
});
w.__nexy_router = router;
w.__nexy_prefetch = (href: string) => router.prefetch(href);
// Only a project with client routes takes over links and the back button.
if (NEXY_ROUTES.some(isNavigable)) router.start();
export {};
