# Build a notes app with Nexy, part 13: search the notes as you type

Part 13 adds a search box above the notes: a React island filters every note of the user at each
key press, in the browser, with no request to the server.

**Before you start:** the app of [part 12](password-reset.md). The project was created with React in
[part 1](create-the-project.md), so React is already installed.

## An island, and why here

The rest of the page stays HTML rendered by the server: the list, the forms, the pages of notes.
Only the search box needs the browser, so only the search box is React. That is an *island*: one
client component inside a server page, made interactive on its own.

## The search component

```tsx filename="src/components/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React writes `{note.text}` as text: a note `<b>x</b>` shows its brackets, with no `| e` to add.

`found` is only computed once something is typed, and that matters for the build: `nx build` renders
each island once to HTML, with placeholders instead of its props. A component that reads a list prop
during that first render gets a placeholder instead of a list, and ships no HTML. This one reads
`notes` only after a key press, so the build renders its search box and the page shows it before
any JavaScript runs.

`aria-live="polite"` makes a screen reader read the results when they change, without interrupting.

## Put the island on the page

The page passes the notes as a prop: a list of dictionaries, which Nexy turns into JSON for the
browser. Every note goes in, not only the five of the current page, so the search covers them all:

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` imports a React component into a `.nexy`
page; the tag passes its attributes as props. `notes="{{ searchable }}"` passes the Python list
itself, not a string. `directive="client:idle"` makes the island interactive once the browser has
nothing more urgent to do.

Open <http://localhost:3000/notes> and type a few letters of a note: the matching notes show under
the box at each key press. Clear the box, and the results go away.

> [!NOTE]
> The props of an island travel in the page, as JSON. Sending every note suits a few hundred of
> them; for thousands, search on the server instead, with a query and a `LIKE` filter.

## What you learned

- An island is a client component inside a server page: here, React for the search box only.
- A `.nexy` page imports it by path and passes Python values as props, serialized to JSON.
- The build renders an island once, with placeholders for its props: read list props after the
  first render, and the island ships HTML.

## Next steps

- [Part 14: tick a note without reloading the page](tick-a-note.md)
- [Islands and hydration](../rendering/islands.md): directives, props and limitations
