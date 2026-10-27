// Calls the request guards of document.ts with a JSON list of cases: { fn, args } -> result or error.
import { isLoopback, isRootLayout, parseRenderRequest, withLocation } from "../../nexy/modules/frontend/document.ts";
const fns = { isLoopback, isRootLayout, parseRenderRequest };
const cases = JSON.parse(process.argv[2]);
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
if (process.argv[3] === "concurrent") {
  // Two renders overlap: each must see its own request location, never the other's.
  const read = async (pathname, wait) =>
    withLocation({ pathname, search: "" }, { id: pathname }, async () => {
      await sleep(wait);
      return { seen: globalThis.__NEXY_LOCATION__.pathname, params: globalThis.__NEXY_LOCATION__.params };
    });
  const results = await Promise.all([read("/a", 30), read("/b", 1)]);
  console.log("@@" + JSON.stringify({ results, after: globalThis.__NEXY_LOCATION__ ?? null }) + "@@");
  process.exit(0);
}
const out = cases.map((c) => {
  try {
    return { ok: fns[c.fn](...c.args) };
  } catch (error) {
    return { error: String(error.message) };
  }
});
console.log("@@" + JSON.stringify(out) + "@@");
