from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME
from nexy.modules.frontend.takeover import TAKEOVER_RUNTIME


def svelte() -> FrontendFramework:
    render_script = (
        ISLANDS_RUNTIME
        + TAKEOVER_RUNTIME
        + """
    (async function() {
        const w = window;
        if (w.__nexy_svelte_init) return;
        w.__nexy_svelte_init = true;
        w.__nexy_renderers = w.__nexy_renderers || {};

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let sv;
        try {
            sv = await import("svelte");
        } catch(e) {
            console.error("[Nexy] Failed to load Svelte runtime:", e);
            return;
        }

        // A layout.svelte receives the page as its `children` snippet. The snippet renders an
        // empty slot element; the next layout (or the page) is then mounted into that element.
        const slotSnippet = () => sv.createRawSnippet(() => ({
            render: () => '<div data-nexy-slot style="display:contents"></div>'
        }));

        function mountChain(target, Comp, props, layouts) {
            const instances = [];
            let slot = target;
            for (const layout of layouts) {
                instances.push(sv.mount(layout, {
                    target: slot,
                    props: { ...props, params: props, children: slotSnippet() }
                }));
                slot = slot.querySelector("[data-nexy-slot]") || slot;
            }
            const page = sv.mount(Comp, { target: slot, props });
            return { layouts, instances, slot, page };
        }

        function teardown(state) {
            sv.unmount(state.page);
            for (let i = state.instances.length - 1; i >= 0; i--) sv.unmount(state.instances[i]);
        }

        const sameChain = (a, b) => a.length === b.length && a.every((c, i) => c === b[i]);

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

                if (layouts.length === 0 && el.innerHTML.trim().length > 0) {
                    el.__nexySvelte = null;
                    sv.hydrate(Comp, { target: el, props });
                    return;
                }
                el.innerHTML = "";
                el.__nexySvelte = mountChain(el, Comp, props, layouts);
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
                el.dataset.nexyMounted = "0";
            }
        }

        // Client-routed projects: the root layout.svelte owns <html>. Its client build holds the
        // body content only (the Vite plugin strips <html>, <head> and <body>), in a new body.
        async function mountDocument(boot) {
            try {
                const pick = (mod) => (mod && mod.default) || mod;
                const Comp = pick(await gi(boot.page));
                const layouts = await Promise.all(
                    (boot.layouts || []).map(async (k) => pick(await gi(k)))
                );
                document.__nexySvelte = nexyTakeOver((body) => {
                    return mountChain(body, Comp, boot.props || {}, layouts);
                });
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
            const nodes = document.querySelectorAll('[data-nexy-fw="svelte"]');
            nodes.forEach((el) => {
                if (el.hasAttribute("data-nexy-island")) {
                    const directive = el.getAttribute("data-nexy-directive");
                    if (directive === "client:only") return;
                    el.__nexyHydrate = () => m(el);
                } else {
                    m(el);
                }
            });
            nexyIslands.init(document);
        }

        // Client navigation: same layouts -> replace the page inside the innermost slot;
        // another chain -> rebuild.
        w.__nexy_renderers.svelte = (Comp, container, props, layouts) => {
            const owned = Boolean(document.__nexySvelte);
            const host = owned
                ? document.body
                : container.querySelector(':scope > [data-nexy-fw="svelte"]') || container;
            const chain = layouts || [];
            const current = owned ? document.__nexySvelte : host.__nexySvelte;
            if (current && sameChain(current.layouts, chain)) {
                sv.unmount(current.page);
                current.slot.innerHTML = "";
                current.page = sv.mount(Comp, { target: current.slot, props: props || {} });
                return;
            }
            if (current) teardown(current);
            host.innerHTML = "";
            const mounted = mountChain(host, Comp, props || {}, chain);
            if (owned) document.__nexySvelte = mounted;
            else host.__nexySvelte = mounted;
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
        name="svelte",
        render=render_script,
        extension=["svelte"],
    )
