# Tutorial: membuat halaman catatan dalam 10 menit

Anda akan membuat proyek, menambahkan halaman, menambahkan titik akhir Python, berbagi data di antara mereka, dan membangun untuk produksi. Anda mengakhirinya dengan satu daftar catatan yang disajikan sebagai halaman dan sebagai JSON.

Baru mengenal Nexy? Lakukan [Mulai cepat](quick-start.md) terlebih dahulu: dibutuhkan waktu tiga menit.

```diagram filename="Seluruh tutorial dalam satu baris"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Buat proyek

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` hadir dengan [uv](https://docs.astral.sh/uv/) dan hanya membuat proyek. Setiap perintah setelahnya dijalankan di dalam lingkungan virtual proyek (atau sebagai `uv run nexy dev`).

Pilih router berbasis file, proyek web, dan kerangka klien apa pun (atau tidak sama sekali). Buka
<http://localhost:3000>. Langkah panjang mencetak masing-masing satu baris dengan durasinya, seperti yang dilakukan `uv`.

<!-- router:modular -->
Jawab `No` pada prompt router berbasis file: `nx new` merancah router modular di `src/apps/`, bukan `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Jawab `Yes` ke prompt router berbasis file untuk halaman tersebut, lalu pasang `APIRouter` Anda yang ada di `nexyconfig.py`: kedua router hidup berdampingan.
<!-- /router -->

## 2. Edit tata letaknya

<!-- router:fbr,custom -->
`src/routes/layout.nexy` memiliki dokumen HTML (dengan perutean klien React adalah `layout.tsx`). Ubah `<title>`:

```nexy
<title>Notes</title>
```

Simpan: browser memuat ulang. Lihat [Tata Letak](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
Pengontrol merender `src/apps/layout.nexy` di sekitar tampilan, dan file tersebut memiliki dokumen HTML. Ubah `<title>`:

```nexy
<title>Notes</title>
```

Simpan: browser memuat ulang. Lihat [Tampilan dari pengontrol](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Tambahkan halaman

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Buka <http://localhost:3000/notes>: Anda akan melihat dua peluru. Disajikan di `/notes`. Bagian antara `---` adalah Python, sisanya adalah Jinja2.
<!-- /router -->

<!-- router:modular -->
Pengontrol mengembalikan tampilan. Buat `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Deklarasikan rute di `src/apps/app_controller.py` dan tambahkan pengontrol ke modul:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Buka <http://localhost:3000/notes>: Anda akan melihat dua peluru. Bagian antara `---` adalah Python, sisanya adalah Jinja2.
<!-- /router -->

## 4. Tambahkan titik akhir

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Anda harus mendapatkan `[{"id":1,"text":"Buy milk"}]`. Nama fungsinya adalah metode HTTP. Dokumen API interaktif ada di `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Tambahkan `NotesApiController` ke `controllers` di `src/apps/app_module.py`, lalu jalankan:

```bash
curl http://localhost:3000/api/notes
```

Anda harus mendapatkan `[{"id":1,"text":"Buy milk"}]`. Nama metodenya adalah metode HTTP. Dokumen API interaktif ada di `/docs`.
<!-- /router -->

## 5. Bagikan datanya

Pindahkan daftar ke modul Python dan gunakan di kedua file:

```python filename="src/catatan.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Membangun dan melayani

```bash
nx build
nx start
```

`nx build` mencetak setiap fase beserta durasinya. `nx start` menyajikan output yang dikompilasi dengan Uvicorn: tidak ada proses Node saat runtime.

## Dimana selanjutnya

- [Perutean](../routing/README.md): segmen dan grup dinamis
- [Actions](../guides/actions.md): memanggil Python dari formulir atau dari klien
- [Testing](../guides/testing.md): halaman pengujian dan titik akhir
- [Deploy](../deployment/README.md): container dan proksi terbalik
