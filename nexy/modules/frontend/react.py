from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME


def react() -> FrontendFramework:
    render_script = (
        ISLANDS_RUNTIME
        + """
    (async function() {
        const w = window;
        if (w.__nexy_react_init) return;
        w.__nexy_react_init = true;

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let React, RDC;
        try {
            [React, RDC] = await Promise.all([
                import("react"),
                import("react-dom/client")
            ]);
        } catch(e) {
            console.error("[Nexy] Failed to load React runtimes:", e);
            return;
        }

        async function m(el) {
            if (!el || el.dataset.nexyMounted === "1") return;

            const key = el.getAttribute("data-nexy-key") || "";
            const path = el.dataset.nexyPath || "";
            const symbol = el.getAttribute("data-nexy-symbol") || "";
            const propsStr = el.dataset.nexyProps || "{}";
            const serverHTML = el.innerHTML;

            let props = {};
            try {
                props = JSON.parse(propsStr);
            } catch(e) {
                console.error("[Nexy] Failed to parse props:", e);
            }

            if (props.children === true || props.children === "true") {
                props.children = React.createElement("div", {
                    dangerouslySetInnerHTML: { __html: serverHTML },
                    style: { display: "contents" },
                    suppressHydrationWarning: true
                });
            }

            el.dataset.nexyMounted = "1";
            const ref = key || path;
            if (!ref) return;

            try {
                const mod = await gi(ref);

                // Robust Export Resolution
                let Comp = null;
                if (symbol && mod[symbol]) {
                    Comp = mod[symbol];
                } else if (mod.default) {
                    Comp = mod.default;
                } else {
                    // Fallback for modules that export the component directly
                    Comp = mod;
                }

                if (!Comp || (typeof Comp !== 'function' && typeof Comp.render !== 'function')) {
                    throw new Error(`No valid React component found in ${ref}.`);
                }

                // Nested layouts (layout.tsx above the page), outermost first.
                const layoutKeys = (el.getAttribute("data-nexy-layouts") || "")
                    .split(",").filter(Boolean);
                const layouts = await Promise.all(layoutKeys.map(async (k) => {
                    const lm = await gi(k);
                    return (lm && lm.default) || lm;
                }));
                let tree = React.createElement(Comp, props);
                for (let i = layouts.length - 1; i >= 0; i--) {
                    tree = React.createElement(layouts[i], { params: props }, tree);
                }
                const element = React.createElement(React.StrictMode, null, tree);

                if (serverHTML.trim() !== "" && !(props.children)) {
                    el.__nexyRoot = RDC.hydrateRoot(el, element);
                } else {
                    el.__nexyRoot = RDC.createRoot(el);
                    el.__nexyRoot.render(element);
                }
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
            }
        }

        function init() {
            const nodes = document.querySelectorAll('[data-nexy-fw="react"]');
            nodes.forEach((el) => {
                if (el.hasAttribute("data-nexy-island")) {
                    const directive = el.getAttribute("data-nexy-directive");
                    if (directive === "client:only") return;
                    const media = el.getAttribute("data-nexy-media") || "";
                    if (media) el.dataset.nexyMedia = media;
                    el.__nexyHydrate = () => m(el);
                } else {
                    m(el);
                }
            });
            nexyIslands.init(document);
        }

        // Client navigation: re-render into the root that already hosts the page, so the
        // layouts keep their state; only the page element changes.
        w.__nexy_render = (Comp, container, props, layouts) => {
            const host = container.querySelector(':scope > [data-nexy-fw="react"]') || container;
            let tree = React.createElement(Comp, props || {});
            const chain = layouts || [];
            for (let i = chain.length - 1; i >= 0; i--) {
                tree = React.createElement(chain[i], { params: props || {} }, tree);
            }
            if (!host.__nexyRoot) host.__nexyRoot = RDC.createRoot(host);
            host.__nexyRoot.render(React.createElement(React.StrictMode, null, tree));
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
        name="react",
        render=render_script,
        extension=["jsx", "tsx"],
    )
