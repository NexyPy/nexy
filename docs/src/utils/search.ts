import { readFileSync, readdirSync, writeFileSync } from 'fs';
import { join, relative, basename } from 'path';

const LOCALES = new Set(['ar', 'de', 'es', 'fr', 'hi', 'ja', 'ko', 'pt', 'ru', 'zh']);

export interface SearchDoc {
  id: number;
  title: string;
  content: string;
  href: string;
  lang: string;
}

function stripMarkdown(text: string): string {
  return text
    .replace(/#+\s+/g, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[*_`]/g, '')
    .trim();
}

function extractTitle(content: string): string {
  const match = content.match(/^#\s+(.+)$/m);
  return match ? match[1].trim() : '';
}

function detectLocale(filename: string): string {
  const base = basename(filename.replace(/\.mdx$/, ''));
  const parts = base.split('.');
  if (parts.length > 1 && LOCALES.has(parts[parts.length - 1])) {
    return parts[parts.length - 1];
  }
  return 'en';
}

function walkMdxFiles(root: string): string[] {
  const files: string[] = [];
  try {
    const entries = readdirSync(root, { withFileTypes: true });
    for (const entry of entries) {
      const full = join(root, entry.name);
      if (entry.isDirectory()) {
        files.push(...walkMdxFiles(full));
      } else if (entry.name.endsWith('.mdx')) {
        files.push(full);
      }
    }
  } catch {}
  return files;
}

export function buildSearchIndex(docsRoot?: string): SearchDoc[] {
  const root = docsRoot ?? join(process.cwd(), 'src', 'routes', 'docs');
  const files = walkMdxFiles(root);
  const index: SearchDoc[] = [];

  for (const filePath of files) {
    const content = readFileSync(filePath, 'utf-8');
    const title = extractTitle(content);
    if (!title) continue;

    const locale = detectLocale(filePath);
    const cleanContent = stripMarkdown(content);
    const rel = relative(root, filePath).replace(/\\/g, '/');
    const parts = rel.split('/').filter((p) => !/^\(.+\)$/.test(p));
    let last = parts[parts.length - 1].replace(/\.mdx$/, '');
    if (locale !== 'en') last = last.replace(`.${locale}`, '');
    parts[parts.length - 1] = last;

    index.push({
      id: index.length,
      title,
      content: cleanContent.slice(0, 300),
      href: `/${locale}/docs/` + parts.join('/'),
      lang: locale,
    });
  }

  return index;
}

export function writeSearchIndex(index?: SearchDoc[]): string {
  const data = index ?? buildSearchIndex();
  const outputPath = join(process.cwd(), 'public', 'search_index.json');
  writeFileSync(outputPath, JSON.stringify(data, null, 2), 'utf-8');
  return outputPath;
}
