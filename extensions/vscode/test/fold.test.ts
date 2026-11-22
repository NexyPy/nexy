import { describe, it, expect } from "vitest";
import { TextDocument } from "vscode-languageserver-textdocument";
import { FoldHandler } from "../src/server/handlers/fold";

function blockLines(text: string): [number, number][] {
  const doc = TextDocument.create("file:///page.nexy", "nexy", 1, text);
  return new FoldHandler().handle(doc).map(range => [range.startLine, range.endLine]);
}

describe("folding a script or style block", () => {
  it("folds a script block from its opening line to its closing line", () => {
    expect(blockLines("<script>\nlet a = 1;\n</script>\n")).toContainEqual([0, 2]);
  });

  it("folds a style block from its opening line to its closing line", () => {
    expect(blockLines("<style>\nh1 { color: red; }\n</style>\n")).toContainEqual([0, 2]);
  });
});
