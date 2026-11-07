# Build a notes app with Nexy, part 2: pages and layouts

Part 2 adds the page that lists the notes, and shows how the layout wraps it in the HTML document.

**Before you start:** the project of [part 1](create-the-project.md), with `nexy dev` running.

## Add the notes page

<!-- router:fbr,custom -->
A page is a file under `src/routes/`, and its path is its URL. Create the notes page:

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` answers `/notes`.
<!-- /router -->

<!-- router:modular -->
A controller answers a URL and returns a view. Give the notes their own folder, with a view:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

and the controller that renders it at `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

A controller answers only once a module lists it. Add it to the root module:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Open <http://localhost:3000/notes>: you should see two bullets. The part between the two `---` lines
is Python, run on the server; the rest is HTML with Jinja2 tags such as `{% for %}` and `{{ note }}`.

## Change the layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` owns the HTML document: `<html>`, `<head>` and `<body>`. Nexy wraps every
page in it, where it writes `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` owns the HTML document: `<html>`, `<head>` and `<body>`. The controller wraps
its view in it by passing the view as `children`.
<!-- /router -->

Open the layout and change the line `<title>Nexy App</title>` to:

```html
<title>Notes</title>
```

Save: the tab of the browser now reads *Notes*, on every page.

## Give the pages room below the header

The header of the layout is fixed: it stays at the top of the window, over the page. The pages of
the starter set their own space below it; the pages of the notes app share one class for that,
`app-page`, which every page of the tutorial puts around its content. Add it at the end of
`src/globale.css`, the stylesheet every page already loads:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, which the starter uses, removes the borders of form fields: these rules give them back,
so the forms of the next parts can be seen.

## What you learned

<!-- router:fbr,custom -->
- A `.nexy` file under `src/routes/` is a page; its folder and name are its URL.
- The root `layout.nexy` wraps every page in the HTML document.
<!-- /router -->
<!-- router:modular -->
- A controller answers a URL and renders a `.nexy` view with `useViews`; a module lists it.
- The layout is a view too: the controller passes the page view to it as `children`.
<!-- /router -->
- A `.nexy` file is Python between `---`, then HTML with Jinja2.
- `src/globale.css` holds the styles every page shares, such as `app-page`.

## Next steps

- [Part 3: dynamic routes and an API](dynamic-routes.md)
- [.nexy files](../views/nexy/README.md): props, components and styles
