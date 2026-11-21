// Renders an island's build snapshot the way the static build does, with React and Preact.
//   node island_snapshot.mjs
// Prints each HTML between @@ markers: react, preact, then react given props.
import { createElement } from "react";
import { renderToString as reactToString } from "react-dom/server";
import { h } from "preact";
import { renderToString as preactToString } from "preact-render-to-string";

const { renderSnapshot } = await import("../../nexy/modules/frontend/scripts/ssg.snapshot.ts");

// `label` has a default, as in #591: the snapshot must show it, never a placeholder.
const Spike = ({ label = "count", open = false }) =>
  createElement("button", { type: "button", className: "  a   b " }, `${label}: ${open ? 1 : 0}`);
const PreactSpike = ({ label = "count" }) => h("button", { type: "button" }, `${label}: 0`);

const react = await renderSnapshot(async (C, props) => reactToString(createElement(C, props)), Spike);
const preact = await renderSnapshot(async (C, props) => preactToString(h(C, props)), PreactSpike);
const given = await renderSnapshot(async (C, props) => reactToString(createElement(C, props)), Spike, { label: "clicks", open: true });
console.log(`@@${react}@@${preact}@@${given}@@`);
