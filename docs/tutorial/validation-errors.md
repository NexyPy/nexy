# Build a notes app with Nexy, part 7: show validation errors

Part 7 refuses a note that is blank or too long, and shows why above the form, on the same page,
still without JavaScript.

**Before you start:** the app of [part 6](create-a-note.md).

## Two kinds of errors

The type hints of an Action already refuse a wrong shape: a form without a `text` field answers
`422` before `create_note` runs. A rule about the value itself, such as "not blank", is yours to
write in the Action.

## Check the note in the Action

A failure sends the visitor back to the list with the reason in the URL; a success goes back to the
list without it:

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` tells the browser to load the next page with a `GET`, so a refresh does not post the form a
second time.

## Show the reason above the form

`useSearchParams()` reads the query string of the current request:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`| e` escapes the message: the query string comes from the visitor, so it is never written into the
page as HTML. `role="alert"` makes a screen reader announce it.

`required` and `maxlength` let the browser stop most mistakes before they leave it. The Action
checks again: a request does not have to come from your form.

Add a note of three spaces: the list comes back with *A note cannot be blank.* above the form.

## What you learned

- Type hints refuse a wrong shape with `422`; rules about the value go in the Action.
- An Action can answer with a `RedirectResponse`; `303` after a form avoids a second post.
- `useSearchParams()` reads the query string, and `| e` escapes what the visitor sent.

## Next steps

- [Part 8: edit and delete a note](edit-and-delete.md)
- [Exceptions and errors](../reference/exceptions.md): every status an Action and a page can answer
