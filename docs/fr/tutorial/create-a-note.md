# Créer une application de notes avec Nexy, partie 6 : créer une note à partir d'un formulaire

La partie 6 ajoute un formulaire au-dessus de la liste : il publie dans une fonction Python marquée `@Action`, qui enregistre la note, et le visiteur revient sur la liste avec la nouvelle note.

**Avant de commencer :** l'application de la [partie 5](store-the-notes.md), avec sa base de données.

## Enregistrer une note

Ajoutez une fonction qui enregistre une note et la renvoie, à côté des deux qui les lisent :

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

## Transformez-le en action

Une action est une fonction Python que le navigateur peut appeler. `@Action` le sert de `POST`, vérifie l'entrée par rapport aux indices de type et l'exécute :

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

Au démarrage, Nexy importe chaque module de `src/` et sert les actions qu'il trouve : il n'y a aucune route à déclarer, pour aucun routeur. `src/actions/` est l'endroit où ce tutoriel les conserve.

## Postez-y le formulaire

Un modèle `.nexy` connaît le chemin de chaque action comme `__actions_path["name"]`. Un simple formulaire HTML y est affiché, de sorte que la page fonctionne avant le chargement de tout script :

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
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
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

L'entrée est nommée `text`, comme le paramètre de `create_note` : c'est ainsi que le champ y accède.

## Afficher une note sous forme de texte, pas sous forme HTML

Désormais, une note est ce qu'un visiteur a tapé. Un modèle `.nexy` écrit une valeur telle quelle, donc une note `<script>…</script>` s'exécuterait dans le navigateur de tous ceux qui ouvriraient la liste. `| e` y échappe : `<` devient `&lt;` et la note s'affiche sous forme de texte.

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

Échapper à chaque valeur provenant d'un visiteur ou de la base de données. `| safe` fait le contraire : conservez-le pour le code HTML que vous avez écrit vous-même.

## Essayez-le

Tapez *Lire la documentation* et appuyez sur **Ajouter**. L'action enregistre la note, puis répond `303` à `/notes`, et le navigateur affiche à nouveau la liste, avec la troisième note en bas.

## Ce que tu as appris

- `@Action` transforme une fonction Python en un point de terminaison `POST`, avec ses indications de type comme entrée.
- Un formulaire y est publié via `__actions_path["name"]`, sans JavaScript, et revient avec `303`.
- Les noms de champs du formulaire sont les noms de paramètres de l'action.
- `| e` montre ce qu'un visiteur a tapé sous forme de texte : échappez à toute valeur qui ne vient pas de vous.

## Prochaines étapes

- [Partie 7 : afficher les erreurs de validation](validation-errors.md)
- [Actions](../guides/actions.md) : appels tapés depuis le navigateur, erreurs et sécurité
