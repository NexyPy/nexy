// Runs the hooks of the Nexy Vite plugin the way Vite calls them, with no Vite installed.
//   node vite_plugin.mjs <serve|build|build-failed|warmup>
// `vite`, `esbuild` and `child_process` are stubs: the scenario prints what the plugin logged
// and the commands it ran when the server, or the build, closed.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { registerHooks } from "node:module";
import { pathToFileURL } from "node:url";

// `build-failed` is a build whose bundle was never written: Vite still closes it.
const scenario = process.argv[2];
const command = scenario === "serve" || scenario === "warmup" ? "serve" : "build";
const SOURCES = new URL("../../nexy/modules/frontend/", import.meta.url);
const ran = [];
globalThis.__nexyRan = ran;

const STUBS = {
  vite: "export const createLogger = () => ({ info() {}, warn() {}, error() {} })",
  esbuild: "export const transform = async (code) => ({ code })",
  child_process: "export const execSync = (cmd) => { globalThis.__nexyRan.push(cmd) }",
};

registerHooks({
  resolve(specifier, context, next) {
    if (specifier in STUBS) return { url: `nexy-stub:${specifier}`, shortCircuit: true };
    if (specifier === "./document") return next("./document.ts", context);
    return next(specifier, context);
  },
  load(url, context, next) {
    const name = url.startsWith("nexy-stub:") ? url.slice("nexy-stub:".length) : null;
    if (name) return { format: "module", source: STUBS[name], shortCircuit: true };
    return next(url, context);
  },
});

const project = fs.mkdtempSync(path.join(os.tmpdir(), "nexy-vite-plugin-"));
const nexyDir = path.join(project, "__nexy__");
fs.mkdirSync(path.join(nexyDir, "src"), { recursive: true });
for (const name of ["vite.ts", "document.ts"]) fs.copyFileSync(new URL(name, SOURCES), path.join(nexyDir, name));
fs.writeFileSync(path.join(nexyDir, "src", "deps.auto.ts"), "export const __NEXY_DEPS: string[] = []\n");
process.chdir(project);

const logged = [];
const log = console.log;
console.log = (...args) => logged.push(args.join(" ").replace(/\x1b\[\d+m/g, ""));
let error = null;
let warmup = null;
try {
  const { default: nexy } = await import(pathToFileURL(path.join(nexyDir, "vite.ts")).href);
  const plugin = [nexy()].flat().find((p) => p.name === "nexy");
  const mode = command === "build" ? "production" : "development";
  const config = await plugin.config?.({ mode }, { command, mode });
  warmup = config?.server?.warmup?.clientFiles ?? null;
  plugin.configResolved?.({ command, mode, build: {} });
  if (scenario === "build") plugin.writeBundle?.();
  plugin.closeBundle?.();
} catch (caught) {
  error = String(caught?.message ?? caught);
} finally {
  console.log = log;
  fs.rmSync(project, { recursive: true, force: true });
}
// `warmup` prints the files the dev server transforms ahead of a request, and nothing else.
const report = scenario === "warmup" ? { warmup, error } : { logged, ran, error };
process.stdout.write("@@" + JSON.stringify(report) + "@@");
