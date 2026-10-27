// Hydrates a server-rendered *document* (root layout owns <html>) with the generated React runtime.
// Usage: node --conditions=browser document.mjs <framework> <mode> <runtime-file>
//   framework: react | preact
//   mode: document | shell | client
// Prints a JSON report on stdout.
import { dirname } from "node:path";
import { pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

const [framework, mode, runtimeFile] = process.argv.slice(2);
const { h, useState, renderToString, cls } =
  framework === "preact"
    ? {
        h: (await import("preact")).h,
        useState: (await import("preact/hooks")).useState,
        renderToString: (await import("preact-render-to-string")).renderToString,
        cls: "class",
      }
    : {
        h: (await import("react")).createElement,
        useState: (await import("react")).useState,
        renderToString: (await import("react-dom/server")).renderToString,
        cls: "className",
      };
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
void dirname;

function RootLayout({ children }) {
  return h(
    "html",
    { lang: "fr", [cls]: "dark" },
    h("head", null, h("title", null, "Layout title")),
    h("body", { [cls]: "antialiased" }, h("header", { id: "head" }, "Header"), h("main", null, children)),
  );
}
function Nested({ children }) {
  return h("section", { [cls]: "nested" }, children);
}
function Counter() {
  const [count, setCount] = useState(0);
  return h("button", { id: "counter", onClick: () => setCount(count + 1) }, `count ${count}`);
}
function Home() {
  return h("div", { id: "home" }, h("p", null, "Home"), h(Counter));
}
function About() {
  return h("p", { id: "about" }, "About");
}

const modules = { ROOT: RootLayout, NESTED: Nested, HOME: Home, ABOUT: About };
const layouts = [RootLayout, Nested];
const wrap = (page) => {
  let node = page ? h(page, {}) : null;
  for (let i = layouts.length - 1; i >= 0; i--) node = h(layouts[i], { params: {} }, node);
  return node;
};

let served = "<!DOCTYPE html>" + renderToString(wrap(mode === "shell" ? null : Home));
if (mode === "client") served = '<!DOCTYPE html><html lang="en"><head></head><body></body></html>';
const boot = { mode, page: "HOME", layouts: ["ROOT", "NESTED"], props: {} };
served = served.replace("</body>", `<script id="__nexy_page" type="application/json">${JSON.stringify(boot)}</script></body>`);

const dom = new JSDOM(served, { pretendToBeVisual: true });
for (const name of Object.getOwnPropertyNames(dom.window)) {
  if (!(name in globalThis)) {
    Object.defineProperty(globalThis, name, { get: () => dom.window[name], configurable: true });
  }
}
Object.defineProperty(globalThis, "window", { value: dom.window, configurable: true });
Object.defineProperty(globalThis, "document", { value: dom.window.document, configurable: true });
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

await import(pathToFileURL(runtimeFile).href);
const html = document.documentElement;
const head = document.getElementById("head");
await until(() => document.getElementById("home"), "page rendered");

const report = { mode };
report.attributesKept = html.getAttribute("lang") === (mode === "client" ? "en" : "fr");
report.layoutRendered = Boolean(document.querySelector("main .nested #home"));
report.title = document.title;

// Interactivity proves hydration attached the handlers.
document.getElementById("counter").click();
await until(() => document.getElementById("counter").textContent === "count 1", "click handled");
report.interactive = true;

// Client navigation: the layouts, <html> and <body> stay; the page changes.
await until(() => window.__nexy_renderers && window.__nexy_renderers[framework], "renderer registered");
await window.__nexy_renderers[framework](About, document.body, {}, [RootLayout, Nested]);
await until(() => document.getElementById("about"), "navigated");
report.navigation = {
  pageSwapped: !document.getElementById("home") && Boolean(document.getElementById("about")),
  htmlPreserved: document.documentElement === html,
  headerPreserved: mode === "client" ? true : document.getElementById("head") === head,
  nestedKept: Boolean(document.querySelector("main .nested #about")),
};
report.hydrationErrors = errors.filter((message) => /hydrat|did not match|mismatch/i.test(message));

console.log("@@" + JSON.stringify(report) + "@@");
process.exit(0);
