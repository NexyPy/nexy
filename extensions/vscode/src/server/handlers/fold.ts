import { FoldingRange, FoldingRangeKind } from "vscode-languageserver";
import { TextDocument } from "vscode-languageserver-textdocument";

export class FoldHandler {
  handle(doc: TextDocument): FoldingRange[] {
    const text = doc.getText();
    const ranges: FoldingRange[] = [];

    this.addHeaderFolding(text, ranges);
    this.addJinjaBlockFolding(text, ranges);
    this.addStyleFolding(text, ranges);
    this.addScriptFolding(text, ranges);
    this.addHtmlTagFolding(text, ranges);

    return ranges;
  }

  private addHeaderFolding(text: string, ranges: FoldingRange[]): void {
    const m = text.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?=\r?\n|$)/m);
    if (!m || m.index === undefined) return;
    const lines = text.slice(0, m.index).split("\n").length - 1;
    const endLine = lines + m[0].split("\n").length - 1;
    ranges.push({
      startLine: lines,
      endLine,
      kind: FoldingRangeKind.Region,
    });
  }

  private addJinjaBlockFolding(text: string, ranges: FoldingRange[]): void {
    const lines = text.split("\n");
    const stack: { keyword: string; startLine: number }[] = [];
    const CLOSE_MAP: Record<string, string> = {
      if: "endif", for: "endfor", block: "endblock",
      macro: "endmacro", call: "endcall", filter: "endfilter",
      with: "endwith", raw: "endraw",
    };

    for (let i = 0; i < lines.length; i++) {
      const openM = lines[i].match(/\{%[-]?\s*(if|for|block|macro|call|filter|with|raw)\b/);
      if (openM) {
        stack.push({ keyword: openM[1], startLine: i });
        continue;
      }
      const closeM = lines[i].match(/\{%[-]?\s*(endif|endfor|endblock|endmacro|endcall|endfilter|endwith|endraw)\b/);
      if (closeM && stack.length > 0) {
        const open = stack.pop()!;
        const expected = CLOSE_MAP[open.keyword];
        if (closeM[1] === expected && open.startLine < i) {
          ranges.push({
            startLine: open.startLine,
            endLine: i,
            kind: FoldingRangeKind.Region,
          });
        }
      }
    }
  }

  private addStyleFolding(text: string, ranges: FoldingRange[]): void {
    const re = /<style[\s\S]*?>/g;
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      const closeIdx = text.indexOf("</style>", m.index);
      if (closeIdx === -1) continue;
      ranges.push({
        startLine: text.slice(0, m.index).split("\n").length - 1,
        endLine: text.slice(0, closeIdx + 8).split("\n").length - 1,
        kind: FoldingRangeKind.Region,
      });
    }
  }

  private addScriptFolding(text: string, ranges: FoldingRange[]): void {
    const re = /<script[\s\S]*?>/g;
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      const closeIdx = text.indexOf("</script>", m.index);
      if (closeIdx === -1) continue;
      ranges.push({
        startLine: text.slice(0, m.index).split("\n").length - 1,
        endLine: text.slice(0, closeIdx + 9).split("\n").length - 1,
        kind: FoldingRangeKind.Region,
      });
    }
  }

  private addHtmlTagFolding(text: string, ranges: FoldingRange[]): void {
    const lines = text.split("\n");
    const stack: { tag: string; startLine: number }[] = [];
    const VOID_TAGS = new Set([
      "area","base","br","col","embed","hr","img","input",
      "keygen","link","menuitem","meta","param","source","track","wbr",
    ]);
    const SKIP_TAGS = new Set(["style", "script"]);

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      const openRe = /<([A-Za-z][A-Za-z0-9_]*)([^>]*)>/g;
      let m: RegExpExecArray | null;
      while ((m = openRe.exec(line)) !== null) {
        const tag = m[1].toLowerCase();
        const attrs = m[2];
        if (attrs.trim().endsWith("/")) continue;
        if (VOID_TAGS.has(tag)) continue;
        if (SKIP_TAGS.has(tag)) continue;
        stack.push({ tag, startLine: i });
      }

      const closeRe = /<\/([A-Za-z][A-Za-z0-9_]*)\s*>/g;
      while ((m = closeRe.exec(line)) !== null) {
        const tag = m[1].toLowerCase();
        if (SKIP_TAGS.has(tag)) continue;
        for (let j = stack.length - 1; j >= 0; j--) {
          if (stack[j].tag === tag && stack[j].startLine < i) {
            ranges.push({
              startLine: stack[j].startLine,
              endLine: i,
              kind: FoldingRangeKind.Region,
            });
            stack.splice(j, 1);
            break;
          }
        }
      }
    }
  }
}