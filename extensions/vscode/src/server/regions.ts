import { TextDocument } from "vscode-languageserver-textdocument";
import { extractHeader } from "../shared/parser/header";
import { extractStyleTags, extractScriptTags } from "../shared/parser/template";
import { extractJinjaExpressions } from "../shared/parser/jinja";

export const PY_SCHEME = "nexy-embed-python";
export const HTML_SCHEME = "nexy-embed-html";
export const CSS_SCHEME = "nexy-embed-css";
export const JS_SCHEME = "nexy-embed-js";
export const TS_SCHEME = "nexy-embed-ts";

export interface VirtualRegion {
  languageId: string;
  scheme: string;
  uri: string;
  content: string;
  startOffset: number;
  endOffset: number;
}

/**
 * Parse a .nexy file and return virtual regions for each embedded language.
 * The Jinja2 template is split: HTML without Jinja2 goes to HTML service,
 * Jinja2 expressions are transformed to TypeScript template literals.
 */
export function parseRegions(sourceUri: string, text: string): VirtualRegion[] {
  const regions: VirtualRegion[] = [];

  // 1. Python header
  const header = extractHeader(text);
  if (header !== null) {
    const headerStart = text.indexOf(header);
    regions.push({
      languageId: "python",
      scheme: PY_SCHEME,
      uri: `${PY_SCHEME}://${sourceUri}.py`,
      content: header,
      startOffset: headerStart,
      endOffset: headerStart + header.length,
    });
  }

  // 2. Template: strip style/script tags first, then create HTML + JS regions
  const templateStart = text.indexOf(extractTemplatePart(text));
  if (templateStart === -1) return regions;

  // 2a. Style regions
  const styleTags = extractStyleTags(text);
  for (const tag of styleTags) {
    const langMap: Record<string, string> = {
      scss: "scss", sass: "sass", less: "less", postcss: "css", css: "css",
    };
    const lang = langMap[tag.lang] || "css";
    regions.push({
      languageId: lang,
      scheme: CSS_SCHEME,
      uri: `${CSS_SCHEME}://${sourceUri}.${lang}`,
      content: tag.content,
      startOffset: tag.start + text.slice(tag.start, tag.end).indexOf(tag.content),
      endOffset: tag.start + text.slice(tag.start, tag.end).indexOf(tag.content) + tag.content.length,
    });
  }

  // 2b. Script regions
  const scriptTags = extractScriptTags(text);
  for (const tag of scriptTags) {
    const langMap: Record<string, string> = {
      ts: "typescript", tsx: "typescriptreact", jsx: "javascriptreact",
      rust: "rust", javascript: "javascript",
    };
    const lang = langMap[tag.lang] || "javascript";
    regions.push({
      languageId: lang,
      scheme: JS_SCHEME,
      uri: `${JS_SCHEME}://${sourceUri}.${tag.lang}`,
      content: tag.content,
      startOffset: tag.start + text.slice(tag.start, tag.end).indexOf(tag.content),
      endOffset: tag.start + text.slice(tag.start, tag.end).indexOf(tag.content) + tag.content.length,
    });
  }

  // 2c. HTML template (with Jinja2 stripped)
  const cleanHtml = stripJinjaForHtml(text);
  regions.push({
    languageId: "html",
    scheme: HTML_SCHEME,
    uri: `${HTML_SCHEME}://${sourceUri}.html`,
    content: cleanHtml,
    startOffset: templateStart,
    endOffset: text.length,
  });

  // 2d. Jinja2 → TypeScript virtual doc
  const tsContent = jinjaToTypescript(text);
  if (tsContent) {
    regions.push({
      languageId: "typescript",
      scheme: TS_SCHEME,
      uri: `${TS_SCHEME}://${sourceUri}.jinja.ts`,
      content: tsContent,
      startOffset: templateStart,
      endOffset: text.length,
    });
  }

  return regions;
}

/**
 * Strip Jinja2 expressions/blocks from HTML for clean delegation to HTML Language Service.
 * {{ expr }} → ___NXY0___, {% block %} → empty string, {# comment #} → empty string.
 */
function stripJinjaForHtml(text: string): string {
  const templateMatch = text.match(/^[ \t]*---[ \t]*\r?\n[\s\S]*?\r?\n[ \t]*---[ \t]*(?:\r?\n|$)(?<template>[\s\S]*)/);
  const tpl = templateMatch?.groups?.template ?? text;

  let result = tpl;
  const expressions = extractJinjaExpressions(tpl);

  // Strip from right to left to keep offsets valid
  for (let i = expressions.length - 1; i >= 0; i--) {
    const expr = expressions[i];
    const placeholder = expr.type === "comment" ? "" : " ";
    result = result.slice(0, expr.start) + placeholder + result.slice(expr.end);
  }

  return result;
}

/**
 * Transform Jinja2 expressions into TypeScript template literal expressions.
 * {{ title|upper }} → ${__jinja(title).upper()}
 * This allows the TypeScript language service to provide completions.
 */
function jinjaToTypescript(text: string): string {
  const templateMatch = text.match(/^[ \t]*---[ \t]*\r?\n[\s\S]*?\r?\n[ \t]*---[ \t]*(?:\r?\n|$)(?<template>[\s\S]*)/);
  const tpl = templateMatch?.groups?.template ?? text;
  if (!tpl.trim()) return "";

  const expressions = extractJinjaExpressions(tpl);
  if (expressions.length === 0) return "";

  let result = "// Virtual Jinja2 → TypeScript\n";
  result += "// Provides IntelliSense for {{ }} expressions\n\n";
  result += "declare function __jinja(val: any): any;\n\n";
  result += "const __tpl = `";

  let lastIdx = 0;
  for (const expr of expressions) {
    if (expr.type !== "expression") continue;
    // Text before this expression
    result += tpl.slice(lastIdx, expr.start);
    // Transform expression: title|upper → ${__jinja(title).upper()}
    const tsExpr = transformJinjaToTS(expr.content);
    result += `\${${tsExpr}}`;
    lastIdx = expr.end;
  }

  result += tpl.slice(lastIdx);
  result += "`;\n";
  result += "export default __tpl;\n";

  return result;
}

function transformJinjaToTS(expr: string): string {
  const parts = expr.split("|").map((p) => p.trim());
  const base = parts[0];

  // Wrap base in __jinja() to tell TS this is a dynamic value
  let result = `__jinja(${base})`;

  for (let i = 1; i < parts.length; i++) {
    const filterParts = parts[i].split(/\s+/);
    const filterName = filterParts[0];
    const args = filterParts.slice(1).join(", ");
    if (args) {
      result = `${filterName}(${result}, ${args})`;
    } else {
      result = `${filterName}(${result})`;
    }
  }

  return result;
}

function extractTemplatePart(text: string): string {
  const m = text.match(/^[ \t]*---[ \t]*\r?\n[\s\S]*?\r?\n[ \t]*---[ \t]*(?:\r?\n|$)(?<template>[\s\S]*)/);
  return m?.groups?.template ?? text;
}
