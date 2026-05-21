# Final docs structure

docs/src/routes/docs/
├── layout.nexy          → Layout with sidebar + TOC
├── index.mdx            → /docs/  (existing, unchanged)
├── getting-started.mdx  → /docs/getting-started  — Architecture & pipeline
├── FBR/
│   └── overview.mdx     → /docs/FBR/overview  — File-based routing internals
├── Modular/
│   └── overview.mdx     → /docs/Modular/overview  — Modular DI & guards
├── .nexy/
│   └── file-format.mdx  → /docs/.nexy/file-format  — Frontmatter, props, slots
├── frontend/
│   └── overview.mdx     → /docs/frontend/overview  — SSR & Vite integration
└── reference/
    ├── cli.mdx          → /docs/reference/cli  — CLI flags & config model
    └── structure.mdx    → /docs/reference/structure  — Project layout & compilation

Sidebar (src/mocks/docs/sidebar.py) updated: 6 sections → 7 links
Manifest (src/manifest.json) updated: English only, all paths valid
Raw .md files at docs/ root removed (won't be routed by Nexy)
