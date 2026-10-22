import { NexyImport, NexyProp, NexyFramework, frameworkFromExt } from "../types";

const HEADER_RE = /^[ \t]*---[ \t]*\r?\n([\s\S]*?)\r?\n[ \t]*---[ \t]*(?=\r?\n|$)/m;
const FROM_IMPORT_RE = /^\s*from\s+["'](?<path>[^"']+)["']\s+import\s+(?<targets>.+?)(?=\r?\n\S|$)/gms;
const FROM_PYMOD_RE = /^\s*from\s+(?!["'])(?<path>[A-Za-z_][\w.]*(?:\.[A-Za-z_][\w.]*)*)\s+import\s+(?<targets>.+?)(?=\r?\n\S|$)/gms;
const LOADER_RE = /^\s*(?<alias>\w+)\s*=\s*(?:__Import|__nexy_loader__\.import_component)\s*\(\s*path\s*=\s*["'](?<path>[^"']+)["']\s*,\s*symbol\s*=\s*["'](?<symbol>[^"']+)["'](?:\s*,\s*framework\s*=\s*["'](?<fw>[^"']+)["'])?\s*\)/gm;
const PROP_RE = /^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*prop\[([^\]]*)\](?:\s*=\s*(.+))?/gm;

export function extractHeader(text: string): string | null {
  const m = HEADER_RE.exec(text);
  return m ? m[1] : null;
}

export function extractTemplate(text: string): string {
  return extractTemplateWithOffset(text).content;
}

export function extractTemplateWithOffset(text: string): { content: string; offset: number } {
  const m = text.match(/^[ \t]*---[ \t]*\r?\n[\s\S]*?\r?\n[ \t]*---[ \t]*(?:\r?\n|$)(?<template>[\s\S]*)/);
  if (m && m.index !== undefined && m.groups?.template !== undefined) {
    const raw = m.groups.template;
    const offset = m.index + m[0].indexOf(raw);
    return { content: raw.trim(), offset };
  }
  const trimmed = text.trimStart();
  const offset = text.indexOf(trimmed);
  return { content: trimmed, offset };
}

export function extractRegionAtOffset(text: string, offset: number): "header" | "template" {
  const headerMatch = HEADER_RE.exec(text);
  if (!headerMatch || headerMatch.index === undefined) return "template";
  const headerStart = headerMatch.index;
  const headerEnd = headerMatch.index + headerMatch[0].length;
  return offset >= headerStart && offset <= headerEnd ? "header" : "template";
}

export function extractImports(header: string): NexyImport[] {
  const imports: NexyImport[] = [];

  let m: RegExpExecArray | null;
  while ((m = FROM_IMPORT_RE.exec(header)) !== null) {
    const path = m.groups!.path;
    const targetsRaw = m.groups!.targets;
    const fw = frameworkFromExt(path);

    const targets = targetsRaw
      .replace(/[()]/g, "")
      .replace(/;/g, "")
      .replace(/\n/g, " ")
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    for (const target of targets) {
      const parts = target.split(/\s+as\s+/i);
      const symbol = parts[0];
      const name = parts[1] || symbol;
      imports.push({ path, name, framework: fw });
    }
  }

  while ((m = FROM_PYMOD_RE.exec(header)) !== null) {
    const path = m.groups!.path;
    const targetsRaw = m.groups!.targets;
    const fw: NexyFramework = "nexy";

    const targets = targetsRaw
      .replace(/[()]/g, "")
      .replace(/;/g, "")
      .replace(/\n/g, " ")
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    for (const target of targets) {
      const parts = target.split(/\s+as\s+/i);
      const symbol = parts[0];
      const name = parts[1] || symbol;
      imports.push({ path, name, framework: fw });
    }
  }

  while ((m = LOADER_RE.exec(header)) !== null) {
    const path = m.groups!.path;
    const alias = m.groups!.alias;
    const symbol = m.groups!.symbol;
    const fwStr = m.groups!.fw;
    const fw: NexyFramework = fwStr
      ? (fwStr as NexyFramework)
      : frameworkFromExt(path);
    imports.push({ path, name: alias || symbol, framework: fw });
  }

  return imports;
}

export function extractProps(header: string): NexyProp[] {
  const props: NexyProp[] = [];
  let m: RegExpExecArray | null;
  while ((m = PROP_RE.exec(header)) !== null) {
    props.push({
      name: m[1],
      type: m[2].trim(),
      defaultValue: m[3]?.trim() || undefined,
    });
  }
  return props;
}

export function parseHeader(text: string): { imports: NexyImport[]; props: NexyProp[] } {
  const header = extractHeader(text);
  if (!header) return { imports: [], props: [] };
  return {
    imports: extractImports(header),
    props: extractProps(header),
  };
}

export function extractHeaderVariables(header: string): string[] {
  const vars: string[] = [];
  const lines = header.split("\n");
  for (const line of lines) {
    if (/: prop\[/.test(line)) continue;
    const m = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?!=)/);
    if (m) vars.push(m[1]);
  }
  return vars;
}

export const NEXY_BUILTIN_COMPONENTS = new Set([
  "Slot", "Fragment", "ClientOnly", "Head", "Html", "Body",
]);

export function findUsedComponents(template: string): string[] {
  const names = [...template.matchAll(/<([A-Z][A-Za-z0-9_]*)/g)].map((m) => m[1]);
  return [...new Set([...names, ...NEXY_BUILTIN_COMPONENTS])];
}
