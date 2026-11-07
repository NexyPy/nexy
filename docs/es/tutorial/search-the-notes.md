# Crea una aplicación de notas con Nexy, parte 13: busca las notas mientras escribes

La parte 13 agrega un cuadro de búsqueda encima de las notas: una isla React filtra cada nota del usuario con cada pulsación de tecla, en el navegador, sin ninguna solicitud al servidor.

**Antes de comenzar:** la aplicación de la [parte 12](password-reset.md). El proyecto se creó con React en la [parte 1](create-the-project.md), por lo que React ya está instalado.

## Una isla, y por qué aquí

El resto de la página sigue siendo HTML renderizado por el servidor: la lista, los formularios, las páginas de notas. Solo el cuadro de búsqueda necesita el navegador, por lo que solo el cuadro de búsqueda es React. Esa es una *isla*: un componente de cliente dentro de una página de servidor, que se vuelve interactivo por sí solo.

## El componente de búsqueda

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

React escribe `{note.text}` como texto: una nota `<b>x</b>` muestra sus corchetes, sin `| e` para agregar.

`found` solo se calcula una vez que se escribe algo, y eso es importante para la compilación: `nx build` representa cada isla una vez en HTML, con marcadores de posición en lugar de sus accesorios. Un componente que lee una propiedad de lista durante ese primer renderizado obtiene un marcador de posición en lugar de una lista y no incluye HTML. Este lee `notes` solo después de presionar una tecla, por lo que la compilación muestra su cuadro de búsqueda y la página lo muestra antes de que se ejecute cualquier JavaScript.

`aria-live="polite"` hace que un lector de pantalla lea los resultados cuando cambian, sin interrumpir.

## Pon la isla en la página.

La página pasa las notas como accesorio: una lista de diccionarios, que Nexy convierte en JSON para el navegador. Cada nota entra, no sólo las cinco de la página actual, por lo que la búsqueda las cubre todas:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
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

`from "@/components/NoteSearch.tsx" import NoteSearch` importa un componente React en una página `.nexy`; la etiqueta pasa sus atributos como accesorios. `notes="{{ searchable }}"` pasa la lista Python en sí, no una cadena. `directive="client:idle"` hace que la isla sea interactiva una vez que el navegador no tiene nada más urgente que hacer.

Abra <http://localhost:3000/notes> y escriba algunas letras de una nota: las notas coincidentes se muestran debajo del cuadro cada vez que presiona una tecla. Borre la casilla y los resultados desaparecerán.

> [!NOTE]
> Los accesorios de una isla viajan en la página, como JSON. Enviar cada nota conviene a unos cientos de ellos; para miles, busque en el servidor, con una consulta y un filtro `LIKE`.

## lo que aprendiste

- Una isla es un componente de cliente dentro de una página de servidor: aquí, React solo para el cuadro de búsqueda.
- Una página `.nexy` la importa por ruta y pasa valores Python como accesorios, serializados en JSON.
- La construcción representa una isla una vez, con marcadores de posición para sus accesorios: lea la lista de accesorios después del primer renderizado y la isla envía HTML.

## Próximos pasos

- [Parte 14: marca una nota sin recargar la página](tick-a-note.md)
- [Islas e hidratación](../rendering/islands.md): directivas, puntales y limitaciones
