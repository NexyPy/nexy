# Cree una aplicación de notas con Nexy, parte 7: muestre errores de validación

La Parte 7 rechaza una nota que esté en blanco o sea demasiado larga, y muestra el motivo arriba del formulario, en la misma página, aún sin JavaScript.

**Antes de comenzar:** la aplicación de la [parte 6](create-a-note.md).

## Dos tipos de errores

Las sugerencias de tipo de una Acción ya rechazan una forma incorrecta: un formulario sin un campo `text` responde `422` antes de que se ejecute `create_note`. Puede escribir una regla sobre el valor en sí, como "no en blanco", en la Acción.

## Consulta la nota en la Acción.

Un error envía al visitante de regreso a la lista con el motivo en la URL; un éxito vuelve a la lista sin él:

```python filename="src/acciones/notas.py"
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

`303` le dice al navegador que cargue la página siguiente con un `GET`, por lo que una actualización no publica el formulario por segunda vez.

## Muestra el motivo encima del formulario.

`useSearchParams()` lee la cadena de consulta de la solicitud actual:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
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

`| e` escapa del mensaje: la cadena de consulta proviene del visitante, por lo que nunca se escribe en la página como HTML. `role="alert"` hace que un lector de pantalla lo anuncie.

`required` y `maxlength` permiten que el navegador detenga la mayoría de los errores antes de que lo abandonen. La Acción vuelve a comprobar: no es necesario que una solicitud provenga de su formulario.

Agregue una nota de tres espacios: la lista volverá con *Una nota no puede estar en blanco* encima del formulario.

## lo que aprendiste

- Las sugerencias de tipo rechazan una forma incorrecta con `422`; Las reglas sobre el valor van en la acción.
- Una Acción puede responder con un `RedirectResponse`; `303` después de un formulario evita una segunda publicación.
- `useSearchParams()` lee la cadena de consulta y `| e` escapa de lo que envió el visitante.

## Próximos pasos

- [Parte 8: editar y eliminar una nota](edit-and-delete.md)
- [Excepciones y errores](../reference/exceptions.md): cada estado que una Acción y una página pueden responder
