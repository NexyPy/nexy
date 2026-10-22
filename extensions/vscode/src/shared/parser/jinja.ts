import { JinjaExpression, JINJA_FILTERS, JINJA_KEYWORDS } from "../types";

const EXPR_RE = /\{\{(?<expr>[\s\S]*?)\}\}/g;
const BLOCK_RE = /\{%[-]?(?<block>[\s\S]*?)[-]?%\}/g;
const COMMENT_RE = /\{#(?<comment>[\s\S]*?)#\}/g;

export function extractJinjaExpressions(template: string): JinjaExpression[] {
  const results: JinjaExpression[] = [];

  let m: RegExpExecArray | null;
  while ((m = EXPR_RE.exec(template)) !== null) {
    results.push({
      type: "expression",
      content: m.groups!.expr.trim(),
      start: m.index,
      end: m.index + m[0].length,
    });
  }

  while ((m = BLOCK_RE.exec(template)) !== null) {
    results.push({
      type: "block",
      content: m.groups!.block.trim(),
      start: m.index,
      end: m.index + m[0].length,
    });
  }

  while ((m = COMMENT_RE.exec(template)) !== null) {
    results.push({
      type: "comment",
      content: m.groups!.comment.trim(),
      start: m.index,
      end: m.index + m[0].length,
    });
  }

  results.sort((a, b) => a.start - b.start);
  return results;
}

export function stripJinja(template: string): { clean: string; map: { original: number; replacement: number; length: number }[] } {
  const expressions = extractJinjaExpressions(template);
  const map: { original: number; replacement: number; length: number }[] = [];
  let result = template;
  let offset = 0;

  for (const expr of expressions) {
    if (expr.type === "comment") {
      const placeholder = "";
      result = result.slice(0, expr.start + offset) + placeholder + result.slice(expr.end + offset);
      map.push({ original: expr.start, replacement: expr.start + offset, length: expr.end - expr.start });
      offset += placeholder.length - (expr.end - expr.start);
    }
  }

  return { clean: result, map };
}

export function extractVariables(expression: string): string[] {
  const vars: string[] = [];
  const parts = expression.split("|");
  const left = parts[0].trim();
  const nameMatch = left.match(/^[A-Za-z_][A-Za-z0-9_.]*/);
  if (nameMatch) vars.push(nameMatch[0]);
  return vars;
}

export function extractFilters(expression: string): string[] {
  const parts = expression.split("|");
  parts.shift();
  return parts
    .map((p) => p.trim().split(/\s+/)[0])
    .filter((f) => f.length > 0);
}

export function isValidJinjaFilter(name: string): boolean {
  return JINJA_FILTERS.has(name);
}

export function isJinjaKeyword(word: string): boolean {
  return JINJA_KEYWORDS.has(word);
}
