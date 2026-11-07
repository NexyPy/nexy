# Build a notes app with Nexy, part 4: components

Part 4 turns each note into a reusable component, a `.nexy` file you import like a Python name and
use like an HTML tag.

**Before you start:** the app of [part 3](dynamic-routes.md).

## Write the component

A component is a `.nexy` file outside the routes. Its props are declared with `prop[...]`, and the
caller passes them as attributes:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

The `<style>` block is sent with every page that uses the card. It is not scoped: `.note` is one
class for the whole page, so give the classes of a component names that only it uses.

## Use it in the list

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` is the import alias of part 1: it points to `src/`. The file name is the component name, in
PascalCase: `NoteCard.nexy` exports `NoteCard`.

Open <http://localhost:3000/notes>: each note is now a card.

## What you learned

- A `.nexy` file outside the routes is a component; its `prop[...]` are its attributes.
- `from "@/components/x.nexy" import X` imports it; `<X />` renders it.
- A `<style>` block is not scoped: name the classes of a component after it.

## Next steps

- [Part 5: store the notes in SQLite](store-the-notes.md)
- [Components](../views/nexy/components.md): `Image`, `Link` and the built-in helpers
