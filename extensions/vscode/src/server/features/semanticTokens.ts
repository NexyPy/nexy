import { SemanticTokens, SemanticTokensBuilder, SemanticTokensLegend } from "vscode-languageserver";
import { TextDocument } from "vscode-languageserver-textdocument";

const TOKEN_TYPES = ["keyword", "variable", "type", "operator", "class", "property", "macro", "comment"] as const;
const TOKEN_MODIFIERS = ["declaration", "readonly", "static"] as const;

export function getSemanticLegend(): SemanticTokensLegend {
  return {
    tokenTypes: [...TOKEN_TYPES],
    tokenModifiers: [...TOKEN_MODIFIERS],
  };
}

export function computeSemanticTokens(doc: TextDocument): SemanticTokens {
  const builder = new SemanticTokensBuilder();
  const text = doc.getText();
  const lines = text.split(/\r?\n/);
  const tokenMap = new Map<string, number>();
  TOKEN_TYPES.forEach((t, i) => tokenMap.set(t, i));

  let inHeader = false;

  for (let lineIdx = 0; lineIdx < lines.length; lineIdx++) {
    const line = lines[lineIdx];

    if (/^---\s*$/.test(line)) {
      inHeader = !inHeader;
      continue;
    }

    if (inHeader) {
      tokenizePythonLine(builder, tokenMap, lineIdx, line);
    } else {
      tokenizeTemplateLine(builder, tokenMap, lineIdx, line);
    }
  }

  return builder.build();
}

function pushTok(
  builder: SemanticTokensBuilder, map: Map<string, number>,
  line: number, col: number, len: number, type: string,
): void {
  const idx = map.get(type);
  if (idx === undefined) return;
  builder.push(line, col, len, idx, 0);
}

function tokenizePythonLine(
  builder: SemanticTokensBuilder, map: Map<string, number>,
  lineIdx: number, line: string,
): void {
  const kwRe = /\b(import|from|as|with|def|class|return|True|False|None)\b/g;
  let m: RegExpExecArray | null;
  while ((m = kwRe.exec(line))) {
    pushTok(builder, map, lineIdx, m.index, m[0].length, "keyword");
  }

  const assignRe = /^\s*([A-Za-z_]\w*)\s*(?::[^=]+)?\s*=/;
  const am = assignRe.exec(line);
  if (am) {
    const varStart = am[0].indexOf(am[1]);
    pushTok(builder, map, lineIdx, am.index + varStart, am[1].length, "variable");
    const eqPos = line.indexOf("=", am.index);
    if (eqPos !== -1) pushTok(builder, map, lineIdx, eqPos, 1, "operator");
  }

  const propRe = /^\s*([A-Za-z_]\w*)\s*:\s*prop\[/;
  const pm = propRe.exec(line);
  if (pm) {
    const varStart = pm[0].indexOf(pm[1]);
    pushTok(builder, map, lineIdx, pm.index + varStart, pm[1].length, "variable");
    const pi = line.indexOf("prop", pm.index);
    if (pi !== -1) pushTok(builder, map, lineIdx, pi, 4, "type");
    const lb = line.indexOf("[", pi);
    const rb = line.indexOf("]", lb + 1);
    if (lb !== -1 && rb !== -1 && rb > lb + 1) {
      pushTok(builder, map, lineIdx, lb + 1, rb - lb - 1, "type");
    }
  }

  const fromRe = /^\s*from\s+(.+?)\s+import\s+(.+)/.exec(line);
  if (fromRe) {
    const modPos = line.indexOf(fromRe[1]);
    if (modPos !== -1) pushTok(builder, map, lineIdx, modPos, fromRe[1].length, "class");
    const syms = fromRe[2].split(/\s*,\s*/);
    let idx = line.indexOf(fromRe[2]);
    for (const sym of syms) {
      if (!sym) continue;
      const pos = line.indexOf(sym, idx);
      if (pos !== -1) {
        pushTok(builder, map, lineIdx, pos, sym.length, "property");
        idx = pos + sym.length;
      }
    }
  }
}

function tokenizeTemplateLine(
  builder: SemanticTokensBuilder, map: Map<string, number>,
  lineIdx: number, line: string,
): void {
  // PascalCase component tags — <Button> (handled by semantic, TextMate only knows lowercase)
  let m: RegExpExecArray | null;
  const compRe = /<([A-Z][A-Za-z0-9_]*)/g;
  while ((m = compRe.exec(line))) {
    const name = m[1];
    const tokenType = name === "Slot" ? "type" : "class";
    pushTok(builder, map, lineIdx, m.index + 1, name.length, tokenType);
  }

  // Jinja2 {{ }} — expression variables
  const jinjaExprRe = /\{\{\s*([A-Za-z_][A-Za-z0-9_.]*)/g;
  while ((m = jinjaExprRe.exec(line))) {
    pushTok(builder, map, lineIdx, m.index + 2, m[1].length, "variable");
  }

  // Jinja2 {% %} — block keywords
  const jinjaBlockRe = /\{%[-]?\s*(if|elif|else|endif|for|endfor|block|endblock|macro|endmacro|call|endcall|filter|endfilter|set|with|endwith|raw|endraw|extends|include|import|from)\b/g;
  while ((m = jinjaBlockRe.exec(line))) {
    pushTok(builder, map, lineIdx, m.index + 2, m[1].length, "keyword");
  }

  // Jinja2 | filter
  const filterRe = /\|\s*([A-Za-z_][A-Za-z0-9_]*)/g;
  while ((m = filterRe.exec(line))) {
    pushTok(builder, map, lineIdx, m.index + 1, m[1].length, "macro");
  }

  // Jinja2 {# #} — comments kept as-is by grammar, mark the delimiters
  const commentRe = /\{#|#\}/g;
  while ((m = commentRe.exec(line))) {
    pushTok(builder, map, lineIdx, m.index, m[0].length, "comment");
  }
}
