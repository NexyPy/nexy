import {
  Diagnostic,
  DiagnosticSeverity,
  Range,
  DiagnosticTag,
  DiagnosticRelatedInformation,
  Location,
} from "vscode-languageserver/node";
import { TextDocument } from "vscode-languageserver-textdocument";
import {
  parseHeader,
  getTemplate,
  findUsedComponentsInTemplate,
  type NexyImport,
  type NexyProp,
} from "../../shared/nexy.parser";
import { extractJinjaExpressions } from "../../shared/parser/jinja";
import { JINJA_FILTERS } from "../../shared/types";
import { findWorkspaceRoot, parseNexyConfig, resolvePythonModulePath, resolveWithAlias } from "../../shared/nexy.config.parser";
import * as fs from "fs";
import { fileURLToPath } from "url";
import * as path from "path";

const FILTER_RE = /\|\s*([a-zA-Z_][a-zA-Z0-9_]*)/g;

export class DiagnosticHandler {
  private builtins = ["print", "len", "range", "str", "int", "float", "bool", "list", "dict", "set", "tuple", "enumerate", "zip", "sum", "min", "max", "abs", "any", "all", "callable", "loop", "self"];

  public handle(doc: TextDocument): Diagnostic[] {
    const text = doc.getText();
    const diagnostics: Diagnostic[] = [];
    const { imports, props } = parseHeader(text);
    const template = getTemplate(text);
    const usedComponents = findUsedComponentsInTemplate(text);

    this.checkImportsExistence(doc, text, imports, diagnostics);
    this.checkMissingImports(doc, text, imports, usedComponents, diagnostics);
    this.checkUnusedImports(doc, text, imports, usedComponents, diagnostics);
    this.checkUnusedProps(doc, text, props, template, diagnostics);
    this.checkJinjaFilters(doc, text, template, diagnostics);
    this.checkPropTypeStrict(doc, text, imports, template, diagnostics);
    this.checkUndefinedSymbols(doc, text, imports, props, diagnostics);

    return diagnostics;
  }

