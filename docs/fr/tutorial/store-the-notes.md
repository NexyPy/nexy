# Créez une application de notes avec Nexy, partie 5 : stockez les notes dans SQLite

La partie 5 déplace les notes d'un dictionnaire Python vers une base de données SQLite, avec un modèle, une migration et deux notes pour commencer, et les pages les lisent à partir de là.

**Avant de commencer :** l'application de la [partie 4](components.md).

## Installer l'ORM et l'outil de migration

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) décrit une table comme une classe Python et Alembic transforme les modifications apportées à ces classes en migrations. Nexy ne s'emballe pas non plus : vous les utilisez tels quels.

## Ouvrir la base de données

L'adresse de la base de données est dans `.env`, à la racine du projet. `nx migrate` et l'application l'ont tous deux lu à partir de là :

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` est un fichier, `dev.db`, à côté de `nexyconfig.py` : SQLite n'a besoin d'aucun serveur. Gardez `.env` hors de Git : il détient les secrets d'une vraie base de données.

Le moteur est la connexion à la base de données. Il lit `DATABASE_URL`, avec le même fichier par défaut lorsque la variable n'est pas définie :

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Décrire une note

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
Le modèle vit avec la fonctionnalité à laquelle il appartient, à côté de son contrôleur :

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` fait de la classe une table, `note`. Le `id` est donné par la base de données lorsqu'une note est enregistrée.

## Créer la table avec une migration

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` écrit le dossier `alembic/` et le pointe vers votre modèle. `-m` compare le modèle avec la base de données et écrit la migration qui crée la table ; `--upgrade` l'exécute. Modifiez le modèle plus tard, exécutez à nouveau les deux dernières commandes et le tableau suit.

## Lire les notes de la base de données

Les fonctions de `src/notes.py` gardent leurs noms, donc les pages changent peu : elles ouvrent désormais une session, interrogent la table et renvoient des objets `Note` au lieu de chaînes.

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
```
<!-- /router -->

## Ajoutez deux notes pour commencer

Un script de départ remplit une base de données vide, de sorte que chaque nouvelle copie du projet commence par quelque chose à afficher :

<!-- router:fbr,custom -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/seed.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def seed() -> None:
    with Session(engine) as session:
        if session.exec(select(Note)).first() is None:
            session.add_all([Note(text="Buy milk"), Note(text="Ship Nexy")])
            session.commit()


if __name__ == "__main__":
    seed()
```
<!-- /router -->

```bash
python -m src.seed
```

Au démarrage, Nexy importe chaque module de `src/` pour retrouver les Actions de [partie 6](create-a-note.md). `if __name__ == "__main__":` conserve le seed de la commande ci-dessus : importé par l'application, le fichier ne définit que `seed`, et ne touche à rien.

## Afficher les notes de la base de données

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

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
  <h1>{{ note.text }}</h1>
  <a href="/notes">All notes</a>
</section>
```

```python filename="src/routes/api/notes.py"
from src.notes import all_notes


async def GET():
    return [note.model_dump() for note in all_notes()]
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
  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import all_notes, find

LAYOUT = "src/apps/layout.nexy"


def page(view: str, **context: object):
    return useViews(LAYOUT, context={"children": useViews(view, context=context)})


@Controller("/notes")
class NotesController:
    async def get(self):
        return page("src/apps/notes/notes_view.nexy")


@Controller("/notes/{id}")
class NoteController:
    async def get(self, id: int):
        note = find(id)
        if note is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=note.text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

Ouvrir <http://localhost:3000/notes> : les deux mêmes cartes, lues maintenant à partir de `dev.db`. Redémarrez `nexy dev`, et ils sont toujours là.

## Ce que tu as appris

- SQLModel décrit une table comme une classe ; le moteur dans `src/configs/db.py` ouvre la base de données.
- `nx migrate` écrit et exécute les migrations : `--init` une fois, puis `-m` et `--upgrade` par modification.
- Les pages et les contrôleurs appellent des fonctions Python simples qui interrogent la base de données : Nexy n'ajoute aucune couche.

## Prochaines étapes

- [Partie 6 : créer une note à partir d'un formulaire](create-a-note.md)
- [SQLite](../databases/sqlite.md) : pragmas, accès asynchrone et tests sur une base de données en mémoire
