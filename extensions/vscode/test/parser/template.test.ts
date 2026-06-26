import { describe, it, expect } from "vitest";
import { extractStyleTags, extractScriptTags } from "../../src/shared/parser/template";

describe("extractStyleTags", () => {
  it("extracts style tags with CSS content", () => {
    const result = extractStyleTags("<style>h1 { color: red; }</style>");
    expect(result).toHaveLength(1);
    expect(result[0].lang).toBe("css");
    expect(result[0].content).toBe("h1 { color: red; }");
  });

  it("extracts style tags with lang attribute", () => {
    const result = extractStyleTags('<style lang="scss">$red: red;</style>');
    expect(result).toHaveLength(1);
    expect(result[0].lang).toBe("scss");
    expect(result[0].content).toBe("$red: red;");
  });

  it("returns empty when no style tags", () => {
    expect(extractStyleTags("<div>text</div>")).toEqual([]);
  });
});

describe("extractScriptTags", () => {
  it("extracts script tags with JS content", () => {
    const result = extractScriptTags("<script>console.log('hi')</script>");
    expect(result).toHaveLength(1);
    expect(result[0].lang).toBe("javascript");
    expect(result[0].content).toBe("console.log('hi')");
  });

  it("extracts script with lang attribute", () => {
    const result = extractScriptTags('<script lang="ts">const x: number = 1;</script>');
    expect(result).toHaveLength(1);
    expect(result[0].lang).toBe("ts");
  });

  it("returns empty when no script tags", () => {
    expect(extractScriptTags("<div>text</div>")).toEqual([]);
  });
});
