// A React Link rendered with a generated base path: the DOM URL is prefixed but the route is not.
import { createElement } from "react";
import { renderToString } from "react-dom/server";
import { load, print, SERVER_LOCATION, stage } from "./adapter_common.mjs";

const dir = stage("react", "react.ts", [], "/app");
const { Link } = await load(dir, "client.ts");
globalThis.__NEXY_LOCATION__ = SERVER_LOCATION;
const html = renderToString(createElement(Link, { href: "/about" }, "About"));
print({ href: /href="([^"]+)"/.exec(html)?.[1] });
