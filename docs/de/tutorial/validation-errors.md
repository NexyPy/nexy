# Erstellen Sie eine Notizen-App mit Nexy, Teil 7: Validierungsfehler anzeigen

Teil 7 lehnt eine Notiz ab, die leer oder zu lang ist, und zeigt, warum oberhalb des Formulars auf derselben Seite immer noch ohne JavaScript.

**Bevor Sie beginnen:** die App von [Teil 6](create-a-note.md).

## Zwei Arten von Fehlern

Die Typhinweise einer Aktion verweigern bereits eine falsche Form: Ein Formular ohne ein `text`-Feld antwortet mit `422`, bevor `create_note` ausgeführt wird. Sie können in der Aktion eine Regel für den Wert selbst schreiben, z. B. „nicht leer“.

## Überprüfen Sie den Hinweis in der Aktion

Bei einem Fehler wird der Besucher mit dem Grund in der URL zurück zur Liste weitergeleitet. ein Erfolg geht ohne ihn auf die Liste zurück:

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

`303` weist den Browser mit einem `GET` an, die nächste Seite zu laden, sodass bei einer Aktualisierung das Formular nicht ein zweites Mal gepostet wird.

## Geben Sie den Grund über dem Formular an

`useSearchParams()` liest den Abfragestring der aktuellen Anfrage:

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

`| e` maskiert die Nachricht: Die Abfragezeichenfolge stammt vom Besucher und wird daher nie als HTML in die Seite geschrieben. `role="alert"` lässt einen Screenreader dies ankündigen.

`required` und `maxlength` lassen den Browser die meisten Fehler stoppen, bevor sie ihn verlassen. Die Aktion prüft noch einmal: Eine Anfrage muss nicht von Ihrem Formular kommen.

Fügen Sie eine Notiz mit drei Leerzeichen hinzu: Die Liste wird mit *Eine Notiz darf nicht leer sein.* über dem Formular angezeigt.

## Was du gelernt hast

- Typhinweise lehnen eine falsche Form mit `422` ab; Regeln über den Wert gehen in die Aktion ein.
- Eine Aktion kann mit einem `RedirectResponse` antworten; `303` nach einem Formular vermeidet einen zweiten Beitrag.
- `useSearchParams()` liest die Abfragezeichenfolge und `| e` maskiert das, was der Besucher gesendet hat.

## Nächste Schritte

- [Teil 8: Eine Notiz bearbeiten und löschen](edit-and-delete.md)
- [Ausnahmen und Fehler](../reference/exceptions.md): Auf jeden Status kann eine Aktion und eine Seite antworten
