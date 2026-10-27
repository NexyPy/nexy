// Link, Image and the hooks of the React and Preact adapters, server-rendered then hydrated.
//   node --conditions=browser adapter_jsx.mjs <react|preact>
import { clickWith, load, openPage, print, SERVER_LOCATION, stage, story } from "./adapter_common.mjs";

const framework = process.argv[2];
const dir = stage(framework, `${framework}.ts`);

const lib = framework === "react"
  ? { h: (await import("react")).createElement, ssr: (await import("react-dom/server")).renderToString }
  : { h: (await import("preact")).h, ssr: (await import("preact-render-to-string")).renderToString };
const adapter = await load(dir, "client.ts");
const { Link, Image, useRouter, usePathname, useParams, useSearchParams } = adapter;
const { h } = lib;
const cls = framework === "react" ? "className" : "class";

function Probe() {
  const router = useRouter();
  const search = useSearchParams();
  return h(
    "div",
    null,
    h("p", { id: "path" }, usePathname()),
    h("p", { id: "params" }, JSON.stringify(useParams())),
    h("p", { id: "tab" }, search.get("tab") ?? ""),
    h("button", { id: "push", onClick: () => router.push("/users/7?tab=x") }, "push"),
  );
}
const App = () =>
  h(
    "div",
    null,
    h(Link, { id: "home", href: "/", exact: true, activeClassName: "on", [cls]: "nav" }, "Home"),
    h(Link, { id: "about", href: "/about", activeClassName: "on", [cls]: "nav" }, "About"),
    h(Link, { id: "user", href: "/users/7" }, "User"),
    h(Probe),
    h(Image, { id: "img", src: "/a.png", alt: "A", width: 800, height: 600 }),
  );

// 1. Server render at /about?tab=a: there is no router yet, the request location is all it has.
globalThis.__NEXY_LOCATION__ = SERVER_LOCATION;
const html = lib.ssr(h(App));

// 2. The browser: the same page, the router running, the markup hydrated.
const page = openPage(html);
const serverSide = page.root.innerHTML;
if (framework === "react") {
  const { hydrateRoot } = await import("react-dom/client");
  hydrateRoot(page.root, h(App));
} else {
  const { hydrate } = await import("preact");
  hydrate(h(App), page.root);
}
await new Promise((resolve) => setTimeout(resolve, 80));

const report = await story(page, { click: clickWith(page.dom.window) });
report.serverHtml = serverSide;
print(report);
