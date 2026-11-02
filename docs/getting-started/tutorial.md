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

<!-- router:modular -->
Answer `No` to the file-based router prompt: `nx new` scaffolds the modular router in `src/apps/`
instead of `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Answer `Yes` to the file-based router prompt for the pages, then mount your existing `APIRouter`
in `nexyconfig.py`: the two routers coexist.
<!-- /router -->

## 2. Edit the layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` owns the HTML document (with React client routing it is `layout.tsx`). Change the `<title>`:

```nexy
<title>Notes</title>
```

Save: the browser reloads. See [Layouts](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
The controller renders `src/apps/layout.nexy` around the view, and that file owns the HTML
document. Change the `<title>`:

```nexy
<title>Notes</title>
```

Save: the browser reloads. See [Views from a controller](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Add a page

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
A controller returns a view. Create `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
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

Declare the route in `src/apps/app_controller.py` and add the controller to the module:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Open <http://localhost:3000/notes>: you should see two bullets. The part between `---` is Python,
the rest is Jinja2.
<!-- /router -->

## 4. Add an endpoint

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

You should get `[{"id":1,"text":"Buy milk"}]`. The function name is the HTTP method. Interactive API docs are at `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Add `NotesApiController` to `controllers` in `src/apps/app_module.py`, then run:

```bash
curl http://localhost:3000/api/notes
```

You should get `[{"id":1,"text":"Buy milk"}]`. The method name is the HTTP method. Interactive API docs are at `/docs`.
<!-- /router -->

## 5. Share the data

Move the list to a Python module and use it in both files:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

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
