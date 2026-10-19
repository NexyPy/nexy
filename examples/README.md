# Nexy Examples

Minimal, runnable examples that replace the former demo application that used to
live in `src/`. Each subfolder is a self-contained Nexy app: run it from inside
the folder so the config and the file-based router resolve against it.

## Structure

```
examples/
└── minimal/            # Smallest possible file-based router app
    ├── nexyconfig.py   # App configuration (framework, ports, aliases)
    └── src/routes/     # File-based routes: one file per URL
        ├── layout.nexy # Shared HTML shell, receives `children`
        └── index.nexy  # Renders at "/"
```

## Run an example

```bash
cd examples/minimal
nexy dev
```

## Conventions

- `.nexy` files use `---` frontmatter for Python logic, then HTML-like markup.
- The file-based router reads `src/routes` relative to the app directory
  (`ROUTER_PATH` in `nexy/config`), one route file per path.
- `layout.nexy` wraps child routes and receives them through the `children`
  prop.

See `docs/` for the full router, component, and configuration reference.