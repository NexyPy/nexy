
/**
 * Nexy docs static site generator.
 *
 * Reads js/content.js and emits a multi-page HTML site (SEO-friendly):
 *   - <locale>/<section>/<page>/index.html   one real HTML document per page
 *   - index.html                             bilingual landing page
 *   - 404.html
 *   - js/search-index.js                     search index (consumed by js/search.js)
 *
 * All internal links are relative, so the site works on GitHub Pages
 * (including project sites under a subpath) and even from file://.
 *
 * Usage:
 *   node js/build.mjs                # default: build into packages/docs (in place)
 *   SITE_URL=https://x.dev node js/build.mjs
 */
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const SITE_URL = process.env.SITE_URL ?? "https://nexy.dev/";

/* ---------------------------------- load data ---------------------------------- */

function loadDocs() {
  const src = fs.readFileSync(path.join(ROOT, "js", "content.js"), "utf8");
  const sandbox = { window: {} };
  vm.runInNewContext(src + "\nwindow.NEXY_DOCS", sandbox);
  return sandbox.window.NEXY_DOCS;
}

const DOCS = loadDocs();

/* ----------------------------------- helpers ----------------------------------- */

/** Inline SVG icons - stroke "currentColor" so they inherit the accent in context. */
/* Official Lucide icon set (lucide.dev, ISC) - same icons the Nexy app uses via lucide-react.
 * All 24x24, stroke 2, round caps. */
const S = (inner) =>
  `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${inner}</svg>`;
const ICONS = {
  search: S('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'),
  github: S('<path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/>'),
  sun: S('<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>'),
  moon: S('<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>'),
  menu: S('<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>'),
  close: S('<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'),
  globe: S('<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>'),
  gradCap: S('<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>'),
  copy: S('<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>'),
  check: S('<path d="M20 6 9 17l-5-5"/>'),
  routers: S('<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>'),
  file: S('<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/>'),
  zap: S('<path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/>'),
  sparkle: S('<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/><path d="M20 3v4"/><path d="M22 5h-4"/><path d="M4 17v2"/><path d="M5 18H3"/>'),
  arrowRight: S('<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>'),
  chevronRight: S('<path d="m9 18 6-6-6-6"/>'),
  arrowLeft: S('<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>'),
  link: S('<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>'),
  server: S('<rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/>'),
  layers: S('<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>'),
  palette: S('<circle cx="13.5" cy="6.5" r=".5"/><circle cx="17.5" cy="10.5" r=".5"/><circle cx="8.5" cy="7.5" r=".5"/><circle cx="6.5" cy="12.5" r=".5"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>'),
  terminal: S('<polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/>'),
  package: S('<path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>'),
  refreshCw: S('<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>'),
  shield: S('<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1 1 0 0 1 1.2 0C14.5 3.8 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>'),
};

function icon(name, size = 16) {
  return `<span class="icon" style="width:${size}px;height:${size}px">${ICONS[name] ?? ""}</span>`;
}

