// Root layout owns <html> in Preact, Vue and Svelte: the server sends the whole document, the browser
// builds the body and swaps it in (nexyTakeOver). Usage:
//   node --conditions=browser takeover.mjs <preact|vue|svelte> <runtime-file>
// Prints a JSON report between @@ markers.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";
import { stripDocumentTags } from "../../nexy/modules/frontend/document.ts";

const [framework, runtimeFile] = process.argv.slice(2);
const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, "$1"));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const boot = { mode: "document", page: "HOME", layouts: ["ROOT", "NESTED"], props: {} };

// The DOM exists before any framework is imported: Vue reads `document` once, at import time.
const dom = new JSDOM("<!DOCTYPE html><html><head></head><body></body></html>", { pretendToBeVisual: true });
for (const name of Object.getOwnPropertyNames(dom.window)) {
  if (!(name in globalThis)) Object.defineProperty(globalThis, name, { get: () => dom.window[name], configurable: true });
}
Object.defineProperty(globalThis, "window", { value: dom.window, configurable: true });
Object.defineProperty(globalThis, "document", { value: dom.window.document, configurable: true });

// A framework gives two builds of the same page: `server` (full document) and `client` (body only).
async function preact() {
  const { h } = await import("preact");
  const { useState } = await import("preact/hooks");
  const { renderToString } = await import("preact-render-to-string");
  const Root = ({ children }) =>
    h("html", { lang: "fr", class: "dark" }, h("head", null, h("title", null, "Layout title")),
      h("body", { class: "antialiased" }, h("header", { id: "head" }, "Header"), h("main", null, children)));
  const Nested = ({ children }) => h("section", { class: "nested" }, children);
  const Counter = () => {
    const [n, setN] = useState(0);
    return h("button", { id: "counter", onClick: () => setN(n + 1) }, `count ${n}`);
  };
  const Home = () => h("div", { id: "home" }, h("p", null, "Home"), h(Counter));
  const About = () => h("p", { id: "about" }, "About");
  const tree = (Page) => h(Root, null, h(Nested, null, h(Page, {})));
  const modules = { ROOT: Root, NESTED: Nested, HOME: Home, ABOUT: About };
  return { served: "<!DOCTYPE html>" + renderToString(tree(Home)), client: modules, About, chain: [Root, Nested] };
}

async function vue() {
  const { h, createSSRApp, ref } = await import("vue");
  const { renderToString } = await import("vue/server-renderer");
  const Counter = { setup() { const n = ref(0); return () => h("button", { id: "counter", onClick: () => n.value++ }, `count ${n.value}`); } };
  const Home = { render: () => h("div", { id: "home" }, [h("p", null, "Home"), h(Counter)]) };
  const About = { render: () => h("p", { id: "about" }, "About") };
  const Nested = { setup: (_, { slots }) => () => h("section", { class: "nested" }, slots.default?.()) };
  // Server layout: the whole document. Client layout: what the stripped template compiles to.
  const RootServer = {
    setup: (_, { slots }) => () =>
      h("html", { lang: "fr", class: "dark" }, [h("head", null, [h("title", null, "Layout title")]),
        h("body", { class: "antialiased" }, [h("header", { id: "head" }, "Header"), h("main", null, slots.default?.())])]),
  };
  const RootClient = {
    setup: (_, { slots }) => () => [h("header", { id: "head" }, "Header"), h("main", null, slots.default?.())],
  };
  const app = createSSRApp({ render: () => h(RootServer, null, { default: () => h(Nested, null, { default: () => h(Home) }) }) });
  const served = "<!DOCTYPE html>" + (await renderToString(app));
  return { served, client: { ROOT: RootClient, NESTED: Nested, HOME: Home, ABOUT: About }, About, chain: [RootClient, Nested] };
}

