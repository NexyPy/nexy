import { Range, TextDocumentPositionParams, WorkspaceEdit } from "vscode-languageserver";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  extractHeader,
  extractTemplateWithOffset,
  parseHeader,
  findUsedComponents,
} from "../../shared/parser/header";
import { ProjectIndexer } from "../indexer";

type RenameKind = "prop" | "componentTag" | "htmlTag" | "attribute";

function classifyWord(
  word: string,
  text: string,
  offset: number,
  imports: string[],
  props: string[],
  usedComponents: string[],
): RenameKind | null {
  if (props.includes(word)) return "prop";
  if (imports.includes(word) || usedComponents.includes(word)) return "componentTag";
  // Check if word is an attribute (followed by =)
  let end = offset;
  while (end < text.length && /\w/.test(text[end])) end++;
  if (end < text.length) {
    const after = text.slice(end, Math.min(end + 50, text.length));
    if (/^\s*=/.test(after)) return "attribute";
  }
  // Otherwise treat as HTML tag if it looks like a tag name
  if (/^[a-z][a-z0-9-]*$/i.test(word)) return "htmlTag";
  return null;
}

export class RenameHandler {
  constructor(private indexer: ProjectIndexer) {}

  prepare(params: TextDocumentPositionParams, doc: TextDocument): { range: Range; word: string } | null {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const word = this.wordAt(text, offset);
    if (!word) return null;
    const wordRange = this.wordRangeAt(doc, offset);
    if (!wordRange) return null;

    const { imports, props } = parseHeader(text);
    const usedComponents = findUsedComponents(text);
    const importNames = imports.map((i) => i.name);
    const propNames = props.map((p) => p.name);
    const kind = classifyWord(word, text, offset, importNames, propNames, usedComponents);
    if (kind === null) return null;

    return { range: wordRange, word };
  }

  handle(params: TextDocumentPositionParams, doc: TextDocument, newName: string): WorkspaceEdit | null {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const word = this.wordAt(text, offset);
    if (!word) return null;

    const { imports, props } = parseHeader(text);
    const usedComponents = findUsedComponents(text);
    const importNames = imports.map((i) => i.name);
    const propNames = props.map((p) => p.name);
    const kind = classifyWord(word, text, offset, importNames, propNames, usedComponents);
    if (kind === null) return null;

    const changes: Record<string, { range: Range; newText: string }[]> = {};

    if (kind === "prop") {
      this.doRenameProp(changes, doc, text, word, newName);
    } else if (kind === "componentTag") {
      this.doRenameComponentTag(changes, doc, text, word, newName, imports);
    } else if (kind === "htmlTag") {
      this.doRenameHtmlTag(changes, doc, text, word, newName, offset);
    } else if (kind === "attribute") {
      this.doRenameAttribute(changes, doc, text, word, newName);
    }

    if (Object.keys(changes).length === 0) return null;
    return { changes };
  }

  private doRenameProp(
    changes: Record<string, { range: Range; newText: string }[]>,
    doc: TextDocument,
    text: string,
    word: string,
    newName: string,
  ): void {
    const header = extractHeader(text);
    if (!header) return;
    const headerStart = text.indexOf(header);
    if (headerStart !== -1) {
      const headerLines = header.split("\n");
      let headerOffset = headerStart;
      for (const line of headerLines) {
        const declRe = new RegExp(`^\\s*(${word})\\s*:`);
        const dm = declRe.exec(line);
        if (dm) {
          const absStart = headerOffset + dm.index + dm[0].indexOf(dm[1]);
          (changes[doc.uri] ??= []).push({
            range: this.rng(doc, absStart, absStart + word.length),
            newText: newName,
          });
        }
        headerOffset += line.length + 1;
      }
    }

    const currentTmpl = extractTemplateWithOffset(text);
    if (currentTmpl.offset !== -1) {
      const tokenRe = new RegExp(`(?<!\\w)${word}(?!\\w)`, "g");
      let m: RegExpExecArray | null;
      while ((m = tokenRe.exec(currentTmpl.content)) !== null) {
        const absStart = currentTmpl.offset + m.index;
        (changes[doc.uri] ??= []).push({
          range: this.rng(doc, absStart, absStart + word.length),
          newText: newName,
        });
      }
    }

    const thisUri = doc.uri;
    const consumers = this.indexer.findFilesImportingFrom(thisUri);
    for (const consumer of consumers) {
      const consumerDoc = TextDocument.create(consumer.uri, "nexy", 1, consumer.text);
      const consumerTmpl = extractTemplateWithOffset(consumer.text);
      if (consumerTmpl.offset === -1) continue;
      const tokenRe = new RegExp(`(?<!\\w)${word}(?!\\w)`, "g");
      let m: RegExpExecArray | null;
      while ((m = tokenRe.exec(consumerTmpl.content)) !== null) {
        const absStart = consumerTmpl.offset + m.index;
        (changes[consumer.uri] ??= []).push({
          range: this.rng(consumerDoc, absStart, absStart + word.length),
          newText: newName,
        });
      }
    }
  }

