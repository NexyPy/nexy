# Nexy VSCode Extension — Agent Guide

## Vision

Offrir une expérience de développement **équivalente à Vue (Volar), Svelte, ou Astro** pour `.nexy` et `.mdx` — IntelliSense complète (complétion, hover, go-to-definition, rename, folding, code actions, diagnostics) pour tous les langages embarqués : Python (`---`), Jinja2 (`{{ }}`/`{% %}`/`{# #}`), HTML, CSS/SCSS/Less (`<style>`), JS/TS/TSX/JSX/Rust (`<script>`), Markdown (`.mdx`).

## Architecture

```
extensions/vscode/
├── package.json                    # Manifeste
├── esbuild.js                      # Build client + server
├── tsconfig.json                   # TypeScript strict
├── vitest.config.ts                # Tests unitaires (vitest)
├── language-configuration.json     # Brackets, commentaires
├── fileicons/                      # Icônes Seti + Nexy
├── syntaxes/
│   ├── nexy.tmLanguage.json        # Grammaire .nexy
│   ├── mdx.tmLanguage.json         # Grammaire .mdx
│   └── jinja2-injection.json       # Injection {{ }} dans strings HTML
├── src/
│   ├── extension.ts                # Entry point
│   ├── semantic.tokens.ts          # Semantic tokens client-side
│   │
│   ├── client/                     # ☆ Côté VSCode (process UI)
│   │   ├── lspClient.ts            #   LSP client bootstrap
│   │   ├── statusBar.ts            #   Barre d'état
│   │   ├── decorations.ts          #   Couleurs par framework
│   │   ├── commands.ts             #   toggleComment, insertImport
│   │   └── providers/
│   │       ├── embedded.provider.ts #    Documents virtuels (py/html/css/js)
│   │       ├── service.delegation.ts#    Délégation aux services natifs
│   │       └── formatting.ts       #    Format on save (ruff + prettier)
│   │
│   ├── server/                     # ☆ LSP serveur (process séparé)
│   │   ├── server.ts               #   Bootstrap + wiring
│   │   ├── indexer.ts              #   Indexeur de projet + résolution imports
│   │   ├── regions.ts              #   Découpage en régions (header/template/…)
│   │   └── handlers/               #   1 handler par feature LSP
│   │       ├── completion.ts       #     Auto-complétion
│   │       ├── diagnostics.ts      #     Diagnostics
│   │       ├── hover.ts            #     Infobulle
│   │       ├── definition.ts       #     Go to definition
│   │       ├── references.ts       #     Find references
│   │       ├── rename.ts           #     Renommer (prepare + handle)
│   │       ├── fold.ts             #     Code folding
│   │       ├── code.actions.ts     #     Quick fixes
│   │       └── code.lens.ts        #     Code Lens
│   │   └── features/               #    Utilitaires standalone (pas des handlers)
│   │       └── semanticTokens.ts   #     Semantic tokens LSP
│   │
│   └── shared/                     # ☆ Types + parsers (0 dépendance VSCode/LSP)
│       ├── types.ts                #   Toutes les interfaces
│       ├── nexy.config.parser.ts   #   findWorkspaceRoot, parseNexyConfig, parseMdxConfig
│       └── parser/
│           ├── header.ts           #   extractHeader, extractProps, findUsedComponents…
│           ├── template.ts         #   extractStyleTags, extractScriptTags
│           └── jinja.ts            #   extractJinjaExpressions, extractFilters…
│
└── test/                           # ☆ Tests unitaires (vitest)
    ├── parser/
    │   ├── header.test.ts
    │   ├── template.test.ts
    │   └── jinja.test.ts
    ├── nexy.config.parser.test.ts
    └── …
```

## Principes clés

### Virtual Document Delegation
Chaque région d'un `.nexy` est projetée en document virtuel :
```
page.nexy
├── page.nexy.py            → Pylance (Python)
├── page.nexy.html          → HTML Language Service
├── page.nexy.css           → CSS Language Service(s)
└── page.nexy.jinja.py      → Jinja2 stubs + prop = Any
```
Mapping aller-retour des positions par `EmbedContentProvider`.

