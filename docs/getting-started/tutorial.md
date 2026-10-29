# Tutorial: build a notes page in 10 minutes

You will create a project, add a page, add a Python endpoint, share data between them, and build
for production. You end with one list of notes served as a page and as JSON.

New to Nexy? Do the [Quick start](quick-start.md) first: it takes three minutes.

```diagram filename="The whole tutorial in one line"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Create the project

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` comes with [uv](https://docs.astral.sh/uv/) and only creates the project. Every command after
it runs inside the project's virtual environment (or as `uv run nexy dev`).

Pick the file-based router, a web project, and any client framework (or none). Open
<http://localhost:3000>. Long steps print one line each with their duration, as `uv` does.

## 2. Edit the layout

`src/routes/layout.nexy` owns the HTML document (with React client routing it is `layout.tsx`). Change the `<title>`:

```nexy
<title>Notes</title>
```

Save: the browser reloads. See [Layouts](../routing/fbr/layouts/README.md).

## 3. Add a page

```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Open <http://localhost:3000/notes>: you should see two bullets. It is served at `/notes`. The part between `---` is Python, the rest is Jinja2.

## 4. Add an endpoint

```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

You should get `[{"id":1,"text":"Buy milk"}]`. The function name is the HTTP method. Interactive API docs are at `/docs`.

## 5. Share the data

Move the list to a Python module and use it in both files:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```

## 6. Build and serve

```bash
nx build
nx start
```

`nx build` prints each phase with its duration. `nx start` serves the compiled output with
Uvicorn: no Node process at runtime.

## Where next

- [Routing](../routing/README.md): dynamic segments and groups
- [Actions](../guides/actions.md): call Python from a form or from the client
- [Testing](../guides/testing.md): test pages and endpoints
- [Deploy](../deployment/README.md): containers and reverse proxies
