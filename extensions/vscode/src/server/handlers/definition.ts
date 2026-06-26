import {
  Definition,
  Location,
  Range,
  TextDocumentPositionParams,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  findUsedComponents,
  NEXY_BUILTIN_COMPONENTS,
} from "../../shared/parser/header";
import { NexyImport, NexyProp } from "../../shared/types";
import { findWorkspaceRoot, parseNexyConfig, resolvePythonModulePath, resolveWithAlias } from "../../shared/nexy.config.parser";
import * as fs from "fs";
import { fileURLToPath, pathToFileURL } from "url";
import * as path from "path";

export class DefinitionHandler {
  public handle(params: TextDocumentPositionParams, doc: TextDocument): Definition | null {
    const text = doc.getText();
    const offset = doc.offsetAt(params.position);
    const { imports, props } = parseHeader(text);

    let start = offset;
    while (start > 0 && /[\w./-]/.test(text[start - 1])) start--;
    let end = offset;
    while (end < text.length && /[\w./-]/.test(text[end])) end++;
    const word = text.slice(start, end);

    // 1. Check if it's an imported component (header or template usage)
    const imp = imports.find(i => i.name === word);
    if (imp) {
      return this.getComponentDefinition(doc, imp);
    }

    // 1b. Check if it's a component tag used in template but not in imports
    // Look up the first import that matches the component path
    const usedComponents = findUsedComponents(text);
    if (usedComponents.includes(word) && !NEXY_BUILTIN_COMPONENTS.has(word)) {
      // Try to find import by path inference
      const impPath = imports.find(i => {
        const base = path.basename(i.path, path.extname(i.path));
        return base === word || i.name === word;
      });
      if (impPath) {
        return this.getComponentDefinition(doc, impPath);
      }
      // Fallback: try resolving as a relative file in the same directory
      const docDir = path.dirname(fileURLToPath(doc.uri));
      const candidates = [`.nexy`, `.tsx`, `.jsx`, `.vue`, `.svelte`];
      for (const ext of candidates) {
        const fp = path.join(docDir, word + ext);
        if (fs.existsSync(fp)) {
          return Location.create(pathToFileURL(fp).toString(), Range.create(0, 0, 0, 0));
        }
      }
    }

    // 2. Check if it's a prop defined in header
    const prop = props.find(p => p.name === word);
    if (prop) {
      const propRegex = new RegExp(`^\\s*${prop.name}\\s*:`, "m");
      const match = text.match(propRegex);
      if (match && match.index !== undefined) {
        const pos = doc.positionAt(match.index);
        return Location.create(doc.uri, Range.create(pos, pos));
      }
    }

    // 3. Check if it's a path in a "from" statement
    const lineStart = text.lastIndexOf("\n", offset - 1) + 1;
    const lineEnd = text.indexOf("\n", offset);
    const lineText = text.slice(lineStart, lineEnd === -1 ? text.length : lineEnd);
    const pathMatch = lineText.match(/from\s+["']([^"']+)["']/);
    if (pathMatch && (word.includes("/") || word.includes("."))) {
       return this.getPathDefinition(doc, pathMatch[1]);
    }

    return null;
  }

  private resolvePath(impPath: string, currentDir: string, symbolName?: string): string | null {
    const workspaceRoot = findWorkspaceRoot(currentDir) ?? currentDir;

    const config = parseNexyConfig(workspaceRoot);
    const aliasResolved = resolveWithAlias(impPath, workspaceRoot, config.useAliases);
    let finalPath = aliasResolved || path.resolve(currentDir, impPath);

    if (fs.existsSync(finalPath)) return finalPath;

    // Fallback: @/ → src/
    if (impPath.startsWith("@") && workspaceRoot !== currentDir) {
      const srcPath = path.join(workspaceRoot, "src", impPath.slice(2));
      if (fs.existsSync(srcPath)) return srcPath;
    }

    // Try with extensions
    const exts = [".nexy", ".mdx", ".tsx", ".jsx", ".vue", ".svelte", ".py"];
    for (const ext of exts) {
      const withExt = finalPath + ext;
      if (fs.existsSync(withExt)) return withExt;
    }

    // Python module path: src.components.X → src/components/X
    const pyResolved = resolvePythonModulePath(impPath, workspaceRoot);
    if (pyResolved) return pyResolved;

    // Python package import (e.g. from nexy import Vite) — look in site-packages
    if (!impPath.startsWith(".") && !impPath.startsWith("@") && !impPath.startsWith("/") && !impPath.includes("/")) {
      const sitePkg = this.resolvePythonPackage(impPath, workspaceRoot, symbolName);
      if (sitePkg) return sitePkg;
    }

    return null;
  }

