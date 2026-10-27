// Link, Image and the composables of the Vue adapter, server-rendered then hydrated.
//   node --conditions=browser adapter_vue.mjs
import { clickWith, load, openPage, print, sleep, stage, story } from "./adapter_common.mjs";

// Vue reads `document` once, when it is imported: the page exists first. The router it opens
// has the same location the server saw, so the server render below sees /about?tab=a too.
const page = openPage("");
const dir = stage("vue", "vue.ts");
const { createSSRApp, defineComponent, h } = await import("vue");
const { renderToString } = await import("vue/server-renderer");
const { Link, Image, useRouter, usePathname, useParams, useSearchParams } = await load(dir, "client.ts");

const Probe = defineComponent({
  setup() {
    const router = useRouter();
    const path = usePathname();
    const params = useParams();
    const search = useSearchParams();
    return () =>
      h("div", null, [
        h("p", { id: "path" }, path.value),
        h("p", { id: "params" }, JSON.stringify(params.value)),
        h("p", { id: "tab" }, search.value.get("tab") ?? ""),
        h("button", { id: "push", onClick: () => router.push("/users/7?tab=x") }, "push"),
      ]);
  },
});
const App = defineComponent({
  render: () =>
    h("div", null, [
      h(Link, { id: "home", href: "/", exact: true, activeClass: "on", class: "nav" }, () => "Home"),
      h(Link, { id: "about", href: "/about", activeClass: "on", class: "nav" }, () => "About"),
      h(Link, { id: "user", href: "/users/7" }, () => "User"),
      h(Probe),
      h(Image, { id: "img", src: "/a.png", alt: "A", width: 800, height: 600 }),
    ]),
});

const html = await renderToString(createSSRApp(App));
page.root.innerHTML = html;
const serverSide = page.root.innerHTML;
createSSRApp(App).mount(page.root);
await sleep(80);

const report = await story(page, { click: clickWith(page.dom.window) });
report.serverHtml = serverSide;
print(report);
