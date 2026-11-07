# Bangun aplikasi catatan dengan Nexy, bagian 14: centang catatan tanpa memuat ulang halaman

Bagian 14 menambahkan tombol **Selesai** ke setiap not. Ini adalah formulir yang berfungsi tanpa JavaScript, dan beberapa baris JavaScript membuatnya tersimpan di tempatnya, tanpa memuat ulang halaman.

**Sebelum Anda memulai:** aplikasi [bagian 13](search-the-notes.md).

## Catatan sudah selesai atau belum

<!-- router:fbr,custom -->
```python filename="src/model/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    done: bool = Field(default=False, sa_column_kwargs={"server_default": "0"})
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/notes/note_model.py"
from sqlmodel import Field, SQLModel


class Note(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text: str
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    done: bool = Field(default=False, sa_column_kwargs={"server_default": "0"})
```
<!-- /router -->

Tabel sudah memiliki catatan, dan SQLite tidak dapat menambahkan kolom yang harus memiliki nilai tanpa ada yang dimasukkan ke dalam baris yang ada. `server_default` memberikannya: migrasi menulis `DEFAULT 0`, dan setiap catatan dimulai sebagai belum selesai.

```bash
nx migrate -m "notes can be done"
nx migrate --upgrade
```

## Balikkan ke dalam database, di belakang Action

<!-- router:fbr,custom -->
```python filename="src/catatan.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note

PAGE_SIZE = 5


def notes_page(user_id: int, number: int) -> tuple[list[Note], bool]:
    """One page of the notes of *user_id*, oldest first, and whether a page comes after it."""
    query = select(Note).where(Note.user_id == user_id).order_by(Note.id)
    with Session(engine) as session:
        found = list(session.exec(query.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE


def all_notes(user_id: int) -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.user_id == user_id).order_by(Note.id)))


def find(user_id: int, note_id: int) -> Note | None:
    """The note, when it belongs to *user_id*: someone else's note is not found."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
    return note if note is not None and note.user_id == user_id else None


def add_note(user_id: int, text: str) -> Note:
    note = Note(text=text, user_id=user_id)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(user_id: int, note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(user_id: int, note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        session.delete(note)
        session.commit()
    return True


def toggle_done(user_id: int, note_id: int) -> bool | None:
    """The new state of the note, or None when the user has no such note."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return None
        note.done = not note.done
        session.commit()
        return note.done
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/catatan.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine

PAGE_SIZE = 5


def notes_page(user_id: int, number: int) -> tuple[list[Note], bool]:
    """One page of the notes of *user_id*, oldest first, and whether a page comes after it."""
    query = select(Note).where(Note.user_id == user_id).order_by(Note.id)
    with Session(engine) as session:
        found = list(session.exec(query.offset((number - 1) * PAGE_SIZE).limit(PAGE_SIZE + 1)))
    return found[:PAGE_SIZE], len(found) > PAGE_SIZE


def all_notes(user_id: int) -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).where(Note.user_id == user_id).order_by(Note.id)))


def find(user_id: int, note_id: int) -> Note | None:
    """The note, when it belongs to *user_id*: someone else's note is not found."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
    return note if note is not None and note.user_id == user_id else None


def add_note(user_id: int, text: str) -> Note:
    note = Note(text=text, user_id=user_id)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note


def change_note(user_id: int, note_id: int, text: str) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        note.text = text
        session.commit()
    return True


def remove_note(user_id: int, note_id: int) -> bool:
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return False
        session.delete(note)
        session.commit()
    return True


def toggle_done(user_id: int, note_id: int) -> bool | None:
    """The new state of the note, or None when the user has no such note."""
    with Session(engine) as session:
        note = session.get(Note, note_id)
        if note is None or note.user_id != user_id:
            return None
        note.done = not note.done
        session.commit()
        return note.done
```
<!-- /router -->

```python filename="src/aksi/catatan.py"
from urllib.parse import urlencode

from nexy import notFound
from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.guard import signed_in_user
from src.notes import add_note, change_note, remove_note, toggle_done

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
    user_id = signed_in_user()
    text = text.strip()
    if error := problem(text):
        return back(error=error)
    add_note(user_id, text)
    return back()


@Action
async def update_note(note_id: int, text: str) -> RedirectResponse:
    user_id = signed_in_user()
    text = text.strip()
    if error := problem(text):
        return back(f"/notes/{note_id}", error)
    if not change_note(user_id, note_id, text):
        notFound()
    return back(f"/notes/{note_id}")


@Action
async def delete_note(note_id: int) -> RedirectResponse:
    if not remove_note(signed_in_user(), note_id):
        notFound()
    return back()


@Action
async def toggle_note(note_id: int) -> bool:
    done = toggle_done(signed_in_user(), note_id)
    if done is None:
        notFound()
    return done
```