  private resolvePythonPackage(pkgName: string, workspaceRoot: string, symbolName?: string): string | null {
    const findPkgDir = (): string | null => {
      const checkDir = (d: string): string | null =>
        fs.existsSync(d) && fs.statSync(d).isDirectory() ? d : null;

      // Windows .venv\Lib\site-packages\
      for (const v of [".venv", "venv"]) {
        const r = checkDir(path.join(workspaceRoot, v, "Lib", "site-packages", pkgName));
        if (r) return r;
      }

      // Unix .venv/lib/python3.X/site-packages/
      for (const v of [".venv", "venv"]) {
        const libDir = path.join(workspaceRoot, v, "lib");
        if (!fs.existsSync(libDir)) continue;
        try {
          for (const e of fs.readdirSync(libDir, { withFileTypes: true })) {
            if (!e.isDirectory() || !e.name.startsWith("python3")) continue;
            const r = checkDir(path.join(libDir, e.name, "site-packages", pkgName));
            if (r) return r;
          }
        } catch { /* ignore */ }
      }
      return null;
    };

    const pkgDir = findPkgDir();
    if (!pkgDir) return null;

    const initPy = path.join(pkgDir, "__init__.py");
    if (!symbolName || !fs.existsSync(initPy)) return initPy;

    // Follow the import chain: find where symbolName is imported from in __init__.py
    try {
      const initContent = fs.readFileSync(initPy, "utf8");
      const chainRe = new RegExp(
        `^\\s*from\\s+[".]*(?<mod>[A-Za-z_][\\w.]*)\\s+import\\s+.*\\b${escapeRegex(symbolName)}\\b`,
        "gm"
      );
      const chainMatch = chainRe.exec(initContent);
      if (chainMatch) {
        const modPath = chainMatch.groups!.mod;
        const resolved = path.resolve(pkgDir, ...modPath.split(".")) + ".py";
        if (fs.existsSync(resolved)) return resolved;
        // Try as package
        const pkgInit = path.join(path.resolve(pkgDir, ...modPath.split(".")), "__init__.py");
        if (fs.existsSync(pkgInit)) return pkgInit;
      }
    } catch { /* ignore */ }

    return initPy;
  }

  private getComponentDefinition(doc: TextDocument, imp: NexyImport): Definition | null {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    const finalPath = this.resolvePath(imp.path, currentDir, imp.name);
    if (finalPath) {
      return Location.create(pathToFileURL(finalPath).toString(), Range.create(0, 0, 0, 0));
    }

    // Fallback: package import (e.g. from nexy import Vite) — show the import line in header
    const text = doc.getText();
    const importRegex = new RegExp(`^.*\\b${imp.name}\\b.*$`, 'm');
    const match = importRegex.exec(text);
    if (match && match.index !== undefined) {
      const pos = doc.positionAt(match.index);
      return Location.create(doc.uri, Range.create(pos, pos));
    }

    return null;
  }

  private getPathDefinition(doc: TextDocument, filePath: string): Definition | null {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    const finalPath = this.resolvePath(filePath, currentDir);
    if (finalPath) {
      return Location.create(pathToFileURL(finalPath).toString(), Range.create(0, 0, 0, 0));
    }
    return null;
  }
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
