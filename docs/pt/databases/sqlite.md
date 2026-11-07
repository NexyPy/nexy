# Use SQLite com Nexy

SQLite é o banco de dados que um novo projeto Nexy usa quando `DATABASE_URL` não está definido: um arquivo, nenhum servidor e o próprio driver de Python, através de SQLModel, SQLAlchemy ou Tortoise-ORM.

## Quando SQLite cabe

- Desenvolvimento, testes e demonstrações: nada para instalar ou iniciar.
- Um site com um servidor e escrita modesta: um blog, uma ferramenta interna, uma pequena loja.
- Dados pesados ​​de leitura enviados com o aplicativo.

Escolha [PostgreSQL](postgresql.md) quando vários servidores escrevem ao mesmo tempo ou quando você precisa de tipos ricos e pesquisa de texto completo em escala.

## A cadeia de conexão

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Banco de dados |
|---|---|
| `sqlite:///dev.db` | `dev.db`, relativo à pasta `nx dev` em que é executado |
| `sqlite:////var/data/app.db` | um caminho absoluto: quatro barras |
| `sqlite://` | na memória, desaparece quando o processo para |
| `sqlite+aiosqlite:///dev.db` | o mesmo arquivo, através do driver assíncrono |

## O motor

`nx new` grava este arquivo quando você escolhe SQLModel. A única linha a ser adicionada para SQLite é `check_same_thread`: uma página e um manipulador podem usar o mecanismo de threads diferentes.

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)
```

## Chaves estrangeiras e WAL

SQLite não impõe chaves estrangeiras a menos que solicitado, por conexão. O modo WAL permite que os leitores continuem enquanto um escritor escreve. Ambos são `PRAGMA` executados em cada nova conexão, configurados próximos ao mecanismo:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlalchemy import event
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.getenv("DATABASE_URL", "sqlite:///dev.db"),
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_pragmas(connection, _record) -> None:
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()
```

## Um modelo

```python filename="src/models/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Uma sessão por solicitação

Uma dependência abre uma sessão para a solicitação e a fecha após a resposta:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Ler e escrever de um manipulador

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


async def GET(session: Session = Depends(get_session)):
    return session.exec(select(Note)).all()


async def POST(body: NewNote, session: Session = Depends(get_session)):
    note = Note(title=body.title)
    session.add(note)
    session.commit()
    session.refresh(note)
    return JSONResponse(note.model_dump(), status_code=201)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_api_controller.py"
from pydantic import BaseModel
from sqlmodel import Session, select

from nexy.decorators import Controller
from nexy.http import Depends, JSONResponse
from src.configs.session import get_session
from src.models.note_model import Note


class NewNote(BaseModel):
    title: str


@Controller("/api/notes")
class NotesApiController:
    async def get(self, session: Session = Depends(get_session)):
        return session.exec(select(Note)).all()

    async def post(self, body: NewNote, session: Session = Depends(get_session)):
        note = Note(title=body.title)
        session.add(note)
        session.commit()
        session.refresh(note)
        return JSONResponse(note.model_dump(), status_code=201)
```

Liste o controlador em `controllers` do módulo raiz.
<!-- /router -->

## Ler de uma página

Uma página `.nexy` executa seu frontmatter no servidor, para que possa chamar o mesmo código. Mantenha a consulta em uma função: apenas os nomes atribuídos no nível superior do frontmatter chegam ao template.

```python filename="src/services/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.services.notes import open_notes

notes = open_notes()
---
<ul>
  {% for note in notes %}
  <li>{{ note.title | e }}</li>
  {% endfor %}
</ul>
```

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/notes/notes_view.nexy")
```
<!-- /router -->

## Crie as tabelas com migrações

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` escreve `alembic/env.py`, que importa os modelos que compara com o banco de dados. Importe cada novo módulo de modelo para lá:

```python filename="alambique/env.py"
import src.models.note_model  # noqa: F401
```

SQLite não pode `ALTER` a maioria das colunas no lugar. Ative o modo batch de Alembic, que copia a tabela, em ambas as chamadas `context.configure(...)` de `alembic/env.py`:

```python filename="alambique/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Assíncrono com `aiosqlite`

```bash
uv add aiosqlite
```

```python filename="src/configs/async_db.py"
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

async_engine = create_async_engine("sqlite+aiosqlite:///dev.db")


async def get_async_session():
    async with AsyncSession(async_engine) as session:
        yield session
```

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes/count.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


async def GET(session: AsyncSession = Depends(get_async_session)):
    count = (await session.exec(select(func.count()).select_from(Note))).one()
    return {"count": count}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/notes_count_api_controller.py"
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from nexy.decorators import Controller
from nexy.http import Depends
from src.configs.async_db import get_async_session
from src.models.note_model import Note


@Controller("/api/notes/count")
class NotesCountApiController:
    async def get(self, session: AsyncSession = Depends(get_async_session)):
        count = (await session.exec(select(func.count()).select_from(Note))).one()
        return {"count": count}
```

Liste o controlador em `controllers` do módulo raiz.
<!-- /router -->

## Testes em um banco de dados na memória

`StaticPool` mantém uma conexão, então o banco de dados na memória permanece durante todo o teste. A dependência do manipulador é trocada por outra que o utiliza:

```python filename="testes/test_notes.py"
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from nexy.app import app
from src.configs.session import get_session

test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
SQLModel.metadata.create_all(test_engine)


def override_session():
    with Session(test_engine) as session:
        yield session


def test_a_note_is_created():
    app.dependency_overrides[get_session] = override_session
    client = TestClient(app)
    client.post("/api/notes", json={"title": "Write the docs"})
    assert client.get("/api/notes").json()[0]["title"] == "Write the docs"
```

## Em produção

- **Mantenha o arquivo em um disco permanente.** O próprio sistema de arquivos de um contêiner é perdido na reimplantação: monte um volume e aponte `DATABASE_URL` para ele com um caminho absoluto.
- **Um servidor, um arquivo.** SQLite tem um gravador por vez. Vários `nx start` trabalhadores na mesma máquina estão bem com o WAL; várias máquinas não são.
- **Faça backup enquanto ele é executado** com `sqlite3 app.db ".backup backup.db"`, não com uma cópia do arquivo.

## Próximas etapas

- [Bancos de dados](../guides/databases.md)
- [Use PostgreSQL com Nexy](postgresql.md)
- [Teste](../guides/testing.md)
