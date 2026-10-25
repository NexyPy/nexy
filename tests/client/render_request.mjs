// Calls the request guards of document.ts with a JSON list of cases: { fn, args } -> result or error.
import { isLoopback, isRootLayout, parseRenderRequest } from "../../nexy/modules/frontend/document.ts";
const fns = { isLoopback, isRootLayout, parseRenderRequest };
const cases = JSON.parse(process.argv[2]);
const out = cases.map((c) => {
  try {
    return { ok: fns[c.fn](...c.args) };
  } catch (error) {
    return { error: String(error.message) };
  }
});
console.log("@@" + JSON.stringify(out) + "@@");