### Jinja2 en 3 couches
1. **Grammaire TextMate** (`jinja2-injection.json`) — colorie `{{ }}`/`{% %}`/`{# #}`, injectée aussi dans `string.quoted.*.html` pour colorer même dans les attributs
2. **Virtual Python** (`page.nexy.jinja.py`) — `{{ x\|upper }}` → stubs Python → Pylance donne complétions
3. **Strip + Remap HTML** — `{% %}`/`{{ }}`/`{# #}` remplacés par espaces avant délégation HTML

### Détection de projet
`findWorkspaceRoot()` (shared/nexy.config.parser.ts) cherche en remontant :
- `nexyconfig.py` → projet Nexy complet
- `src/mdxconfig` → projet MDX

## Philosophy (KISS · TDD · SOLID)

- **KISS**: 1 fonction = 1 responsabilité, < 20 lignes. Regex simple > AST si 95% des cas sont couverts.
- **TDD**: Un test d'abord (red), code minimal (green), puis refactor. `vitest` runner. `test/` en miroir de `src/`.
- **SOLID**: `DiagnosticHandler` → diagnostics, `ProjectIndexer` → indexation, `findWorkspaceRoot` → workspace. Chaque fichier = une responsabilité.
- **DRY**: Patterns Jinja2, extensions, couleurs définis UNE SEULE fois dans `shared/types.ts` ou `shared/parser/`.
- **Pas de dead code**: `handlers/` = 1 handler par feature LSP. `features/` = utilitaires standalone. Rien d'autre.

## Commands

```bash
pnpm vitest run                  # Tests
npx tsc --noEmit                 # Typecheck
node esbuild.js                  # Build
npx vsce package --no-dependencies  # VSIX
pnpm add -D <pkg>                # Ajouter dépendance dev
```

## Tests

49 tests, 4 fichiers, 0 échec. Tous les tests sont dans `test/` avec `vitest` :
- `test/parser/header.test.ts` — extractHeader, extractImports, extractProps, findUsedComponents
- `test/parser/template.test.ts` — extractStyleTags, extractScriptTags
- `test/parser/jinja.test.ts` — extractJinjaExpressions, extractVariables, extractFilters, isValidJinjaFilter
- `test/nexy.config.parser.test.ts` — findWorkspaceRoot, parseMdxConfig, parseNexyConfig (filesystem temp)

### Ajouter un test
1. Créer `test/<name>.test.ts`
2. `import { describe, it, expect } from "vitest"`
3. `pnpm vitest run`

### Tester du filesystem
```typescript
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

let tmpDir: string;
beforeEach(() => { tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "nexy-test-")); });
afterEach(() => { fs.rmSync(tmpDir, { recursive: true, force: true }); });
```

## Conventions

- **Langue**: 100% anglais dans les sources. Francais autorisé dans AGENTS.md.
- **Noms**: PascalCase classes/interfaces, camelCase fonctions/variables, UPPER_CASE constantes.
- **Imports**: nommés explicites, pas de `import *`.
- **Pas de `any`**: `unknown` + type guards.
- **Handler pattern**: classes avec `handle(params, doc)` retournent `T | null`.
- **Git**: Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`).

## Gotchas

- `features/semanticTokens.ts` et `src/semantic.tokens.ts` sont DEUX fichiers différents (LSP server vs client-side).
- Le fichier `_nexy.tmLanguage.json` est un brouillon — ignorer.
- `vsce package --no-dependencies` nécessaire sous pnpm.
- Pylance nécessite des vrais fichiers `.py` sur disque (`.nexy-virt/`) avec `__init__.py`.
- Position mapping fragile — tester avec accents/émojis/CRLF.
- Les trois échecs `findUsedComponents` dans les tests sont NORMAUX — `NEXY_BUILTIN_COMPONENTS` a été ajouté.
