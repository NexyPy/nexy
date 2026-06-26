import { Location, Range, TextDocumentPositionParams } from "vscode-languageserver";
import { TextDocument } from "vscode-languageserver-textdocument";
import { ProjectIndexer } from "../indexer";
import { extractHeader, extractTemplate } from "../../shared/parser/header";
import { extractJinjaExpressions } from "../../shared/parser/jinja";

export class ReferenceHandler {
  constructor(private indexer: ProjectIndexer) {}

  handle(params: TextDocumentPositionParams, doc: TextDocument): Location[] {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const word = this.wordAtOffset(text, offset);
    if (!word) return [];

    const locations: Location[] = [];
    const { imports, props } = this.parseHeader(text);
    const isProp = props.some((p) => p.name === word);
    const isImport = imports.some((i) => i.name === word);

    if (!isProp && !isImport) return [];

    const template = extractTemplate(text);
    const templateOffset = text.indexOf(template);
    if (templateOffset === -1) return locations;

    const re = new RegExp(`\\b${word}\\b`, "g");
    let m: RegExpExecArray | null;

    while ((m = re.exec(template)) !== null) {
      const absStart = templateOffset + m.index;
      locations.push({
        uri: doc.uri,
        range: this.rng(doc, absStart, absStart + word.length),
      });
    }

    return locations;
  }

  private wordAtOffset(text: string, offset: number): string {
    let start = offset;
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /\w/.test(text[end])) end++;
    return text.slice(start, end);
  }

  private parseHeader(text: string): { imports: { name: string }[]; props: { name: string }[] } {
    const header = extractHeader(text);
    if (!header) return { imports: [], props: [] };
    const imports: { name: string }[] = [];
    const props: { name: string }[] = [];

    const fromRe = /^\s*from\s+["']([^"']+)["']\s+import\s+(.+?)(?=\r?\n\S|$)/gms;
    let m: RegExpExecArray | null;
    while ((m = fromRe.exec(header)) !== null) {
      for (const raw of m[2].split(",")) {
        imports.push({ name: raw.trim().split(/\s+as\s+/i).pop() || raw.trim() });
      }
    }

    const propRe = /^([A-Za-z_]\w*)\s*:\s*prop/gm;
    while ((m = propRe.exec(header)) !== null) {
      props.push({ name: m[1] });
    }

    return { imports, props };
  }

  private rng(doc: TextDocument, start: number, end: number): Range {
    return { start: doc.positionAt(start), end: doc.positionAt(end) };
  }
}
