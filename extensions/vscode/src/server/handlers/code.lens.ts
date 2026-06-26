import { CodeLens, Range, CodeLensParams } from "vscode-languageserver";
import { TextDocument } from "vscode-languageserver-textdocument";

export class CodeLensHandler {
  handle(params: CodeLensParams, doc: TextDocument): CodeLens[] {
    const text = doc.getText();
    const lenses: CodeLens[] = [];

    // Show "N usages" lens on each prop declaration
    const propRe = /^([A-Za-z_]\w*)\s*:\s*prop/gm;
    let m: RegExpExecArray | null;
    while ((m = propRe.exec(text)) !== null) {
      const propName = m[1];
      const propPos = doc.positionAt(m.index + m[0].indexOf(propName));
      const template = this.getTemplate(text);
      const usageCount = template ? this.countUsages(template, propName) : 0;
      lenses.push({
        range: { start: propPos, end: propPos },
        command: {
          title: usageCount === 0 ? "0 usages" : `${usageCount} ${usageCount === 1 ? "usage" : "usages"}`,
          command: "",
        },
      });
    }

    return lenses;
  }

  private getTemplate(text: string): string | null {
    const m = text.match(/^\s*---\s*(?:[\s\S]*?)\s*---\s*(?<template>.*)/s);
    return m?.groups?.template?.trim() ?? null;
  }

  private countUsages(template: string, name: string): number {
    const re = new RegExp(`(?<![\\w.])${name}(?![\\w(])`, "g");
    const matches = template.match(re);
    return matches ? matches.length : 0;
  }
}