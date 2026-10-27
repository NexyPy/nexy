// Mounts one generated framework runtime in jsdom and exercises nested layouts.
// Usage: node --conditions=browser scenario.mjs <framework> <runtime-file>
// Prints a JSON report on stdout.
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { JSDOM } from "jsdom";

const [framework, runtimeFile] = process.argv.slice(2);
const here = dirname(fileURLToPath(import.meta.url));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const dom = new JSDOM(
  `<!doctype html><body><main>
     <ncc id="island" data-nexy-fw="${framework}" data-nexy-key="A"
          data-nexy-layouts="L1,L2" data-nexy-props="{}" style="display: contents;"></ncc>
   </main></body>`,
  { pretendToBeVisual: true },
);
for (const name of Object.getOwnPropertyNames(dom.window)) {
  if (!(name in globalThis)) {
    Object.defineProperty(globalThis, name, { get: () => dom.window[name], configurable: true });
  }
}
Object.defineProperty(globalThis, "window", { value: dom.window, configurable: true });
Object.defineProperty(globalThis, "document", { value: dom.window.document, configurable: true });

async function svelteModule(name, source) {
  const { compile } = await import("svelte/compiler");
  const { js } = compile(source, { generate: "client", filename: `${name}.svelte`, runes: true });
  const dir = join(here, ".generated");
  mkdirSync(dir, { recursive: true });
  const file = join(dir, `${name}.svelte.mjs`);
  writeFileSync(file, js.code);
  return (await import(pathToFileURL(file).href)).default;
}

async function components() {
  if (framework === "react") {
    const { createElement: h } = await import("react");
    return {
      L1: ({ children }) => h("div", { className: "l1" }, children),
      L2: ({ children }) => h("section", { className: "l2" }, children),
      A: () => h("p", { id: "a" }, "A"),
      B: () => h("p", { id: "b" }, "B"),
      C: () => h("p", { id: "c" }, "C"),
    };
  }
  if (framework === "preact") {
    const { h } = await import("preact");
    return {
      L1: ({ children }) => h("div", { class: "l1" }, children),
      L2: ({ children }) => h("section", { class: "l2" }, children),
      A: () => h("p", { id: "a" }, "A"),
      B: () => h("p", { id: "b" }, "B"),
      C: () => h("p", { id: "c" }, "C"),
    };
  }
  if (framework === "vue") {
    const { h } = await import("vue");
    const layout = (tag, cls) => ({
      render() {
        return h(tag, { class: cls }, this.$slots.default && this.$slots.default());
      },
    });
    const page = (id) => ({ render: () => h("p", { id }, id.toUpperCase()) });
    return { L1: layout("div", "l1"), L2: layout("section", "l2"), A: page("a"), B: page("b"), C: page("c") };
  }
  if (framework === "solid") {
    const { default: h } = await import("solid-js/h");
    const layout = (tag, cls) => (props) => h(tag, { class: cls }, () => props.children);
    const page = (id) => () => h("p", { id }, id.toUpperCase());
    return { L1: layout("div", "l1"), L2: layout("section", "l2"), A: page("a"), B: page("b"), C: page("c") };
  }
  if (framework === "svelte") {
    const layout = (tag, cls) =>
      `<script>let { children } = $props();</script><${tag} class="${cls}">{@render children?.()}</${tag}>`;
    const page = (id) => `<p id="${id}">${id.toUpperCase()}</p>`;
    return {
      L1: await svelteModule("L1", layout("div", "l1")),
      L2: await svelteModule("L2", layout("section", "l2")),
      A: await svelteModule("A", page("a")),
      B: await svelteModule("B", page("b")),
      C: await svelteModule("C", page("c")),
    };
  }
  throw new Error(`unknown framework ${framework}`);
}

const modules = await components();
window.__nexy_import = async (key) => ({ default: modules[key] });
await import(pathToFileURL(runtimeFile).href);

const main = document.querySelector("main");
async function until(predicate, label, timeout = 3000) {
  const start = Date.now();
  while (!predicate()) {
    if (Date.now() - start > timeout) throw new Error(`timeout: ${label}`);
    await sleep(20);
  }
  await sleep(60);
}

const report = { framework };
await until(() => main.querySelector("#a"), "initial mount");
report.initial = {
  nested: Boolean(main.querySelector(".l1 .l2 #a")),
  html: main.innerHTML.replace(/<!--.*?-->/g, ""),
};
const l1 = main.querySelector(".l1");
const l2 = main.querySelector(".l2");

await until(() => window.__nexy_renderers && window.__nexy_renderers[framework], "renderer registered");
const render = window.__nexy_renderers[framework];

await render(modules.B, main, {}, [modules.L1, modules.L2]);
await until(() => main.querySelector("#b"), "navigate to B");
report.sameChain = {
  nested: Boolean(main.querySelector(".l1 .l2 #b")),
  oldPageGone: !main.querySelector("#a"),
  l1Preserved: main.querySelector(".l1") === l1,
  l2Preserved: main.querySelector(".l2") === l2,
};

await render(modules.C, main, {}, [modules.L1]);
await until(() => main.querySelector("#c"), "navigate to C");
report.otherChain = {
  inL1: Boolean(main.querySelector(".l1 #c")),
  l2Gone: !main.querySelector(".l2"),
  noStalePage: !main.querySelector("#b"),
};

console.log("@@" + JSON.stringify(report) + "@@");
process.exit(0);
