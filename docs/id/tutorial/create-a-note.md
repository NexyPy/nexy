# Membangun aplikasi catatan dengan Nexy, bagian 6: membuat catatan dari formulir

Bagian 6 menambahkan formulir di atas daftar: formulir tersebut diposkan ke fungsi Python bertanda `@Action`, yang menyimpan catatan, dan pengunjung kembali ke daftar dengan catatan baru di dalamnya.

**Sebelum Anda memulai:** aplikasi [bagian 5](store-the-notes.md), dengan database-nya.

## Simpan catatan

Tambahkan fungsi yang menyimpan satu catatan dan mengembalikannya, di samping dua catatan yang membacanya:

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
```
<!-- /router -->

## Ubah itu menjadi Tindakan

Tindakan adalah fungsi Python yang dapat dipanggil oleh browser. `@Action` menyajikannya sebagai `POST`, memeriksa input terhadap petunjuk tipe, dan menjalankannya:

```python filename="src/aksi/catatan.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

Saat startup, Nexy mengimpor setiap modul `src/` dan menyajikan Tindakan yang ditemukannya: tidak ada rute yang harus dideklarasikan, untuk router mana pun. `src/actions/` adalah tempat tutorial ini menyimpannya.

## Posting formulir itu ke sana

Templat `.nexy` mengetahui jalur setiap Tindakan sebagai `__actions_path["name"]`. Formulir HTML biasa diposting di sana, sehingga halaman berfungsi sebelum skrip apa pun dimuat:

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
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

Inputnya diberi nama `text`, seperti parameter `create_note`: itulah cara bidang mencapainya.

## Tampilkan catatan sebagai teks, bukan sebagai HTML

Mulai sekarang, catatan adalah apa yang diketik pengunjung. Templat `.nexy` menulis nilai sebagaimana adanya, sehingga catatan `<script>…</script>` akan berjalan di browser setiap orang yang membuka daftar. `| e` lolos: `<` menjadi `&lt;`, dan catatan ditampilkan sebagai teks.

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

Hindari setiap nilai yang datang dari pengunjung atau dari database. `| safe` melakukan yang sebaliknya: simpan untuk HTML yang Anda tulis sendiri.

## Cobalah

Ketik *Baca dokumen* dan tekan **Tambah**. Tindakan menyimpan catatan, lalu menjawab `303` kembali ke `/notes`, dan browser menampilkan daftar itu lagi, dengan catatan ketiga di bagian bawah.

## Apa yang Anda pelajari

- `@Action` mengubah fungsi Python menjadi titik akhir `POST`, dengan petunjuk tipenya sebagai masukan.
- Formulir diposkan melalui `__actions_path["name"]`, tanpa JavaScript, dan kembali dengan `303`.
- Nama bidang formulir adalah nama parameter Tindakan.
- `| e` menunjukkan apa yang diketik pengunjung sebagai teks: escape every value that not come from you.

## Langkah selanjutnya

- [Bagian 7: tampilkan kesalahan validasi](validation-errors.md)
- [Tindakan](../guides/actions.md): panggilan yang diketik dari browser, kesalahan dan keamanan
