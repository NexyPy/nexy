// What every framework adapter scenario shares: a jsdom page that was "server rendered" at /about,
// a real router installed on it, and the observations each scenario prints.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";
import { createRouter } from "../../nexy/modules/frontend/client/router.ts";

const SOURCES = new URL("../../nexy/modules/frontend/client/", import.meta.url);
const STAGE = new URL("./.generated/adapters/", import.meta.url);

/** Copy an adapter next to router.ts and shared.ts as the generated project does (client.<ext>). */
export function stage(framework, adapter, extras = []) {
  const dir = new URL(`${framework}/`, STAGE);
  fs.mkdirSync(dir, { recursive: true });
  const copy = (from, to) => fs.copyFileSync(new URL(from, SOURCES), new URL(to, dir));
  copy("router.ts", "router.ts");
  copy("shared.ts", "shared.ts");
  copy(adapter, `client${path.extname(adapter)}`);
  for (const extra of extras) copy(extra, extra);
  return dir;
}

export const load = (dir, file) => import(pathToFileURL(path.join(dir.pathname.replace(/^\/(\w:)/, "$1"), file)).href);

export const SERVER_LOCATION = { pathname: "/about", search: "?tab=a", hash: "", params: {} };

const ROUTES = {
  "/": "/src/routes/index.tsx",
  "/about": "/src/routes/about.tsx",
};
export const match = (pathname) => {
  if (ROUTES[pathname]) return { file: ROUTES[pathname], layouts: [], params: {} };
  const user = /^\/users\/([^/]+)$/.exec(pathname);
  return user ? { file: "/src/routes/users/[id].tsx", layouts: [], params: { id: user[1] } } : null;
};

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** Build the page around server-rendered `html`, with the router running. Call after the SSR step. */
export function openPage(html) {
  const dom = new JSDOM(`<!DOCTYPE html><body><div id="root">${html}</div></body>`, {
    url: "http://localhost/about?tab=a",
    pretendToBeVisual: true,
  });
  for (const name of Object.getOwnPropertyNames(dom.window)) {
    if (!(name in globalThis)) Object.defineProperty(globalThis, name, { get: () => dom.window[name], configurable: true });
  }
  dom.window.scrollTo = () => {}; // jsdom has no layout to scroll
  Object.defineProperty(globalThis, "window", { value: dom.window, configurable: true });
  Object.defineProperty(globalThis, "document", { value: dom.window.document, configurable: true });
  delete globalThis.__NEXY_LOCATION__;

  const rendered = [];
  const prefetched = [];
  const router = createRouter({
    match,
    render: async (m) => void rendered.push(m.file),
    prefetch: (m) => void prefetched.push(m.file),
  });
  globalThis.__nexy_router = router;
  router.start();

  const errors = [];
  const original = console.error;
  console.error = (...args) => {
    errors.push(args.map(String).join(" ").slice(0, 200));
    original.apply(console, args);
  };
  return { dom, router, rendered, prefetched, errors, root: dom.window.document.getElementById("root") };
}

const text = (doc, id) => doc.getElementById(id)?.textContent ?? null;

/** Everything a scenario reports, read from the DOM. */
export function observe(doc) {
  const link = (id) => {
    const a = doc.getElementById(id);
    return a && { href: a.getAttribute("href"), class: a.getAttribute("class"), current: a.getAttribute("aria-current"), marker: a.getAttribute("data-nexy-link") };
  };
  const img = doc.getElementById("img");
  return {
    links: { home: link("home"), about: link("about"), user: link("user"), replace: link("replace"), quiet: link("quiet") },
    path: text(doc, "path"),
    params: text(doc, "params"),
    tab: text(doc, "tab"),
    image: img && {
      src: img.getAttribute("src"),
      alt: img.getAttribute("alt"),
      width: img.getAttribute("width"),
      height: img.getAttribute("height"),
      loading: img.getAttribute("loading"),
      decoding: img.getAttribute("decoding"),
      fetchpriority: img.getAttribute("fetchpriority"),
      style: (img.getAttribute("style") ?? "").replace(/\s+/g, ""),
    },
  };
}

/** Hover a link, click another, push through the router object: the same story for every framework. */
export async function story(page, { click }) {
  const doc = page.dom.window.document;
  const initial = observe(doc);

  doc.getElementById("user").dispatchEvent(new page.dom.window.MouseEvent("mouseover", { bubbles: true }));
  doc.getElementById("user").dispatchEvent(new page.dom.window.MouseEvent("mouseenter", { bubbles: false }));
  await sleep(30);
  const afterHover = [...page.prefetched];

  click(doc.getElementById("home"));
  await sleep(120);
  const afterClick = { ...observe(doc), url: page.dom.window.location.pathname + page.dom.window.location.search, rendered: [...page.rendered] };

  click(doc.getElementById("push"));
  await sleep(120);
  const afterPush = { ...observe(doc), url: page.dom.window.location.pathname + page.dom.window.location.search };

  return { initial, afterHover, afterClick, afterPush, errors: page.errors };
}

export function clickWith(window) {
  return (element) => element.dispatchEvent(new window.MouseEvent("click", { bubbles: true, cancelable: true, button: 0 }));
}

export function print(report) {
  console.log("@@" + JSON.stringify(report) + "@@");
  process.exit(0);
}
