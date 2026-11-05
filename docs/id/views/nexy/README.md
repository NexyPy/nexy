# file .nexy

File `.nexy` adalah komponen: Python di atas, HTML di tengah, CSS di bawah.

**Sebelum Anda memulai:** proyek yang dibuat oleh [Mulai cepat](../../getting-started/quick-start.md). File `.nexy` tidak memerlukan konfigurasi build: `nx dev` mengkompilasinya saat disimpan.

```nexy filename="src/rute/blog/[siput].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Masalah depan

Segala sesuatu di antara dua garis `---` adalah Python. Impor diselesaikan saat komponen dikompilasi; sisanya berjalan untuk setiap permintaan, sehingga dapat membaca status permintaan.

| Apa | Contoh |
|---|---|
| Impor modul | `import json`, `from datetime import datetime` |
| Impor komponen | `from "@/components/card.nexy" import Card` |
| Mendeklarasikan properti | `title: prop[str] = "Default"` |
| Hitung nilai | `year = datetime.now().year` |
| Baca permintaan | `pathname = usePathname()` |
| Cache halaman (ISR) | `revalidate = 60` |

## Properti

Properti adalah API komponen. `prop[type]` mendeklarasikan tipenya, `= value` memberikan default. Properti tanpa default harus diteruskan oleh induknya.

Impor yang dimulai dengan alias diselesaikan melalui `useAliases`. Pengaturan `nx new` menulis peta `@` ke `src`, yang menjadikan `@/components/card.nexy` berarti `src/components/card.nexy`.

## Templat

Di bawah frontmatter adalah HTML dengan Jinja2. Variabel dari frontmatter dan properti berada dalam cakupan.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

Pelarian otomatis **nonaktif**: templat adalah HTML milik proyek, jadi `{{ value }}` dimasukkan seperti yang tertulis. Hilangkan nilai-nilai yang tidak dipercaya dengan `{{ value | e }}`. `| safe` oleh karena itu tidak mengubah apa pun.

> [!CATATAN]
> bungkus JavaScript yang berisi `{{` atau `{%` di `{% raw %}...{% endraw %}`. Kerangka kerja seperti Vue dan Svelte menggunakan tanda kurung kurawal yang sama.

## Komponen

Setiap callable yang diimpor yang namanya dimulai dengan huruf besar dapat digunakan sebagai tag. Kompilator menulis ulang menjadi panggilan Jinja: atribut menjadi argumen kata kunci.

```nexy filename="src/rute/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

Baris terakhir tepatnya `{{ Audio("/theme.mp3", controls=True) }}`. Kedua sintaksis tersebut valid untuk pembantu bawaan `Image`, `Link`, `Audio` dan `Video` - lihat [komponen](components.md#two-syntaxes-one-function).

Anak-anak dirender melalui `<Slot />` (huruf kapital S) di dalam komponen anak, dan melalui `{{ children }}` di dalam tata letak.

Berikan nilai yang dihitung dengan Jinja di dalam atribut: `<Icon path="{{ icon }}" size="{{ size }}" />`. Nama kosong seperti `path=icon` adalah teks `icon`, bukan variabelnya. Untuk memberikan komponen kelas CSS, deklarasikan prop `class_name`: `class` adalah kata kunci Python.

> [!CATATAN]
> tag pembantu selalu menutup sendiri. Meneruskan konten ke `Link` melewati argumen `children` (`<Link href="/about" children="About" />`), bukan melalui konten elemen.

## Gaya

`<style>` blok dikeluarkan dengan halaman yang mendeklarasikannya. Mereka tidak tercakup: nama kelas yang digunakan dalam dua komponen adalah satu kelas. Awalan atau namespace kelas Anda.

## Aturan yang menghemat waktu

- Satu komponen per file. Nama file adalah nama komponen, dalam PascalCase (`CopyChip.nexy`). Komponen `.nexy` diimpor sebagai modul Python: tanda hubung pada nama (`copy-chip.nexy`) tidak dapat dikompilasi.
- Deklarasikan props sebelum menggunakannya: variabel yang tidak dideklarasikan dirender sebagai string kosong, karena undefinisi Jinja2 tidak bersuara di sini.
- Pertahankan efek samping di dalam fungsi - materi depan berjalan kembali pada setiap permintaan.

## Langkah selanjutnya

- [Markdown dan MDX](markdown.md): halaman konten
- [ISR](../../rendering/isr.md): menyimpan halaman per jalur dalam cache
- [CSR](../../rendering/csr.md): rendering sisi klien
