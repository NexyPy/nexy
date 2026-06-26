import * as fs from "fs";
import * as path from "path";
import { MdxMapping } from "./types";

export interface NexyConfig {
  useAliases: Record<string, string>;
}

/** Walk up from startDir to find workspace root containing nexyconfig.py or src/mdxconfig. */
export function findWorkspaceRoot(startDir: string): string | null {
  let dir = startDir;
  while (dir !== path.parse(dir).root) {
    if (fs.existsSync(path.join(dir, "nexyconfig.py"))) return dir;
    if (fs.existsSync(path.join(dir, "src", "mdxconfig"))) return dir;
    dir = path.dirname(dir);
  }
  return null;
}

const MDX_MAPPING_RE = /^\s*(\w+):\s*use\s+\{\s*(\w*)\s*\}\s+from\s+"([^"]*)"\s*$/;

export function parseMdxConfig(workspaceRoot: string): MdxMapping[] {
  const configPath = path.join(workspaceRoot, "src", "mdxconfig");
  if (!fs.existsSync(configPath)) return [];

  const content = fs.readFileSync(configPath, "utf8");
  const mappings: MdxMapping[] = [];

  for (const line of content.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const m = MDX_MAPPING_RE.exec(trimmed);
    if (!m) continue;
    mappings.push({ element: m[1], symbol: m[2], source: m[3] });
  }

  return mappings;
}

export function parseNexyConfig(workspaceRoot: string): NexyConfig {
  const configPath = path.join(workspaceRoot, "nexyconfig.py");
  const config: NexyConfig = { useAliases: {} };

  if (fs.existsSync(configPath)) {
    const content = fs.readFileSync(configPath, "utf8");
    
    // Simple Regex extraction for useAliases (KISS)
    // Supports: useAliases: dict[str, str] = {"@": "src/components"}
    const aliasRegex = /useAliases\s*(?::[^=]+)?\s*=\s*({[\s\S]*?})/;
    const match = content.match(aliasRegex);
    
    if (match) {
      try {
        // Clean up Python dict string to approximate JSON
        let jsonStr = match[1]
          .replace(/'/g, '"')          // Single quotes -> double quotes
          .replace(/#.*$/gm, "")       // Remove comments
          .replace(/,\s*}/g, "}");     // Remove trailing commas
          
        config.useAliases = JSON.parse(jsonStr);
      } catch (e) {
        console.error("Error parsing aliases in nexyconfig.py", e);
      }
    }
  }

  return config;
}

const RESOLVE_EXTS = [".nexy", ".mdx", ".tsx", ".jsx", ".vue", ".svelte", ".py"];

/** Convert Python dotted module path to filesystem path and resolve. */
export function resolvePythonModulePath(impPath: string, workspaceRoot: string): string | null {
  if (!impPath.includes(".") || impPath.startsWith(".") || impPath.includes("/") || impPath.startsWith("@")) return null;

  const fsPath = path.join(workspaceRoot, ...impPath.split("."));
  // Try exact path as file (not directory)
  if (fs.existsSync(fsPath) && fs.statSync(fsPath).isFile()) return fsPath;
  // Try with extensions
  for (const ext of RESOLVE_EXTS) {
    const candidate = fsPath + ext;
    if (fs.existsSync(candidate)) return candidate;
  }
  // Try as package: dir/__init__.ext
  for (const ext of [".py", ".nexy"]) {
    const initPath = path.join(fsPath, `__init__${ext}`);
    if (fs.existsSync(initPath)) return initPath;
  }
  return null;
}

export function resolveWithAlias(importPath: string, workspaceRoot: string, aliases: Record<string, string>): string | null {
  // Sort aliases by length descending to match longest prefix first
  const sortedAliases = Object.entries(aliases).sort((a, b) => b[0].length - a[0].length);

  for (const [alias, replacement] of sortedAliases) {
    if (importPath === alias || importPath.startsWith(alias)) {
      const relativePart = importPath.slice(alias.length);
      // Handle cases where alias doesn't end with / but import does (e.g., @ -> src/ and @components)
      const cleanRelativePart = relativePart.startsWith("/") ? relativePart.slice(1) : relativePart;
      return path.resolve(workspaceRoot, replacement, cleanRelativePart);
    }
  }
  return null;
}
