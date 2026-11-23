// Compiles a Solid component the way the static build does, then renders it in Node.
//   node solid_server_jsx.mjs
// esbuild is not installed here: the plugin gets a stand-in whose `transform` only removes the
// one type annotation of the component, as esbuild would. Prints the HTML between @@ markers.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const { solidServerJsx } = await import("../../nexy/modules/frontend/scripts/solid.server.ts");

const SOURCE = `
import { createSignal } from "solid-js";
export default function Hello(props: { name?: string }) {
  const [count] = createSignal(2);
  return <><p class="hello">hello {props.name ?? "you"}</p><span>{count()}</span></>;
}
`;

let load;
const build = {
  onLoad(_options, callback) {
    load = callback;
  },
  esbuild: {
    transform: async (code) => ({ code: code.replace(": { name?: string }", "") }),
  },
};
solidServerJsx().setup(build);

const file = path.join(import.meta.dirname, "hello.tsx");
fs.writeFileSync(file, SOURCE);
try {
  const { contents } = await load({ path: file });
  const out = path.join(import.meta.dirname, "hello.server.mjs");
  fs.writeFileSync(out, contents);
  const Hello = (await import(pathToFileURL(out).href)).default;
  const { renderToString } = await import("solid-js/web");
  console.log(`@@${renderToString(() => Hello({}))}@@`);
  fs.rmSync(out);
} finally {
  fs.rmSync(file);
}
