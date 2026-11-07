# Bangun aplikasi catatan dengan Nexy, bagian 3: rute dinamis dan API

Bagian 3 memberikan setiap catatan URL-nya sendiri, `/notes/1`, dan menyajikan catatan yang sama seperti JSON di `/api/notes`, keduanya dibaca dari satu modul Python.

**Sebelum Anda memulai:** aplikasi [bagian 2](pages-and-layouts.md).

## Simpan catatan dalam satu modul

Halaman dan API akan membaca daftar yang sama. Pindahkan ke modulnya sendiri, dengan fungsi yang menemukan satu catatan:

```python filename="src/catatan.py"
NOTES = {1: "Buy milk", 2: "Ship Nexy"}


def find(note_id: int) -> str | None:
    return NOTES.get(note_id)
```

## Tautkan setiap catatan ke halamannya

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for id, text in notes %}
    <li><a href="/notes/{{ id }}">{{ text }}</a></li>
    {% endfor %}
  </ul>
</section>
```
<!-- /router -->

## Tambahkan halaman per catatan

<!-- router:fbr,custom -->
Nama folder atau file dalam tanda kurung adalah segmen URL: `[id].nexy` menjawab `/notes/1`, `/notes/2`, dan meneruskan segmen tersebut ke halaman sebagai penyangga. `id: prop[int]` mengubahnya menjadi angka, jadi `/notes/abc` menjawab `404` sebelum halaman dijalankan.

```nexy filename="src/rute/catatan/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
text = find(id)
if text is None:
    notFound()
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
`{id}` di jalur pengontrol adalah segmen URL, diteruskan ke metode dengan nama tersebut. `id: int` mengubahnya menjadi angka, jadi `/notes/abc` menjawab `404` sebelum metode dijalankan.

```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

`notFound()` menghentikan permintaan dengan `404`: catatan yang tidak ada jawaban seperti URL yang tidak ada.

## Sajikan catatan sebagai JSON

<!-- router:fbr,custom -->
File `.py` di bawah `src/routes/` adalah rute API. Setiap fungsi yang diberi nama berdasarkan metode HTTP menjawab metode tersebut:

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": id, "text": text} for id, text in NOTES.items()]
```
<!-- /router -->

<!-- router:modular -->
Tiga pengontrol catatan, dalam satu file. Setiap metode yang diberi nama berdasarkan metode HTTP menjawab metode tersebut:

```python filename="src/apps/notes/notes_controller.py"
from nexy import notFound
from nexy.decorators import Controller
from nexy.hooks import useViews
from src.notes import NOTES, find

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
        text = find(id)
        if text is None:
            notFound()
        return page("src/apps/notes/note_view.nexy", text=text)


@Controller("/api/notes")
class NotesApiController:
    async def get(self) -> list[dict]:
        return [{"id": id, "text": text} for id, text in NOTES.items()]
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NoteController, NotesApiController, NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController, NoteController, NotesApiController]
```
<!-- /router -->

Periksa tiga URL:

- <http://localhost:3000/notes/1> menunjukkan *Beli susu*;
- <http://localhost:3000/notes/9> jawaban *Halaman tidak ditemukan*;
- `curl http://localhost:3000/api/notes` mencetak `[{"id":1,"text":"Buy milk"},{"id":2,"text":"Ship Nexy"}]`.

API ini terdaftar, beserta skemanya, di <http://localhost:3000/docs>.

## Apa yang Anda pelajari

<!-- router:fbr,custom -->
- `[id].nexy` adalah segmen dinamis; `id: prop[int]` membaca dan mengubahnya.
- File `.py` di bawah `src/routes/` menjawab JSON, satu fungsi per metode HTTP.
<!-- /router -->
<!-- router:modular -->
- `{id}` di jalur pengontrol adalah segmen dinamis; `id: int` mengubahnya.
- Metode pengontrol yang mengembalikan data menjawab JSON; salah satu yang mengembalikan `useViews` menjawab halaman.
<!-- /router -->
- `notFound()` jawaban `404` dari mana saja; modul bersama menjaga halaman dan API tetap berjalan.

## Langkah selanjutnya

- [Bagian 4: komponen](components.md)
- [Pengecualian dan kesalahan](../reference/exceptions.md): `notFound`, `redirect` dan pintu keluar lainnya