function esc(s) {
  return String(s)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function slugify(text) {
  return text
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^\w]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** Relative href from current doc dir (e.g. "en/routing/overview") to an absolute doc path ("/en/routing/fbr"). */
function relTo(docDir, abs) {
  const target = path.posix.dirname(`${abs.replace(/^\/+|\/+$/g, "")}/index.html`);
  let rel = path.posix.relative(docDir, target);
  if (!rel.startsWith(".")) rel = `./${rel}`;
  return rel.endsWith("/") ? rel : `${rel}/`;
}

/** Relative href from current doc dir to the site root landing page. */
function relHome(docDir) {
  let rel = path.posix.relative(docDir, ".");
  return rel === "" ? "./" : `${rel}/`;
}

/** Render inline markup: `code` and [[label|#/abs/path]] links. */
function inline(text, rel) {
  let out = "";
  for (const part of text.split(/(`[^`]+`|\[\[[^\]]+\]\])/g)) {
    if (!part) continue;
    if (part.startsWith("`") && part.endsWith("`")) {
      out += `<code>${esc(part.slice(1, -1))}</code>`;
    } else if (part.startsWith("[[") && part.endsWith("]]")) {
      const [label, abs] = part.slice(2, -2).split("|");
      out += `<a href="${rel(abs.trim().replace(/^#/, ""))}" data-nav>${esc(label.trim())}</a>`;
    } else {
      out += esc(part);
    }
  }
  return out;
}

/* --------------------------------- highlighting -------------------------------- */

function buildLang(spec) {
  const master = new RegExp(spec.map(([, src]) => `(${src})`).join("|"), "g");
  return (code) => {
    const out = [];
    let last = 0;
    let m;
    const re = new RegExp(master.source, master.flags);
    while ((m = re.exec(code)) !== null) {
      if (m.index > last) out.push(esc(code.slice(last, m.index)));
      let cls = null;
      for (let i = 0; i < spec.length; i++) if (m[i + 1] !== undefined) cls = spec[i][0];
      out.push(cls ? `<span class="tk-${cls}">${esc(m[0])}</span>` : esc(m[0]));
      last = m.index + m[0].length;
      if (m[0] === "") re.lastIndex++;
    }
    if (last < code.length) out.push(esc(code.slice(last)));
    return out.join("");
  };
}

const HL = {
  python: buildLang([
    ["s", String.raw`"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`],
    ["c", String.raw`#[^\n]*`],
    ["d", String.raw`@\w+`],
    ["f", String.raw`\b[A-Za-z_]\w*(?=\()`],
    ["k", String.raw`\b(?:def|class|import|from|return|if|elif|else|for|while|try|except|finally|with|as|pass|break|continue|lambda|yield|async|await|raise|not|and|or|in|is|None|True|False|self|global|nonlocal|del)\b`],
    ["n", String.raw`\b\d+(?:\.\d+)?\b`],
  ]),
  bash: buildLang([
    ["s", String.raw`"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`],
    ["c", String.raw`#[^\n]*`],
    ["v", String.raw`\$\{?[A-Za-z_][\w]*\}?`],
    ["o", String.raw`--?[A-Za-z][\w-]*`],
    ["k", String.raw`\b(?:cd|echo|if|then|else|fi|for|do|done|while|function|export|source|sudo|python|pip|uv|npm|nexy)\b`],
    ["n", String.raw`\b\d+\b`],
  ]),
  json: buildLang([
    ["k", String.raw`"[^"\n]*"(?=\s*:)`],
    ["s", String.raw`"(?:[^"\\\n]|\\.)*"`],
    ["b", String.raw`\b(?:true|false|null)\b`],
    ["n", String.raw`-?\b\d+(?:\.\d+)?\b`],
  ]),
  js: buildLang([
    ["c", String.raw`\/\/[^\n]*|\/\*[\s\S]*?\*\/`],
    ["s", String.raw`"(?:[^"\\\n]|\\.)*"|'(?:[^'\\\n]|\\.)*'`],
    ["k", String.raw`\b(?:const|let|var|function|return|import|export|from|if|else|for|while|new|class|async|await|=>|interface|type)\b`],
    ["f", String.raw`\b[A-Za-z_$][\w$]*(?=\()`],
    ["n", String.raw`\b\d+(?:\.\d+)?\b`],
  ]),
};

function highlight(lang, code, fname) {
  const fn = HL[lang] ?? esc;
  const label = esc(fname || lang);
  return `<div class="codeblock" data-lang="${esc(lang)}">
  <div class="code-head">
    <span class="code-fname">${label}</span>
    ${fname && lang && lang !== "text" ? `<span class="code-lang">${esc(lang)}</span>` : ""}
    <button class="copy" type="button" aria-label="Copy" title="Copy">${icon("copy", 14)}</button>
  </div>
  <pre><code>${fn(code)}</code></pre>
</div>`;
}

/* -------------------------------- block rendering ------------------------------- */

function plainTextOf(block) {
  const [type, ...rest] = block;
  if (type === "code") return rest[1] ?? "";
  if (type === "table") return rest.flat(1).map((c) => (Array.isArray(c) ? c.join(" ") : c)).join(" ");
  if (type === "ul" || type === "ol") return rest[0].join(" ");
  if (type === "pkgtabs") return rest[0].map(([, code]) => code).join(" ");
  if (typeof rest[0] !== "string") return "";
  return rest[0].replace(/`/g, "").replace(/\[\[([^\]]*)\|#\/[^\]]+\]\]/g, "$1");
}

function renderBlocks(blocks, rel, ids, toc) {
  const html = [];
  let h2Seen = false;
  for (const block of blocks) {
    const [type, ...rest] = block;
    switch (type) {
      case "lead":
        html.push(`<p class="lead">${inline(rest[0], rel)}</p>`);
        break;
      case "p":
        html.push(`<p>${inline(rest[0], rel)}</p>`);
        break;
      case "h2":
      case "h3": {
        const text = rest[0];
        const base = slugify(text);
        let id = base;
        let n = 2;
        while (ids.has(id)) id = `${base}-${n++}`;
        ids.add(id);
        toc.push({ id, text, level: type });
        if (type === "h2") {
          if (h2Seen) html.push('<hr class="section-sep" role="separator" aria-hidden="true" />');
          h2Seen = true;
        }
        html.push(`<${type} id="${id}">${inline(text, rel)}<a class="heading-anchor" href="#${id}" aria-label="${type === "h2" ? "Section" : "Sub-section"} link">${icon("link", 14)}</a></${type}>`);
        break;
      }
      case "ul":
      case "ol":
        html.push(`<${type}>${rest[0].map((li) => `<li>${inline(li, rel)}</li>`).join("")}</${type}>`);
        break;
      case "code":
        html.push(highlight(rest[0], rest[1], rest[2]));
        break;
      case "pkgtabs": {
        const tabs = rest[0]
          .map(
            ([label, code], i) =>
              `<div class="code-tab"${i === 0 ? ' data-active=""' : ""}><button type="button" class="code-tab-label" role="tab" aria-selected="${i === 0}">${esc(label)}</button><div class="code-tab-body">${highlight("bash", code, `${label} install`)}</div></div>`
          )
          .join("");
        html.push(`<div class="code-tabs" role="tablist">${tabs}</div>`);
        break;
      }
      case "callout": {
        const icon = { tip: "?", note: "i", warn: "!", danger: "!" }[rest[0]] ?? "i";
        html.push(`<div class="callout callout-${esc(rest[0])}"><span class="callout-icon">${icon}</span><div>${inline(rest[1], rel)}</div></div>`);
        break;
      }
      case "quote":
        html.push(`<blockquote>${inline(rest[0], rel)}</blockquote>`);
        break;
      case "api": {
        for (const it of rest[0]) {
          const name = it.name;
          const base = slugify(name);
          let id = base;
          let n = 2;
          while (ids.has(id)) id = `${base}-${n++}`;
          ids.add(id);
          toc.push({ id, text: name, level: "h3" });
          html.push(`<div class="api-item">`);
          html.push(`<h3 id="${id}">${it.kind ? `<span class="api-badge">${esc(it.kind)}</span>` : ""}${esc(name)}<a class="heading-anchor" href="#${id}" aria-label="Link">${icon("link", 14)}</a></h3>`);
          if (it.sig) html.push(`<div class="api-sig"><code>${esc(it.sig)}</code></div>`);
          if (it.desc) html.push(`<p>${inline(it.desc, rel)}</p>`);
          if (it.params && it.params.length) {
            html.push(`<div class="table-wrap"><table class="api-params"><thead><tr><th>Argument</th><th>Type</th><th>Description</th></tr></thead><tbody>`);
            for (const p of it.params) {
              const pn = Array.isArray(p) ? p[0] : p.name;
              const pt = Array.isArray(p) ? p[1] : p.type;
              const pd = Array.isArray(p) ? p[2] : p.desc;
              html.push(`<tr><td><code>${esc(pn)}</code></td><td><code>${esc(pt)}</code></td><td>${inline(pd, rel)}</td></tr>`);
            }
            html.push(`</tbody></table></div>`);
          }
          if (it.returns) html.push(`<p class="api-returns"><span class="api-label">Returns</span> <code>${esc(it.returns)}</code></p>`);
          if (it.example) html.push(highlight(it.example[0], it.example[1], it.example[2] ?? `${name}.py`));
          html.push(`</div>`);
        }
        break;
      }
      case "table": {
        const [headers, rows] = rest;
        html.push(
          `<div class="table-wrap"><table><thead><tr>${headers.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead>` +
            `<tbody>${rows.map((r) => `<tr>${r.map((c) => `<td>${inline(String(c), rel)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`
        );
        break;
      }
      default:
        break;
    }
  }
  return html.join("\n");
}

/* ---------------------------------- navigation --------------------------------- */

function orderedSections() {
  const byId = new Map(DOCS.sections.map((s) => [s.id, s]));
  const partIds = (DOCS.sidebar.fbr ?? DOCS.sidebar.modular ?? []).flatMap((p) =>
    p.pages.map((it) => (typeof it === "string" ? it : it.section))
  );
  const unlisted = DOCS.sections.filter((s) => !partIds.includes(s.id)).map((s) => s.id);
  return [...partIds, ...unlisted].filter((id) => byId.has(id)).map((id) => byId.get(id));
}

function readingOrder() {
  const byId = new Map(DOCS.sections.map((s) => [s.id, s]));
  const out = [];
  for (const part of DOCS.sidebar.fbr ?? []) {
    for (const it of part.pages) {
      if (typeof it === "string") {
        const sec = byId.get(it);
        if (sec) sec.pages.forEach((p) => out.push({ section: sec.id, id: p.id }));
      } else if (it.pages) {
        const sec = byId.get(it.section);
        if (sec) it.pages.forEach((pid) => out.push({ section: sec.id, id: pid }));
      } else {
        out.push({ section: it.section, id: it.page });
      }
    }
  }
  for (const s of DOCS.sections) {
    if (!out.some((o) => o.section === s.id)) s.pages.forEach((p) => out.push({ section: s.id, id: p.id }));
  }
  return out;
}

function pageInOrder(order, section, id) {
  const idx = order.findIndex((o) => o.section === section && o.id === id);
  return idx >= 0 ? { idx, path: order[idx] } : null;
}

function sidebarPageLi(sec, p, locale, activeSection, activePage, docDir) {
  const active = sec.id === activeSection && p.id === activePage;
  const href = relTo(docDir, `/${locale}/${sec.id}/${p.id}`);
  return `<li${active ? ' class="active"' : ""}><a href="${href}" data-nav${active ? ' aria-current="page"' : ""}>${esc(p.title[locale])}</a></li>`;
}

function sidebarSectionGroup(sec, locale, activeSection, activePage, docDir, spec) {
  const open = sec.id === activeSection;
  const byPageId = (id) => sec.pages.find((p) => p.id === id);
  const pages = spec
    ? spec
        .map((id) => byPageId(id))
        .filter(Boolean)
        .map((p) => sidebarPageLi(sec, p, locale, activeSection, activePage, docDir))
        .join("")
    : sec.pages.map((p) => sidebarPageLi(sec, p, locale, activeSection, activePage, docDir)).join("");
  const gid = `grp-${esc(sec.id)}`;
  if (sec.accordion === false) {
    return `<div class="nav-group pinned${open ? " open" : ""}">
  <div class="nav-group-title" aria-hidden="true">
    <span>${esc(sec.nav[locale])}</span>
  </div>
  <ul id="${gid}" class="group-list pinned">${pages}</ul>
</div>`;
  }
  return `<div class="nav-group${open ? " open" : ""}">
  <button class="nav-group-title" type="button" aria-expanded="${open}" aria-controls="${gid}">
    <span>${esc(sec.nav[locale])}</span>
    <span class="chev" aria-hidden="true"></span>
  </button>
  <ul id="${gid}" class="group-list">${pages}</ul>
</div>`;
}

function sidebarStandaloneLink(sec, pageId, locale, activePage, docDir) {
  const p = sec.pages.find((x) => x.id === pageId);
  if (!p) return "";
  const href = relTo(docDir, `/${locale}/${sec.id}/${p.id}`);
  return `<div class="nav-group">
  <ul class="group-list sidebar-standalone">
    <li><a href="${href}" data-nav>${esc(p.title[locale])}</a></li>
  </ul>
</div>`;
}

function sidebarPartsHTML(parts, locale, activeSection, activePage, docDir) {
  const byId = new Map(DOCS.sections.map((s) => [s.id, s]));
  return parts
    .map((part, i) => {
      const inner = part.pages
        .map((it) => {
          if (typeof it === "string") {
            const sec = byId.get(it);
            return sec ? sidebarSectionGroup(sec, locale, activeSection, activePage, docDir) : "";
          }
          if (it.pages) {
            const sec = byId.get(it.section);
            return sec ? sidebarSectionGroup(sec, locale, activeSection, activePage, docDir, it.pages) : "";
          }
          const sec = byId.get(it.section);
          return sec ? sidebarStandaloneLink(sec, it.page, locale, activePage, docDir) : "";
        })
        .join("");
      return `${i > 0 ? '<div class="part-sep" aria-hidden="true"></div>' : ""}<div class="sidebar-part">
  <div class="part-title">Part ${i + 1} &middot; ${esc(part.en)}</div>
  ${inner}
</div>`;
    })
    .join("");
}

function sidebarHTML(locale, activeSection, activePage, docDir) {
  const t = L[locale];
  const tab = activeSection === "reference" ? "reference" : activeSection === "changelog" ? "changelog" : "docs";
  const byId = new Map(DOCS.sections.map((s) => [s.id, s]));
  let groups;
  if (tab !== "docs") {
    const sec = byId.get(tab);
    groups = sec ? sidebarSectionGroup(sec, locale, activeSection, activePage, docDir) : "";
  } else {
    groups = ["fbr", "modular"]
      .map(
        (mode) =>
          `<div class="sidebar-mode" data-mode="${mode}"${mode === "fbr" ? "" : ' hidden'}>
  ${sidebarPartsHTML(DOCS.sidebar[mode] ?? [], locale, activeSection, activePage, docDir)}
</div>`
      )
      .join("");
  }
  return `
<nav class="sidebar" id="sidebar" aria-label="${t.nav}">
  ${tab === "docs" ? `<div class="sidebar-router">
    <div class="sidebar-router-label">${icon("routers", 14)} ${esc(t.routerLabel)}</div>
    <div class="router-seg" id="routerSeg" role="group" aria-label="${esc(t.routerLabel)}">
      <button type="button" class="router-opt" data-route="fbr" aria-pressed="true">${icon("file", 14)}<span>${esc(t.routerFbr)}</span></button>
      <button type="button" class="router-opt" data-route="modular" aria-pressed="false">${icon("layers", 14)}<span>${esc(t.routerModular)}</span></button>
    </div>
  </div>` : ""}
  ${groups}
  <div class="sidebar-footer">
    <a class="sidebar-version" href="${relTo(docDir, `/${locale}/changelog/releases`)}" data-nav>
      <span class="sv-title">${esc(DOCS.brand)}</span>
      <span class="sv-value">v${esc(DOCS.version)} <span class="sv-note">${t.releaseNotes}</span></span>
    </a>
    <a class="sidebar-link" href="${DOCS.github}" target="_blank" rel="noopener">${SOCIALS.github} GitHub</a>
  </div>
</nav>`;
}

function headerHTML(locale, docDir, section, opts = {}) {
  const t = L[locale];
  const home = relHome(docDir);
  const secOf = (id) => DOCS.sections.find((s) => s.id === id);
  const firstSection = DOCS.sections[0];
  const learnHref = relTo(docDir, `/${locale}/${firstSection.id}/${firstSection.pages[0].id}`);
  const refSec = secOf("reference") ?? firstSection;
  const chgSec = secOf("changelog") ?? firstSection;
  const refHref = relTo(docDir, `/${locale}/${refSec.id}/${refSec.pages[0].id}`);
  const chgHref = relTo(docDir, `/${locale}/${chgSec.id}/${chgSec.pages[0].id}`);
  const activeKey = section === "reference" ? "reference" : section === "changelog" ? "changelog" : section !== "overview" ? "docs" : "";
  const nav = [
    { key: "docs", label: t.docs, href: learnHref },
    { key: "reference", label: refSec.nav[locale], href: refHref },
    { key: "changelog", label: chgSec.nav[locale], href: chgHref },
  ];
  const navLinks = nav
    .map(
      (n) =>
        `<a class="app-nav-link${activeKey === n.key ? " active" : ""}" href="${n.href}" data-nav>${esc(n.label)}</a>`
    )
    .join("");
  const mobileMenu = opts.landing
    ? `
  <div class="app-mobile-menu" id="mobileNav" hidden>
    ${navLinks.replaceAll('class="app-nav-link', 'class="app-nav-link app-nav-link-mobile')}
    <a class="read-pill" href="${learnHref}" data-nav>${icon("gradCap", 15)} ${t.learn}</a>
  </div>`
    : "";
  const searchModal = `
  <div class="search-modal" id="searchModal" hidden>
    <div class="search-modal-backdrop" data-close></div>
    <div class="search-modal-panel" role="dialog" aria-modal="true" aria-label="${t.search}">
      <div class="search-modal-head">
        ${icon("search", 18)}
        <input id="searchInput" type="text" autocomplete="off" spellcheck="false"
          placeholder="${t.searchModalPlaceholder}" aria-label="${t.search}" />
        <button class="modal-close" type="button" aria-label="${t.close}">${icon("close", 18)}</button>
      </div>
      <div class="search-modal-body" id="searchPanel"></div>
      <div class="search-modal-foot">
        <span>${t.searchNav} <kbd>↑</kbd> <kbd>↓</kbd></span>
        <span>${t.searchSelect} <kbd>${t.searchEnter}</kbd></span>
      </div>
    </div>
  </div>`;
  return `
<header class="app-hdr">
  <button class="icon-btn menu-btn" id="menuBtn" type="button" aria-label="${t.menu}" aria-expanded="false">${icon("menu")}</button>
  <div class="app-hdr-inner">
    <nav class="app-nav" aria-label="Main">
      <a class="app-brand" href="${home}" data-nav>
        <img class="logo" src="${home}assets/logo.svg" alt="Nexy" height="21" />
      </a>
      <span class="app-nav-divider" aria-hidden="true"></span>
      ${navLinks}
    </nav>
    <aside class="app-actions">
      <button class="search-trigger" id="searchTrigger" type="button" aria-label="${t.search}">
        ${icon("search", 15)}
        <span class="st-label">${t.search}</span>
        <span class="kbd-hint"><kbd>?</kbd><kbd>K</kbd></span>
      </button>
      <a class="icon-btn gh-btn" href="${DOCS.github}" target="_blank" rel="noopener" aria-label="GitHub" title="GitHub">${icon("github", 17)}</a>
      <button class="icon-btn theme-btn" id="themeBtn" type="button" aria-label="${t.theme}" title="${t.theme}">${icon("sun", 17)}</button>
    </aside>
  </div>
  ${mobileMenu}
  ${searchModal}
</header>`;
}

/* ---------------------------------- page shell --------------------------------- */

function pageShell(locale, section, page) {
  const t = L[locale];
  const docDir = `${locale}/${section}/${page.id}`;
  const home = relHome(docDir);
  const ids = new Set();
  const toc = [];
  const body = renderBlocks(page.content[locale], (abs) => relTo(docDir, abs), ids, toc);

  const tocItems =
    toc.length > 0
      ? toc
          .map(
            (item) =>
              `<li><a href="#${item.id}" class="${item.level === "h3" ? "toc-h3" : ""}">${esc(item.text)}</a></li>`
          )
          .join("")
      : "";

  const order = readingOrder();
  const loc = pageInOrder(order, section, page.id);
  const byId = (sid) => DOCS.sections.find((s) => s.id === sid);
  const resolve = (path) => {
    const sec = byId(path.section);
    const p = sec?.pages.find((x) => x.id === path.id);
    return p ? { ...p, section: sec.id } : null;
  };
  const prev = loc && loc.idx > 0 ? resolve(order[loc.idx - 1]) : null;
  const next = loc && loc.idx < order.length - 1 ? resolve(order[loc.idx + 1]) : null;
  const pager = `
<nav class="pager" aria-label="${t.pager}">
  ${prev ? `<a class="pager-link prev" href="${relTo(docDir, `/${locale}/${prev.section}/${prev.id}`)}" data-nav>${icon("arrowLeft", 14)}<span class="pager-label">${t.prev}</span><span class="pager-title">${esc(prev.title[locale])}</span></a>` : `<span></span>`}
  ${next ? `<a class="pager-link next" href="${relTo(docDir, `/${locale}/${next.section}/${next.id}`)}" data-nav><span class="pager-label">${t.next}</span><span class="pager-title">${esc(next.title[locale])}</span>${icon("arrowRight", 14)}</a>` : `<span></span>`}
</nav>`;

  const desc = page.content[locale]
    .map(plainTextOf)
    .join(" ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 155);

  const canonical = `${SITE_URL}${locale}/${section}/${page.id}/`;

  const bodyHtml = `
  <div class="layout">
    ${sidebarHTML(locale, section, page.id, docDir)}
    <div class="content" id="content">
      <nav class="breadcrumb" aria-label="${t.pager}">
        <ol>
          <li><a href="${home}" data-nav>${esc(t.footer.home)}</a></li>
          <li aria-hidden="true">${icon("chevronRight", 12)}</li>
          <li><a href="${relTo(docDir, `/${locale}/${section}/${byId(section).pages[0].id}`)}" data-nav>${esc(byId(section).nav[locale])}</a></li>
          <li aria-hidden="true">${icon("chevronRight", 12)}</li>
          <li aria-current="page">${esc(page.title[locale])}</li>
        </ol>
      </nav>
      <header class="page-head">
        <div class="page-head-text">
          <h1>${esc(page.title[locale])}</h1>
          ${desc ? `<p class="page-desc">${esc(desc)}</p>` : ""}
        </div>
      </header>
      <article class="article">
        ${body}
        ${pager}
        <p class="edit-line">
          <a href="${DOCS.github}" target="_blank" rel="noopener">${t.editOnGitHub}</a>
        </p>
      </article>
    </div>
    <aside class="toc" aria-label="${t.onThisPage}">
      <p class="toc-title">${t.onThisPage}</p>
      <ul class="toc-list">${tocItems}</ul>
    </aside>
  </div>`;

  return {
    body: bodyHtml,
    title: `${page.title[locale]} · ${t.siteName}`,
    desc,
    keywords: (page.keywords?.[locale] ?? []).join(", "),
    canonical,
    sectionTitle: byId(section).nav[locale],
    sectionUrl: `${SITE_URL}${locale}/${section}/${byId(section).pages[0].id}/`,
    datePublished: DOCS.datePublished ?? "2026-01-01",
    dateModified: DOCS.dateModified ?? "2026-01-01",
    docDir,
    section,
    hreflang: {
      en: `${SITE_URL}en/${section}/${page.id}/`,
    },
  };
}

/* ----------------------------------- documents ---------------------------------- */

function seoHead(locale, home, { title, desc, canonical, keywords, type = "website", jsonLd = "", hreflang }) {
  const og = type === "article" ? "article" : "website";
  const hreflangEn = hreflang?.en ?? documentHreflang("en", canonical);
  return `
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script>(function(){try{var s=localStorage.getItem("nexy-theme");var d=s?s:(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");document.documentElement.dataset.theme=d;}catch(e){document.documentElement.dataset.theme="dark";}})();</script>
  <title>${esc(title)}</title>
  <meta name="description" content="${esc(desc)}" />
  ${keywords ? `<meta name="keywords" content="${esc(keywords)}" />` : ""}
  <meta name="robots" content="index, follow, max-image-preview:large" />
  <meta name="theme-color" content="#019486" />
  <meta name="color-scheme" content="light dark" />
  <link rel="canonical" href="${esc(canonical)}" />
  <link rel="alternate" hreflang="x-default" href="${esc(hreflangEn)}" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="${esc(title)}" />
  <meta name="twitter:description" content="${esc(desc)}" />
  <meta name="twitter:image" content="${SITE_URL}assets/og.png" />
  <meta property="og:type" content="${og}" />
  <meta property="og:site_name" content="${esc(DOCS.brand)}" />
  <meta property="og:title" content="${esc(title)}" />
  <meta property="og:description" content="${esc(desc)}" />
  <meta property="og:url" content="${esc(canonical)}" />
  <meta property="og:image" content="${SITE_URL}assets/og.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:locale" content="en_US" />
  <link rel="icon" href="${home}assets/logo.svg" type="image/svg+xml" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Geist:wght@500;600;700;800&family=Inter:wght@300;400;500;600&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="${home}css/style.css" />
  ${jsonLd ? `<script type="application/ld+json">${jsonLd}</script>` : ""}`;
}

/** Returns the canonical URL for a given doc URL (English-only docs). */
function documentHreflang(locale, canonical) {
  const stripped = canonical.replace(/^https?:\/\/[^/]+/, "").replace(/^\//, "");
  const m = stripped.match(/^(en|fr)\//);
  const path = m ? stripped.slice(3) : stripped;
  return `${SITE_URL}${path}`;
}

function documentHTML(locale, shell) {
  const t = L[locale];
  const home = relHome(shell.docDir);
  const jsonLd = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "TechArticle",
    headline: shell.title,
    description: shell.desc,
    inLanguage: locale,
    datePublished: shell.datePublished,
    dateModified: shell.dateModified,
    author: { "@type": "Organization", name: DOCS.brand, url: SITE_URL },
    publisher: { "@type": "Organization", name: DOCS.brand, url: SITE_URL },
    mainEntityOfPage: shell.canonical,
    url: shell.canonical,
    breadcrumb: {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Home", item: SITE_URL },
        {
          "@type": "ListItem",
          position: 2,
          name: shell.sectionTitle,
          item: shell.sectionUrl,
        },
        { "@type": "ListItem", position: 3, name: shell.title, item: shell.canonical },
      ],
    },
  });
  return `<!doctype html>
<html lang="${locale}">
<head>
  ${seoHead(locale, home, {
    title: shell.title,
    desc: shell.desc,
    keywords: shell.keywords,
    canonical: shell.canonical,
    type: "article",
    jsonLd,
  })}
</head>
<body class="docs" data-locale="${locale}">
  <a class="skip-link" href="#content">${t.skipContent}</a>
  ${headerHTML(locale, shell.docDir, shell.section)}
  ${shell.body}
  ${footerHTML(locale, shell.docDir)}
  <script src="${home}js/search-index.js"></script>
  <script src="${home}js/search.js"></script>
  <script src="${home}js/site.js"></script>
</body>
</html>`;
}

const SOCIALS = {
  linkedin:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z"/></svg>',
  sync:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z"/></svg>',
  github:
    '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>',
  user: S('<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>'),
};

function footerLink(href, label, ext) {
  return `<li><a href="${href}"${ext ? ' target="_blank" rel="noopener"' : ' data-nav'}>${esc(label)}</a></li>`;
}

function footerHTML(locale, docDir) {
  const t = L[locale];
  const home = relHome(docDir);
  const socials = [
    ["https://www.linkedin.com/company/luilka-cg", SOCIALS.linkedin],
    ["https://www.linkedin.com/company/nexy-dev", SOCIALS.sync],
    [DOCS.github, SOCIALS.github],
  ]
    .map(
      ([href, svg]) => `<li><a href="${href}" class="footer-social" target="_blank" rel="noopener" aria-label="social">${svg}</a></li>`
    )
    .join("");
  const resources = orderedSections()
    .slice(0, 5)
    .map((s) => [`${s.nav[locale]}`, relTo(docDir, `/${locale}/${s.id}/${s.pages[0].id}`), false]);
  const community = [
    [t.footer.community, relTo(docDir, `/${locale}/getting-started/introduction`), false],
    [t.releaseNotes, relTo(docDir, `/${locale}/changelog/releases`), false],
    ["GitHub", DOCS.github, true],
  ];
  return `
<footer class="footer">
  <div class="footer-top">
    <div class="footer-brand">
      <a href="${home}" data-nav><img class="logo" src="${home}assets/logo.svg" alt="Nexy" height="24" /></a>
      <p>${esc(t.footer.taglineShort)}</p>
      <ul class="footer-socials">${socials}</ul>
    </div>
    <div class="footer-col"><h4>${esc(t.footer.resources)}</h4><ul>${[...resources, [home, t.footer.home, false]].map(([label, href, ext]) => footerLink(href, label, ext)).join("")}</ul></div>
    <div class="footer-col"><h4>${esc(t.footer.communityTitle)}</h4><ul>${community.map(([href, label, ext]) => footerLink(href, label, ext)).join("")}</ul></div>
  </div>
  <div class="footer-bottom">
    <div class="fb-brand">
      <img class="logo" src="${home}assets/logo.svg" alt="" height="16" />
      <span>${esc(DOCS.brand)} <span class="fb-version">v${esc(DOCS.version)}</span></span>
    </div>
    <p class="fb-tagline">${esc(t.footer.tagline)}</p>
    <p class="fb-legal">© ${new Date().getFullYear()} <a href="${DOCS.github}" target="_blank" rel="noopener">NexyPy</a> · MIT License</p>
  </div>
</footer>`;
}

/* ------------------------------- landing (app-style) ------------------------------ */

const LANDING = {
  chip: "Now with API reference docs",
  headline: ["Python for the modern web,", "reimagined"],
  subheadline: "Build full-stack applications, APIs, and modern web experiences - Python first.",
  getStarted: "Get started",
  viewOnGithub: "View on GitHub",
  whatTitle: "What is Nexy ?",
  whatDesc: "Nexy is a Python web framework optimized for building fast, content-driven websites, API services, and more.",
  what: [
    ["Server-First", "Nexy improves performance by rendering components on the server, sending lightweight HTML to the browser.", "zap"],
    ["Customizable", "Extend Nexy with your favorite tools - JavaScript UI components, CSS libraries, themes, and more.", "palette"],
    ["Content-Driven", "Nexy works with your content wherever it lives: your file system, an API, or your favorite CMS.", "file"],
  ],
  whatsTitle: "What's in Nexy ?",
  cells: [
    ["File-Based Router", "Auto-discovers routes from src/routes/. Dynamic params, nested layouts, guards and locale dispatch.", "routers"],
    ["Multi-Framework", "React, Preact, Solid, Vue and Svelte - bring your own components. CSR, SSR and fast refresh.", "layers"],
    ["Jinja2 + MDX", "Server-side Markdown rendering with auto heading IDs and table-of-contents extraction.", "file"],
    ["i18n Built-In", "Locale auto-detection, RTL support and the @i18n() decorator for class-level translation.", "globe"],
    ["Dependency Injection", "@Injectable with singleton, request and transient scopes. Thread-safe container.", "package"],
    ["CLI Toolchain", "new, init, dev, start, build… 8 commands with Typer + Rich terminal output.", "terminal"],
    ["8 Request Hooks", "usePathname, useRouter, useQuery, useSession, useCookies, useSearchParams, useToc, useViews.", "link"],
    ["FastAPI Foundation", "HTTP, WebSocket and async support with middleware stack and OpenAPI docs.", "shield"],
    ["Vite + HMR", "WebSocket-based fast refresh and optional CSS/JS inlining.", "refreshCw"],
  ],
  builtTitle: "Built on a foundation of fast, production-grade tooling",
  builtDesc: "Nexy combines a modern compiler, a powerful template engine, and a fast asset builder.",
  tools: [
    ["FastAPI", "Foundation for routers with HTTP, WebSocket and async support.", "zap"],
    ["Jinja2", "Renders HTML templates on the server side securely and flexibly.", "tpl"],
    ["Vite", "Handles bundling and hot reload of the frontend for fast development.", "vite"],
  ],
  flexTitle: "Maximum Flexibility",
  flexDesc: "Bring your existing React, Preact, Solid, Vue or Svelte components - SSR and fast refresh included.",
  flexTitleLabel: "app/Page.tsx",
  flexNote: "Import any component into your .nexy pages and let Nexy handle SSR output on the server.",
  communityTitle: "Our Community",
  communityDesc: "Nexy is maintained by a passionate community of developers. Join us and help shape the future of Python web development.",
  joinCommunity: "Join Community",
};

/** Nexy mark - reused across the landing (hero chip + community glyph). */
function nexyMark() {
  return `<svg width="27" height="26" viewBox="0 0 27 26" fill="none" aria-hidden="true"><path d="M17.3047 0.457275H17.5771V0.719971L21.3936 4.38696L25.4395 8.22974C25.7119 8.48855 25.8661 8.84812 25.8662 9.22388V24.0002C25.8661 24.7576 25.2515 25.3713 24.4941 25.3713H18.0342C17.277 25.3711 16.6632 24.7574 16.6631 24.0002V9.28931H9.66016V24.0002C9.66004 24.7576 9.04543 25.3713 8.28809 25.3713H1.82812C1.07088 25.3712 0.457152 24.7575 0.457031 24.0002V16.9309C0.457031 16.5505 0.615288 16.1864 0.893555 15.927L2.42676 14.4973L2.42773 14.4963L8.74512 8.63208V1.82837C8.74524 1.07105 9.35984 0.457275 10.1172 0.457275H16.6631V-0.158936L17.3047 0.457275Z" stroke="url(#ngr)" stroke-width="0.914286"/><defs><linearGradient id="ngr" x1="23.3" y1="19.4" x2="8.9" y2="5.9" gradientUnits="userSpaceOnUse"><stop stop-color="#00D084"/><stop offset="1" stop-color="#61ABED"/></linearGradient></defs></svg>`;
}

/** Subtle full-width hairline used between landing sections. */
function hBar() {
  return '<hr class="section-sep" role="presentation" aria-hidden="true" />';
}

function homeSection(opts) {
  return `
<section class="l-section">
  <div class="l-section-inner">
    <h2>${esc(opts.title)}</h2>
    ${opts.desc ? `<p class="l-lead">${esc(opts.desc)}</p>` : ""}
    ${opts.body}
  </div>
</section>`;
}

const homeBar = () => hBar();

function lArrow() {
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="l-cta-icon"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>';
}

function homeHero() {
  const heroCode = `from src.services.users import UserService
from src.models.users import User

user_service = UserService()

def GET(id: int):
    user = user_service.get_by_id(id)
    return user

def POST(user: User):
    return user_service.create(user)`;
  return `
<section class="l-hero">
  <div class="l-hero-grid">
    <div class="hero-left">
      <div class="l-chip-row">
        <span class="l-chip"><span class="dot"></span>${esc(LANDING.chip)}</span>
        <a href="https://pepy.tech/projects/nexy" target="_blank" rel="noopener" class="l-chip l-pepy" aria-label="PyPI downloads">
          <img src="https://static.pepy.tech/personalized-badge/nexy?period=total&units=INTERNATIONAL_SYSTEM&left_color=BRIGHTGREEN&right_color=BLUE&left_text=downloads" alt="PyPI downloads" />
        </a>
      </div>
      <h1><span class="muted">${esc(LANDING.headline[0])}</span> <span class="acc">${esc(LANDING.headline[1])}</span></h1>
      <p class="l-sub">${esc(LANDING.subheadline)}</p>
      <div class="l-cta">
        <a class="l-btn l-btn-solid" href="en/getting-started/quick-start/" data-nav>${esc(LANDING.getStarted)}${lArrow()}</a>
        <a class="l-btn l-btn-ghost" href="${DOCS.github}" target="_blank" rel="noopener">${esc(LANDING.viewOnGithub)}${icon("github", 16)}</a>
      </div>
    </div>
    <div class="l-hero-code">
      <div class="l-code">
        <div class="l-code-top">
          <span class="l-dots"><i></i><i></i><i></i></span>
          <span class="l-fname">app.nexy</span>
        </div>
        <pre><code>${HL.python(heroCode)}</code></pre>
      </div>
      <div class="l-term"><span class="l-term-dot"></span><code>uvx nexy new</code><span class="l-term-meta">✦ scaffold a project</span></div>
    </div>
  </div>
</section>`;
}

function homeWhat() {
  return homeSection({
    title: LANDING.whatTitle,
    desc: LANDING.whatDesc,
    body: `<div class="l-what">${LANDING.what
      .map(([t, d, ico]) => `<article class="l-card-out"><div class="l-card-ico">${icon(ico, 19)}</div><h3>${esc(t)}</h3><p>${esc(d)}</p></article>`)
      .join("")}</div>`,
  });
}

function homeWhy() {
  const groups = [0, 3, 6].map((start) =>
    LANDING.cells
      .slice(start, start + 3)
      .map(
        ([t, d, ico]) =>
          `<div class="l-why-row"><div class="l-why-head"><span class="l-why-ico">${icon(ico, 18)}</span><h3 class="l-why-title">${esc(t)}</h3></div><p>${esc(d)}</p></div>`
      )
      .join("")
  );
  return homeSection({
    title: LANDING.whatsTitle,
    body: `<div class="l-why">${groups.map((g) => `<div class="l-why-col">${g}</div>`).join("")}</div>`,
  });
}

function homeTools() {
  return homeSection({
    title: LANDING.builtTitle,
    desc: LANDING.builtDesc,
    body: `<div class="l-tools">${LANDING.tools.map(([t, d, kind]) => toolCard(t, d, kind)).join("")}</div>`,
  });
}

function toolCard(title, desc, kind) {
  let emblem = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/></svg>';
  if (kind === "tpl") emblem = '<span class="l-tpl">{{ }}</span>';
  if (kind === "vite") emblem = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="m12 2 9 18-9 2-9-2 9-18Z" fill="currentColor"/></svg>';
  return `<article class="l-tool"><div class="l-tool-icon">${emblem}</div><h3>${esc(title)}</h3><p>${esc(desc)}</p></article>`;
}

function homeFlex() {
  const code = `import React from "react";
import { Nexy } from "@components/card";

export function Page() {
  return <Nexy>. Hello from your component</Nexy>
}`;
  return homeSection({
    title: LANDING.flexTitle,
    desc: LANDING.flexDesc,
    body: `<div class="l-flex">
      <div class="l-code">
        <div class="l-code-top"><span class="l-dots"><i></i><i></i><i></i></span><span class="l-fname">${esc(LANDING.flexTitleLabel)}</span></div>
        <pre><code>${HL.js ? HL.js(code) : esc(code)}</code></pre>
      </div>
      <p class="l-flexnote">${esc(LANDING.flexNote)}</p>
    </div>`,
  });
}

function homeCommunity() {
  return `<section class="l-section l-community">
    <div class="l-section-inner l-band">
      <div>
        <h2>${esc(LANDING.communityTitle)}</h2>
        <p>${esc(LANDING.communityDesc)}</p>
        <div class="l-cta">
          <a class="l-btn l-btn-solid" href="en/getting-started/introduction/" data-nav>${esc(LANDING.joinCommunity)}${lArrow()}</a>
          <a class="l-btn l-btn-ghost" href="${DOCS.github}" target="_blank" rel="noopener">${esc(LANDING.viewOnGithub)}${icon("github", 16)}</a>
        </div>
      </div>
      <div class="l-band-glyph" aria-hidden="true">${nexyMark()}</div>
    </div>
  </section>`;
}

function landingHTML() {
  return `<!doctype html>
<html lang="en">
<head>
  ${seoHead("en", "./", {
    title: `${DOCS.brand} · ${DOCS.tagline}`,
    desc: "Official documentation for Nexy, the full-stack Python web framework built on FastAPI. Two routers, plain .nexy files, and great developer experience.",
    keywords: "nexy, python, web framework, fastapi, full stack, documentation, .nexy files, fbr, modular routing, hooks, seo",
    canonical: SITE_URL,
    hreflang: {
      en: `${SITE_URL}en/getting-started/introduction/`,
    },
    jsonLd: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      name: DOCS.brand,
      applicationCategory: "DeveloperApplication",
      operatingSystem: "macOS, Windows, Linux",
      softwareVersion: DOCS.version,
      description: DOCS.tagline,
      url: SITE_URL,
      publisher: { "@type": "Organization", name: DOCS.brand, url: SITE_URL },
    }),
  })}
</head>
<body class="landing" data-locale="en">
  <a class="skip-link" href="#l-main">Skip to content</a>
  ${headerHTML("en", ".", "overview", { landing: true })}
  <main class="l-main" id="l-main">
    ${homeHero()}
    ${homeBar()}
    ${homeWhat()}
    ${homeBar()}
    ${homeWhy()}
    ${homeBar()}
    ${homeTools()}
    ${homeBar()}
    ${homeFlex()}
    ${homeBar()}
    ${homeCommunity()}
  </main>
  ${footerHTML("en", ".")}
  <script src="js/search-index.js"></script>
  <script src="js/search.js"></script>
  <script src="js/site.js"></script>
</body>
</html>`;
}

function notFoundHTML() {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script>(function(){try{var s=localStorage.getItem("nexy-theme");var d=s?s:(matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light");document.documentElement.dataset.theme=d;}catch(e){document.documentElement.dataset.theme="dark";}})();</script>
  <title>404 · Nexy</title>
  <meta http-equiv="refresh" content="0; url=./" />
  <link rel="icon" href="assets/logo.svg" type="image/svg+xml" />
  <link rel="stylesheet" href="css/style.css" />
</head>
<body class="landing">
  <a class="skip-link" href="#l-main">Skip to content</a>
  ${headerHTML("en", ".", "overview")}
  <main class="l-main" id="l-main">
    <section class="l-hero">
      <div class="l-hero-grid" style="grid-template-columns:1fr">
        <div class="hero-left" style="max-width:540px;margin:0 auto;text-align:center;align-items:center">
          <h1 style="font-size:56px;color:var(--warn)">404</h1>
          <p class="l-sub">This page does not exist. Redirecting you home…</p>
          <div class="l-cta" style="justify-content:center"><a class="l-btn l-btn-solid" href="./" data-nav>Back to the docs</a></div>
        </div>
      </div>
    </section>
  </main>
  ${footerHTML("en", ".")}
  <script src="js/search-index.js"></script>
  <script src="js/search.js"></script>
  <script src="js/site.js"></script>
</body>
</html>`;
}

/* ------------------------------------- i18n -------------------------------------- */

const L = {
  en: {
    siteName: "Nexy Docs",
    nav: "Documentation",
    home: "Home",
    search: "Search",
    searchPlaceholder: "Search the docs…",
    searchModalPlaceholder: "Search the docs…",
    searchNav: "Navigate with",
    searchSelect: "Select with",
    searchEnter: "Enter",
    kbd: "Ctrl K",
    menu: "Menu",
    learn: "Learn",
    readme: "Readme",
    docs: "Docs",
    showcase: "Showcases",
    blog: "Blog",
    community: "Community",
    theme: "Toggle theme",
    close: "Close",
    onThisPage: "On this page",
    prev: "Previous",
    next: "Next",
    pager: "Page navigation",
    editOnGitHub: "Edit this page on GitHub",
    releaseNotes: "Release notes",
    routerLabel: "Router",
    routerFbr: "File-based",
    routerModular: "Modular",
    skipContent: "Skip to content",
    footer: {
      start: "Start",
      home: "Home",
      quickStart: "Quick start",
      intro: "Introduction",
      guides: "Guides",
      more: "More",
      community: "Community",
      communityTitle: "Stay in touch",
      resources: "Documentation",
      taglineShort: "The full-stack Python web framework on FastAPI.",
      tagline: "New eXperience for PYthon",
    },
  },
};

/* ------------------------------------- build ------------------------------------- */

const searchIndex = {};

let pageCount = 0;
for (const locale of DOCS.locales) {
  for (const section of DOCS.sections) {
    for (const page of section.pages) {
      const shell = pageShell(locale, section.id, page);
      const doc = documentHTML(locale, shell);
      const outDir = path.join(ROOT, locale, section.id, page.id);
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(path.join(outDir, "index.html"), doc);
      pageCount++;

      if (!searchIndex[locale]) searchIndex[locale] = [];
      searchIndex[locale].push({
        u: `${locale}/${section.id}/${page.id}/`,
        t: page.title[locale],
        s: section.nav[locale],
        k: page.keywords[locale],
        b: page.content[locale].map(plainTextOf).join(" ").replace(/\s+/g, " ").trim().slice(0, 1200),
      });
    }
  }
}

fs.mkdirSync(path.join(ROOT, "js"), { recursive: true });
fs.writeFileSync(
  path.join(ROOT, "js", "search-index.js"),
  "window.NEXY_SEARCH_INDEX = " + JSON.stringify(searchIndex) + ";\n"
);
fs.writeFileSync(path.join(ROOT, "index.html"), landingHTML());
fs.writeFileSync(path.join(ROOT, "404.html"), notFoundHTML());

/* sitemap.xml + robots.txt */
{
  const today = (DOCS.dateModified ?? "2026-01-01").slice(0, 10);
  const urls = [`${SITE_URL}`];
  for (const locale of DOCS.locales) {
    for (const section of DOCS.sections) {
      for (const page of section.pages) {
        urls.push(`${SITE_URL}${locale}/${section.id}/${page.id}/`);
      }
    }
  }
  const sitemap =
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
    urls.map((u) => `  <url>\n    <loc>${u}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>${u === `${SITE_URL}` ? "1.0" : "0.8"}</priority>\n  </url>`).join("\n") +
    `\n</urlset>\n`;
  fs.writeFileSync(path.join(ROOT, "sitemap.xml"), sitemap);
  fs.writeFileSync(
    path.join(ROOT, "robots.txt"),
    `User-agent: *\nAllow: /\n\nSitemap: ${SITE_URL}sitemap.xml\n`
  );
}

console.log(`[build] ${pageCount} pages generated (en) + landing + 404 + sitemap + robots + search index`);
