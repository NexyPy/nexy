# How do I deploy a Nexy app on Vercel?

Run `nx add vercel`, commit the generated files together with your `nx build` output, and point the Vercel Python runtime at `src/server.py:app`.

## Add the platform files

From the root of a Nexy project:

```bash
nx add vercel
nx build
```

`nx add vercel` writes `src/server.py` and `vercel.json`. It also appends ignore rules for the files that change while the app runs: `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` and `__pycache__/`. Running the command again keeps files that already exist and does not duplicate the ignore rules.

## Point Vercel at the app

In the Vercel project settings, select the Python runtime and use `src/server.py:app` as the entry point. Vercel discovers the name `app` in that module; `nx start` is not involved.

The generated `src/server.py` imports the lazy `nexy.app.app` after it has prepared the working folder. You can use the same entry point with `uvicorn src.server:app` locally.

## Commit the build output

When Vercel has no build command, it receives only what the repository contains. Commit `__nexy__/` after every `nx build`, with the compiled routes, the client bundle under `__nexy__/client/` and the manifest at `__nexy__/client/.vite/manifest.json`.

Keep `vite.config.ts` at the project root and commit it. In production Nexy reads the Vite manifest to write the stylesheet and script tags, but it emits those tags only when `vite.config.ts` exists. Without that file the page still answers 200 and arrives without CSS or client JavaScript.

Do not commit `__nexy__/build-cache.json`: it contains absolute paths from the machine that ran the build. `__nexy__/server.port` belongs to `nx start`, and `__nexy__/.temp/` is scratch space.

## Accept a read-only filesystem

Vercel mounts the project read-only while a Python application starts. Nexy writes generated files during startup, so a bare `from nexy.app import app` can fail with `OSError: [Errno 30] Read-only file system`.

The generated entry point copies six project items into a writable temporary folder before importing the app: `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` and `vite.config.ts`. It changes the working directory and puts the copy first on `sys.path`, because Nexy resolves routes from the current directory. Add any other file your app reads at runtime to that list by hand.

## Cache static assets

The generated `vercel.json` contains the two cache rules that a deployed Nexy site uses: files under `/assets/` are immutable for one year, and images and fonts under `public/` stay fresh for one day with a one-week stale-while-revalidate window. Add other rules in the same file if your project needs them.

## Check the deployment

Before pushing, import the entry point and ask it for one page:

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Then open `/`, one generated route and one file under `/assets/`. Compare the response with `nx start` locally: status, content type and size should match. A page that is smaller than the local one by exactly the two client tags means `vite.config.ts` was missing from the copied project.
