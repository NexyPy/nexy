# Modular guards: who may read, write and publish

A newsroom API on the modular router of Nexy, with three levels of access. Each level is a guard: a
FastAPI dependency that reads the request and raises to refuse it, put on a controller or a method
with `@UseGuard(...)`.

| Route | Who | Guard |
|---|---|---|
| `GET /api/stories/`, `GET /api/stories/{slug}/` | anyone | none |
| `GET /api/drafts/`, `POST /api/drafts/` | any known key | `require_key`, on the controller |
| `POST /api/drafts/{slug}/publish/` | an editor's key | `require_editor`, on the controller |
| `DELETE /api/stories/{slug}/` | an editor's key | `require_editor`, on this method only |

No key, or a wrong one, answers 401; a writer's key where an editor's is needed answers 403. A draft
answers 404 to the public, as if it did not exist.

```python filename="src/apps/stories/stories_controller.py"
@Controller("/stories/{slug}")
class StoryController:
    async def get(self, slug: str): ...  # public

    @UseGuard(require_editor)  # on this method only
    async def delete(self, slug: str): ...
```

`require_editor` is built on `require_key` with `Depends`, so it checks the key first, then the
role. Keys are compared with `hmac.compare_digest`: the time of the answer does not tell how much of
a guess was right.

## Files

| File | What it does |
|---|---|
| `src/apps/guards.py` | `require_key` and `require_editor` |
| `src/apps/stories/stories_controller.py` | the four controllers, and where each guard goes |
| `src/apps/stories/stories_module.py` | the controllers, under the `/api` prefix |
| `src/apps/app_module.py` | the root module: the home page, and `imports = (StoriesModule,)` |
| `src/apps/stories/store.py` | the stories, in memory |

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/modular-guards
uv sync
npm install          # or pnpm install, bun install
uv run nexy dev
```

Then call it, and open `/docs` for the API reference:

```bash
curl localhost:3000/api/drafts/                                   # 401
curl -H "X-Api-Key: demo-writer-key" localhost:3000/api/drafts/   # 200
curl -X POST -H "X-Api-Key: demo-writer-key" localhost:3000/api/drafts/bridge-vote/publish/   # 403
curl -X POST -H "X-Api-Key: demo-editor-key" localhost:3000/api/drafts/bridge-vote/publish/   # 200
```

The two demo keys are for a first run only. Set your own before the API leaves your machine:
`NEWSROOM_KEYS="a-long-random-key:writer,another-one:editor"`.

Every address ends with `/`: a controller answers on its path with a slash, and the same path
without it redirects there (307).

The stories are kept in memory, so `nexyconfig.py` sets `useWorkers = 1`: `nx start` otherwise runs
one process per CPU on Linux and macOS, each with its own stories. A real API keeps them in a
database.

## Test it

```bash
uv run pytest
```

The tests call each route with no key, a wrong key, a writer's key and an editor's key, and follow
no redirect, so each one uses the exact address a client must use.
