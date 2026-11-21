// Checks how the client build picks and renders the snapshots of an island per set of props.
//   node island_variants.mjs <project folder>
// Prints one JSON object.
const { readIslandProps, propsFor, renderVariants } = await import(
  "../../nexy/modules/frontend/scripts/ssg.variants.ts"
);

const all = readIslandProps(process.argv[2]);
const warnings = [];
const render = async (props) => {
  if (props.label === "boom") throw new Error("it broke");
  return `<b>${props.label}</b>`;
};
const picked = propsFor(all, "src/components/spike.tsx", "default", ["default", "Badge"]);
const rendered = await renderVariants("src/components/spike.tsx", render, picked, (m) => warnings.push(m));

console.log(JSON.stringify({
  missing: readIslandProps(process.argv[2] + "/nowhere"),
  defaultExport: propsFor(all, "src/components/spike.tsx", "default", ["default", "Badge"]),
  namedExport: propsFor(all, "src/components/spike.tsx", "Badge", ["default", "Badge"]),
  otherFile: propsFor(all, "src/components/other.tsx", "default", ["default"]),
  rendered,
  warnings,
}));
