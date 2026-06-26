import { describe, it, expect, beforeEach, afterEach } from "vitest";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";
import { findWorkspaceRoot, parseMdxConfig, parseNexyConfig, resolvePythonModulePath } from "../src/shared/nexy.config.parser";

let tmpDir: string;

beforeEach(() => {
  tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "nexy-test-"));
});

afterEach(() => {
  fs.rmSync(tmpDir, { recursive: true, force: true });
});

describe("findWorkspaceRoot", () => {
  it("returns dir containing nexyconfig.py", () => {
    fs.writeFileSync(path.join(tmpDir, "nexyconfig.py"), "useAliases = {}");
    const sub = fs.mkdtempSync(path.join(tmpDir, "sub-"));
    expect(findWorkspaceRoot(sub)).toBe(tmpDir);
  });

  it("returns dir containing src/mdxconfig", () => {
    const srcDir = path.join(tmpDir, "src");
    fs.mkdirSync(srcDir);
    fs.writeFileSync(path.join(srcDir, "mdxconfig"), "h1: use { H } from './h.nexy'");
    const sub = fs.mkdtempSync(path.join(tmpDir, "sub-"));
    expect(findWorkspaceRoot(sub)).toBe(tmpDir);
  });

  it("prefers nexyconfig.py over src/mdxconfig", () => {
    fs.writeFileSync(path.join(tmpDir, "nexyconfig.py"), "");
    const srcDir = path.join(tmpDir, "src");
    fs.mkdirSync(srcDir);
    fs.writeFileSync(path.join(srcDir, "mdxconfig"), "");
    expect(findWorkspaceRoot(tmpDir)).toBe(tmpDir);
  });

  it("returns null when neither is found", () => {
    expect(findWorkspaceRoot(tmpDir)).toBeNull();
  });

  it("stops at filesystem root", () => {
    expect(findWorkspaceRoot(tmpDir)).toBeNull();
  });
});

describe("parseMdxConfig", () => {
  it("returns empty array when src/mdxconfig does not exist", () => {
    expect(parseMdxConfig(tmpDir)).toEqual([]);
  });

  it("parses element mappings", () => {
    const srcDir = path.join(tmpDir, "src");
    fs.mkdirSync(srcDir);
    fs.writeFileSync(path.join(srcDir, "mdxconfig"), [
      'h1: use { Heading } from "./comp/Heading.nexy"',
      'img: use {} from "./comp/Image.nexy"',
      'table: use { Table } from "./comp/Table.nexy"',
    ].join("\n"));

    const result = parseMdxConfig(tmpDir);
    expect(result).toHaveLength(3);
    expect(result[0]).toEqual({ element: "h1", symbol: "Heading", source: "./comp/Heading.nexy" });
    expect(result[1]).toEqual({ element: "img", symbol: "", source: "./comp/Image.nexy" });
    expect(result[2]).toEqual({ element: "table", symbol: "Table", source: "./comp/Table.nexy" });
  });

  it("skips comments and blank lines", () => {
    const srcDir = path.join(tmpDir, "src");
    fs.mkdirSync(srcDir);
    fs.writeFileSync(path.join(srcDir, "mdxconfig"), [
      "# this is a comment",
      "",
      '  h1: use { H } from "./h.nexy"  ',
    ].join("\n"));

    expect(parseMdxConfig(tmpDir)).toHaveLength(1);
  });

  it("returns empty when file has no valid mappings", () => {
    const srcDir = path.join(tmpDir, "src");
    fs.mkdirSync(srcDir);
    fs.writeFileSync(path.join(srcDir, "mdxconfig"), "some random text\nnot a mapping");
    expect(parseMdxConfig(tmpDir)).toEqual([]);
  });
});

describe("parseNexyConfig", () => {
  it("returns empty aliases when no file", () => {
    expect(parseNexyConfig(tmpDir)).toEqual({ useAliases: {} });
  });

  it("parses useAliases dict", () => {
    fs.writeFileSync(path.join(tmpDir, "nexyconfig.py"), 'useAliases: dict[str, str] = {"@": "src"}');
    expect(parseNexyConfig(tmpDir)).toEqual({ useAliases: { "@": "src" } });
  });

  it("handles multiple aliases", () => {
    fs.writeFileSync(path.join(tmpDir, "nexyconfig.py"),
      "useAliases = {\n  '@components': 'src/components',\n  '@lib': 'src/lib',\n}");
    const result = parseNexyConfig(tmpDir);
    expect(result.useAliases["@components"]).toBe("src/components");
    expect(result.useAliases["@lib"]).toBe("src/lib");
  });
});

describe("resolvePythonModulePath", () => {
  it("resolves dotted path to existing file", () => {
    const compDir = path.join(tmpDir, "src", "components");
    fs.mkdirSync(compDir, { recursive: true });
    fs.writeFileSync(path.join(compDir, "sidebar.nexy"), "---\n---\n<div>sidebar</div>");

    const resolved = resolvePythonModulePath("src.components.sidebar", tmpDir);
    expect(resolved).toBe(path.join(compDir, "sidebar.nexy"));
  });

  it("resolves dotted path to __init__.py", () => {
    const pkgDir = path.join(tmpDir, "src", "components");
    fs.mkdirSync(pkgDir, { recursive: true });
    fs.writeFileSync(path.join(pkgDir, "__init__.py"), "# package");

    const resolved = resolvePythonModulePath("src.components", tmpDir);
    expect(resolved).toBe(path.join(pkgDir, "__init__.py"));
  });

  it("returns null for system modules (not on disk)", () => {
    expect(resolvePythonModulePath("os.path", tmpDir)).toBeNull();
  });

  it("returns null for relative paths", () => {
    expect(resolvePythonModulePath("./components/sidebar", tmpDir)).toBeNull();
  });

  it("returns null for alias paths", () => {
    expect(resolvePythonModulePath("@/components/sidebar", tmpDir)).toBeNull();
  });

  it("returns null for paths without dots", () => {
    expect(resolvePythonModulePath("sidebar", tmpDir)).toBeNull();
  });
});
