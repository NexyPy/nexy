interface StyleTag {
  lang: string;
  content: string;
  start: number;
  end: number;
}

interface ScriptTag {
  lang: string;
  content: string;
  start: number;
  end: number;
}

const STYLE_RE = /<style\b(?:\s+lang\s*=\s*["'](?<lang>[^"']+)["'])?[^>]*>(?<content>[\s\S]*?)<\/style>/gi;
const SCRIPT_RE = /<script\b(?:\s+lang\s*=\s*["'](?<lang>[^"']+)["'])?[^>]*>(?<content>[\s\S]*?)<\/script>/gi;

export function extractStyleTags(template: string): StyleTag[] {
  const tags: StyleTag[] = [];
  let m: RegExpExecArray | null;
  while ((m = STYLE_RE.exec(template)) !== null) {
    tags.push({
      lang: m.groups?.lang?.toLowerCase() || "css",
      content: m.groups!.content,
      start: m.index,
      end: m.index + m[0].length,
    });
  }
  return tags;
}

export function extractScriptTags(template: string): ScriptTag[] {
  const tags: ScriptTag[] = [];
  let m: RegExpExecArray | null;
  while ((m = SCRIPT_RE.exec(template)) !== null) {
    tags.push({
      lang: m.groups?.lang?.toLowerCase() || "javascript",
      content: m.groups!.content,
      start: m.index,
      end: m.index + m[0].length,
    });
  }
  return tags;
}
