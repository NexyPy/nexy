from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME


def solid() -> FrontendFramework:
    render_script = (
        ISLANDS_RUNTIME
        + """
    (async function() {
        const w = window;
        if (w.__nexy_solid_init) return;
        w.__nexy_solid_init = true;
        w.__nexy_renderers = w.__nexy_renderers || {};

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let sj, sw;
        try {
            [sj, sw] = await Promise.all([import("solid-js"), import("solid-js/web")]);
        } catch(e) {
            console.error("[Nexy] Failed to load Solid runtime:", e);
            return;
        }

        // Layouts are built once; only the page lives in a signal, so a navigation re-creates
        // the page and leaves the layouts (and their state) alone.
        function build(Comp, props, layouts) {
            const [page, setPage] = sj.createSignal({ Comp, props });
            const pageNode = () => {
                const p = page();
                return sj.untrack(() => sj.createComponent(p.Comp, p.props));
            };
            let node = pageNode;
            for (let i = layouts.length - 1; i >= 0; i--) {
                const layout = layouts[i];
                const inner = node;
                node = () => sj.createComponent(layout, {
                    params: props,
                    get children() { return inner(); }
                });
            }
            return { root: () => node(), setPage };
        }

        const sameChain = (a, b) => a.length === b.length && a.every((c, i) => c === b[i]);

        function mountInto(host, Comp, props, layouts) {
            const built = build(Comp, props, layouts);
            host.innerHTML = "";
            const dispose = sw.render(built.root, host);
            host.__nexySolid = { layouts, setPage: built.setPage, dispose };
        }

        async function m(el) {
            if (!el || el.dataset.nexyMounted === "1") return;
            el.dataset.nexyMounted = "1";
            const key = el.getAttribute("data-nexy-key") || "";
            const path = el.dataset.nexyPath || "";
            const symbol = el.getAttribute("data-nexy-symbol") || "";
            let props = {};
            try { props = JSON.parse(el.dataset.nexyProps || "{}"); } catch(e) {}
            const ref = key || path;
            if (!ref) return;

            try {
                const mod = await gi(ref);
                const Comp = (mod && mod.default) !== undefined
                    ? mod.default
                    : (symbol && mod && mod[symbol]);
                const layoutKeys = (el.getAttribute("data-nexy-layouts") || "")
                    .split(",").filter(Boolean);
                const layouts = await Promise.all(layoutKeys.map(async (k) => {
                    const lm = await gi(k);
                    return (lm && lm.default) || lm;
                }));
                mountInto(el, Comp, props, layouts);
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
                el.dataset.nexyMounted = "0";
            }
        }

        const resolveComponent = (mod) => (mod && mod.default) || mod;

        // Client-routed projects: the root layout.tsx owns <html>, so Solid takes over the whole
        // document. The server rendered it (mode "document"), rendered only the layouts around an
        // empty page ("shell", dynamic routes in production), or could not render ("client").
        async function mountDocument(boot) {
            const props = boot.props || {};
            if (boot.mode === "client") {
                console.error(
                    "[Nexy] Solid needs the server-rendered document (Node renderer unavailable)."
                );
                return;
            }
            try {
                const Page = resolveComponent(await gi(boot.page));
                const layouts = await Promise.all(
                    (boot.layouts || []).map(async (k) => resolveComponent(await gi(k)))
                );
                // Solid reads its hydration registry from here; the server emits it as a script.
                globalThis._$HY = globalThis._$HY
                    || { events: [], completed: new WeakSet(), r: {} };
                const shell = boot.mode === "shell";
                const built = build(shell ? () => null : Page, shell ? {} : props, layouts);
                const dispose = sw.hydrate(built.root, document);
                document.__nexySolid = { layouts, setPage: built.setPage, dispose };
                if (shell) built.setPage({ Comp: Page, props });
            } catch(e) {
                console.error("[Nexy] Failed to mount the document:", e);
            }
        }

        function init() {
            const boot = document.getElementById("__nexy_page");
            if (boot) {
                try {
                    mountDocument(JSON.parse(boot.textContent || "{}"));
                } catch(e) {
                    console.error("[Nexy] Invalid page description:", e);
                }
                return;
            }
            const nodes = document.querySelectorAll('[data-nexy-fw="solid"]');
            for (let i = 0; i < nodes.length; i++) {
                if (nodes[i].hasAttribute("data-nexy-island")) {
                    const directive = nodes[i].getAttribute("data-nexy-directive");
                    if (directive === "client:only") continue;
                    const el = nodes[i];
                    el.__nexyHydrate = () => m(el);
                } else {
                    m(nodes[i]);
                }
            }
            nexyIslands.init(document);
        }

        // Client navigation: same layouts -> swap the page only; another chain -> remount.
        w.__nexy_renderers.solid = (Comp, container, props, layouts) => {
            const owner = document.__nexySolid;
            if (owner) {
                // The document is Solid's root: only the page can change in place. Another layout
                // chain cannot be swapped under <html>, so load that page normally.
                if (sameChain(owner.layouts, layouts || [])) {
                    owner.setPage({ Comp, props: props || {} });
                } else {
                    w.location.reload();
                }
                return;
            }
            const host = container.querySelector(':scope > [data-nexy-fw="solid"]') || container;
            const chain = layouts || [];
            const current = host.__nexySolid;
            if (current && sameChain(current.layouts, chain)) {
                current.setPage({ Comp, props: props || {} });
                return;
            }
            if (current) current.dispose();
            mountInto(host, Comp, props || {}, chain);
        };

        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", init);
        } else {
            init();
        }
    })();
    """
    )

    return FrontendFramework(
        name="solid",
        render=render_script,
        extension=["jsx", "tsx"],
    )
