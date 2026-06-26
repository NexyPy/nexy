import * as vscode from "vscode";
import * as fs from "fs";
import * as path from "path";
import { findWorkspaceRoot, parseNexyConfig } from "../../shared/nexy.config.parser";
import { 
  EmbedContentProvider, 
  getDocumentRegions as getRegionsRaw,
  RegionInfo,
  PY_SCHEME, 
  HTML_SCHEME, 
  CSS_SCHEME, 
  JS_SCHEME 
} from "./embedded.provider";

const LANG_EXT: Record<string, string> = {
  python: "py",
  html: "html",
  typescript: "ts",
  typescriptreact: "tsx",
  javascript: "js",
  javascriptreact: "jsx",
  scss: "scss",
  sass: "sass",
  less: "less",
  css: "css",
  markdown: "md",
  rust: "rs",
};

  const PYTHON_CACHE = new Map<string, { uri: vscode.Uri; filePath: string; contentHash: number }>();
  const REGION_CACHE = new Map<string, { version: number; regions: RegionInfo[] }>();

  let pyActivated = false;
  let cssActivated = false;
  let tsActivated = false;

  function cachedRegions(document: vscode.TextDocument): RegionInfo[] {
    const key = document.uri.toString();
    const cached = REGION_CACHE.get(key);
    if (cached && cached.version === document.version) return cached.regions;
    const regions = getRegionsRaw(document);
    REGION_CACHE.set(key, { version: document.version, regions });
    return regions;
  }

  function getRegionAtPosition(document: vscode.TextDocument, position: vscode.Position): RegionInfo | undefined {
    const offset = document.offsetAt(position);
    const regions = cachedRegions(document);
    return regions
      .filter(r => offset >= r.start && offset <= r.end)
      .sort((a, b) => (a.end - a.start) - (b.end - b.start))[0];
  }

  function hashContent(s: string): number {
    let h = 0;
    for (let i = 0; i < s.length; i++) h = ((h << 5) - h) + s.charCodeAt(i) | 0;
    return h;
  }

  function ensureVirtFile(
    cache: Map<string, { uri: vscode.Uri; filePath: string; contentHash: number }>,
    key: string,
    filePath: string,
    content: string,
  ): vscode.Uri {
    let entry = cache.get(key);
    const contentHash = hashContent(content);
    if (entry && entry.contentHash === contentHash) return entry.uri;
    if (!entry) {
      const virtDir = path.dirname(filePath);
      fs.mkdirSync(virtDir, { recursive: true });
      // Ensure .nexy-virt/ is a Python package so Pylance includes it
      const initPy = path.join(virtDir, '__init__.py');
      if (!fs.existsSync(initPy)) fs.writeFileSync(initPy, '', 'utf8');
      const uri = vscode.Uri.file(filePath);
      fs.writeFileSync(filePath, content, 'utf8');
      entry = { uri, filePath, contentHash };
      cache.set(key, entry);
    } else if (entry.contentHash !== contentHash) {
      fs.writeFileSync(entry.filePath, content, 'utf8');
      entry.contentHash = contentHash;
    }
    return entry.uri;
  }

  const NEXY_STUBS = [
    'from typing import Any',
    'prop = Any  # Nexy prop type',
    '__all__: list[str] = []',
    '',
    '# Nexy runtime stubs — silences Pylance when nexy package is not in path',
    'try:',
    '    from nexy import Template as __Template, Import as __Import',
    '    from nexy.routers.context import current_request, usePathname',
    '    from nexy.core.config import Config',
    'except ImportError:',
    '    __Template: Any = None',
    '    __Import: Any = None',
    '    current_request: Any = None',
    '    usePathname: Any = None',
    '    Config: Any = None',
    '',
  ];

  function getOrCreatePythonVirt(document: vscode.TextDocument, region: { scheme: string; languageId: string; content: string }): { uri: vscode.Uri; stubLines: number } {
    const key = document.uri.fsPath;
    const virtDir = path.join(path.dirname(key), '.nexy-virt');
    const filePath = path.join(virtDir, path.basename(key) + '.py');
    const stubs = NEXY_STUBS.join('\n') + '\n';
    const hasStubs = region.content.includes('prop') || region.content.includes('from typing');
    const content = hasStubs ? stubs + region.content : region.content;
    const stubLines = hasStubs ? NEXY_STUBS.length + 1 : 0;
    return { uri: ensureVirtFile(PYTHON_CACHE, key, filePath, content), stubLines };
  }

