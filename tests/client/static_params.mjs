// Runs writeDocuments of the Nexy document renderer on one dynamic client route, with no Vite.
//   node static_params.mjs <sync|async>
// `vite` is a stub whose server loads the route below; the scenario prints the files written
// under __nexy__/client/static.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { registerHooks } from "node:module";
import { pathToFileURL } from "node:url";

const kind = process.argv[2];
const SOURCE = new URL("../../nexy/modules/frontend/document.ts", import.meta.url);
const { createElement } = await import("react");

const params = [{ slug: "hello" }, { slug: "world" }];
globalThis.__nexyRoute = {
  default: ({ slug }) => createElement("h1", null, `Post ${slug}`),
  generateStaticParams: kind === "async" ? async () => params : () => params,
};

registerHooks({
  resolve(specifier, context, next) {
    if (specifier === "vite") return { url: "nexy-stub:vite", shortCircuit: true };
    // The renderer imports react from its own folder: resolve it from this one.
    if (specifier.startsWith("react")) return next(specifier, { ...context, parentURL: import.meta.url });
    return next(specifier, context);
  },
  load(url, context, next) {
    if (url !== "nexy-stub:vite") return next(url, context);
    const source =
      "export const createServer = async () => ({ ssrLoadModule: async () => globalThis.__nexyRoute, close: async () => {} })";
    return { format: "module", source, shortCircuit: true };
  },
});

const project = fs.mkdtempSync(path.join(os.tmpdir(), "nexy-static-params-"));
const nexyDir = path.join(project, "__nexy__");
fs.mkdirSync(path.join(nexyDir, "src"), { recursive: true });
fs.writeFileSync(path.join(nexyDir, "mode.auto.json"), JSON.stringify({ csr: true, framework: "react" }));
const route = { path: "/blog/{slug}", file: "/src/routes/blog/[slug].tsx", layouts: [], params: ["slug"] };
fs.writeFileSync(path.join(nexyDir, "src", "routes.client.auto.ts"), `export const NEXY_ROUTES = ${JSON.stringify([route])}\n`);
process.chdir(project);

const written = [];
let error = null;
try {
  const { writeDocuments } = await import(SOURCE.href);
  await writeDocuments();
  const root = path.join(nexyDir, "client", "static");
  for (const entry of fs.readdirSync(root, { recursive: true })) {
    if (String(entry).endsWith(".html")) written.push(String(entry).split(path.sep).join("/"));
  }
} catch (caught) {
  error = String(caught?.stack ?? caught);
} finally {
  fs.rmSync(project, { recursive: true, force: true });
}
process.stdout.write("@@" + JSON.stringify({ written: written.sort(), error }) + "@@");
