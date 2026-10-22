/**
 * Nexy docs - runtime.
 *
 * - Soft navigation: clicking an internal link fetches the target page and swaps
 *   the content without a full reload (SEO stays intact: every page is a real file).
 * - Search UI (fuzzy suggestions via NexySearch).
 * - Dark/light theme, copy buttons, mobile sidebar, scroll-spy TOC.
 */
(function () {
  "use strict";

  const $ = (sel, root) => (root || document).querySelector(sel);
  const $$ = (sel, root) => Array.from((root || document).querySelectorAll(sel));

  const prefersReducedMotion = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------ soft navigation ------------------------------ */

  function currentLocale() {
    const m = location.pathname.match(/(^|\/)(en|fr)(?:\/|$)/);
    return m ? m[2] : document.body.dataset.locale || "en";
  }

  function isInternal(href) {
    if (!href) return false;
    if (href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) return false;
    try {
      const url = new URL(href, location.href);
      return url.origin === location.origin;
    } catch {
      return false;
    }
  }

  let pendingNav = null;

  async function softNavigate(url, replace) {
    if (location.protocol === "file:") return; // fetch is blocked on file://
    if (pendingNav) return;
    const abs = new URL(url, location.href).href;
    if (abs === location.href) return;
    pendingNav = true;
    try {
      const res = await fetch(abs, { headers: { "X-Nexy-Soft": "1" } });
      if (!res.ok) throw new Error(res.status);
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, "text/html");
      const title = doc.querySelector("title")?.textContent || document.title;
      const newBody = doc.body.innerHTML;
      const commit = () => {
        if (replace) history.replaceState({}, "", abs);
        else history.pushState({}, "", abs);
        document.title = title;
        document.body.dataset.locale = currentLocale();
        document.body.innerHTML = newBody;
        window.scrollTo({ top: 0 });
        init();
      };
      if (document.startViewTransition && !prefersReducedMotion()) document.startViewTransition(commit);
      else commit();
    } catch (err) {
      // fallback to a full page load
      location.href = abs;
    } finally {
      pendingNav = false;
    }
  }

  document.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button !== 0) return;
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const link = e.target.closest("a[href]");
    if (!link) return;
    const href = link.getAttribute("href");
    if (!href || href.startsWith("#")) return;
    if (!isInternal(href)) return;
    if (link.target && link.target !== "_self") return;
    e.preventDefault();
    const url = new URL(href, location.href);
    if (url.hash) {
      // same-page anchor
      if (url.pathname === location.pathname) {
        const el = document.getElementById(url.hash.slice(1));
        if (el) el.scrollIntoView({ behavior: "smooth" });
        return;
      }
    }
    softNavigate(url.href);
  });

  window.addEventListener("popstate", () => {
    if (location.protocol !== "file:") softNavigate(location.href, true);
  });

  /* ----------------------------------- theme ----------------------------------- */

  function themeFromStorage() {
    try { return localStorage.getItem("nexy-theme"); } catch { return null; }
  }
  const MOON_ICON =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>';
  const SUN_ICON =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>';
  function applyTheme(t, animate) {
    const btn = $("#themeBtn");
    if (btn) btn.innerHTML = t === "dark" ? MOON_ICON : SUN_ICON;
    const commit = () => { document.documentElement.dataset.theme = t; };
    if (animate && document.startViewTransition && !prefersReducedMotion()) document.startViewTransition(commit);
    else commit();
    try { localStorage.setItem("nexy-theme", t); } catch {}
  }
  function initTheme() {
    const stored = themeFromStorage();
    const t = stored || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    applyTheme(t);
    document.addEventListener("click", (e) => {
      const btn = e.target.closest("#themeBtn");
      if (!btn) return;
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      applyTheme(next, true);
    });
  }

  /* ----------------------------------- search ----------------------------------- */

  function posixRelative(fromDir, toDir) {
    const from = fromDir.split("/").filter(Boolean);
    const to = toDir.split("/").filter(Boolean);
    let i = 0;
    while (i < from.length && i < to.length && from[i] === to[i]) i++;
    const up = from.length - i;
    const parts = [];
    for (let k = 0; k < up; k++) parts.push("..");
    parts.push(...to.slice(i));
    let rel = parts.join("/");
    if (!rel) rel = "./";
    return rel.endsWith("/") ? rel : `${rel}/`;
  }

  function currentDir() {
    let p = location.pathname;
    p = p.split("?")[0];
    if (p.endsWith("/")) p = p.slice(0, -1);
    if (p.endsWith("/index.html")) p = p.slice(0, -"/index.html".length);
    return p.replace(/^\/+/g, "");
  }

  /** Convert an absolute doc path like "en/routing/fbr/" to an href relative to the current page. */
  function relDoc(abs) {
    const target = abs.replace(/^\/+|\/+$/g, "");
    return posixRelative(currentDir(), target);
  }

  function searchItemHTML(r) {
    return `<a class="search-item" href="${relDoc(r.href)}" data-nav>
      <div class="search-item-title">${r.title}</div>
      <div class="search-item-path">${r.section}</div>
      ${r.snippet ? `<div class="search-item-snippet">${r.snippet}</div>` : ""}
    </a>`;
  }

  function openModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.dataset.prev = document.activeElement ? document.activeElement.id : "";
    m.hidden = false;
    document.body.style.overflow = "hidden";
  }
  function closeModal(id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.hidden = true;
    document.body.style.overflow = "";
    const prev = document.getElementById(m.dataset.prev || "");
    if (prev) prev.focus();
  }

  function runSearch(input) {
    const locale = currentLocale();
    const q = input.value;
    const panel = $("#searchPanel");
    if (!panel) return;
    if (!q.trim()) { panel.innerHTML = ""; return; }
    const { results, dym } = window.NexySearch.query(q, locale);
    let html = "";
    if (dym.length) {
      html += `<div class="search-didyoumean"><span class="dym-label">Did you mean:</span>` +
        dym.map((t) => `<button class="dym-chip" type="button" data-q="${t}">${t}</button>`).join("") + "</div>";
    }
    if (!results.length) {
      html += `<div class="search-empty">No results for "${q}"</div>`;
    } else {
      let lastSection = "";
      for (const r of results) {
        if (r.section !== lastSection) { html += `<div class="search-section-label">${r.section}</div>`; lastSection = r.section; }
        html += searchItemHTML(r);
      }
    }
    panel.innerHTML = html;
  }

  let searchTimer = null;
  function initSearch() {
    const input = $("#searchInput");
    if (!input) return;
    const panel = $("#searchPanel");
    input.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => runSearch(input), 120);
    });
    input.addEventListener("keydown", (e) => {
      const items = $$(".search-item", panel);
      if (e.key === "Escape") { closeModal("searchModal"); return; }
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        let idx = items.findIndex((el) => el.classList.contains("active"));
        idx = e.key === "ArrowDown" ? Math.min(idx + 1, items.length - 1) : Math.max(idx - 1, 0);
        items.forEach((el, i) => el.classList.toggle("active", i === idx));
        items[idx]?.scrollIntoView({ block: "nearest" });
      } else if (e.key === "Enter") {
        const active = $(".search-item.active", panel) || items[0];
        if (active) { closeModal("searchModal"); active.click(); }
      }
    });
    panel.addEventListener("click", (e) => {
      const chip = e.target.closest(".dym-chip");
      if (chip) { input.value = chip.dataset.q; runSearch(input); }
      const item = e.target.closest(".search-item");
      if (item) { closeModal("searchModal"); }
    });
  }

  function initModals() {
    document.addEventListener("click", (e) => {
      if (e.target.closest("#searchTrigger")) {
        openModal("searchModal");
        setTimeout(() => $("#searchInput")?.focus(), 30);
        return;
      }
      const closer = e.target.closest("[data-close]");
      if (closer) {
        const modal = closer.closest(".search-modal");
        if (modal) closeModal(modal.id);
      }
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        if (!$("#searchModal")?.hidden) closeModal("searchModal");
        return;
      }
      const modal = $("#searchModal");
      if (e.key === "Tab") {
        const alive = [modal].find((m) => m && !m.hidden);
        if (alive) {
          const focusables = Array.from(alive.querySelectorAll("input, a, button"))
            .filter((el) => !el.hasAttribute("hidden") && el.offsetParent !== null);
          if (!focusables.length) return;
          const first = focusables[0];
          const last = focusables[focusables.length - 1];
          if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
          else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        }
      }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        openModal("searchModal");
        setTimeout(() => $("#searchInput")?.focus(), 30);
      }
    });
  }

  /* ----------------------------------- misc ----------------------------------- */

  function initCopy() {
    const COPY_ICON =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>';
    const CHECK_ICON =
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>';
    document.addEventListener("click", async (e) => {
      const btn = e.target.closest(".copy");
      if (!btn) return;
      const block = btn.closest(".codeblock");
      const code = block ? block.querySelector("code") : null;
      const text = code ? code.innerText : "";
      const done = () => { btn.innerHTML = CHECK_ICON; setTimeout(() => { btn.innerHTML = COPY_ICON; }, 1200); };
      try {
        await navigator.clipboard.writeText(text);
        done();
      } catch {
        const ta = document.createElement("textarea");
        ta.value = text;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
        done();
      }
    });
  }

  function initSidebar() {
    const btn = $("#menuBtn");
    if (!btn) return;
    const mobileNav = document.getElementById("mobileNav");
    if (mobileNav) {
      const close = () => { mobileNav.hidden = true; btn.setAttribute("aria-expanded", "false"); };
      btn.addEventListener("click", () => {
        const open = mobileNav.hidden;
        mobileNav.hidden = !open;
        btn.setAttribute("aria-expanded", String(open));
      });
      mobileNav.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
      document.addEventListener("click", (e) => {
        if (!mobileNav.hidden && !e.target.closest(".app-mobile-menu") && !e.target.closest("#menuBtn")) close();
      });
      return;
    }
    const sidebar = $("#sidebar");
    if (!sidebar) return;
    const close = () => { sidebar.classList.remove("open"); btn.setAttribute("aria-expanded", "false"); };
    btn.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      btn.setAttribute("aria-expanded", String(open));
    });
    sidebar.addEventListener("click", (e) => { if (e.target.closest("a")) close(); });
    document.addEventListener("click", (e) => {
      if (sidebar.classList.contains("open") && !e.target.closest(".sidebar") && !e.target.closest("#menuBtn")) close();
    });
  }

  function initScrollSpy() {
    const links = $$(".toc-list a");
    if (!links.length) return;
    const ids = links.map((a) => a.getAttribute("href").slice(1)).filter(Boolean);
    const map = new Map();
    ids.forEach((id, i) => map.set(id, links[i]));
    const io = new IntersectionObserver(
      (entries) => {
        for (const en of entries) {
          if (en.isIntersecting) {
            links.forEach((a) => a.classList.remove("active"));
            const link = map.get(en.target.id);
            if (link) link.classList.add("active");
          }
        }
      },
      { rootMargin: "-70px 0px -70% 0px", threshold: 0 }
    );
    $$(".article h2[id], .article h3[id]").forEach((h) => io.observe(h));
  }

  function initTabs() {
    document.addEventListener("click", (e) => {
      const label = e.target.closest(".code-tab-label");
      if (!label) return;
      const tab = label.closest(".code-tab");
      const tabs = tab.parentElement;
      tabs.querySelectorAll(".code-tab").forEach((t) => {
        t.removeAttribute("data-active");
        const l = t.querySelector(".code-tab-label");
        if (l) l.setAttribute("aria-selected", "false");
      });
      tab.setAttribute("data-active", "");
      label.setAttribute("aria-selected", "true");
    });
  }

  function initAccordion() {
    document.addEventListener("click", (e) => {
      const title = e.target.closest(".nav-group-title");
      if (!title) return;
      const group = title.closest(".nav-group");
      if (!group || group.classList.contains("pinned")) return;
      const willOpen = !group.classList.contains("open");
      const sidebar = group.closest(".sidebar");
      if (sidebar) {
        sidebar.querySelectorAll(".nav-group.open").forEach((g) => {
          if (g !== group) {
            g.classList.remove("open");
            const t = g.querySelector(".nav-group-title");
            if (t) t.setAttribute("aria-expanded", "false");
          }
        });
      }
      group.classList.toggle("open", willOpen);
      title.setAttribute("aria-expanded", String(willOpen));
    });
  }

  function initRouterFilter() {
    const seg = $("#routerSeg");
    if (!seg) return;
    const opts = $$(".router-opt", seg);
    const STORE = "nexy.router";
    let mode = "fbr";
    try {
      const saved = localStorage.getItem(STORE);
      if (saved === "modular" || saved === "fbr") mode = saved;
    } catch {
      /* storage unavailable */
    }
    const setPressed = () => {
      opts.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.route === mode)));
    };
    const apply = () => {
      $$(".sidebar-mode", document).forEach((el) => {
        el.hidden = el.dataset.mode !== mode;
      });
      setPressed();
    };
    const syncFromActive = () => {
      const active = $("#sidebar [aria-current=\"page\"]");
      if (!active) return;
      const wrapper = active.closest(".sidebar-mode");
      if (wrapper && wrapper.dataset.mode && wrapper.dataset.mode !== mode) {
        mode = wrapper.dataset.mode;
        try {
          localStorage.setItem(STORE, mode);
        } catch {
          /* storage unavailable */
        }
      }
    };
    seg.addEventListener("click", (e) => {
      const btn = e.target.closest(".router-opt");
      if (!btn) return;
      mode = btn.dataset.route;
      try {
        localStorage.setItem(STORE, mode);
      } catch {
        /* storage unavailable */
      }
      apply();
    });
    syncFromActive();
    apply();
  }

  function init() {
    initTheme();
    initSearch();
    initModals();
    initCopy();
    initSidebar();
    initAccordion();
    initScrollSpy();
    initTabs();
    initRouterFilter();
  }

  initModals();
  initTheme();
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