  private checkUndefinedSymbols(doc: TextDocument, text: string, imports: NexyImport[], props: NexyProp[], diags: Diagnostic[]) {
    const pythonKeywords = ["from", "import", "as", "if", "else", "elif", "for", "in", "while", "def", "class", "return", "True", "False", "None", "not", "and", "or", "is", "prop"];
    const jinjaGlobals = ["range", "dict", "lipsum", "cycler", "joiner", "namespace", "g", "request", "csrf_token", "url_for"];
    const usageRegex = /\b([a-zA-Z_][a-zA-Z0-9_]*)\b(?:\s*\()?/g;

    const definedSymbols = new Set([
      ...imports.map(i => i.name),
      ...props.map(p => p.name),
      ...this.builtins,
      ...pythonKeywords,
      ...jinjaGlobals,
    ]);

    // 0. Scan Template for {% for x in y %} and {% set x = ... %} to add loop/set variables
    const template = getTemplate(text);
    const templateStartOffset = text.indexOf(template);
    if (templateStartOffset !== -1) {
      const templateLines = template.split('\n');
      for (const line of templateLines) {
        const forMatch = line.match(/\{%\s*for\s+(\w+)\s+/);
        if (forMatch) definedSymbols.add(forMatch[1]);
        const setMatch = line.match(/\{%\s*set\s+(\w+)\s*=/);
        if (setMatch) definedSymbols.add(setMatch[1]);
      }
    }

    // 1. Scan Header for definitions and usages
    const headerMatch = text.match(/^\s*---[ \t]*\r?\n([\s\S]*?)\r?\n[ \t]*---[ \t]*(?=\r?\n|$)/m);
    if (headerMatch) {
      const header = headerMatch[1];
      const headerOffset = headerMatch.index! + headerMatch[0].indexOf(header);

      // Find assignments and function/class definitions in header
      const definitionRegex = /^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=|^\s*(?:def|class)\s+([a-zA-Z_][a-zA-Z0-9_]*)/gm;
      let defMatch: RegExpExecArray | null;
      while ((defMatch = definitionRegex.exec(header)) !== null) {
        definedSymbols.add(defMatch[1] || defMatch[2]);
      }

      // Strip string contents and import module paths before checking symbols
      const cleaned = header
        .replace(/"[^"]*"/g, (m) => ' '.repeat(m.length))
        .replace(/'[^']*'/g, (m) => ' '.repeat(m.length))
        .replace(/^[ \t]*from\s+.*$/gm, (m) => ' '.repeat(m.length));

      let match: RegExpExecArray | null;
      while ((match = usageRegex.exec(cleaned)) !== null) {
        const symbol = match[1];
        const fullMatch = match[0];
        const isCall = fullMatch.endsWith("(");

        if (!definedSymbols.has(symbol)) {
          const start = headerOffset + match.index;
          diags.push({
            severity: DiagnosticSeverity.Error,
            range: Range.create(doc.positionAt(start), doc.positionAt(start + symbol.length)),
            message: `Undefined ${isCall ? "function" : "symbol"} "${symbol}" in header.`,
            source: "nexy",
          });
        }
      }
    }

    // 2. Scan Template for usages in Jinja expressions {{ ... }}
    if (templateStartOffset === -1) return;
    const jinjaRegex = /\{\{([\s\S]*?)\}\}/g;
    let jinjaMatch: RegExpExecArray | null;

    while ((jinjaMatch = jinjaRegex.exec(template)) !== null) {
      const expression = jinjaMatch[1];
      const expressionOffset = jinjaMatch.index + 2; // +2 for {{

      // Strip string contents so "label" inside {{ link.get("label") }} is not checked
      const cleanedExpression = expression
        .replace(/"[^"]*"/g, (m) => ' '.repeat(m.length))
        .replace(/'[^']*'/g, (m) => ' '.repeat(m.length));

      let symbolMatch: RegExpExecArray | null;
      while ((symbolMatch = usageRegex.exec(cleanedExpression)) !== null) {
        const symbol = symbolMatch[1];
        const fullMatch = symbolMatch[0];
        const isCall = fullMatch.endsWith("(");

        // Skip symbols that are method/property access (after a dot)
        const beforePos = symbolMatch.index;
        if (beforePos > 0 && cleanedExpression[beforePos - 1] === '.') continue;

        // Skip Jinja2 filters (after a pipe)
        if (beforePos > 0 && cleanedExpression[beforePos - 1] === '|') continue;

        if (!definedSymbols.has(symbol)) {
          const start = templateStartOffset + expressionOffset + symbolMatch.index;
          diags.push({
            severity: DiagnosticSeverity.Error,
            range: Range.create(doc.positionAt(start), doc.positionAt(start + symbol.length)),
            message: `Undefined ${isCall ? "function" : "symbol"} "${symbol}" used in template. Must be declared or imported in the header.`,
            source: "nexy",
          });
        }
      }
    }
  }

  private checkImportsExistence(doc: TextDocument, text: string, imports: NexyImport[], diags: Diagnostic[]) {
    const docPath = fileURLToPath(doc.uri);
    const currentDir = path.dirname(docPath);
    
    // Trouver la racine du projet pour les alias
    const workspaceRoot = this.getWorkspaceRoot(doc);
    const config = parseNexyConfig(workspaceRoot);

    imports.forEach(imp => {
      // Skip system/library imports (don't start with . or @ or /, no dots)
      if (!imp.path.startsWith(".") && !imp.path.startsWith("@") && !imp.path.startsWith("/") && !imp.path.includes("/") && !imp.path.includes(".")) {
        return; 
      }

      // Python module path: src.components.X → src/components/X
      const pyResolved = resolvePythonModulePath(imp.path, workspaceRoot);
      if (pyResolved) return;

      let resolvedPath = path.resolve(currentDir, imp.path);
      
      // Essayer de résoudre avec les alias
      const aliasResolved = resolveWithAlias(imp.path, workspaceRoot, config.useAliases);
      if (aliasResolved) {
        resolvedPath = aliasResolved;
      }

      // Add common extensions if missing
      const exts = ["", ".nexy", ".mdx", ".vue", ".tsx", ".jsx", ".svelte", ".py"];
      let exists = false;
      for (const ext of exts) {
        if (fs.existsSync(resolvedPath + ext)) {
          exists = true;
          break;
        }
      }

      if (!exists) {
        // Chercher l'offset de l'import
        const importRegex = new RegExp(`from\\s+["']${imp.path}["']`, 'g');
        const match = importRegex.exec(text);
        if (match) {
          const pathStart = match.index + match[0].indexOf(imp.path);
          diags.push({
            severity: DiagnosticSeverity.Error,
            range: Range.create(doc.positionAt(pathStart), doc.positionAt(pathStart + imp.path.length)),
            message: `Module not found: ${imp.path}${aliasResolved ? ` (resolved to: ${aliasResolved})` : ""}`,
            source: "nexy"
          });
        }
      }
    });
  }

  private checkPropTypeStrict(doc: TextDocument, text: string, imports: NexyImport[], template: string, diags: Diagnostic[]) {
    const templateStartOffset = text.indexOf(template);
    if (templateStartOffset === -1) return;

    const componentUsageRegex = /<([A-Z][A-Za-z0-9_]*)\s+([^>]*)\/?>/g;
    let match: RegExpExecArray | null;

    while ((match = componentUsageRegex.exec(template)) !== null) {
      const componentName = match[1];
      const attrsText = match[2];
      const imp = imports.find(i => i.name === componentName);
      
      if (imp) {
        // Obtenir le contenu du composant pour localiser la définition de la prop
        let propDefinitions: { name: string, start: number, end: number, sourceUri: string }[] = [];
        try {
          const workspaceRoot = this.getWorkspaceRoot(doc);
          const config = parseNexyConfig(workspaceRoot);
          const resolvedPath = resolveWithAlias(imp.path, workspaceRoot, config.useAliases) || path.resolve(path.dirname(fileURLToPath(doc.uri)), imp.path);
          
          if (fs.existsSync(resolvedPath)) {
            const source = fs.readFileSync(resolvedPath, "utf8");
            const parsed = parseHeader(source);
            const sourceUri = "file://" + resolvedPath.split(path.sep).join("/");
            
            parsed.props.forEach(p => {
              const pIdx = source.indexOf(`${p.name} : prop`);
              if (pIdx !== -1) {
                propDefinitions.push({
                  name: p.name,
                  start: pIdx,
                  end: pIdx + p.name.length,
                  sourceUri
                });
              }
            });
          }
        } catch { /* ignore */ }

        const componentProps = this.getComponentProps(doc, imp);
        const attrRegex = /([a-zA-Z0-9-]+)="([^"]*)"/g;
        let attrMatch: RegExpExecArray | null;
        while ((attrMatch = attrRegex.exec(attrsText)) !== null) {
          const attrName = attrMatch[1];
          const attrValue = attrMatch[2];
          const propDef = componentProps.find(p => p.name === attrName);
          const propLocation = propDefinitions.find(pd => pd.name === attrName);
          
          if (!propDef) {
            const attrStart = templateStartOffset + match.index + match[0].indexOf(`${attrName}=`);
            diags.push({
              severity: DiagnosticSeverity.Error,
              range: Range.create(doc.positionAt(attrStart), doc.positionAt(attrStart + attrName.length)),
              message: `Prop "${attrName}" is not defined in component "${componentName}".`,
              source: "nexy",
            });
            continue;
          }

          let error = false;
          let expectedType = propDef.type;

          if (propDef.type === "int" && isNaN(Number(attrValue))) error = true;
          if (propDef.type === "bool" && !["true", "false"].includes(attrValue.toLowerCase())) error = true;
          if (propDef.type === "float" && isNaN(parseFloat(attrValue))) error = true;
          
          if (error) {
            const attrValueOffset = match.index + match[0].indexOf(`${attrName}="${attrValue}"`) + attrName.length + 2;
            const diagnostic: Diagnostic = {
              severity: DiagnosticSeverity.Error,
              range: Range.create(doc.positionAt(templateStartOffset + attrValueOffset), doc.positionAt(templateStartOffset + attrValueOffset + attrValue.length)),
              message: `Type '${attrValue}' is not assignable to type '${expectedType}'.`,
              source: "nexy",
            };

            if (propLocation) {
              diagnostic.relatedInformation = [
                DiagnosticRelatedInformation.create(
                  Location.create(propLocation.sourceUri, Range.create(0, 0, 1000, 0)), // Simplifié, idéalement calculé
                  `The expected type comes from property '${attrName}' which is declared here on component '${componentName}'`
                )
              ];
            }
            diags.push(diagnostic);
          }
        }
      }
    }
  }

  private getWorkspaceRoot(doc: TextDocument): string {
    const docPath = fileURLToPath(doc.uri);
    return findWorkspaceRoot(path.dirname(docPath)) ?? path.dirname(docPath);
  }

  private getComponentProps(doc: TextDocument, imp: NexyImport): NexyProp[] {
    try {
      const docPath = fileURLToPath(doc.uri);
      const currentDir = path.dirname(docPath);
      
      // Trouver la racine du projet pour les alias
      const workspaceRoot = this.getWorkspaceRoot(doc);
      const config = parseNexyConfig(workspaceRoot);

      let resolvedPath = path.resolve(currentDir, imp.path);
      const aliasResolved = resolveWithAlias(imp.path, workspaceRoot, config.useAliases);
      if (aliasResolved) {
        resolvedPath = aliasResolved;
      }
      
      if (!fs.existsSync(resolvedPath)) return [];
      const source = fs.readFileSync(resolvedPath, "utf8");
      
      if (imp.framework === "nexy") {
        return parseHeader(source).props;
      }
      
      // Support polyglotte pour l'extraction des props (Synchronisé avec completion.ts)
      const props: NexyProp[] = [];

      if (imp.framework === "vue") {
        const patterns = [
          /props:\s*{([\s\S]*?)}/g,
          /props:\s*\[([\s\S]*?)\]/g,
          /defineProps\s*\(\s*{([\s\S]*?)}\s*\)/g,
          /defineProps\s*<\s*{([\s\S]*?)}\s*>\s*\(/g
        ];
        patterns.forEach(p => {
          const m = p.exec(source);
          if (m) {
            const matches = m[1].matchAll(/(\w+)\s*[:?]/g);
            for (const match of matches) props.push({ name: match[1], type: "any" });
          }
        });
      } else if (imp.framework === "react") {
        const reactPropsRegex = /(?:interface|type)\s+(?:[A-Z]\w*Props|Props)\s*=?\s*{([\s\S]*?)}/g;
        const m = reactPropsRegex.exec(source);
        if (m) {
          const matches = m[1].matchAll(/(\w+)\s*(?:\?|:)/g);
          for (const match of matches) props.push({ name: match[1], type: "any" });
        }
      } else if (imp.framework === "rust") {
        const rustPropsRegex = /struct\s+(?:\w+Props|Props)\s*{([\s\S]*?)}/g;
        const m = rustPropsRegex.exec(source);
        if (m) {
          const matches = m[1].matchAll(/pub\s+(\w+)\s*:/g);
          for (const match of matches) props.push({ name: match[1], type: "any" });
        }
      }
      
      return props;
    } catch { return []; }
  }

  private checkMissingImports(doc: TextDocument, text: string, imports: NexyImport[], used: string[], diags: Diagnostic[]) {
    used.forEach(name => {
      if (!imports.find(i => i.name === name)) {
        const idx = text.indexOf(`<${name}`);
        if (idx !== -1) {
          diags.push({
            severity: DiagnosticSeverity.Warning,
            range: Range.create(doc.positionAt(idx + 1), doc.positionAt(idx + 1 + name.length)),
            message: `<${name}> is not imported.`,
            source: "nexy",
            code: "nexy.missingImport",
          });
        }
      }
    });
  }

  private checkUnusedImports(doc: TextDocument, text: string, imports: NexyImport[], used: string[], diags: Diagnostic[]) {
    imports.forEach(imp => {
      if (!used.includes(imp.name)) {
        // Souligner toute la ligne d'import pour plus de visibilité
        const importRegex = new RegExp(`^.*\\b${imp.name}\\b.*$`, 'm');
        const match = importRegex.exec(text);
        
        if (match) {
          const start = match.index;
          const end = match.index + match[0].length;
          diags.push({
            severity: DiagnosticSeverity.Hint,
            range: Range.create(doc.positionAt(start), doc.positionAt(end)),
            message: `Import "${imp.name}" unused in template.`,
            source: "nexy",
            code: "nexy.unusedImport",
            tags: [DiagnosticTag.Unnecessary]
          });
        }
      }
    });
  }

  private checkUnusedProps(doc: TextDocument, text: string, props: NexyProp[], template: string, diags: Diagnostic[]) {
    props.forEach(prop => {
      if (!new RegExp(`\\b${prop.name}\\b`).test(template)) {
        const idx = text.indexOf(prop.name);
        if (idx !== -1) {
          diags.push({
            severity: DiagnosticSeverity.Hint,
            range: Range.create(doc.positionAt(idx), doc.positionAt(idx + prop.name.length)),
            message: `Prop "${prop.name}" unused.`,
            source: "nexy",
            code: "nexy.unusedProp",
            tags: [DiagnosticTag.Unnecessary]
          });
        }
      }
    });
  }

  private checkJinjaFilters(doc: TextDocument, text: string, template: string, diags: Diagnostic[]) {
    const templateStartOffset = text.indexOf(template);
    const expressions = extractJinjaExpressions(template);
    // Only match filters inside Jinja blocks, not in raw HTML/JS/CSS
    for (const expr of expressions) {
      const rawBlock = template.slice(expr.start, expr.end);
      let match: RegExpExecArray | null;
      while ((match = FILTER_RE.exec(rawBlock)) !== null) {
        if (!JINJA_FILTERS.has(match[1])) {
          const globalStart = templateStartOffset + expr.start + match.index + match[0].indexOf(match[1]);
          diags.push({
            severity: DiagnosticSeverity.Warning,
            range: Range.create(doc.positionAt(globalStart), doc.positionAt(globalStart + match[1].length)),
            message: `Unknown Jinja2 filter "${match[1]}".`,
            source: "nexy",
          });
        }
      }
    }
  }
}
