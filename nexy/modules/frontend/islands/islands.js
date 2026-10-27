
const nexyIslands = (() => {
    function idle(cb) {
        if ("requestIdleCallback" in window) {
            requestIdleCallback(cb, { timeout: 2000 });
        } else {
            setTimeout(cb, 200);
        }
    }
    function whenVisible(el, cb) {
        if (!("IntersectionObserver" in window)) { idle(cb); return; }
        const io = new IntersectionObserver((entries) => {
            for (const entry of entries) {
                if (entry.isIntersecting) {
                    io.disconnect();
                    cb();
                }
            }
        }, { rootMargin: "200px" });
        io.observe(el);
    }
    function whenMedia(query, cb) {
        const mql = window.matchMedia(query);
        if (mql.matches) { cb(); return; }
        mql.addEventListener("change", (e) => { if (e.matches) cb(); }, { once: true });
    }
    function schedule(el, directive, hydrate) {
        if (directive === "client:visible") { whenVisible(el, hydrate); return; }
        if (directive === "client:media") {
            const query = el.getAttribute("data-nexy-media") || "(min-width: 768px)";
            whenMedia(query, hydrate); return;
        }
        if (directive === "client:idle") { idle(hydrate); return; }
        hydrate();
    }
    function init(root) {
        const nodes = (root || document).querySelectorAll("[data-nexy-island]");
        nodes.forEach((el) => {
            const directive = el.getAttribute("data-nexy-directive") || "client:load";
            if (directive === "client:only") return; // rendered client-side only
            if (directive === "client:manual") return; // caller hydrates explicitly
            schedule(el, directive, () => {
                const h = el.__nexyHydrate;
                if (h) h();
            });
        });
    }
    return { init, schedule };
})();
