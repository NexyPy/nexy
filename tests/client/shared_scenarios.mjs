// The pure helpers every adapter shares (nexy/modules/frontend/client/shared.ts).
import { cssText, imageAttributes, isActive, pathOf } from "../../nexy/modules/frontend/client/shared.ts";

const out = {
  paths: ["/", "/about", "/about/", "/about?x=1#top", "", "/a/b//"].map(pathOf),
  active: {
    same: isActive("/about", "/about"),
    trailing: isActive("/about/", "/about"),
    query: isActive("/about", "/about?tab=1"),
    parent: isActive("/docs/intro", "/docs"),
    parentExact: isActive("/docs/intro", "/docs", true),
    sibling: isActive("/docsx", "/docs"),
    root: isActive("/about", "/"),
    rootSelf: isActive("/", "/"),
  },
  image: {
    basic: imageAttributes({ src: "/a.png", alt: "A" }),
    sized: imageAttributes({ src: "/a.png", alt: "A", width: 800, height: 600 }),
    widthOnly: imageAttributes({ src: "/a.png", alt: "A", width: 800 }),
    priority: imageAttributes({ src: "/a.png", alt: "A", priority: true }),
    fill: imageAttributes({ src: "/a.png", alt: "", fill: true, width: 10, height: 10 }),
    explicitLoading: imageAttributes({ src: "/a.png", alt: "", loading: "eager" }),
    responsive: imageAttributes({ src: "/a.png", alt: "", sizes: "100vw", srcSet: "/a.png 1x, /b.png 2x" }),
  },
  css: {
    camel: cssText({ maxWidth: "100%", objectFit: "cover" }),
    empty: cssText(undefined),
  },
};
console.log("@@" + JSON.stringify(out) + "@@");
