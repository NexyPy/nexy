
    // Builds the page in a detached <body>, then swaps it for the live one. <html> and <head> stay
    // as the server sent them; the attributes of the old body are kept when the new one lacks them.
    function nexyTakeOver(render) {
        const fresh = document.createElement("body");
        const result = render(fresh);
        // Preact renders its own <html><body> inside the target; the others render body content.
        const own = fresh.querySelector(":scope > html > body") || fresh;
        const live = document.body;
        for (const attr of Array.from(live.attributes)) {
            if (!own.hasAttribute(attr.name)) own.setAttribute(attr.name, attr.value);
        }
        live.replaceWith(own);
        return result;
    }

    (async function() {
        const w = window;
        if (w.__nexy_vue_init) return;
        w.__nexy_vue_init = true;
        w.__nexy_renderers = w.__nexy_renderers || {};

        const gi = w.__nexy_import || ((p) => import(/* @vite-ignore */ p));

        let Vue;
        try {
            Vue = await import("vue");
        } catch(e) {
            console.error("[Nexy] Failed to load Vue runtime:", e);
            return;
        }

        function resolveComponent(mod, symbol) {
            if (symbol && mod[symbol]) return mod[symbol];
            if (mod.__vccOpts) return mod;
            if (mod.default) return mod.default;
            return mod;
        }

        // The whole page is one reactive state: a navigation swaps the page and keeps the
        // layouts mounted, a different layout chain remounts them.
        function makeRoot(state) {
            return {
                render: () => {
                    const s = state.value;
                    let node = () => Vue.h(s.Comp, s.props, s.slots);
                    for (let i = s.layouts.length - 1; i >= 0; i--) {
                        const layout = s.layouts[i];
                        const inner = node;
                        node = () => Vue.h(layout, s.props, { default: inner });
                    }
                    return node();
                }
            };
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
            } catch(e) {}

            let slots = {};
            if (props.children === true || props.children === "true") {
                slots.default = () => Vue.h("div", {
                    innerHTML: serverHTML,
                    style: { display: "contents" }
                });
                delete props.children;
            }

            el.dataset.nexyMounted = "1";
            const ref = key || path;
            if (!ref) return;

            try {
                const mod = await gi(ref);
                const Comp = resolveComponent(mod, symbol);

                if (!Comp || (typeof Comp !== 'object' && typeof Comp !== 'function')) {
                    throw new Error(`The module at ${ref} does not export a valid Vue component.`);
                }

                // Nested layouts (layout.vue above the page), outermost first.
                const layoutKeys = (el.getAttribute("data-nexy-layouts") || "")
                    .split(",").filter(Boolean);
                const layouts = await Promise.all(layoutKeys.map(async (k) => {
                    return resolveComponent(await gi(k), "");
                }));

                const state = Vue.shallowRef({ Comp, props, slots, layouts });
                el.__nexyVue = { state };
                const hydrate = serverHTML.trim() !== "" && !slots.default && layouts.length === 0;
                const app = hydrate
                    ? Vue.createSSRApp(makeRoot(state))
                    : Vue.createApp(makeRoot(state));
                if (!hydrate) el.innerHTML = "";
                app.mount(el);
            } catch(e) {
                console.error(`[Nexy] Execution error in ${ref}:`, e);
                // Unmark so it can be retried or debugged
                el.dataset.nexyMounted = "0";
            }
        }

        // Client-routed projects: the root layout.vue owns <html>. The browser builds the body.
        async function mountDocument(boot) {
            try {
                const Comp = resolveComponent(await gi(boot.page), "");
                const layouts = await Promise.all((boot.layouts || []).map(async (key) => {
                    return resolveComponent(await gi(key), "");
                }));
                const state = Vue.shallowRef({ Comp, props: boot.props || {}, slots: {}, layouts });
                nexyTakeOver((body) => Vue.createApp(makeRoot(state)).mount(body));
                document.__nexyVue = { state };
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
            const nodes = document.querySelectorAll('[data-nexy-fw="vue"]');
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

        // Client navigation: update the state of the app that already hosts the page, so the
        // layouts keep their state; mount a fresh app only on the first navigation.
        w.__nexy_renderers.vue = (Comp, container, props, layouts) => {
            const next = { Comp, props: props || {}, slots: {}, layouts: layouts || [] };
            if (document.__nexyVue) {
                document.__nexyVue.state.value = next;
                return;
            }
            const host = container.querySelector(':scope > [data-nexy-fw="vue"]') || container;
            if (host.__nexyVue) {
                host.__nexyVue.state.value = next;
                return;
            }
            host.innerHTML = "";
            const state = Vue.shallowRef(next);
            host.__nexyVue = { state };
            Vue.createApp(makeRoot(state)).mount(host);
        };

        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", init);
        } else {
            init();
        }
    })();
    