async function svelte() {
  const { compile } = await import("svelte/compiler");
  const { render } = await import("svelte/server");
  const sources = {
    Root: `<script>let { children } = $props();</script>
<html lang="fr" class="dark"><head><title>Layout title</title><script>window.__theme = 1</script></head>
<body class="antialiased"><header id="head">Header</header><main>{@render children()}</main></body></html>`,
    Nested: `<script>let { children } = $props();</script><section class="nested">{@render children()}</section>`,
    Home: `<script>let n = $state(0);</script><div id="home"><p>Home</p><button id="counter" onclick={() => n++}>count {n}</button></div>`,
    About: `<p id="about">About</p>`,
    Page: `<script>import Root from "./Root.server.mjs"; import Nested from "./Nested.server.mjs"; import Home from "./Home.server.mjs";</script>
<Root><Nested><Home /></Nested></Root>`,
  };
  const dir = path.join(here, ".generated", "svelte-takeover");
  fs.mkdirSync(dir, { recursive: true });
  const build = (name, source, generate, suffix) => {
    const { js } = compile(source, { generate, filename: `${name}.svelte`, runes: true });
    fs.writeFileSync(path.join(dir, `${name}.${suffix}.mjs`), js.code);
  };
  for (const name of ["Root", "Nested", "Home", "About", "Page"]) build(name, sources[name], "server", "server");
  // The browser gets the root layout without <html>, <head> and <body>.
  for (const name of ["Root", "Nested", "Home", "About"]) {
    build(name, name === "Root" ? stripDocumentTags(sources[name], "svelte") : sources[name], "client", "client");
  }
  const { default: Page } = await import(pathToFileURL(path.join(dir, "Page.server.mjs")).href);
  const served = "<!DOCTYPE html>" + render(Page).body;
  return { served, dir };
}

const built = await (framework === "preact" ? preact() : framework === "vue" ? vue() : svelte());

let modules;
let About;
let chain;
if (framework === "svelte") {
  const load = async (name) => (await import(pathToFileURL(path.join(built.dir, `${name}.client.mjs`)).href)).default;
  // The client modules import "svelte" and must run after the DOM globals exist.
  var loadSvelte = async () => {
    modules = { ROOT: await load("Root"), NESTED: await load("Nested"), HOME: await load("Home"), ABOUT: await load("About") };
    About = modules.ABOUT;
    chain = [modules.ROOT, modules.NESTED];
  };
} else {
  modules = built.client;
  About = built.About;
  chain = built.chain;
}

const served = built.served.replace(
  "</body>",
  `<script id="__nexy_page" type="application/json">${JSON.stringify(boot)}</script></body>`,
);
document.open();
document.write(served);
document.close();
if (framework === "svelte") await loadSvelte();
window.__nexy_import = async (key) => ({ default: modules[key] });

const errors = [];
const originalError = console.error;
console.error = (...args) => {
  errors.push(args.map(String).join(" ").slice(0, 300));
  originalError.apply(console, args);
};
async function until(predicate, label, timeout = 4000) {
  const start = Date.now();
  while (!predicate()) {
    if (Date.now() - start > timeout) throw new Error(`timeout: ${label}`);
    await sleep(20);
  }
  await sleep(60);
}

const html = document.documentElement;
const head = document.head;
const headBefore = head.innerHTML;
const doctype = document.doctype;
await import(pathToFileURL(runtimeFile).href);
await until(() => document.getElementById("home") && document.getElementById("counter"), "page rendered");

const report = { framework };
report.htmlKept = document.documentElement === html && html.getAttribute("lang") === "fr" && html.className === "dark";
report.headKept = document.head === head && head.innerHTML === headBefore && document.title === "Layout title";
report.doctypeKept = document.doctype === doctype;
report.bodyAttributes = document.body.className === "antialiased";
report.layoutRendered = Boolean(document.querySelector("main .nested #home"));
report.singleBody = document.querySelectorAll("body").length === 1;
const counter = document.getElementById("counter");
counter.click();
await until(() => document.getElementById("counter").textContent.includes("1"), "click handled");
report.interactive = true;

const header = document.getElementById("head");
const body = document.body;
await until(() => window.__nexy_renderers && window.__nexy_renderers[framework], "renderer registered");
await window.__nexy_renderers[framework](About, document.body, {}, chain);
await until(() => document.getElementById("about"), "navigated");
report.navigation = {
  pageSwapped: !document.getElementById("home") && Boolean(document.getElementById("about")),
  htmlPreserved: document.documentElement === html,
  bodyPreserved: document.body === body,
  headerPreserved: document.getElementById("head") === header,
  nestedKept: Boolean(document.querySelector("main .nested #about")),
};
report.errors = errors;
console.log("@@" + JSON.stringify(report) + "@@");
process.exit(0);
