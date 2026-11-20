// Drives the framework-neutral client router (nexy/modules/frontend/client/router.ts) in jsdom.
// Prints one JSON object between @@ markers: scenario name -> observations.
import { JSDOM } from "jsdom";
import { createRouter, hold, searchParamsOf } from "../../nexy/modules/frontend/client/router.ts";

const ROUTES = {
  "/": { file: "/src/routes/index.tsx", layouts: [], params: {} },
  "/about": { file: "/src/routes/about.tsx", layouts: [], params: {} },
  "/slow": { file: "/src/routes/slow.tsx", layouts: [], params: {} },
  "/broken": { file: "/src/routes/broken.tsx", layouts: [], params: {} },
};
const match = (pathname) => {
  if (ROUTES[pathname]) return ROUTES[pathname];
  const user = /^\/users\/([^/]+)$/.exec(pathname);
  return user ? { file: "/src/routes/users/[id].tsx", layouts: [], params: { id: user[1] } } : null;
};

// Every window opened, closed before the process exits.
const windows = [];

function world({ url = "http://localhost/", render } = {}) {
  const dom = new JSDOM(`<!DOCTYPE html><body><main id="m"></main><h2 id="section">S</h2></body>`, {
    url,
    pretendToBeVisual: true,
  });
  const real = dom.window;
  const assigned = [];
  const scrolls = [];
  const rendered = [];
  const prefetched = [];
  let scrollY = 0;
  real.scrollTo = (x, y) => {
    scrollY = y;
    scrolls.push([x, y]);
  };
  Object.defineProperty(real, "scrollY", { get: () => scrollY });
  real.HTMLElement.prototype.scrollIntoView = function () {
    scrolls.push(["into", this.id]);
  };
  // The proxies wrap empty objects: jsdom's own properties are not configurable.
  const loc = new Proxy({}, {
    get(_target, prop) {
      if (prop === "assign") return (u) => assigned.push(String(u));
      const value = real.location[prop];
      return typeof value === "function" ? value.bind(real.location) : value;
    },
  });
  const win = new Proxy({}, {
    get(_target, prop) {
      if (prop === "location") return loc;
      const value = real[prop];
      return typeof value === "function" && prop !== "CustomEvent" ? value.bind(real) : value;
    },
    set(_target, prop, value) {
      real[prop] = value;
      return true;
    },
  });
  const router = createRouter({
    match,
    win,
    render: render ?? (async (m) => void rendered.push(m.file)),
    prefetch: (m) => prefetched.push(m.file),
  });
  const events = [];
  real.document.addEventListener("nexy:navigated", (e) => events.push(e.detail.pathname));
  const stop = router.start();
  windows.push(real);
  return { dom, real, router, assigned, scrolls, rendered, prefetched, events, stop, setScroll: (y) => (scrollY = y) };
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const out = {};

// 1. A navigation renders first, then moves the URL, and announces itself.
{
  const w = world();
  const ok = await w.router.navigate("/about");
  out.navigate = {
    ok,
    path: w.real.location.pathname,
    rendered: w.rendered,
    location: w.router.getLocation().pathname,
    events: w.events,
    state: w.real.history.state?.nexy === true,
  };
}

// 2. A page that fails to render never moves the URL; the server takes over.
{
  const w = world({ render: async () => { throw new Error("boom"); } });
  const silence = console.error;
  console.error = () => {};
  const ok = await w.router.navigate("/broken");
  console.error = silence;
  out.renderFailure = { ok, path: w.real.location.pathname, assigned: w.assigned };
}

// 3. An unknown path and another origin are the server's business.
{
  const w = world();
  const a = await w.router.navigate("/nowhere");
  const b = await w.router.navigate("https://example.com/about");
  out.serverOwned = { a, b, assigned: w.assigned, rendered: w.rendered };
}

// 4. A newer navigation wins over one that is still rendering.
{
  const gates = {};
  const w = world({
    render: async (m) => {
      if (m.file.includes("slow")) await new Promise((resolve) => (gates.slow = resolve));
    },
  });
  const first = w.router.navigate("/slow");
  await sleep(10);
  const second = w.router.navigate("/about");
  await second;
  gates.slow();
  const firstResult = await first;
  out.concurrent = { first: firstResult, path: w.real.location.pathname, length: w.real.history.length };
}

// 5. Only the fragment changes: nothing renders, the target scrolls into view.
{
  const w = world();
  const ok = await w.router.navigate("/#section");
  out.hash = { ok, rendered: w.rendered, hash: w.real.location.hash, scrolls: w.scrolls };
}

// 6. replace keeps the history length.
{
  const w = world();
  const before = w.real.history.length;
  await w.router.replace("/about");
  out.replace = { grew: w.real.history.length - before, path: w.real.location.pathname };
}

// 7. Subscribers hear each change once; the location keeps its identity otherwise.
{
  const w = world();
  let calls = 0;
  w.router.subscribe(() => calls++);
  const first = w.router.getLocation();
  await w.router.navigate("/about");
  const second = w.router.getLocation();
  await w.router.navigate("/about");
  out.subscribe = { calls, changed: first !== second, stable: second === w.router.getLocation() };
}

// 8. Going back renders the previous page and restores its scroll position.
{
  const w = world();
  w.setScroll(420);
  await w.router.navigate("/about");
  w.rendered.length = 0;
  w.real.history.back();
  await sleep(80);
  out.back = { path: w.real.location.pathname, rendered: w.rendered, scrolled: w.scrolls.at(-1) };
}

// 9. Dynamic params reach the location, and the query string is exposed.
{
  const w = world();
  await w.router.navigate("/users/42?tab=posts");
  out.params = {
    params: w.router.getLocation().params,
    search: w.router.getLocation().search,
    query: searchParamsOf(w.router.getLocation().search),
  };
}

// 10. Which clicks become navigations.
{
  const w = world();
  const doc = w.real.document;
  const click = (attrs, init = {}) => {
    const a = doc.createElement("a");
    for (const [k, v] of Object.entries(attrs)) a.setAttribute(k, v);
    a.textContent = "x";
    doc.body.append(a);
    const event = new w.real.MouseEvent("click", { bubbles: true, cancelable: true, button: 0, ...init });
    a.dispatchEvent(event);
    a.remove();
    return event.defaultPrevented;
  };
  out.clicks = {
    plain: click({ href: "/about" }),
    withLinkAttr: click({ href: "/about", "data-nexy-link": "true" }),
    ctrl: click({ href: "/about" }, { ctrlKey: true }),
    middle: click({ href: "/about" }, { button: 1 }),
    blank: click({ href: "/about", target: "_blank" }),
    download: click({ href: "/about", download: "" }),
    reload: click({ href: "/about", "data-nexy-reload": "" }),
    external: click({ href: "https://example.com/about" }),
    rel: click({ href: "/about", rel: "external" }),
    unknown: click({ href: "/nowhere" }),
    hashOnly: click({ href: "#section" }),
    mailto: click({ href: "mailto:a@b.c" }),
  };
}

// 11. Prefetch warms each route once, and ignores what it cannot serve.
{
  const w = world();
  w.router.prefetch("/about");
  w.router.prefetch("/about");
  w.router.prefetch("/nowhere");
  w.router.prefetch("https://example.com/about");
  out.prefetch = w.prefetched;
}

// 12. Navigating to the page already shown does nothing.
{
  const w = world();
  const ok = await w.router.navigate("/");
  out.samePage = { ok, rendered: w.rendered, length: w.real.history.length };
}

// 12. With view transitions the page change happens inside one, unless the visitor prefers calm.
{
  const calls = [];
  const w = world();
  w.real.document.startViewTransition = (update) => {
    calls.push("start");
    return { updateCallbackDone: update().then(() => calls.push("done")) };
  };
  w.real.matchMedia = () => ({ matches: false });
  await w.router.navigate("/about");
  const calm = world();
  const calmCalls = [];
  calm.real.document.startViewTransition = (update) => {
    calmCalls.push("start");
    return { updateCallbackDone: update() };
  };
  calm.real.matchMedia = () => ({ matches: true });
  await calm.router.navigate("/about");
  out.viewTransition = { calls, rendered: w.rendered, calmCalls, calmRendered: calm.rendered };
}

// 12b. A transition the browser skips rejects `ready` and `finished`: the router handles both, so
// going back twice quickly logs nothing.
{
  const unhandled = [];
  const listen = (reason) => unhandled.push(String(reason));
  process.on("unhandledRejection", listen);
  const w = world();
  w.real.document.startViewTransition = (update) => ({
    updateCallbackDone: update(),
    ready: Promise.reject(new Error("Transition was skipped")),
    finished: Promise.reject(new Error("Transition was skipped")),
  });
  w.real.matchMedia = () => ({ matches: false });
  await w.router.navigate("/about");
  await new Promise((resolve) => setTimeout(resolve, 10));
  process.off("unhandledRejection", listen);
  out.skippedTransition = { unhandled, rendered: w.rendered };
}

// 13. Transition subscribers hear a navigation start and end: `transition()` is pending in between.
{
  let release;
  const w = world({ render: () => new Promise((resolve) => (release = resolve)) });
  const states = [];
  w.router.subscribeTransition(() => states.push(w.router.transition().pending));
  const done = w.router.navigate("/about");
  await sleep(0);
  release();
  await done;
  const superseded = world({ render: (m) => (m.file.endsWith("slow.tsx") ? sleep(30) : Promise.resolve()) });
  const after = [];
  superseded.router.subscribeTransition(() => after.push(superseded.router.transition().pending));
  await Promise.all([superseded.router.navigate("/slow"), sleep(5).then(() => superseded.router.navigate("/about"))]);
  out.transition = { states, superseded: after };
}

// 14. A blocker holds the back and forward buttons too; once it is gone they move again.
{
  const w = world();
  await w.router.navigate("/about");
  const stop = w.router.blocker(() => "unsaved");
  w.real.history.back();
  await sleep(40);
  const held = w.real.location.pathname;
  const heldRendered = [...w.rendered];
  stop();
  w.real.history.back();
  await sleep(40);
  out.backBlocked = { held, heldRendered, after: w.real.location.pathname, rendered: w.rendered };
}

// 15. A guard asks before leaving: a refusal stays, a yes goes on, and a reload is asked too.
{
  const w = world();
  const answers = [false, true];
  const asked = [];
  w.real.confirm = (message) => (asked.push(message), answers.shift());
  const release = w.router.guard("Leave?");
  const refused = await w.router.navigate("/about");
  const accepted = await w.router.navigate("/about");
  const held = new w.real.Event("beforeunload", { cancelable: true });
  w.real.dispatchEvent(held);
  release();
  const freed = new w.real.Event("beforeunload", { cancelable: true });
  w.real.dispatchEvent(freed);
  out.guard = { asked, refused, accepted, held: held.defaultPrevented, freed: freed.defaultPrevented };
}

// 16. hold() is what every useBlocker calls: true guards, false holds nothing, a function blocks.
{
  const w = world();
  w.real.confirm = () => false;
  const free = hold(w.router, false);
  const freeOk = await w.router.navigate("/about");
  free();
  const guarded = hold(w.router, true);
  const guardedOk = await w.router.navigate("/");
  guarded();
  const blocked = hold(w.router, () => "no");
  const blockedOk = await w.router.navigate("/");
  blocked();
  out.hold = { freeOk, guardedOk, blockedOk };
}

for (const window of windows) window.close();
console.log("@@" + JSON.stringify(out) + "@@");
process.exit(0);
