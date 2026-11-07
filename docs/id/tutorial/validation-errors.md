# Bangun aplikasi catatan dengan Nexy, bagian 7: tampilkan kesalahan validasi

Bagian 7 menolak catatan yang kosong atau terlalu panjang, dan menunjukkan alasannya di atas formulir, di halaman yang sama, masih tanpa JavaScript.

**Sebelum Anda memulai:** aplikasi [bagian 6](create-a-note.md) .

## Dua jenis kesalahan

Petunjuk jenis suatu Tindakan sudah menolak bentuk yang salah: formulir tanpa bidang `text` menjawab `422` sebelum `create_note` dijalankan. Aturan tentang nilai itu sendiri, seperti "tidak kosong", adalah milik Anda untuk ditulis di Tindakan.

## Periksa catatan di Tindakan

Kegagalan mengirim pengunjung kembali ke daftar dengan alasan di URL; kesuksesan akan kembali ke daftar tanpanya:

```python filename="src/aksi/catatan.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` memberitahu browser untuk memuat halaman berikutnya dengan `GET`, sehingga penyegaran tidak memposting formulir untuk kedua kalinya.

## Tunjukkan alasannya di atas formulir

`useSearchParams()` membaca string kueri dari permintaan saat ini:

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
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
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`| e` lolos dari pesan: string kueri berasal dari pengunjung, sehingga tidak pernah ditulis ke halaman sebagai HTML. `role="alert"` membuat pembaca layar mengumumkannya.

`required` dan `maxlength` membiarkan browser menghentikan sebagian besar kesalahan sebelum meninggalkannya. Tindakan memeriksa lagi: permintaan tidak harus datang dari formulir Anda.

Tambahkan catatan tiga spasi: daftar muncul kembali dengan *Catatan tidak boleh kosong.* di atas formulir.

## Apa yang Anda pelajari

- Ketik petunjuk menolak bentuk yang salah dengan `422`; aturan tentang nilai yang masuk dalam Aksi.
- Suatu Tindakan dapat dijawab dengan `RedirectResponse`; `303` setelah formulir menghindari postingan kedua.
- `useSearchParams()` membaca string kueri, dan `| e` lolos dari apa yang dikirim pengunjung.

## Langkah selanjutnya

- [Bagian 8: mengedit dan menghapus catatan](edit-and-delete.md)
- [Pengecualian dan kesalahan](../reference/exceptions.md): setiap status dapat dijawab oleh Tindakan dan halaman
