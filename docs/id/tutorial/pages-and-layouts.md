# Bangun aplikasi catatan dengan Nexy, bagian 2: halaman dan tata letak

Bagian 2 menambahkan halaman yang mencantumkan catatan, dan memperlihatkan bagaimana tata letak membungkusnya dalam dokumen HTML.

**Sebelum Anda memulai:** proyek [bagian 1](create-the-project.md), dengan `nexy dev` sedang berjalan.

## Tambahkan halaman catatan

<!-- router:fbr,custom -->
Halaman adalah file di bawah `src/routes/`, dan jalurnya adalah URL-nya. Buat halaman catatan:

```nexy filename="src/rute/catatan/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` jawaban `/notes`.
<!-- /router -->

<!-- router:modular -->
Pengontrol menjawab URL dan mengembalikan tampilan. Berikan catatan pada foldernya sendiri, dengan maksud:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

dan pengontrol yang merendernya di `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Pengontrol hanya menjawab ketika modul mencantumkannya. Tambahkan ke modul root:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Buka <http://localhost:3000/notes>: Anda akan melihat dua peluru. Bagian antara dua baris `---` adalah Python, dijalankan di server; selebihnya adalah HTML dengan tag Jinja2 seperti `{% for %}` dan `{{ note }}`.

## Ubah tata letaknya

<!-- router:fbr,custom -->
`src/routes/layout.nexy` memiliki dokumen HTML: `<html>`, `<head>` dan `<body>`. Nexy membungkus setiap halaman di dalamnya, di mana ia menulis `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` memiliki dokumen HTML: `<html>`, `<head>` dan `<body>`. Pengontrol membungkus pandangannya di dalamnya dengan meneruskan tampilan sebagai `children`.
<!-- /router -->

Buka layout dan ubah baris `<title>Nexy App</title>` menjadi:

```html
<title>Notes</title>
```

Simpan: tab browser sekarang bertuliskan *Catatan*, di setiap halaman.

## Berikan ruang pada halaman di bawah header

Header tata letak sudah diperbaiki: tetap berada di bagian atas jendela, di atas halaman. Halaman-halaman pembuka mengatur ruangnya sendiri di bawahnya; halaman-halaman aplikasi catatan berbagi satu kelas untuk itu, `app-page`, yang setiap halaman tutorialnya memuat kontennya. Tambahkan di akhir `src/globale.css`, stylesheet yang sudah dimuat setiap halaman:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, yang digunakan oleh starter, menghilangkan batas bidang formulir: aturan ini mengembalikannya, sehingga bentuk bagian selanjutnya dapat dilihat.

## Apa yang Anda pelajari

<!-- router:fbr,custom -->
- File `.nexy` di bawah `src/routes/` adalah halaman; folder dan namanya adalah URL-nya.
- Root `layout.nexy` membungkus setiap halaman dalam dokumen HTML.
<!-- /router -->
<!-- router:modular -->
- Pengontrol menjawab URL dan merender tampilan `.nexy` dengan `useViews`; sebuah modul mencantumkannya.
- Tata letaknya juga berupa tampilan: pengontrol meneruskan tampilan halaman ke dalamnya sebagai `children`.
<!-- /router -->
- File `.nexy` berada di Python di antara `---`, lalu HTML dengan Jinja2.
- `src/globale.css` menampung gaya yang dibagikan setiap halaman, seperti `app-page`.

## Langkah selanjutnya

- [Bagian 3: rute dinamis dan API](dynamic-routes.md)
- [File .nexy](../views/nexy/README.md): props, komponen, dan gaya
