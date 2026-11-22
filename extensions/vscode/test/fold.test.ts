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

describe("folding a block written the other ways HTML allows (#615)", () => {
  it("ends a script block at a closing tag with a space", () => {
    expect(blockLines("<script>\nlet a = 1;\n</script >\n")).toContainEqual([0, 2]);
  });

  it("folds a script block written in capitals", () => {
    expect(blockLines("<SCRIPT>\nlet a = 1;\n</SCRIPT>\n")).toContainEqual([0, 2]);
  });

  it("does not open a block at a longer tag name", () => {
    expect(blockLines("<scripts>\n\n</script>\n")).not.toContainEqual([0, 2]);
  });
});

describe("folding a block closed with text before the bracket", () => {
  it("ends a script block at </script foo>, as a browser does", () => {
    expect(blockLines("<script>\nlet a = 1;\n</script foo>\n")).toContainEqual([0, 2]);
  });
});
