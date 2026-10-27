// Solid counterpart of document.mjs: the root layout owns <html>.
//   server <mode> <out.html>                      (plain Node: Solid's server build renders)
//   client <mode> <runtime-file> <served.html>    (node --conditions=browser: hydrates in jsdom)
// The client step prints a JSON report between @@ markers.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { transformSync } from "@babel/core";

const here = path.dirname(new URL(import.meta.url).pathname.replace(/^\/(\w:)/, "$1"));
const [side, mode, a, b] = process.argv.slice(2);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const boot = { mode, page: "HOME", layouts: ["ROOT", "NESTED"], props: {} };

function compile(generate, target) {
  const source = fs.readFileSync(path.join(here, "solid_app.jsx"), "utf8");
  const { code } = transformSync(source, {
    filename: "solid_app.jsx",
    babelrc: false,
    configFile: false,
    presets: [["babel-preset-solid", { generate, hydratable: true }]],
  });
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, code);
  return pathToFileURL(target).href;
}

if (side === "server") {
  const { renderToString, createComponent } = await import("solid-js/web");
  const app = await import(compile("ssr", path.join(here, ".generated", "solid_app.server.mjs")));
  const page = mode === "shell" ? () => null : app.Home;
  const html = renderToString(() =>
    createComponent(app.RootLayout, {
      get children() {
        return createComponent(app.Nested, { get children() { return createComponent(page, {}); } });
      },
    }),
  );
  let served = "<!DOCTYPE html>" + html;
  if (mode === "client") served = '<!DOCTYPE html><html lang="en"><head></head><body></body></html>';
  served = served.replace("</body>", `<script id="__nexy_page" type="application/json">${JSON.stringify(boot)}</script></body>`);
  fs.writeFileSync(a, served);
  process.exit(0);
}

const { JSDOM } = await import("jsdom");
const dom = new JSDOM(fs.readFileSync(b, "utf8"), { pretendToBeVisual: true });
for (const name of Object.getOwnPropertyNames(dom.window)) {
  if (!(name in globalThis)) Object.defineProperty(globalThis, name, { get: () => dom.window[name], configurable: true });
}
Object.defineProperty(globalThis, "window", { value: dom.window, configurable: true });
Object.defineProperty(globalThis, "document", { value: dom.window.document, configurable: true });
const app = await import(compile("dom", path.join(here, ".generated", "solid_app.client.mjs")));
const modules = { ROOT: app.RootLayout, NESTED: app.Nested, HOME: app.Home, ABOUT: app.About };
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

await import(pathToFileURL(a).href);
const html = document.documentElement;
const head = document.getElementById("head");
await until(() => document.getElementById("home"), "page rendered");

const report = { mode };
report.attributesKept = html.getAttribute("lang") === "fr";
report.layoutRendered = Boolean(document.querySelector("main .nested #home"));
report.title = document.title;
document.getElementById("counter").click();
await until(() => document.getElementById("counter").textContent.includes("1"), "click handled");
report.interactive = true;

await until(() => window.__nexy_renderers && window.__nexy_renderers.solid, "renderer registered");
window.__nexy_renderers.solid(app.About, document.body, {}, [app.RootLayout, app.Nested]);
await until(() => document.getElementById("about"), "navigated");
report.navigation = {
  pageSwapped: !document.getElementById("home") && Boolean(document.getElementById("about")),
  htmlPreserved: document.documentElement === html,
  headerPreserved: document.getElementById("head") === head,
  nestedKept: Boolean(document.querySelector("main .nested #about")),
};
report.hydrationErrors = errors.filter((message) => /hydrat|did not match|mismatch/i.test(message));
console.log("@@" + JSON.stringify(report) + "@@");
process.exit(0);
