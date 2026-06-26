# Nexy Documentation

docs/src/routes/docs/
├── layout.nexy                → Sidebar + TOC + breadcrumb
├── index.mdx                  → /docs  — Introduction (FR)
├── create_a_projet.mdx        → /docs/create_a_projet  — Project creation (FR)
├── projet_structure.mdx       → /docs/projet_structure  — Project layout (FR)
├── build_and_deploy.mdx       → /docs/build_and_deploy  — Build & deploy (EN)
├── fbrouters/
│   ├── index.mdx              → /docs/fbrouters  — FBR overview (FR)
│   ├── pages.mdx              → /docs/fbrouters/pages  — Pages (FR)
│   ├── layouts.mdx            → /docs/fbrouters/layouts  — Layouts (FR)
│   ├── dependencies.mdx       → /docs/fbrouters/dependencies  — Dependencies (FR)
│   ├── middlewares.mdx        → /docs/fbrouters/middlewares  — Middlewares (FR)
│   ├── route_handlers.mdx     → /docs/fbrouters/route_handlers  — API handlers (FR)
│   ├── route_parameters.mdx   → /docs/fbrouters/route_parameters  — Dynamic routes (FR)
│   └── query_parameters.mdx   → /docs/fbrouters/query_parameters  — Query strings (FR)
├── components/
│   ├── index.mdx              → /docs/components  — Component system (EN)
│   ├── usage.mdx              → /docs/components/usage  — Creating components (EN)
│   ├── markup.mdx             → /docs/components/markup  — Template syntax (EN)
│   ├── python.mdx             → /docs/components/python  — Python frontmatter (EN)
│   ├── properties.mdx         → /docs/components/properties  — Props (EN)
│   ├── conditional.mdx        → /docs/components/conditional  — Conditions (EN)
│   └── modules.mdx            → /docs/components/modules  — Module system (EN)
├── frontend/
│   └── index.mdx              → /docs/frontend/overview  — SSR & Vite (EN)
├── Modular/
│   └── overview.mdx           → /docs/modular/overview  — DI & guards (EN)
├── nexy-file/
│   └── file-format.mdx        → /docs/nexy-file/file-format  — .nexy spec (EN)
└── reference/
    ├── cli.mdx                → /docs/reference/cli  — CLI flags (EN)
    └── structure.mdx          → /docs/reference/structure  — Compilation (EN)

## Sources
- Sidebar: `src/mocks/docs/sidebar.py` — FBR, Components, Getting Started
- Nav manifest: `src/manifest.json` — Site-wide navigation metadata
- Layout: `src/routes/docs/layout.nexy` — Wraps every doc page
- Style: `src/globale.css` — Tailwind v4 + custom `.toc`, `.sidebar`, `.mdx-content`