  private doRenameComponentTag(
    changes: Record<string, { range: Range; newText: string }[]>,
    doc: TextDocument,
    text: string,
    word: string,
    newName: string,
    imports: { name: string; path: string }[],
  ): void {
    // Rename in current file's template
    const currentTmpl = extractTemplateWithOffset(text);
    if (currentTmpl.offset !== -1) {
      const tagRe = new RegExp(`(<|</)${word}([^a-zA-Z])`, "g");
      let m: RegExpExecArray | null;
      while ((m = tagRe.exec(currentTmpl.content)) !== null) {
        const absStart = currentTmpl.offset + m.index + m[1].length;
        (changes[doc.uri] ??= []).push({
          range: this.rng(doc, absStart, absStart + word.length),
          newText: newName,
        });
      }
    }

    // Rename in header imports
    const header = extractHeader(text);
    if (header) {
      const headerStart = text.indexOf(header);
      if (headerStart !== -1) {
        const impRe = new RegExp(`(?:from\\s+"[^"]*"\\s+import\\s+.*?\\b)(${word})\\b`, "g");
        let m: RegExpExecArray | null;
        while ((m = impRe.exec(header)) !== null) {
          const absStart = headerStart + m.index + m[0].lastIndexOf(word);
          (changes[doc.uri] ??= []).push({
            range: this.rng(doc, absStart, absStart + word.length),
            newText: newName,
          });
        }
      }
    }

    // Cross-file: all consumers that use this component tag
    const thisUri = doc.uri;
    const consumers = this.indexer.findFilesImportingFrom(thisUri);
    for (const consumer of consumers) {
      const consumerDoc = TextDocument.create(consumer.uri, "nexy", 1, consumer.text);
      const consumerTmpl = extractTemplateWithOffset(consumer.text);
      if (consumerTmpl.offset === -1) continue;
      const tagRe = new RegExp(`(<|</)${word}([^a-zA-Z])`, "g");
      let m: RegExpExecArray | null;
      while ((m = tagRe.exec(consumerTmpl.content)) !== null) {
        const absStart = consumerTmpl.offset + m.index + m[1].length;
        (changes[consumer.uri] ??= []).push({
          range: this.rng(consumerDoc, absStart, absStart + word.length),
          newText: newName,
        });
      }
    }
  }

  private doRenameHtmlTag(
    changes: Record<string, { range: Range; newText: string }[]>,
    doc: TextDocument,
    text: string,
    word: string,
    newName: string,
    offset: number,
  ): void {
    const currentTmpl = extractTemplateWithOffset(text);
    if (currentTmpl.offset === -1) return;
    const relOffset = offset - currentTmpl.offset;
    if (relOffset < 0 || relOffset > currentTmpl.content.length) return;
    const pair = this.findHtmlTagPair(currentTmpl.content, word, relOffset);
    if (!pair) return;
    const openWordStart = currentTmpl.offset + pair.openStart + 1;
    (changes[doc.uri] ??= []).push({
      range: this.rng(doc, openWordStart, openWordStart + word.length),
      newText: newName,
    });
    const closeWordStart = currentTmpl.offset + pair.closeStart + 2;
    (changes[doc.uri] ??= []).push({
      range: this.rng(doc, closeWordStart, closeWordStart + word.length),
      newText: newName,
    });
  }

  private findHtmlTagPair(
    content: string,
    tag: string,
    relOffset: number,
  ): { openStart: number; closeStart: number } | null {
    const tagRe = new RegExp(`<(\/?)${tag}([^>]*?)>`, 'g');
    const matches: { isOpen: boolean; offset: number }[] = [];
    let m: RegExpExecArray | null;
    while ((m = tagRe.exec(content)) !== null) {
      const isClose = m[1] === '/';
      if (!isClose && m[2]?.trim()?.endsWith('/')) continue;
      matches.push({ isOpen: !isClose, offset: m.index });
    }
    const idx = matches.findIndex(match => {
      const nameStart = match.isOpen ? match.offset + 1 : match.offset + 2;
      const nameEnd = nameStart + tag.length;
      return relOffset >= nameStart && relOffset <= nameEnd;
    });
    if (idx === -1) return null;
    if (matches[idx].isOpen) {
      let depth = 0;
      for (let i = idx; i < matches.length; i++) {
        if (matches[i].isOpen) depth++;
        else depth--;
        if (depth === 0) return { openStart: matches[idx].offset, closeStart: matches[i].offset };
      }
    } else {
      let depth = 0;
      for (let i = idx; i >= 0; i--) {
        if (!matches[i].isOpen) depth++;
        else depth--;
        if (depth === 0) return { openStart: matches[i].offset, closeStart: matches[idx].offset };
      }
    }
    return null;
  }

  private doRenameAttribute(
    changes: Record<string, { range: Range; newText: string }[]>,
    doc: TextDocument,
    text: string,
    word: string,
    newName: string,
  ): void {
    const currentTmpl = extractTemplateWithOffset(text);
    if (currentTmpl.offset === -1) return;
    const attrRe = new RegExp(`\\b${word}(?=\\s*=)`, "g");
    let m: RegExpExecArray | null;
    while ((m = attrRe.exec(currentTmpl.content)) !== null) {
      const absStart = currentTmpl.offset + m.index;
      (changes[doc.uri] ??= []).push({
        range: this.rng(doc, absStart, absStart + word.length),
        newText: newName,
      });
    }
  }

  private wordAt(text: string, offset: number): string {
    let start = offset;
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /\w/.test(text[end])) end++;
    return text.slice(start, end);
  }

  private rng(doc: TextDocument, start: number, end: number): Range {
    return { start: doc.positionAt(start), end: doc.positionAt(end) };
  }

  private wordRangeAt(doc: TextDocument, offset: number): Range | null {
    const text = doc.getText();
    let start = offset;
    while (start > 0 && /\w/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /\w/.test(text[end])) end++;
    if (start === end) return null;
    return { start: doc.positionAt(start), end: doc.positionAt(end) };
  }
}
