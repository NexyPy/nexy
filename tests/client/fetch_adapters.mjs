// useFetch in each framework: two components read one URL, a third reads a URL that fails.
//   node --conditions=browser fetch_adapters.mjs <react|preact|vue|svelte|solid>
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { load, openPage, print, sleep, stage } from "./adapter_common.mjs";

const framework = process.argv[2];
const ADAPTERS = { react: "react.ts", preact: "preact.ts", vue: "vue.ts", svelte: "svelte.ts", solid: "solid.tsx" };
const extras = framework === "svelte" ? ["Link.svelte", "Image.svelte"] : [];
const dir = stage(`fetch-${framework}`, ADAPTERS[framework], extras);
const folder = dir.pathname.replace(/^\/(\w:)/, "$1");
const page = openPage("");

const calls = [];
let users = [{ id: 1 }];
globalThis.fetch = async (url) => {
  calls.push(url);
  await sleep(5);
  if (url === "/api/missing") return new Response(JSON.stringify({ detail: "No such thing" }), { status: 404 });
  return new Response(JSON.stringify(users), { headers: { "content-type": "application/json" } });
};

/** What a reader shows: `pending`, `error:<status>`, or its data as JSON. */
export const shown = (state) =>
  state.pending ? "pending" : state.error ? `error:${state.error.status}` : JSON.stringify(state.data);

async function mountJsx(lib) {
  const { h, mount } = lib;
  const { useFetch } = await load(dir, "client.ts");
  const Reader = ({ id, url }) => {
    const state = useFetch(url);
    return h("div", null, h("p", { id }, shown(state)), h("button", { id: `${id}-refresh`, onClick: () => state.refresh() }, "r"));
  };
  mount(h("div", null, h(Reader, { id: "a", url: "/api/users" }), h(Reader, { id: "b", url: "/api/users" }), h(Reader, { id: "c", url: "/api/missing" })));
}

async function mountVue() {
  const { createApp, defineComponent, h } = await import("vue");
  const { useFetch } = await load(dir, "client.ts");
  const Reader = defineComponent({
    props: { id: String, url: String },
    setup(props) {
      const { data, error, pending, refresh } = useFetch(props.url);
      return () =>
        h("div", null, [
          h("p", { id: props.id }, shown({ data: data.value, error: error.value, pending: pending.value })),
          h("button", { id: `${props.id}-refresh`, onClick: () => refresh() }, "r"),
        ]);
    },
  });
  const App = { render: () => h("div", null, [h(Reader, { id: "a", url: "/api/users" }), h(Reader, { id: "b", url: "/api/users" }), h(Reader, { id: "c", url: "/api/missing" })]) };
  createApp(App).mount(page.root);
}

async function mountSvelte() {
  const { compile } = await import("svelte/compiler");
  const { mount } = await import("svelte");
  const READER = `<script>
  import { useFetch } from './client.ts'
  let { id, url } = $props()
  const users = useFetch(url)
  const shown = (s) => s.pending ? 'pending' : s.error ? 'error:' + s.error.status : JSON.stringify(s.data)
</script>
<div><p {id}>{shown($users)}</p><button id={id + '-refresh'} onclick={() => users.refresh()}>r</button></div>`;
  const APP = `<script>import Reader from './Reader.svelte'</script>
<div><Reader id="a" url="/api/users" /><Reader id="b" url="/api/users" /><Reader id="c" url="/api/missing" /></div>`;
  const build = (name, source) => {
    const { js } = compile(source, { generate: "client", filename: `${name}.svelte`, runes: true });
    const out = path.join(folder, `${name}.client.mjs`);
    fs.writeFileSync(out, js.code.replace(/(['"])\.\/Reader\.svelte\1/g, "$1./Reader.client.mjs$1"));
    return pathToFileURL(out).href;
  };
  build("Reader", READER);
  mount((await import(build("App", APP))).default, { target: page.root });
}

async function mountSolid() {
  const { transformSync } = await import("@babel/core");
  const READER = `
import { useFetch } from "./client.tsx";
const shown = (s) => s.pending ? "pending" : s.error ? "error:" + s.error.status : JSON.stringify(s.data);
function Reader(props) {
  const users = useFetch(props.url);
  return <div><p id={props.id}>{shown({ data: users.data(), error: users.error(), pending: users.pending() })}</p>
    <button id={props.id + "-refresh"} onClick={() => users.refresh()}>r</button></div>;
}
export default function App() {
  return <div><Reader id="a" url="/api/users" /><Reader id="b" url="/api/users" /><Reader id="c" url="/api/missing" /></div>;
}`;
  const build = (name, source) => {
    const { code } = transformSync(source, {
      filename: `${name}.tsx`, babelrc: false, configFile: false,
      presets: [["babel-preset-solid", { generate: "dom" }], ["@babel/preset-typescript", { isTSX: true, allExtensions: true }]],
    });
    const out = path.join(folder, `${name}.dom.mjs`);
    fs.writeFileSync(out, code.replace(/(['"])\.\/client\.tsx\1/g, "$1./client.dom.mjs$1"));
    return pathToFileURL(out).href;
  };
  build("client", fs.readFileSync(path.join(folder, "client.tsx"), "utf8"));
  const app = (await import(build("app", READER))).default;
  const { render, createComponent } = await import("solid-js/web");
  render(() => createComponent(app, {}), page.root);
}

const MOUNT = {
  react: async () => {
    const { createElement } = await import("react");
    const { createRoot } = await import("react-dom/client");
    const { flushSync } = await import("react-dom");
    const root = createRoot(page.root);
    await mountJsx({ h: createElement, mount: (tree) => flushSync(() => root.render(tree)) });
  },
  preact: async () => {
    const { h, render } = await import("preact");
    await mountJsx({ h, mount: (tree) => render(tree, page.root) });
  },
  vue: mountVue,
  svelte: mountSvelte,
  solid: mountSolid,
};

const doc = page.dom.window.document;
const text = (id) => doc.getElementById(id)?.textContent ?? null;
const read = () => ({ a: text("a"), b: text("b"), c: text("c") });
const click = (id) => doc.getElementById(id).dispatchEvent(new page.dom.window.MouseEvent("click", { bubbles: true }));

await MOUNT[framework]();
const firstPaint = read();
await sleep(60);
const loaded = { ...read(), calls: calls.filter((url) => url === "/api/users").length };
users = [{ id: 1 }, { id: 2 }];
click("a-refresh");
await sleep(60);
const refreshed = { ...read(), calls: calls.filter((url) => url === "/api/users").length };
print({ firstPaint, loaded, refreshed, errors: page.errors });
