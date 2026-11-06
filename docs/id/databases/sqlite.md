# Gunakan SQLite dengan Nexy

SQLite adalah database yang digunakan proyek Nexy baru ketika `DATABASE_URL` tidak disetel: satu file, tanpa server, dan driver Python sendiri, melalui SQLModel, SQLAlchemy atau Tortoise-ORM.

## Ketika SQLite cocok

- Pengembangan, pengujian, dan demo: tidak ada yang perlu diinstal atau dimulai.
- Sebuah situs dengan satu server dan menulis sederhana: blog, alat internal, toko kecil.
- Data berat yang dapat dibaca dikirimkan bersama aplikasi.

Pilih [PostgreSQL](postgresql.md) ketika beberapa server menulis sekaligus, atau ketika Anda memerlukan tipe kaya dan pencarian teks lengkap dalam skala besar.

## String koneksi

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

| URL | Basis data |
|---|---|
| `sqlite:///dev.db` | `dev.db`, relatif terhadap folder tempat `nx dev` dijalankan |
| `sqlite:////var/data/app.db` | jalur absolut: empat garis miring |
| `sqlite://` | dalam memori, hilang ketika proses berhenti |
| `sqlite+aiosqlite:///dev.db` | file yang sama, melalui driver async |

## Mesinnya

`nx new` menulis file ini ketika Anda memilih SQLModel. Satu baris yang ditambahkan untuk SQLite adalah `check_same_thread`: halaman dan pengendali dapat menggunakan mesin dari thread yang berbeda.

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

## Kunci asing dan WAL

SQLite tidak menerapkan kunci asing kecuali diminta, per koneksi. Mode WAL memungkinkan pembaca melanjutkan sementara seorang penulis menulis. Keduanya adalah `PRAGMA` yang dijalankan pada setiap koneksi baru, dipasang di sebelah mesin:

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

## Seorang model

```python filename="src/model/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    done: bool = False
```

## Sesi per permintaan

Ketergantungan membuka sesi untuk permintaan dan menutupnya setelah jawabannya:

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

## Membaca dan menulis dari seorang pawang

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

## Membaca dari satu halaman

Halaman `.nexy` menjalankan frontmatternya di server, sehingga dapat memanggil kode yang sama. Pertahankan kueri dalam suatu fungsi: hanya nama yang ditetapkan di tingkat atas materi depan yang mencapai templat.

```python filename="src/layanan/catatan.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def open_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.done == False)))  # noqa: E712
```

```nexy filename="src/rute/catatan.nexy"
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

## Buat tabel dengan migrasi

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` menulis `alembic/env.py`, yang mengimpor model yang dibandingkan dengan database. Impor setiap modul model baru di sana:

```python filename="alembic/env.py"
import src.models.note_model  # noqa: F401
```

SQLite tidak dapat `ALTER` sebagian besar kolom terpasang. Aktifkan mode batch Alembic, yang menyalin tabel, di kedua panggilan `context.configure(...)` dari `alembic/env.py`:

```python filename="alembic/env.py"
context.configure(connection=connection, target_metadata=target_metadata, render_as_batch=True)
```

## Asinkron dengan `aiosqlite`

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

## Pengujian pada database dalam memori

`StaticPool` menyimpan satu koneksi, sehingga database dalam memori tetap aktif selama keseluruhan pengujian. Ketergantungan handler ditukar dengan yang menggunakannya:

```python filename="tes/test_notes.py"
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

## Dalam produksi

- **Simpan file di disk persisten.** Sistem file container hilang saat penerapan ulang: pasang volume dan arahkan `DATABASE_URL` ke volume tersebut dengan jalur absolut.
- **Satu server, satu file.** SQLite memiliki satu penulis pada satu waktu. Beberapa `nx start` pekerja pada mesin yang sama baik-baik saja dengan WAL; beberapa mesin tidak.
- **Cadangkan saat dijalankan** dengan `sqlite3 app.db ".backup backup.db"`, bukan dengan salinan file.

## Langkah selanjutnya

- [Basis Data](../guides/databases.md)
- [Gunakan PostgreSQL dengan Nexy](postgresql.md)
- [Pengujian](../guides/testing.md)
