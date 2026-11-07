# Crie um aplicativo de notas com Nexy, parte 5: armazene as notas em SQLite

A Parte 5 move as notas de um dicionário Python para um banco de dados SQLite, com um modelo, uma migração e duas notas para começar, e as páginas as leem a partir daí.

**Antes de começar:** o aplicativo da [parte 4](components.md).

## Instale o ORM e a ferramenta de migração

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) descreve uma tabela como uma classe Python e Alembic transforma alterações nessas classes em migrações. Nexy também não embrulha: você os usa como estão.

## Abra o banco de dados

O endereço do banco de dados vai em `.env`, na raiz do projeto. `nx migrate` e o aplicativo leem a partir daí:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` é um arquivo, `dev.db`, próximo a `nexyconfig.py`: SQLite não precisa de servidor. Mantenha `.env` fora do Git: ele contém os segredos de um banco de dados real.

O mecanismo é a conexão com o banco de dados. Ele lê `DATABASE_URL`, com o mesmo arquivo como padrão quando a variável não está definida:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Descreva uma nota

<!-- router:fbr,custom -->
```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
O modelo convive com o recurso ao qual pertence, junto ao seu controlador:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` transforma a classe em uma tabela, `note`. O `id` é fornecido pelo banco de dados quando uma nota é salva.

## Crie a tabela com uma migração

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` escreve a pasta `alembic/` e aponta para o seu modelo. `-m` compara o modelo com o banco de dados e escreve a migração que cria a tabela; `--upgrade` executa. Altere o modelo posteriormente, execute os dois últimos comandos novamente e a tabela segue.

## Leia as notas do banco de dados

As funções de `src/notes.py` mantêm seus nomes, então as páginas mudam pouco: elas agora abrem uma sessão, consultam a tabela e retornam objetos `Note` em vez de strings.

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

## Adicione duas notas para começar

Um script inicial preenche um banco de dados vazio, então cada nova cópia do projeto começa com algo para mostrar:

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

Na inicialização, Nexy importa cada módulo de `src/` para encontrar as ações de [parte 6](create-a-note.md). `if __name__ == "__main__":` mantém a semente do comando acima: importado pelo app, o arquivo apenas define `seed` e não toca em nada.

## Mostrar as notas do banco de dados

<!-- router:fbr,custom -->
```nexy filename="src/rotas/notes/index.nexy"
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

```nexy filename="src/rotas/notas/[id].nexy"
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

Abra <http://localhost:3000/notes>: os mesmos dois cartões, agora lidos em `dev.db`. Reinicie `nexy dev` e eles ainda estarão lá.

## O que você aprendeu

- SQLModel descreve uma tabela como uma classe; o mecanismo em `src/configs/db.py` abre o banco de dados.
- `nx migrate` escreve e executa as migrações: `--init` uma vez, depois `-m` e `--upgrade` por alteração.
- Páginas e controladores chamam funções Python simples que consultam o banco de dados: Nexy não adiciona nenhuma camada.

## Próximas etapas

- [Parte 6: crie uma nota a partir de um formulário](create-a-note.md)
- [SQLite](../databases/sqlite.md): pragmas, acesso assíncrono e testes em um banco de dados na memória
