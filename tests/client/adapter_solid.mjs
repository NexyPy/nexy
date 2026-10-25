// Link, Image and the accessors of the Solid adapter, server-rendered then hydrated.
// Solid's server and browser builds differ, so two processes:
//   node adapter_solid.mjs server                       writes the served HTML
//   node --conditions=browser adapter_solid.mjs client  hydrates it and tells the story
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { transformSync } from "@babel/core";
import { clickWith, openPage, print, SERVER_LOCATION, sleep, stage, story } from "./adapter_common.mjs";

const side = process.argv[2];
const dir = stage("solid", "solid.tsx");
const folder = dir.pathname.replace(/^\/(\w:)/, "$1");
const served = path.join(folder, "served.html");

const APP = `
import { Link, Image, useRouter, usePathname, useParams, useSearchParams } from "./client.tsx";
export default function App() {
  const router = useRouter();
  const path = usePathname();
  const params = useParams();
  const search = useSearchParams();
  return (
    <div>
      <Link id="home" href="/" exact activeClassName="on" class="nav">Home</Link>
      <Link id="about" href="/about" activeClassName="on" class="nav">About</Link>
      <Link id="user" href="/users/7">User</Link>
      <div>
        <p id="path">{path()}</p>
        <p id="params">{JSON.stringify(params())}</p>
        <p id="tab">{search().get("tab") ?? ""}</p>
        <button id="push" onClick={() => router.push("/users/7?tab=x")}>push</button>
      </div>
      <Image id="img" src="/a.png" alt="A" width={800} height={600} />
    </div>
  );
}
`;

function build(name, source, generate) {
  const { code } = transformSync(source, {
    filename: `${name}.tsx`,
    babelrc: false,
    configFile: false,
    presets: [
      ["babel-preset-solid", { generate, hydratable: true }],
      ["@babel/preset-typescript", { isTSX: true, allExtensions: true }],
    ],
  });
  const out = path.join(folder, `${name}.${generate}.mjs`);
  fs.writeFileSync(out, code.replace(/(['"])\.\/client\.tsx\1/g, `$1./client.${generate}.mjs$1`));
  return pathToFileURL(out).href;
}
const adapterSource = fs.readFileSync(path.join(folder, "client.tsx"), "utf8");

if (side === "server") {
  globalThis.__NEXY_LOCATION__ = SERVER_LOCATION;
  build("client", adapterSource, "ssr");
  const app = (await import(build("app", APP, "ssr"))).default;
  const { renderToString, createComponent } = await import("solid-js/web");
  fs.writeFileSync(served, renderToString(() => createComponent(app, {})));
  process.exit(0);
}

const page = openPage(fs.readFileSync(served, "utf8"));
const serverSide = page.root.innerHTML;
build("client", adapterSource, "dom");
const app = (await import(build("app", APP, "dom"))).default;
globalThis._$HY = { events: [], completed: new WeakSet(), r: {} };
const { hydrate, createComponent } = await import("solid-js/web");
hydrate(() => createComponent(app, {}), page.root);
await sleep(80);

const report = await story(page, { click: clickWith(page.dom.window) });
report.serverHtml = serverSide;
print(report);