function virtualUri(document: vscode.TextDocument, region: { scheme: string; languageId: string }): vscode.Uri {
  const ext = LANG_EXT[region.languageId] || region.languageId;
  return vscode.Uri.parse(`${region.scheme}://${document.uri.path}.${ext}`);
}

export function registerServiceDelegation(
  context: vscode.ExtensionContext,
  providers: Record<string, EmbedContentProvider>,
  isNexyProject: boolean
) {
  const selector = [{ language: "nexy", scheme: "file" }];
  if (isNexyProject) {
    selector.push({ language: "mdx", scheme: "file" });
  }

  const toRel = (document: vscode.TextDocument, baseStart: number, pos: vscode.Position) => {
    const text = document.getText().slice(baseStart, document.offsetAt(pos));
    const lines = text.split(/\r?\n/);
    return new vscode.Position(lines.length - 1, lines[lines.length - 1].length);
  };

  /** Detect if cursor is inside a Jinja2 {{ }}, {% %}, or {# #} expression in the template. */
  function getJinjaContext(
    document: vscode.TextDocument,
    pos: vscode.Position,
    templateStart: number
  ): { prefix: string; delimiter: string; templateLine: number } | null {
    const offset = document.offsetAt(pos);
    const text = document.getText();
    const before = text.slice(0, offset);

    const pairs: [string, string, string][] = [
      ['{{', '}}', 'expression'],
      ['{%', '%}', 'block'],
      ['{#', '#}', 'comment'],
    ];
    for (const [open, close, _kind] of pairs) {
      const lastOpen = before.lastIndexOf(open);
      if (lastOpen === -1) continue;
      const between = text.slice(lastOpen + open.length, offset);
      if (between.includes(close)) continue;
      const after = text.slice(offset);
      if (after.indexOf(close) === -1) continue;
      const beforeInTemplate = text.slice(templateStart, offset);
      const line = beforeInTemplate.split('\n').length - 1;
      return { prefix: between, delimiter: open, templateLine: line };
    }
    return null;
  }

  /** Scan template lines above cursor for {% for x in y %} and {% set x = ... %} and return Python stub declarations. */
  function extractTemplateVariables(
    document: vscode.TextDocument,
    templateStart: number,
    upToLine: number
  ): string[] {
    const text = document.getText();
    const lines = text.slice(templateStart).split('\n');
    const stubs: string[] = [];
    const openVars: string[] = [];

    for (let i = 0; i < Math.min(upToLine, lines.length); i++) {
      const line = lines[i];
      const forMatch = line.match(/\{%\s*for\s+(\w+)\s+/);
      if (forMatch) openVars.push(forMatch[1]);
      if (/\{%\s*endfor\s*%\}/.test(line) && openVars.length > 0) openVars.pop();
      const setMatch = line.match(/\{%\s*set\s+(\w+)\s*=/);
      if (setMatch) stubs.push(`${setMatch[1]}: Any = None`);
    }

    for (const v of openVars) {
      stubs.push(`${v}: Any = None`);
    }

    return [...new Set(stubs)];
  }

  /** Transform Jinja2 expression/block prefix to valid Python for Pylance. */
  function transformJinjaPrefix(prefix: string, delimiter: string): string {
    const result = prefix.trimEnd();

    if (delimiter === '{%') {
      const trimmed = result.trimStart();
      if (/^(for|if|elif|while)\b/.test(trimmed) && !result.trimEnd().endsWith(':')) {
        return result.trimEnd() + ':\n    pass';
      }
      if (/^set\s+/.test(trimmed)) {
        return trimmed.replace(/^set\s+/, '');
      }
    }

    return result;
  }

  const triggers = ['.', '"', "'", ' ', '<', '/', ':', '{', '%', '|', '='];

  context.subscriptions.push(
    // 1. Completion
    vscode.languages.registerCompletionItemProvider(
      selector,
      {
        async provideCompletionItems(document, position, token, contextParam) {
          if (document.languageId === "mdx" && !isNexyProject) return null;

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          // If in template inside Jinja2 expression, delegate to Python with context
          if (region.scheme === HTML_SCHEME || region.scheme === CSS_SCHEME || region.scheme === JS_SCHEME) {
            const jinjaCtx = getJinjaContext(document, position, region.start);
            if (jinjaCtx !== null && jinjaCtx.delimiter !== '{#') {
              const stubs = extractTemplateVariables(document, region.start, jinjaCtx.templateLine);
              const transformed = transformJinjaPrefix(jinjaCtx.prefix, jinjaCtx.delimiter);

              // Include header context so Pylance knows about props, imports, and variables
              const allRegions = cachedRegions(document);
              const headerRegion = allRegions.find(r => r.languageId === "python");
              const headerContent = headerRegion ? headerRegion.content : '';

              const pyLines: string[] = [...NEXY_STUBS];
              if (headerContent.trim()) pyLines.push('', headerContent.trimEnd());
              if (stubs.length > 0) pyLines.push('', ...stubs);
              pyLines.push('', transformed);
              const pyContent = pyLines.join('\n');
              const pyLine = pyLines.length - 1;

              const pyPath = path.join(
                path.dirname(document.uri.fsPath),
                '.nexy-virt',
                path.basename(document.uri.fsPath) + '.jinja.py',
              );
              fs.mkdirSync(path.dirname(pyPath), { recursive: true });
              fs.writeFileSync(pyPath, pyContent, 'utf8');
              const pyUri = vscode.Uri.file(pyPath);

              if (!pyActivated) {
                await vscode.extensions.getExtension("ms-python.python")?.activate();
                pyActivated = true;
              }

              const list = (await vscode.commands.executeCommand(
                "vscode.executeCompletionItemProvider",
                pyUri,
                new vscode.Position(pyLine, transformed.length),
                contextParam.triggerCharacter,
              )) as vscode.CompletionList | vscode.CompletionItem[];

              if (list) {
                const items = Array.isArray(list) ? list : list.items;
                return items.map(sanitizeCompletionItem);
              }
            }
          }

          const provider = providers[region.scheme];
          if (!provider) return null;

          const pyVirt = region.languageId === "python"
            ? getOrCreatePythonVirt(document, region)
            : null;
          const uri = pyVirt ? pyVirt.uri : virtualUri(document, region);
          provider.set(uri, region.content);

          let relPos = toRel(document, region.start, position);
          if (pyVirt && pyVirt.stubLines > 0) {
            relPos = new vscode.Position(relPos.line + pyVirt.stubLines, relPos.character);
          }
          
          // Force activation des extensions cibles si nécessaire
          if (region.languageId === "python" && !pyActivated) {
            await vscode.extensions.getExtension("ms-python.python")?.activate();
            pyActivated = true;
          } else if (region.languageId === "css" && !cssActivated) {
            await vscode.extensions.getExtension("vscode.css-language-features")?.activate();
            cssActivated = true;
          } else if (region.languageId === "javascript" && !tsActivated) {
            await vscode.extensions.getExtension("vscode.typescript-language-features")?.activate();
            tsActivated = true;
          }

          const list = (await vscode.commands.executeCommand(
            "vscode.executeCompletionItemProvider",
            uri,
            relPos,
            contextParam.triggerCharacter
          )) as vscode.CompletionList | vscode.CompletionItem[];

          if (!list) return null;
          const items = Array.isArray(list) ? list : list.items;
          
          return items.map(sanitizeCompletionItem);
        }
      },
      ...triggers
    ),

    // 2. Hover
    vscode.languages.registerHoverProvider(
      selector,
      {
        async provideHover(document, position) {
          if (document.languageId === "mdx" && !isNexyProject) return null;

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          const provider = providers[region.scheme];
          if (!provider) return null;

          const pyVirt = region.languageId === "python"
            ? getOrCreatePythonVirt(document, region)
            : null;
          const uri = pyVirt ? pyVirt.uri : virtualUri(document, region);
          provider.set(uri, region.content);

          let relPos = toRel(document, region.start, position);
          if (pyVirt && pyVirt.stubLines > 0) {
            relPos = new vscode.Position(relPos.line + pyVirt.stubLines, relPos.character);
          }
          const hover = (await vscode.commands.executeCommand(
            "vscode.executeHoverProvider",
            uri,
            relPos
          )) as vscode.Hover[];

          if (!hover || hover.length === 0) return null;
          return hover[0];
        }
      }
    ),

    // 3. Definition
    vscode.languages.registerDefinitionProvider(
      selector,
      {
        async provideDefinition(document, position) {
          if (document.languageId === "mdx" && !isNexyProject) return null;

          // Check if cursor is on a component tag (uppercase)
          const text = document.getText();
          const offset = document.offsetAt(position);
          let wordStart = offset;
          while (wordStart > 0 && /\w/.test(text[wordStart - 1])) wordStart--;
          let wordEnd = offset;
          while (wordEnd < text.length && /\w/.test(text[wordEnd])) wordEnd++;
          const word = text.slice(wordStart, wordEnd);

          if (word && /^[A-Z]/.test(word)) {
            const headerMatch = text.match(/^[ \t]*---[ \t]*\r?\n([\s\S]*?)\r?\n[ \t]*---[ \t]*(?=\r?\n|$)/m);
            if (headerMatch) {
              const fromRe = /^\s*from\s+["']([^"']+)["']\s+import\s+(.+?)(?=\r?\n\S|$)/gms;
              let m: RegExpExecArray | null;
              fromRe.lastIndex = 0;
              while ((m = fromRe.exec(headerMatch[1])) !== null) {
                const targets = m[2].split(",").map((t: string) => t.trim().split(/\s+as\s+/i).pop() || t.trim());
                if (targets.includes(word)) {
                  const importPath = m[1];
                  const docDir = path.dirname(document.uri.fsPath);
                  const workspaceRoot = findWorkspaceRoot(docDir) ?? docDir;
                  const config = parseNexyConfig(workspaceRoot);
                  let resolved = importPath;
                  if (importPath.startsWith("@") || importPath.startsWith("~")) {
                    let found = false;
                    for (const [alias, replacement] of Object.entries(config.useAliases)) {
                      if (importPath.startsWith(alias)) {
                        resolved = path.join(workspaceRoot, replacement, importPath.slice(alias.length).replace(/^\//, ""));
                        found = true;
                        break;
                      }
                    }
                    if (!found) {
                      resolved = path.join(workspaceRoot, "src", importPath.slice(2));
                    }
                  } else if (importPath.startsWith(".")) {
                    resolved = path.resolve(docDir, importPath);
                  } else {
                    resolved = path.resolve(docDir, importPath);
                  }
                  const exts = [".nexy", ".mdx", ".py", ".tsx", ".jsx", ".vue", ".svelte"];
                  for (const candidate of [resolved, ...exts.map(e => resolved + e)]) {
                    if (fs.existsSync(candidate)) {
                      return new vscode.Location(vscode.Uri.file(candidate), new vscode.Position(0, 0));
                    }
                  }
                  // Case-insensitive fallback
                  const dir = path.dirname(resolved);
                  const base = path.basename(resolved);
                  if (fs.existsSync(dir)) {
                    const files = fs.readdirSync(dir);
                    const ciMatch = files.find((f: string) => f.toLowerCase() === base.toLowerCase());
                    if (ciMatch) {
                      return new vscode.Location(vscode.Uri.file(path.join(dir, ciMatch)), new vscode.Position(0, 0));
                    }
                  }
                }
              }
            }
          }

          const region = getRegionAtPosition(document, position);
          if (!region) return null;

          const provider = providers[region.scheme];
          if (!provider) return null;

          const pyVirt = region.languageId === "python"
            ? getOrCreatePythonVirt(document, region)
            : null;
          const uri = pyVirt ? pyVirt.uri : virtualUri(document, region);
          provider.set(uri, region.content);

          let relPos = toRel(document, region.start, position);
          if (pyVirt && pyVirt.stubLines > 0) {
            relPos = new vscode.Position(relPos.line + pyVirt.stubLines, relPos.character);
          }
          const definitions = (await vscode.commands.executeCommand(
            "vscode.executeDefinitionProvider",
            uri,
            relPos
          )) as vscode.Location | vscode.Location[];

          if (!definitions) return null;
          
           const ptShift = pyVirt?.stubLines ?? 0;
           const mapLocation = (loc: vscode.Location) => {
            if (loc.uri.toString() === uri.toString()) {
              const adjStartLine = Math.max(0, loc.range.start.line - ptShift);
              const adjEndLine = Math.max(0, loc.range.end.line - ptShift);
              const start = document.positionAt(region.start + (adjStartLine > 0 ? region.content.split("\n").slice(0, adjStartLine).join("\n").length + 1 : 0) + loc.range.start.character);
              const end = document.positionAt(region.start + (adjEndLine > 0 ? region.content.split("\n").slice(0, adjEndLine).join("\n").length + 1 : 0) + loc.range.end.character);
              return new vscode.Location(document.uri, new vscode.Range(start, end));
            }
            return loc;
          };

          return Array.isArray(definitions) ? definitions.map(mapLocation) : mapLocation(definitions);
        }
      }
    )
  );

  // 4. Color Provider (CSS color picker for <style> blocks)
  function toAbsRange(document: vscode.TextDocument, region: RegionInfo, range: vscode.Range): vscode.Range {
    const lineToOffset = (line: number) => line > 0
      ? region.content.split('\n').slice(0, line).join('\n').length + 1
      : 0;
    const start = region.start + lineToOffset(range.start.line) + range.start.character;
    const end = region.start + lineToOffset(range.end.line) + range.end.character;
    return new vscode.Range(document.positionAt(start), document.positionAt(end));
  }

  function toRelRange(region: RegionInfo, range: vscode.Range): vscode.Range {
    const lineToOffset = (line: number) => line > 0
      ? region.content.split('\n').slice(0, line).join('\n').length + 1
      : 0;
    const startOffset = lineToOffset(range.start.line) + range.start.character;
    const endOffset = lineToOffset(range.end.line) + range.end.character;
    const regionLines = region.content.split('\n');
    let relStartLine = 0;
    let relStartChar = startOffset;
    for (let i = 0; i < regionLines.length; i++) {
      const lineLen = regionLines[i].length + 1;
      if (relStartChar < lineLen) { relStartLine = i; break; }
      relStartChar -= lineLen;
    }
    let relEndLine = relStartLine;
    let relEndChar = relStartChar + (endOffset - startOffset);
    while (relEndChar > regionLines[relEndLine].length + 1 && relEndLine < regionLines.length - 1) {
      relEndChar -= regionLines[relEndLine].length + 1;
      relEndLine++;
    }
    return new vscode.Range(relStartLine, relStartChar, relEndLine, relEndChar);
  }

  // Cache CSS virtual documents for color provider — reuse until content changes
  const CSS_DOC_CACHE = new Map<string, { uri: vscode.Uri; hash: number }>();
  async function getOrCreateCssDoc(region: RegionInfo): Promise<{ uri: vscode.Uri }> {
    const key = region.scheme + '::' + region.start;
    const hash = hashContent(region.content);
    const cached = CSS_DOC_CACHE.get(key);
    if (cached && cached.hash === hash) return { uri: cached.uri };
    const doc = await vscode.workspace.openTextDocument({
      language: region.languageId,
      content: region.content,
    });
    CSS_DOC_CACHE.set(key, { uri: doc.uri, hash });
    return { uri: doc.uri };
  }

  context.subscriptions.push(
    vscode.languages.registerColorProvider(
      selector,
      {
        async provideDocumentColors(document: vscode.TextDocument): Promise<vscode.ColorInformation[]> {
          if (document.languageId === "mdx" && !isNexyProject) return [];

          const allRegions = cachedRegions(document);
          const cssRegions = allRegions.filter(r => r.scheme === CSS_SCHEME && r.languageId.startsWith("css"));
          const allColors: vscode.ColorInformation[] = [];

          for (const region of cssRegions) {
            // Use an in-memory untitled CSS document — no disk writes
            if (!cssActivated) {
              await vscode.extensions.getExtension("vscode.css-language-features")?.activate();
              cssActivated = true;
            }

            const { uri: cssUri } = await getOrCreateCssDoc(region);

            const colors = await vscode.commands.executeCommand<vscode.ColorInformation[]>(
              "vscode.executeDocumentColorProvider",
              cssUri,
            );

            if (colors) {
              for (const c of colors) {
                allColors.push({
                  color: c.color,
                  range: toAbsRange(document, region, c.range),
                });
              }
            }
          }

          return allColors;
        },

        async provideColorPresentations(color: vscode.Color, context: { readonly document: vscode.TextDocument; readonly range: vscode.Range }): Promise<vscode.ColorPresentation[]> {
          const { document, range } = context;
          if (document.languageId === "mdx" && !isNexyProject) return [];

          const offset = document.offsetAt(range.start);
          const allRegions = cachedRegions(document);
          const region = allRegions.find(r => offset >= r.start && offset <= r.end && r.scheme === CSS_SCHEME);
          if (!region) return [];

          if (!cssActivated) {
            await vscode.extensions.getExtension("vscode.css-language-features")?.activate();
            cssActivated = true;
          }
          const { uri: cssUri } = await getOrCreateCssDoc(region);
          const relRange = toRelRange(region, range);

          const presentations = await vscode.commands.executeCommand<vscode.ColorPresentation[]>(
            "vscode.executeColorPresentationProvider",
            { color, range: relRange },
            { uri: cssUri },
          );

          return presentations || [];
        },
      },
    ),
  );

  // 5. Diagnostics Delegation
  const diagnosticCollection = vscode.languages.createDiagnosticCollection("nexy-embedded");
  context.subscriptions.push(diagnosticCollection);

  const NEXY_BUILTINS = new Set(['prop', 'Slot', 'Fragment', 'ClientOnly']);

  const JINJA2_TEMPLATE_VARS = new Set([
    'loop', 'forloop', 'super', 'block', 'varargs', 'kwargs',
    'caller', 'children', 'cycler', 'joiner', 'namespace',
  ]);

  function extractNexyImportNames(header: string): string[] {
    const names: string[] = [];
    const fromRe = /^\s*from\s+["'][^"']+\.(?:nexy|mdx|tsx|jsx|vue|svelte|py|rs)["']\s+import\s+(.+?)(?=\r?\n\S|$)/gms;
    const pyRe = /^\s*from\s+([A-Za-z_][\w.]*)\s+import\s+(.+?)(?=\r?\n\S|$)/gms;
    let m: RegExpExecArray | null;
    while ((m = fromRe.exec(header)) !== null) {
      for (const raw of m[1].split(",")) {
        names.push(raw.trim().split(/\s+as\s+/i).pop() || raw.trim());
      }
    }
    while ((m = pyRe.exec(header)) !== null) {
      for (const raw of m[2].split(",")) {
        names.push(raw.trim().split(/\s+as\s+/i).pop() || raw.trim());
      }
    }
    return names;
  }

  function isPythonUndefinedSymbol(
    message: string,
    knownNames: string[],
    builtins: Set<string>,
  ): boolean {
    const nexyNames = new Set([...knownNames, ...builtins, ...JINJA2_TEMPLATE_VARS]);
    const patterns = [
      /"([^"]+)" is not defined/,
      /'([^']+)' is not defined/,
      /Undefined symbol ["']([^"']+)["']/,
      /Cannot access member ["']([^"']+)["']/,
      /reportUndefinedVariable.*["']([^"']+)["']/,
      /"([^"]+)" is not defined by imported module/,
      /'([^']+)' is not defined by imported module/,
      /Import "([^"]+)" could not be resolved/,
    ];
    for (const pat of patterns) {
      const m = message.match(pat);
      if (m && m[1] && nexyNames.has(m[1])) return true;
    }
    return false;
  }

  function hasNexyImportPath(message: string): boolean {
    return /\.(?:nexy|mdx)["']/.test(message);
  }

  function isNexyFalsePositive(d: vscode.Diagnostic): boolean {
    const msg = d.message;
    // reportMissingModuleSource — Pylance can't find nexy package
    if (d.code === 'reportMissingModuleSource' && /["']nexy/i.test(msg)) return true;
    // Import cannot be resolved for nexy.*
    if (/import\s+["']nexy/i.test(msg)) return true;
    if (/(cannot import|import.*cannot be resolved)/i.test(msg) && /nexy/i.test(msg)) return true;
    // Lambda false positives in Jinja2 context
    if (/lambda/i.test(msg) && /parameter/i.test(msg)) return true;
    // Redefinition of __Import or __Template (stub clashes with header)
    if (/["'](__Import|__Template|__JinjaTemplate)["']/.test(msg)) return true;
    return false;
  }

  context.subscriptions.push(
    vscode.languages.onDidChangeDiagnostics(e => {
      e.uris.forEach(uri => {
        const isPylanceFile = uri.scheme === "file" && uri.fsPath.includes(".nexy-virt");
        if (!providers[uri.scheme] && !isPylanceFile) return;

        // Resolve original .nexy/.mdx document
        let originalUri: vscode.Uri;
        let document: vscode.TextDocument | undefined;
        if (isPylanceFile) {
          // Pylance reports against .nexy-virt/*.py — find matching .nexy file
          const virtDir = path.dirname(uri.fsPath);
          const baseNoExt = path.basename(uri.fsPath, '.py');
          const origFile = path.join(path.dirname(virtDir), baseNoExt);
          originalUri = vscode.Uri.file(origFile);
          document = vscode.workspace.textDocuments.find(d => d.uri.fsPath === origFile);
        } else {
          const originalUriStr = uri.path.split(".").slice(0, -1).join(".");
          originalUri = vscode.Uri.file(originalUriStr);
          document = vscode.workspace.textDocuments.find(d => d.uri.fsPath === originalUri.fsPath);
        }
        if (!document) return;

        const isNexyFile = document.languageId === "nexy";
        const isMdxFile = document.languageId === "mdx";
        if (!isNexyFile && !(isMdxFile && isNexyProject)) return;

        const regions = cachedRegions(document);
        const region = isPylanceFile
          ? regions.find(r => r.languageId === "python")
          : regions.find(r => uri.scheme === r.scheme);
        if (!region) return;

        let diagnostics = vscode.languages.getDiagnostics(uri);

        if (region.languageId === "python") {
          const full = document.getText();
          const headerMatch = full.match(/^---[ \t]*\r?\n([\s\S]*?)\r?\n---[ \t]*(?=\r?\n|$)/m);
          const headerText = headerMatch ? headerMatch[1] : "";
          const nexyImportNames = extractNexyImportNames(headerText);
          const nexyImportSet = new Set(nexyImportNames);
          diagnostics = diagnostics.filter(d => {
            if (isNexyFalsePositive(d)) return false;
            if (isPythonUndefinedSymbol(d.message, nexyImportNames, NEXY_BUILTINS)) return false;
            if (hasNexyImportPath(d.message)) return false;
            // Catch-all: Pylance reportUndefinedVariable for any known import
            if (d.code === 'reportUndefinedVariable') {
              const symMatch = d.message.match(/["']([^"']+)["']/);
              if (symMatch && nexyImportSet.has(symMatch[1])) return false;
            }
            return true;
          });
        }

        // Adjust line offset for stubs prepended to Python virtual files
        const stubShift = (region.languageId === "python" && isPylanceFile
          && (region.content.includes('prop') || region.content.includes('from typing')))
          ? NEXY_STUBS.length + 1
          : 0;

        const mappedDiagnostics = diagnostics.map(d => {
          const adjLine = Math.max(0, d.range.start.line - stubShift);
          const adjEndLine = Math.max(0, d.range.end.line - stubShift);
          const offsetStart = region!.start + (adjLine > 0
            ? region!.content.split("\n").slice(0, adjLine).join("\n").length + 1
            : 0) + d.range.start.character;
          const offsetEnd = region!.start + (adjEndLine > 0
            ? region!.content.split("\n").slice(0, adjEndLine).join("\n").length + 1
            : 0) + d.range.end.character;
          const start = document.positionAt(offsetStart);
          const end = document.positionAt(offsetEnd);
          const newDiagnostic = new vscode.Diagnostic(new vscode.Range(start, end), d.message, d.severity);
          newDiagnostic.source = `nexy (${region!.languageId})`;
          newDiagnostic.code = d.code;
          newDiagnostic.relatedInformation = d.relatedInformation;
          newDiagnostic.tags = d.tags;
          return newDiagnostic;
        });
        diagnosticCollection.set(originalUri, mappedDiagnostics);
      });
    })
  );
}

function sanitizeCompletionItem(item: vscode.CompletionItem): vscode.CompletionItem {
  const out = new vscode.CompletionItem(item.label, item.kind);
  out.detail = item.detail;
  out.documentation = item.documentation;
  out.sortText = item.sortText;
  out.filterText = item.filterText;
  out.insertText = item.insertText ?? (typeof (item as any).textEdit?.newText === "string"
    ? (item as any).textEdit.newText
    : undefined);
  // Preserve auto-import edits from Pylance (was being deleted — kills auto-import)
  out.additionalTextEdits = item.additionalTextEdits;
  (out as any).textEdit = undefined;
  out.command = item.command;
  return out;
}
