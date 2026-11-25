// Responsive images are resolved from the generated manifest in every adapter's shared helper.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { stage } from "./adapter_common.mjs";

const dir = stage("responsive-image", "shared.ts", [], "/app");
fs.writeFileSync(new URL("image-manifest.auto.ts", dir), `export const IMAGE_VARIANTS = {
  'logo.png': {
    src: '/images/logo-abc-640.webp',
    srcset: '/images/logo-abc-320.webp 320w, /images/logo-abc-640.webp 640w',
    sizes: '(max-width: 640px) 100vw, 640px',
    width: 1200,
    height: 600,
  },
}\n`);
const file = path.join(dir.pathname, "shared.ts");
const { imageAttributes } = await import(pathToFileURL(file).href + `?t=${Date.now()}`);

const out = {
  generated: imageAttributes({ src: "/logo.png", alt: "Logo" }),
  explicit: imageAttributes({ src: "/logo.png", alt: "Logo", srcSet: "/a.png 1x", sizes: "50vw" }),
  fallback: imageAttributes({ src: "/plain.png", alt: "Plain" }),
};
console.log("@@" + JSON.stringify(out) + "@@");
