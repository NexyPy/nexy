# Membangun aplikasi catatan dengan Nexy, bagian 5: menyimpan catatan di SQLite

Bagian 5 memindahkan catatan dari kamus Python ke dalam database SQLite, dengan model, migrasi, dan dua catatan untuk memulai, dan halaman membacanya dari sana.

**Sebelum Anda memulai:** aplikasi [bagian 4](components.md).

## Instal ORM dan alat migrasi

```bash
uv add sqlmodel alembic
```

[SQLModel](https://sqlmodel.tiangolo.com/) mendeskripsikan tabel sebagai kelas Python, dan Alembic mengubah perubahan pada kelas tersebut menjadi migrasi. Nexy juga tidak membungkus: Anda menggunakannya sebagaimana adanya.

## Buka basis data

Alamat database ada di `.env`, di akar proyek. `nx migrate` dan aplikasi membacanya dari sana:

```bash filename=".env"
DATABASE_URL=sqlite:///dev.db
```

`sqlite:///dev.db` adalah file, `dev.db`, di sebelah `nexyconfig.py`: SQLite tidak memerlukan server. Jauhkan `.env` dari Git: Git menyimpan rahasia database sebenarnya.

Mesinnya adalah koneksi ke database. Bunyinya `DATABASE_URL`, dengan file yang sama sebagai default ketika variabel tidak disetel:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dev.db"))
```

## Jelaskan sebuah catatan

<!-- router:fbr,custom -->
```python filename="src/model/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

<!-- router:modular -->
Model hidup dengan fitur yang dimilikinya, di samping pengontrolnya:

```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
```
<!-- /router -->

`table=True` menjadikan kelas sebagai tabel, `note`. `id` diberikan oleh database saat catatan disimpan.

## Buat tabel dengan migrasi

```bash
nx migrate --init
nx migrate -m "create notes"
nx migrate --upgrade
```

`--init` menulis folder `alembic/` dan mengarahkannya ke model Anda. `-m` membandingkan model dengan database dan menulis migrasi yang membuat tabel; `--upgrade` menjalankannya. Ubah modelnya nanti, jalankan kembali dua perintah terakhir, dan tabel akan menyusul.

## Baca catatan dari database

Fungsi `src/notes.py` tetap menggunakan namanya, sehingga halamannya sedikit berubah: sekarang mereka membuka sesi, menanyakan tabel, dan mengembalikan objek `Note` alih-alih string.

<!-- router:fbr,custom -->
```python filename="src/catatan.py"
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
```python filename="src/catatan.py"
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

## Tambahkan dua catatan untuk memulai

Skrip awal mengisi database kosong, sehingga setiap salinan baru proyek dimulai dengan sesuatu untuk ditampilkan:

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

Saat startup, Nexy mengimpor setiap modul `src/` untuk menemukan Tindakan [bagian 6](create-a-note.md). `if __name__ == "__main__":` menyimpan benih untuk perintah di atas: diimpor oleh aplikasi, file hanya mendefinisikan `seed`, dan tidak menyentuh apa pun.

## Tampilkan catatan dari database

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
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

```nexy filename="src/rute/catatan/[id].nexy"
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

Buka <http://localhost:3000/notes>: dua kartu yang sama, sekarang dibaca dari `dev.db`. Mulai ulang `nexy dev`, dan mereka masih di sana.

## Apa yang Anda pelajari

- SQLModel mendeskripsikan tabel sebagai kelas; mesin di `src/configs/db.py` membuka database.
- `nx migrate` menulis dan menjalankan migrasi: `--init` sekali, lalu `-m` dan `--upgrade` per perubahan.
- Halaman dan pengontrol memanggil fungsi biasa Python yang menanyakan database: Nexy tidak menambahkan lapisan.

## Langkah selanjutnya

- [Bagian 6: membuat catatan dari formulir](create-a-note.md)
- [SQLite](../databases/sqlite.md): pragma, akses asinkron, dan pengujian pada database dalam memori
