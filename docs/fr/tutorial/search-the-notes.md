# Créez une application de notes avec Nexy, partie 13 : recherchez les notes pendant que vous tapez

La partie 13 ajoute un champ de recherche au dessus des notes : un îlot React filtre chaque note de l'utilisateur à chaque appui sur une touche, dans le navigateur, sans aucune requête au serveur.

**Avant de commencer :** l'application de la [partie 12](password-reset.md). Le projet a été créé avec React dans la [partie 1](create-the-project.md), donc React est déjà installé.

## Une île, et pourquoi ici

Le reste de la page reste HTML rendu par le serveur : la liste, les formulaires, les pages de notes. Seul le champ de recherche a besoin du navigateur, donc seul le champ de recherche est React. Il s'agit d'une *île* : un composant client à l'intérieur d'une page serveur, rendu interactif par lui-même.

## Le composant de recherche

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

React écrit `{note.text}` sous forme de texte : une note `<b>x</b>` montre ses crochets, sans `| e` à ajouter.

`found` n'est calculé qu'une fois que quelque chose est tapé, et cela compte pour la construction : `nx build` restitue chaque île une fois au format HTML, avec des espaces réservés au lieu de ses accessoires. Un composant qui lit un accessoire de liste lors de ce premier rendu obtient un espace réservé au lieu d'une liste et ne fournit aucun code HTML. Celui-ci ne lit `notes` qu'après avoir appuyé sur une touche, de sorte que la construction affiche son champ de recherche et la page l'affiche avant toute exécution de JavaScript.

`aria-live="polite"` permet à un lecteur d'écran de lire les résultats lorsqu'ils changent, sans interruption.

## Mettez l'île sur la page

La page transmet les notes comme accessoire : une liste de dictionnaires, que Nexy transforme en JSON pour le navigateur. Chaque note est saisie, pas seulement les cinq de la page actuelle, la recherche les couvre donc toutes :

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

`from "@/components/NoteSearch.tsx" import NoteSearch` importe un composant React dans une page `.nexy` ; la balise transmet ses attributs sous forme d'accessoires. `notes="{{ searchable }}"` transmet la liste Python elle-même, pas une chaîne. `directive="client:idle"` rend l'île interactive une fois que le navigateur n'a plus rien de plus urgent à faire.

Ouvrez <http://localhost:3000/notes> et tapez quelques lettres d'une note : les notes correspondantes s'affichent sous la case à chaque pression sur une touche. Décochez la case et les résultats disparaissent.

> [!NOTE]
> Les accessoires d'une île voyagent dans la page, au format JSON. Envoyer chaque note convient à quelques centaines d’entre eux ; pour des milliers, recherchez plutôt sur le serveur, avec une requête et un filtre `LIKE`.

## Ce que tu as appris

- Un îlot est un composant client au sein d'une page serveur : ici, React pour le champ de recherche uniquement.
- Une page `.nexy` l'importe par chemin et transmet les valeurs Python comme accessoires, sérialisées en JSON.
- La construction restitue une île une fois, avec des espaces réservés pour ses accessoires : lisez la liste des accessoires après le premier rendu, et l'île expédie du HTML.

## Prochaines étapes

- [Partie 14 : cocher une note sans recharger la page](tick-a-note.md)
- [Îles et hydratation](../rendering/islands.md) : directives, accessoires et limites
