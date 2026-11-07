# Bangun aplikasi catatan dengan Nexy, bagian 8: edit dan hapus catatan

Bagian 8 menempatkan dua formulir pada halaman catatan: satu menyimpan teks baru, yang lain menghapus catatan, dan keduanya merupakan Tindakan seperti yang membuatnya.

**Sebelum Anda memulai:** aplikasi [bagian 7](validation-errors.md).

## Mengubah dan menghapus catatan di database

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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True
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


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None:
            return False
        session.delete(note)
        session.commit()
    return True
```
<!-- /router -->

## Dua Tindakan lagi

`update_note` memeriksa teks dengan aturan yang sama seperti `create_note`, dan mengirimkan kegagalan kembali ke halaman catatan. `delete_note` kembali ke daftar:

```python filename="src/aksi/catatan.py"
from urllib.parse import urlencode

from nexy import notFound
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note, change_note, remove_note

MAX_LENGTH = 200


def back(path: str = "/notes", error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"{path}{query}", status_code=303)


def problem(text: str) -> str:
    if not text:
        return "A note cannot be blank."
    if len(text) > MAX_LENGTH:
        return f"A note is at most {MAX_LENGTH} characters."
    return ""


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if error := problem(text):
        return back(error=error)
    add_note(text)
    return back()


@Action
async def update_note(note_id: int, text: str) -> RedirectResponse:
    text = text.strip()
    if error := problem(text):
        return back(f"/notes/{note_id}", error)
    if not change_note(note_id, text):
        notFound()
    return back(f"/notes/{note_id}")


@Action
async def delete_note(note_id: int) -> RedirectResponse:
    if not remove_note(note_id):
        notFound()
    return back()
```

Aturan `create_note` dipindahkan ke `problem`, jadi dua Action yang mengambil teks tidak bisa terpisah. Catatan yang sudah tidak ada lagi menjawab `404`, menyukai halamannya.

## Bentuk halaman catatan

Id bergerak dalam bidang tersembunyi bernama `note_id`, nama parameternya:

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/[id].nexy"
---
from nexy import notFound, useSearchParams
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['update_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <input name="text" value="{{ note.text | e }}" maxlength="200" required>
    <button type="submit">Save</button>
  </form>

  <form method="post" action="{{ __actions_path['delete_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <button type="submit">Delete</button>
  </form>

  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
Tampilan sekarang memerlukan keseluruhan catatan, bukan hanya teksnya:

```nexy filename="src/apps/notes/note_view.nexy"
---
from nexy import useSearchParams

note: prop[object]
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['update_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <input name="text" value="{{ note.text | e }}" maxlength="200" required>
    <button type="submit">Save</button>
  </form>

  <form method="post" action="{{ __actions_path['delete_note'] }}">
    <input type="hidden" name="note_id" value="{{ note.id }}">
    <button type="submit">Delete</button>
  </form>

  <a href="/notes">All notes</a>
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
        return page("src/apps/notes/note_view.nexy", note=note)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [note.model_dump() for note in all_notes()]
```
<!-- /router -->

Buka <http://localhost:3000/notes/1>, ubah *Beli susu* menjadi *Beli susu oat* dan tekan **Simpan**: halaman muncul kembali dengan teks baru. Tekan **Hapus**: Anda masuk dalam daftar, tanpa catatan.

## Apa yang Anda pelajari

- Satu halaman dapat menampung beberapa formulir, masing-masing memposting ke Action-nya sendiri.
- Bidang tersembunyi membawa id; namanya adalah nama parameter Aksi.
- Aturan yang dimiliki bersama oleh dua Tindakan berada dalam satu fungsi, yang dipanggil oleh keduanya.

## Langkah selanjutnya

- [Bagian 9: memberi nomor halaman pada catatan](paginate-the-notes.md)
- [Formulir tanpa JavaScript](../guides/actions.md#forms-without-javascript): bagaimana suatu formulir mencapai suatu Tindakan
