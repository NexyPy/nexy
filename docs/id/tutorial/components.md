# Bangun aplikasi catatan dengan Nexy, bagian 4: komponen

Bagian 4 mengubah setiap catatan menjadi komponen yang dapat digunakan kembali, file `.nexy` yang Anda impor seperti nama Python dan digunakan seperti tag HTML.

**Sebelum Anda memulai:** aplikasi [bagian 3](dynamic-routes.md).

## Tulis komponennya

Komponen adalah file `.nexy` di luar rute. Propsnya dideklarasikan dengan `prop[...]`, dan pemanggil meneruskannya sebagai atribut:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

Blok `<style>` dikirim bersama setiap halaman yang menggunakan kartu. Itu tidak tercakup: `.note` adalah satu kelas untuk seluruh halaman, jadi berikan nama kelas komponen yang hanya digunakannya.

## Gunakan dalam daftar

<!-- router:fbr,custom -->
```nexy filename="src/rute/catatan/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` adalah alias impor bagian 1: menunjuk ke `src/`. Nama file adalah nama komponen, dalam PascalCase: `NoteCard.nexy` ekspor `NoteCard`.

Buka <http://localhost:3000/notes>: setiap not kini menjadi kartu.

## Apa yang Anda pelajari

- File `.nexy` di luar rute adalah sebuah komponen; `prop[...]`-nya adalah atributnya.
- `from "@/components/x.nexy" import X` mengimpornya; `<X />` menerjemahkannya.
- Blok `<style>` tidak tercakup: beri nama kelas komponen setelahnya.

## Langkah selanjutnya

- [Bagian 5: menyimpan catatan di SQLite](store-the-notes.md)
- [Komponen](../views/nexy/components.md): `Image`, `Link` dan pembantu bawaan
