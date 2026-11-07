# Erstellen Sie eine Notizen-App mit Nexy, Teil 13: Durchsuchen Sie die Notizen während der Eingabe

Teil 13 fügt über den Notizen ein Suchfeld hinzu: Eine React-Insel filtert jede Notiz des Benutzers bei jedem Tastendruck im Browser, ohne dass eine Anfrage an den Server gestellt wird.

**Bevor Sie beginnen:** die App von [Teil 12](password-reset.md). Das Projekt wurde mit React in [Teil 1](create-the-project.md) erstellt, daher ist React bereits installiert.

## Eine Insel und warum hier

Der Rest der Seite bleibt vom Server gerendertes HTML: die Liste, die Formulare, die Notizseiten. Nur das Suchfeld benötigt den Browser, daher ist nur das Suchfeld React. Das ist eine *Insel*: eine Client-Komponente innerhalb einer Serverseite, die eigenständig interaktiv ist.

## Die Suchkomponente

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

React schreibt `{note.text}` als Text: Eine Notiz `<b>x</b>` zeigt ihre Klammern, ohne `| e` zum Hinzufügen.

`found` wird erst berechnet, wenn etwas eingegeben wurde, und das ist für den Build wichtig: `nx build` rendert jede Insel einmal in HTML, mit Platzhaltern anstelle ihrer Requisiten. Eine Komponente, die beim ersten Rendern eine Listen-Requisite liest, erhält einen Platzhalter anstelle einer Liste und liefert kein HTML. Dieser liest `notes` erst nach einem Tastendruck, sodass der Build sein Suchfeld rendert und die Seite es anzeigt, bevor JavaScript ausgeführt wird.

`aria-live="polite"` lässt einen Bildschirmleser die Ergebnisse vorlesen, wenn sie sich ändern, ohne sie zu unterbrechen.

## Bringen Sie die Insel auf die Seite

Die Seite übergibt die Notizen als Requisite: eine Liste von Wörterbüchern, die Nexy für den Browser in JSON umwandelt. Jede Notiz geht ein, nicht nur die fünf der aktuellen Seite, daher deckt die Suche alle ab:

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

`from "@/components/NoteSearch.tsx" import NoteSearch` importiert eine React-Komponente in eine `.nexy`-Seite; Das Tag übergibt seine Attribute als Requisiten. `notes="{{ searchable }}"` übergibt die Python-Liste selbst, keine Zeichenfolge. `directive="client:idle"` macht die Insel interaktiv, sobald der Browser nichts Dringenderes zu tun hat.

Öffnen Sie <http://localhost:3000/notes> und geben Sie einige Buchstaben einer Notiz ein: Die entsprechenden Notizen werden bei jedem Tastendruck unter dem Feld angezeigt. Leeren Sie das Kästchen und die Ergebnisse verschwinden.

> [!NOTE]
> Die Requisiten einer Insel wandern auf der Seite als JSON. Das Versenden jeder Notiz passt zu ein paar Hundert von ihnen; Suchen Sie für Tausende stattdessen auf dem Server mit einer Abfrage und einem `LIKE`-Filter.

## Was du gelernt hast

- Eine Insel ist eine Client-Komponente innerhalb einer Serverseite: hier React nur für das Suchfeld.
- Eine `.nexy`-Seite importiert sie nach Pfad und übergibt Python-Werte als Requisiten, serialisiert in JSON.
- Der Build rendert eine Insel einmal mit Platzhaltern für ihre Requisiten: Listen Sie die Requisiten nach dem ersten Rendern auf, und die Insel liefert HTML aus.

## Nächste Schritte

- [Teil 14: Eine Notiz ankreuzen, ohne die Seite neu zu laden](tick-a-note.md)
- [Inseln und Flüssigkeitszufuhr](../rendering/islands.md): Richtlinien, Requisiten und Einschränkungen
