import * as fs from "fs";
import * as path from "path";
import { fileURLToPath, pathToFileURL } from "url";
import {
  ComponentInfo,
  NexyDoc,
  NexyImport,
  NexyProp,
  ProjectIndex,
  frameworkFromExt,
  ROUTE_FILE_EXTS,
} from "../shared/types";
import { parseHeader } from "../shared/parser/header";
import { resolvePythonModulePath } from "../shared/nexy.config.parser";

export class ProjectIndexer {
  private index: ProjectIndex = {
    rootUri: "",
    components: new Map(),
    files: new Map(),
    aliases: {},
  };

  private disposed = false;

  initialize(rootUri: string): void {
    this.index.rootUri = rootUri;
    this.index.aliases = this.readAliases(rootUri);
    this.scanWorkspace(rootUri);
  }

  getIndex(): ProjectIndex {
    return this.index;
  }

  getComponent(name: string): ComponentInfo | undefined {
    return this.index.components.get(name);
  }

  getDoc(uri: string): NexyDoc | undefined {
    return this.index.files.get(uri);
  }

  /** Find all indexed files that import from a given source URI. */
  findFilesImportingFrom(sourceUri: string): { uri: string; text: string; imports: NexyImport[] }[] {
    const consumers: { uri: string; text: string; imports: NexyImport[] }[] = [];
    const normalizeUri = (u: string) => process.platform === "win32" ? u.toLowerCase() : u;
    const normSource = normalizeUri(sourceUri);
    for (const [uri, doc] of this.index.files) {
      if (normalizeUri(uri) === normSource) continue;
      for (const imp of doc.imports) {
        const resolved = this.resolveImportPath(imp, uri);
        if (resolved && normalizeUri(pathToFileURL(resolved).toString()) === normSource) {
          consumers.push({ uri, text: doc.text, imports: doc.imports });
          break;
        }
      }
    }
    return consumers;
  }

  updateDoc(uri: string, text: string, version: number): void {
    const doc = this.buildDoc(uri, text, version);
    this.index.files.set(uri, doc);
    this.indexDocComponents(doc);
  }

  removeDoc(uri: string): void {
    const doc = this.index.files.get(uri);
    if (doc) {
      for (const imp of doc.imports) {
        this.index.components.delete(imp.name);
      }
    }
    this.index.files.delete(uri);
  }

  resolveImportPath(imp: NexyImport, fromUri: string): string | null {
    const fromPath = fileURLToPath(fromUri);
    const fromDir = path.dirname(fromPath);

    // Alias resolution
    for (const [alias, replacement] of Object.entries(this.index.aliases)) {
      if (imp.path.startsWith(alias)) {
        const rel = imp.path.slice(alias.length).replace(/^\//, "");
        const resolved = path.resolve(this.index.rootUri, replacement, rel);
        return this.resolveWithExt(resolved);
      }
    }

    // Relative resolution
    if (imp.path.startsWith(".")) {
      const resolved = path.resolve(fromDir, imp.path);
      return this.resolveWithExt(resolved);
    }

    // Python module path: src.components.X → src/components/X
    const pyResolved = resolvePythonModulePath(imp.path, fileURLToPath(this.index.rootUri));
    if (pyResolved) return pyResolved;

    return null;
  }

  private resolveWithExt(basePath: string): string | null {
    for (const ext of ["", ...ROUTE_FILE_EXTS]) {
      const p = basePath + ext;
      if (fs.existsSync(p)) return p;
    }
    return null;
  }

  private readAliases(rootUri: string): Record<string, string> {
    const configPath = path.join(rootUri, "nexyconfig.py");
    if (!fs.existsSync(configPath)) return {};

    try {
      const content = fs.readFileSync(configPath, "utf8");
      const m = content.match(/useAliases\s*(?::[^=]+)?\s*=\s*({[\s\S]*?})/);
      if (!m) return {};
      const json = m[1].replace(/'/g, '"').replace(/#.*$/gm, "").replace(/,\s*}/g, "}");
      return JSON.parse(json);
    } catch {
      return {};
    }
  }

  private scanWorkspace(rootUri: string): void {
    if (!fs.existsSync(rootUri)) return;
    const walkDir = (dir: string): void => {
      let entries: fs.Dirent[];
      try {
        entries = fs.readdirSync(dir, { withFileTypes: true });
      } catch {
        return;
      }
      for (const entry of entries) {
        if (entry.name.startsWith(".") || entry.name === "node_modules" || entry.name === "__pycache__" || entry.name === "__nexy__") continue;
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walkDir(full);
        else if (ROUTE_FILE_EXTS.includes(path.extname(entry.name).toLowerCase())) {
          const uri = pathToFileURL(full).toString();
          try {
            const text = fs.readFileSync(full, "utf8");
            const doc = this.buildDoc(uri, text, 1);
            this.index.files.set(uri, doc);
            this.indexDocComponents(doc);
          } catch {
            // skip unreadable files
          }
        }
      }
    };
    walkDir(rootUri);
  }

  private buildDoc(uri: string, text: string, version: number): NexyDoc {
    const { imports, props } = parseHeader(text);
    const template = this.extractTemplate(text);
    return { uri, text, version, header: "", template, regions: [], imports, props };
  }

  private extractTemplate(text: string): string {
    const m = text.match(/^\s*---\s*(?:[\s\S]*?)\s*---\s*(?<template>.*)/s);
    return m?.groups?.template?.trim() ?? text.trim();
  }

  private indexDocComponents(doc: NexyDoc): void {
    const template = this.extractTemplate(doc.text);
    const used = [...template.matchAll(/<([A-Z][A-Za-z0-9_]*)/g)].map((m) => m[1]);

    for (const imp of doc.imports) {
      if (this.index.components.has(imp.name)) continue;
      if (!used.includes(imp.name)) continue;

      const resolvedPath = this.resolveImportPath(imp, doc.uri);
      let props: NexyProp[] = imp.framework === "nexy" && resolvedPath
        ? this.readComponentProps(resolvedPath)
        : [];

      this.index.components.set(imp.name, {
        name: imp.name,
        filePath: resolvedPath ?? imp.path,
        framework: imp.framework,
        props,
        uri: resolvedPath ? pathToFileURL(resolvedPath).toString() : doc.uri,
      });
    }
  }

  private readComponentProps(filePath: string): NexyProp[] {
    try {
      const text = fs.readFileSync(filePath, "utf8");
      return parseHeader(text).props;
    } catch {
      return [];
    }
  }

  dispose(): void {
    this.disposed = true;
    this.index.components.clear();
    this.index.files.clear();
  }
}
