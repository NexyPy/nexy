# Bangun aplikasi catatan dengan Nexy, bagian 13: cari catatan saat Anda mengetik

Bagian 13 menambahkan kotak pencarian di atas catatan: pulau React memfilter setiap catatan pengguna pada setiap penekanan tombol, di browser, tanpa permintaan ke server.

**Sebelum Anda memulai:** aplikasi [bagian 12](password-reset.md). Proyek ini dibuat dengan React di [bagian 1](create-the-project.md), jadi React sudah diinstal.

## Sebuah pulau, dan mengapa di sini

Sisa halamannya tetap berupa HTML yang dirender oleh server: daftar, formulir, halaman catatan. Hanya kotak pencarian yang memerlukan browser, jadi hanya kotak pencarian yang React. Itu adalah *pulau*: satu komponen klien di dalam halaman server, dibuat interaktif dengan sendirinya.

## Komponen pencarian

```tsx filename="src/components/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React menulis `{note.text}` sebagai teks: catatan `<b>x</b>` menunjukkan tanda kurung, tanpa `| e` untuk ditambahkan.

`found` hanya dihitung setelah sesuatu diketik, dan itu penting untuk pembangunan: `nx build` merender setiap pulau satu kali ke HTML, dengan placeholder, bukan propsnya. Komponen yang membaca prop daftar selama render pertama tersebut mendapatkan placeholder alih-alih daftar, dan tidak mengirimkan HTML. Yang ini membaca `notes` hanya setelah tombol ditekan, sehingga build merender kotak pencariannya dan halaman menampilkannya sebelum JavaScript dijalankan.

`aria-live="polite"` membuat pembaca layar membaca hasilnya saat berubah, tanpa menyela.

## Letakkan pulau di halaman

Halaman tersebut meneruskan catatan sebagai penyangga: daftar kamus, yang diubah Nexy menjadi JSON untuk browser. Setiap catatan masuk, tidak hanya lima halaman saat ini, jadi pencarian mencakup semuanya:

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
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
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
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` mengimpor komponen React ke halaman `.nexy`; tag meneruskan atributnya sebagai props. `notes="{{ searchable }}"` meneruskan daftar Python itu sendiri, bukan string. `directive="client:idle"` membuat pulau menjadi interaktif ketika browser tidak melakukan hal lain yang mendesak.

Buka <http://localhost:3000/notes> dan ketik beberapa huruf catatan: catatan yang cocok akan muncul di bawah kotak setiap kali tombol ditekan. Kosongkan kotaknya, dan hasilnya akan hilang.

> [!NOTE]
> Alat peraga perjalanan pulau di halaman, sebagai JSON. Mengirim setiap catatan cocok untuk beberapa ratus catatan; untuk ribuan, cari di server saja, dengan kueri dan filter `LIKE`.

## Apa yang Anda pelajari

- Pulau adalah komponen klien di dalam halaman server: di sini, React hanya untuk kotak pencarian.
- Halaman `.nexy` mengimpornya berdasarkan jalur dan meneruskan nilai Python sebagai props, diserialkan ke JSON.
- Build tersebut merender sebuah pulau satu kali, dengan placeholder untuk propsnya: props daftar baca setelah render pertama, dan pulau tersebut mengirimkan HTML.

## Langkah selanjutnya

- [Bagian 14: centang catatan tanpa memuat ulang halaman](tick-a-note.md)
- [Pulau dan hidrasi](../rendering/islands.md): arahan, alat peraga dan batasan
