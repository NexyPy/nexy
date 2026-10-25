// Link, Image and the stores of the Svelte adapter, server-rendered then hydrated.
//   node --conditions=browser adapter_svelte.mjs
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { clickWith, openPage, print, sleep, stage, story } from "./adapter_common.mjs";

const page = openPage("");
const dir = stage("svelte", "svelte.ts", ["Link.svelte", "Image.svelte"]);
const folder = dir.pathname.replace(/^\/(\w:)/, "$1");
const { compile } = await import("svelte/compiler");
const { hydrate } = await import("svelte");
const { render } = await import("svelte/server");

const APP = `<script lang="ts">
  import Link from './Link.svelte'
  import Image from './Image.svelte'
  import { router, pathname, params, searchParams } from './client.ts'
</script>
<div>
  <Link id="home" href="/" exact activeClass="on" class="nav">Home</Link>
  <Link id="about" href="/about" activeClass="on" class="nav">About</Link>
  <Link id="user" href="/users/7">User</Link>
  <div>
    <p id="path">{$pathname}</p>
    <p id="params">{JSON.stringify($params)}</p>
    <p id="tab">{$searchParams.get('tab') ?? ''}</p>
    <button id="push" onclick={() => router.push('/users/7?tab=x')}>push</button>
  </div>
  <Image id="img" src="/a.png" alt="A" width={800} height={600} />
</div>
`;

/** Compile a component for the server or the browser; its imports of .svelte files follow. */
function build(name, source, generate) {
  const { js } = compile(source, { generate, filename: `${name}.svelte`, runes: true });
  const code = js.code.replace(/(['"])\.\/(Link|Image)\.svelte\1/g, `$1./$2.${generate}.mjs$1`);
  const out = path.join(folder, `${name}.${generate}.mjs`);
  fs.writeFileSync(out, code);
  return pathToFileURL(out).href;
}
const sources = {
  Link: fs.readFileSync(path.join(folder, "Link.svelte"), "utf8"),
  Image: fs.readFileSync(path.join(folder, "Image.svelte"), "utf8"),
  App: APP,
};
for (const name of ["Link", "Image"]) {
  build(name, sources[name], "server");
  build(name, sources[name], "client");
}
const server = (await import(build("App", APP, "server"))).default;
const client = (await import(build("App", APP, "client"))).default;

const html = render(server).body.replace(/^<!--\[-->|<!--\]-->$/g, "");
page.root.innerHTML = render(server).body;
const serverSide = page.root.innerHTML;
hydrate(client, { target: page.root });
await sleep(80);

const report = await story(page, { click: clickWith(page.dom.window) });
report.serverHtml = serverSide;
void html;
print(report);
