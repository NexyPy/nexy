import { describe, it, expect } from "vitest";
import { extractHeader, extractImports, extractProps, parseHeader, findUsedComponents, extractRegionAtOffset } from "../../src/shared/parser/header";

describe("extractHeader", () => {
  it("extracts header content between --- markers", () => {
    const text = "---\ntitle : prop[str] = \"Hello\"\n---\n<div>{{ title }}</div>";
    expect(extractHeader(text)).toBe('title : prop[str] = "Hello"');
  });

  it("returns null when no header", () => {
    expect(extractHeader("<div>plain html</div>")).toBeNull();
  });

  it("returns null for empty text", () => {
    expect(extractHeader("")).toBeNull();
  });
});

describe("extractImports", () => {
  it("extracts from-import statements", () => {
    const header = 'from "./Button.nexy" import Button\nfrom "./Card.vue" import Card';
    const result = extractImports(header);
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ path: "./Button.nexy", name: "Button", framework: "nexy" });
    expect(result[1]).toMatchObject({ path: "./Card.vue", name: "Card", framework: "vue" });
  });

  it("returns empty when no imports", () => {
    expect(extractImports("title : prop[str]")).toEqual([]);
  });

  it("handles imports with multiline target list without parentheses", () => {
    const header = 'from "./utils.nexy" import UtilOne, UtilTwo';
    const result = extractImports(header);
    expect(result).toHaveLength(2);
    expect(result[0].name).toBe("UtilOne");
    expect(result[1].name).toBe("UtilTwo");
  });

  it("extracts Python-style unquoted module imports", () => {
    const header = "from src.components.sidebar import Sidebar\nfrom src.lib.utils import Helper";
    const result = extractImports(header);
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ path: "src.components.sidebar", name: "Sidebar", framework: "nexy" });
    expect(result[1]).toMatchObject({ path: "src.lib.utils", name: "Helper", framework: "nexy" });
  });

  it("handles both quoted and unquoted imports in same header", () => {
    const header = 'from "./Button.nexy" import Button\nfrom src.components.card import Card';
    const result = extractImports(header);
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ path: "./Button.nexy", name: "Button" });
    expect(result[1]).toMatchObject({ path: "src.components.card", name: "Card" });
  });
});

describe("extractProps", () => {
  it("extracts typed props", () => {
    const header = 'title : prop[str] = "Hello"\ncount : prop[int]';
    const props = extractProps(header);
    expect(props).toEqual([
      { name: "title", type: "str", defaultValue: '"Hello"' },
      { name: "count", type: "int", defaultValue: undefined },
    ]);
  });

  it("returns empty when no props", () => {
    expect(extractProps("from './x' import Y")).toEqual([]);
  });

  it("returns empty for empty header", () => {
    expect(extractProps("")).toEqual([]);
  });
});

describe("parseHeader", () => {
  it("returns imports and props from full .nexy text", () => {
    const text = "---\nfrom \"./Btn.nexy\" import Btn\nlabel : prop[str]\n---\n<Btn />";
    const result = parseHeader(text);
    expect(result.imports).toHaveLength(1);
    expect(result.props).toHaveLength(1);
    expect(result.imports[0].name).toBe("Btn");
    expect(result.props[0].name).toBe("label");
  });

  it("returns empty for text without header", () => {
    expect(parseHeader("<div>plain</div>")).toEqual({ imports: [], props: [] });
  });
});

describe("findUsedComponents", () => {
  const BUILTINS = ["Slot", "Fragment", "ClientOnly", "Head", "Html", "Body"];

  it("finds PascalCase components in template", () => {
    expect(findUsedComponents("<Button /><Card>text</Card>")).toEqual(["Button", "Card", ...BUILTINS]);
  });

  it("ignores lowercase HTML tags", () => {
    expect(findUsedComponents("<div><span>text</span></div>")).toEqual(BUILTINS);
  });

  it("returns unique names", () => {
    expect(findUsedComponents("<Button /><Button />")).toEqual(["Button", ...BUILTINS]);
  });
});

describe("extractRegionAtOffset", () => {
  it("returns header for offset inside header", () => {
    const text = "---\nfoo\n---\nbar";
    expect(extractRegionAtOffset(text, 0)).toBe("header");
    expect(extractRegionAtOffset(text, 6)).toBe("header");
  });

  it("returns template for offset in template", () => {
    const text = "---\nfoo\n---\nbar";
    expect(extractRegionAtOffset(text, 12)).toBe("template");
  });

  it("returns template when no header", () => {
    expect(extractRegionAtOffset("<div>text</div>", 3)).toBe("template");
  });
});
