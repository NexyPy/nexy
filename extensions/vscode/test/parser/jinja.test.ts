import { describe, it, expect } from "vitest";
import {
  extractJinjaExpressions, extractVariables, extractFilters,
  isValidJinjaFilter, isJinjaKeyword,
} from "../../src/shared/parser/jinja";

describe("extractJinjaExpressions", () => {
  it("extracts {{ expressions }}", () => {
    const result = extractJinjaExpressions("Hello {{ name }}!");
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({ type: "expression", content: "name" });
  });

  it("extracts {% blocks %}", () => {
    const result = extractJinjaExpressions("{% if active %}yes{% endif %}");
    expect(result).toHaveLength(2);
    expect(result[0]).toMatchObject({ type: "block", content: "if active" });
    expect(result[1]).toMatchObject({ type: "block", content: "endif" });
  });

  it("extracts {# comments #}", () => {
    const result = extractJinjaExpressions("start{# comment here #}end");
    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({ type: "comment", content: "comment here" });
  });

  it("returns results in source order", () => {
    const result = extractJinjaExpressions("{% if x %}{{ y }}{% endif %}");
    expect(result.map((e) => e.type)).toEqual(["block", "expression", "block"]);
  });

  it("returns empty for plain text", () => {
    expect(extractJinjaExpressions("<div>plain</div>")).toEqual([]);
  });
});

describe("extractVariables", () => {
  it("extracts variable name from simple expression", () => {
    expect(extractVariables("title")).toEqual(["title"]);
  });

  it("extracts variable before filter", () => {
    expect(extractVariables("title|upper")).toEqual(["title"]);
  });

  it("returns empty for literal expression", () => {
    expect(extractVariables('"hello"')).toEqual([]);
  });
});

describe("extractFilters", () => {
  it("extracts filter names from piped expression", () => {
    expect(extractFilters("title|upper|trim")).toEqual(["upper", "trim"]);
  });

  it("returns empty when no filters", () => {
    expect(extractFilters("title")).toEqual([]);
  });
});

describe("isValidJinjaFilter", () => {
  it("returns true for known filters", () => {
    expect(isValidJinjaFilter("upper")).toBe(true);
    expect(isValidJinjaFilter("escape")).toBe(true);
    expect(isValidJinjaFilter("default")).toBe(true);
  });

  it("returns false for unknown filters", () => {
    expect(isValidJinjaFilter("foobar")).toBe(false);
    expect(isValidJinjaFilter("myfilter")).toBe(false);
  });
});

describe("isJinjaKeyword", () => {
  it("returns true for keywords", () => {
    expect(isJinjaKeyword("if")).toBe(true);
    expect(isJinjaKeyword("endif")).toBe(true);
    expect(isJinjaKeyword("for")).toBe(true);
  });

  it("returns false for non-keywords", () => {
    expect(isJinjaKeyword("foo")).toBe(false);
  });
});