`toggle_note` mengembalikan keadaan baru, `bool`. Formulir yang diposkan ke dalamnya akan mengembalikan `303` seperti biasa ke halaman; skrip yang meminta JSON mendapat `true` atau `false`. Satu Tindakan melayani keduanya.

## Sebuah tombol yang merupakan formulir

Kartu tersebut menunjukkan status yang diketahui server, dan memposting id catatannya:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
done: prop[bool]
---
<article class="note{% if done %} note-done{% endif %}">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
  <form method="post" action="{{ __actions_path['toggle_note'] }}" data-toggle>
    <input type="hidden" name="note_id" value="{{ id }}">
    <button type="submit" aria-pressed="{{ 'true' if done else 'false' }}">{{ 'Done' if done else 'To do' }}</button>
  </form>
</article>

<style>
  .note { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
  .note-done a { text-decoration: line-through; opacity: 0.6; }
</style>
```

`aria-pressed` memberi tahu pembaca layar bahwa tombol tersebut adalah tombol pengalih, dan apakah tombol tersebut aktif.

## Simpan tanpa memuat ulang

Daftar meneruskan `done` ke setiap kartu, dan menambahkan satu skrip untuk semua kartu di halaman:

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
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
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" done="{{ note.done }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>

  <script type="module">
    // With JavaScript on, the Done buttons save without leaving the page.
    document.addEventListener("submit", async (event) => {
      const form = event.target.closest("form[data-toggle]")
      if (!form) return
      event.preventDefault()
      const button = form.querySelector("button")
      button.disabled = true
      const answer = await fetch(form.action, {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ note_id: Number(form.elements.note_id.value) }),
      })
      button.disabled = false
      if (!answer.ok) return form.submit()
      const done = await answer.json()
      button.setAttribute("aria-pressed", String(done))
      button.textContent = done ? "Done" : "To do"
      form.closest(".note").classList.toggle("note-done", done)
    })
  </script>
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
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" done="{{ note.done }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>

  <script type="module">
    // With JavaScript on, the Done buttons save without leaving the page.
    document.addEventListener("submit", async (event) => {
      const form = event.target.closest("form[data-toggle]")
      if (!form) return
      event.preventDefault()
      const button = form.querySelector("button")
      button.disabled = true
      const answer = await fetch(form.action, {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json" },
        body: JSON.stringify({ note_id: Number(form.elements.note_id.value) }),
      })
      button.disabled = false
      if (!answer.ok) return form.submit()
      const done = await answer.json()
      button.setAttribute("aria-pressed", String(done))
      button.textContent = done ? "Done" : "To do"
      form.closest(".note").classList.toggle("note-done", done)
    })
  </script>
</section>
```
<!-- /router -->

Script mendengarkan setiap bentuk halaman, dan hanya mengambil bentuk yang ditandai `data-toggle`. Ia mengirimkan `note_id` yang sama dengan formulir, seperti JSON, dan memperbarui tombol dengan jawabannya. Jika panggilan gagal, formulir akan diposkan dengan cara normal, sehingga klik tidak akan pernah hilang.

Mengapa bukan pulau React, seperti pada bagian 13? Status setiap catatan diketahui oleh server pada setiap permintaan, dan formulir sudah menunjukkannya dengan benar, sebelum skrip apa pun dijalankan. Script hanya mengubah cara formulir dikirim. Itu adalah *peningkatan progresif*: halaman berfungsi tanpa JavaScript, dan lebih baik dengan itu.

Buka <http://localhost:3000/notes> dan tekan **Untuk melakukan** pada catatan: catatan berubah menjadi **Selesai**, catatan dicoret, dan halaman tidak dimuat ulang. Muat ulang: catatan masih selesai.

## Apa yang Anda pelajari

- `server_default` memungkinkan migrasi menambahkan kolom yang diperlukan ke tabel yang memiliki baris.
- One Action menjawab formulir dengan `303`, dan skrip meminta JSON dengan nilai kembaliannya.
- Peningkatan progresif: formulir yang berfungsi sendiri, dan skrip yang mengirimkannya ke tempatnya.

## Langkah selanjutnya

- Unit 5: melampaui permintaan (berikutnya)
- [Tindakan](../guides/actions.md): panggilan yang diketik dari browser, kesalahan dan keamanan
