import {
  CodeAction,
  CodeActionKind,
  CodeActionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import { findWorkspaceRoot, parseNexyConfig, resolvePythonModulePath } from "../../shared/nexy.config.parser";
import * as path from "path";
import * as fs from "fs";
import { fileURLToPath } from "url";

const IMPORT_EXTS = [".nexy", ".py", ".mdx", ".tsx", ".jsx", ".vue", ".svelte"];

function findRealFile(componentsDir: string, componentName: string): string | null {
  if (!fs.existsSync(componentsDir)) return null;
  let files: string[];
  try {
    files = fs.readdirSync(componentsDir);
  } catch {
    return null;
  }
  // 1. Exact case match first
  for (const ext of IMPORT_EXTS) {
    const target = componentName + ext;
    if (files.includes(target)) return path.join(componentsDir, target);
  }
  // 2. Case-insensitive fallback on Windows
  if (process.platform === "win32") {
    for (const ext of IMPORT_EXTS) {
      const target = (componentName + ext).toLowerCase();
      const found = files.find((f) => f.toLowerCase() === target);
      if (found) return path.join(componentsDir, found);
    }
  }
  // 3. Walk subdirectories recursively
  for (const entry of files) {
    const full = path.join(componentsDir, entry);
    if (fs.statSync(full).isDirectory()) {
      const nested = findRealFile(full, componentName);
      if (nested) return nested;
    }
  }
  return null;
}

export class CodeActionHandler {
  public handle(params: CodeActionParams, doc: TextDocument): CodeAction[] {
    const text = doc.getText();
    const actions: CodeAction[] = [];

    for (const diagnostic of params.context.diagnostics) {
      if (diagnostic.source !== "nexy" || !diagnostic.code) continue;

      if (diagnostic.code === "nexy.missingImport") {
        actions.push(...this.getMissingImportActions(doc, text, diagnostic));
      } else if (diagnostic.code === "nexy.unusedImport" || diagnostic.code === "nexy.unusedProp") {
        actions.push(this.getRemoveUnusedAction(doc, text, diagnostic));
      }
    }
    return actions;
  }

  private getMissingImportActions(doc: TextDocument, text: string, diagnostic: any): CodeAction[] {
    const componentName = text.slice(doc.offsetAt(diagnostic.range.start), doc.offsetAt(diagnostic.range.end));
    const headerMatch = text.match(/^---\s*$/m);
    if (!headerMatch || headerMatch.index === undefined) return [];

    const insertPosition = doc.positionAt(text.indexOf("\n", headerMatch.index) + 1);
    
    let importPath = `./components/${componentName}.nexy`;
    try {
      const currentFilePath = fileURLToPath(doc.uri);
      const currentDir = path.dirname(currentFilePath);
      
      const workspaceRoot = findWorkspaceRoot(currentDir) ?? currentDir;

      const config = parseNexyConfig(workspaceRoot);
      const componentsDir = path.join(workspaceRoot, "src", "components");
      let realFile = findRealFile(componentsDir, componentName);

      // Fallback: try Python module path resolution
      if (!realFile) {
        const pyResolved = resolvePythonModulePath(`src.components.${componentName}`, workspaceRoot);
        if (pyResolved) realFile = pyResolved;
      }

      if (realFile) {
        let usedAlias = false;
        for (const [alias, replacement] of Object.entries(config.useAliases)) {
          const aliasFullPath = path.resolve(workspaceRoot, replacement);
          if (realFile.startsWith(aliasFullPath)) {
            const relativeToAlias = path.relative(aliasFullPath, realFile).split(path.sep).join("/");
            importPath = `${alias}/${relativeToAlias}`;
            usedAlias = true;
            break;
          }
        }

        if (!usedAlias) {
          // Prefer Python-style module path for files under src/
          const srcDir = path.join(workspaceRoot, "src");
          if (realFile.startsWith(srcDir)) {
            const rel = path.relative(srcDir, realFile).split(path.sep).join("/");
            importPath = "src." + rel.replace(/\.[^.]+$/, "").replace(/\//g, ".");
          } else {
            const rel = path.relative(currentDir, realFile);
            importPath = (rel.startsWith(".") ? rel : `./${rel}`).split(path.sep).join("/");
          }
        }
      }
    } catch { /* ignore */ }

    const actions: CodeAction[] = [];
    actions.push({
      title: `Add import for "${componentName}" (${importPath})`,
      kind: CodeActionKind.QuickFix,
      diagnostics: [diagnostic],
      edit: {
        changes: {
          [doc.uri]: [{ range: { start: insertPosition, end: insertPosition }, newText: `from "${importPath}" import ${componentName}\n` }],
        },
      },
    });

    // If multiple extensions match, offer alternatives
    return actions;
  }

  private getRemoveUnusedAction(doc: TextDocument, text: string, diagnostic: any): CodeAction {
    const start = doc.offsetAt(diagnostic.range.start);
    const lineStart = text.lastIndexOf("\n", start - 1) + 1;
    let lineEnd = text.indexOf("\n", doc.offsetAt(diagnostic.range.end));
    lineEnd = lineEnd === -1 ? text.length : lineEnd + 1;

    return {
      title: diagnostic.code === "nexy.unusedImport" ? "Remove unused import" : "Remove unused prop",
      kind: CodeActionKind.QuickFix,
      diagnostics: [diagnostic],
      edit: { changes: { [doc.uri]: [{ range: { start: doc.positionAt(lineStart), end: doc.positionAt(lineEnd) }, newText: "" }] } }
    };
  }
}
