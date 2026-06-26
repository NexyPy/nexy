import * as vscode from "vscode";

/**
 * Strip Jinja2 from a string, replacing inline expressions with a single space
 * and removing block-level syntax entirely. This lets CSS/JS/HTML language services
 * see clean code without {{ }} / {% %} / {# #} noise.
 */
function stripJinja2(text: string): string {
  // Block-level: {% %} and {# #} → remove entirely (they span lines)
  let result = text
    .replace(/\{%[\s\S]*?%\}/g, '')
    .replace(/\{#[\s\S]*?#\}/g, '');
  // Inline: {{ }} → single space (preserves general structure)
  result = result.replace(/\{\{[\s\S]*?\}\}/g, ' ');
  return result;
}
import { getTemplate } from "../../shared/nexy.parser";

export const PY_SCHEME = "nexy-embed-python";
export const HTML_SCHEME = "nexy-embed-html";
export const CSS_SCHEME = "nexy-embed-css";
export const JS_SCHEME = "nexy-embed-js";

export class EmbedContentProvider implements vscode.TextDocumentContentProvider {
  private _onDidChange = new vscode.EventEmitter<vscode.Uri>();
  onDidChange = this._onDidChange.event;
  private store = new Map<string, string>();

  public set(uri: vscode.Uri, content: string) {
    this.store.set(uri.toString(), content);
    this._onDidChange.fire(uri);
  }

  public provideTextDocumentContent(uri: vscode.Uri): string {
    return this.store.get(uri.toString()) ?? "";
  }
}

export interface RegionInfo {
  languageId: string;
  scheme: string;
  content: string;
  start: number;
  end: number;
}

/**
 * Transform a Nexy header into valid Python for Pylance.
 * - Lines with `from "..." import ...` are replaced with spaces
 *   (invalid Python syntax otherwise — Nexy-specific import sugar).
 * - All other lines are kept as-is for full Pylance analysis.
 * Character positions are preserved so diagnostic remapping stays correct.
 */
function sanitizeHeaderForPython(header: string): string {
  return header
    .split('\n')
    .map(line => {
      // Quoted imports (from "...") are invalid Python — replace with spaces
      if (/^\s*from\s+["']/.test(line)) {
        return ' '.repeat(line.length);
      }
      // Python-native imports (from module import ...) are valid Python —
      // keep them so Pylance can resolve and provide completions.
      return line;
    })
    .join('\n');
}

export function getDocumentRegions(document: vscode.TextDocument): RegionInfo[] {
  const fullText = document.getText();
  const regions: RegionInfo[] = [];

  // Header Python
  const headerMatch = fullText.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?=\r?\n|$)/m);
  if (headerMatch && headerMatch.index !== undefined) {
    const start = headerMatch.index + headerMatch[0].indexOf("\n") + 1;
    const content = sanitizeHeaderForPython(headerMatch[1]);
    regions.push({ languageId: "python", scheme: PY_SCHEME, content, start, end: start + content.length });
  }

  // Template HTML/Markdown
  const tmplText = getTemplate(fullText);
  const templateStart = fullText.indexOf(tmplText);
  if (templateStart !== -1) {
    const styleRegex = /<style\b(?:\s+lang\s*=\s*["'](?<lang>scss|sass|less|postcss)["'])?[^>]*>(?<content>[\s\S]*?)<\/style>/gi;
    const scriptRegex = /<script\b(?:\s+lang\s*=\s*["'](?<lang>ts|tsx|jsx|rust)["'])?[^>]*>(?<content>[\s\S]*?)<\/script>/gi;

    let m: RegExpExecArray | null;
    while ((m = styleRegex.exec(tmplText)) !== null) {
      const lang = m.groups?.lang || "css";
      const rawContent = m.groups?.content || "";
      const content = stripJinja2(rawContent);
      const contentStart = m.index + m[0].indexOf(rawContent);
      regions.push({
        languageId: lang === "scss" ? "scss" : lang === "sass" ? "sass" : lang === "less" ? "less" : "css",
        scheme: CSS_SCHEME,
        content: content,
        start: templateStart + contentStart,
        end: templateStart + contentStart + content.length,
      });
    }

    while ((m = scriptRegex.exec(tmplText)) !== null) {
      const lang = m.groups?.lang || "javascript";
      const rawContent = m.groups?.content || "";
      const content = stripJinja2(rawContent);
      const contentStart = m.index + m[0].indexOf(rawContent);
      regions.push({
        languageId: lang === "ts" ? "typescript" : lang === "tsx" ? "typescriptreact" : lang === "jsx" ? "javascriptreact" : lang === "rust" ? "rust" : "javascript",
        scheme: JS_SCHEME,
        content: content,
        start: templateStart + contentStart,
        end: templateStart + contentStart + content.length,
      });
    }

    // Le reste est considéré comme HTML ou Markdown — strip Jinja2 for clean delegation
    const languageId = document.languageId === "mdx" ? "markdown" : "html";
    regions.push({
      languageId: languageId,
      scheme: HTML_SCHEME,
      content: stripJinja2(tmplText),
      start: templateStart,
      end: templateStart + tmplText.length,
    });

    // Delegation MDX pour le Markdown pur
    if (document.languageId === "mdx") {
       regions.push({
         languageId: "markdown",
         scheme: "nexy-mdx-markdown",
         content: tmplText,
         start: templateStart,
         end: templateStart + tmplText.length
       });
    }
  }

  return regions;
}

export function getRegionAtPosition(document: vscode.TextDocument, position: vscode.Position): RegionInfo | undefined {
  const offset = document.offsetAt(position);
  const regions = getDocumentRegions(document);
  return regions
    .filter(r => offset >= r.start && offset <= r.end)
    .sort((a, b) => (a.end - a.start) - (b.end - b.start))[0];
}
