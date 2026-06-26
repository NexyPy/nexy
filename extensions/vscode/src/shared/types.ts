export type NexyFramework = "vue" | "nexy" | "react" | "solid" | "preact" | "svelte" | "unknown";

export type RegionType = "header" | "template" | "style" | "script";

export interface Region {
  type: RegionType;
  languageId: string;
  content: string;
  start: number;
  end: number;
  parentUri: string;
}

export interface NexyProp {
  name: string;
  type: string;
  defaultValue?: string;
}

export interface NexyImport {
  path: string;
  name: string;
  framework: NexyFramework;
}

export interface NexyDoc {
  uri: string;
  text: string;
  version: number;
  header: string;
  template: string;
  regions: Region[];
  imports: NexyImport[];
  props: NexyProp[];
}

export interface MdxMapping {
  element: string;
  symbol: string;
  source: string;
}

export interface ComponentInfo {
  name: string;
  filePath: string;
  framework: NexyFramework;
  props: NexyProp[];
  uri: string;
}

export interface ProjectIndex {
  rootUri: string;
  components: Map<string, ComponentInfo>;
  files: Map<string, NexyDoc>;
  aliases: Record<string, string>;
}

export interface JinjaExpression {
  type: "expression" | "block" | "comment";
  content: string;
  start: number;
  end: number;
}

export interface DiagnosticResult {
  message: string;
  startLine: number;
  startChar: number;
  endLine: number;
  endChar: number;
  severity: "error" | "warning" | "information" | "hint";
}

export function frameworkFromExt(path: string): NexyFramework {
  if (path.endsWith(".vue")) return "vue";
  if (path.endsWith(".nexy") || path.endsWith(".mdx")) return "nexy";
  if (path.endsWith(".tsx") || path.endsWith(".jsx")) return "react";
  if (path.endsWith(".svelte")) return "svelte";
  if (path.endsWith(".solid")) return "solid";
  if (path.endsWith(".preact")) return "preact";
  return "unknown";
}

export const ROUTE_FILE_EXTS = [".nexy", ".mdx", ".vue", ".tsx", ".jsx", ".svelte", ".solid", ".preact", ".py"];

export const JINJA_FILTERS = new Set([
  "abs", "attr", "batch", "capitalize", "center", "count", "default", "dictsort",
  "escape", "filesizeformat", "first", "float", "forceescape", "format", "groupby",
  "indent", "int", "items", "join", "last", "length", "list", "lower", "map", "max",
  "min", "pprint", "random", "reject", "rejectattr", "replace", "reverse", "round",
  "safe", "select", "selectattr", "slice", "sort", "string", "striptags", "sum",
  "title", "tojson", "trim", "truncate", "unique", "upper", "urlencode", "urlize",
  "wordcount", "wordwrap",
]);

export const JINJA_KEYWORDS = new Set([
  "if", "elif", "else", "endif", "for", "endfor", "in", "block", "endblock",
  "extends", "include", "macro", "endmacro", "set", "with", "endwith", "raw",
  "endraw", "import", "from", "as", "not", "and", "or", "is", "true", "false",
  "none", "call", "endcall", "filter", "endfilter", "scoped", "recursive",
]);

export const PYTHON_KEYWORDS = new Set([
  "False", "None", "True", "and", "as", "assert", "async", "await", "break",
  "class", "continue", "def", "del", "elif", "else", "except", "finally", "for",
  "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "not", "or",
  "pass", "raise", "return", "try", "while", "with", "yield", "prop",
]);

export const PYTHON_BUILTINS = new Set([
  "abs", "all", "any", "bool", "callable", "dict", "enumerate", "float", "int",
  "len", "list", "max", "min", "print", "range", "set", "str", "sum", "tuple", "zip",
]);
