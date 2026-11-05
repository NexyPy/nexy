# Komponen

Nexy mengekspor sekumpulan kecil pembantu yang mengembalikan string HTML. Masing-masing digunakan dalam dua cara dalam templat `.nexy`: sebagai panggilan Jinja, atau sebagai tag gaya HTML.

## Dua sintaksis, satu fungsi

```nexy filename="src/rute/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

Kedua baris menghasilkan markup yang sama:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

Kompiler menulis ulang `<Audio ... />` menjadi `{{ Audio(...) }}`, sehingga bentuk tag bukanlah API kedua: atribut adalah argumen kata kunci fungsi.

## Aturan formulir tag

| Di tag | Menjadi |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, boolean nyata |
| `width=640` | `width=640`, angka |
| `src="{{ url }}"` | `src=(url)`, dievaluasi dalam Jinja |
| `value` | `"value"` lainnya, string |

- Tag harus dimulai dengan huruf besar dan diimpor di bagian depan; jika tidak, kompiler akan memunculkan `Missing Import: <Name> used but not declared.`
- Bentuk tagnya adalah **menutup sendiri**. `<Audio src="/a.mp3" />` dan `{{ Audio("/a.mp3") }}` setara; menulis anak-anak di dalam tag pembantu tidak didukung.
- Atribut HTML kosong bukan boolean di sini: `controls` menjadi `controls=""`, yang merupakan kesalahan. Tulis `controls=True`.

> [!CATATAN]
> `class_name` adalah kata kunci yang didokumentasikan untuk kelas CSS. Argumen kata kunci tambahan menjadi atribut HTML, sehingga `class="nav"` juga mencapai output.

## Gambar

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` merender `<img>` dengan pemuatan lambat secara default.

## Tautan

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` merender `<a data-nexy-link>` yang ditangani oleh router klien. Dengan `prefetch=True`, mengarahkan atau menyentuh tautan akan menghangatkan target melalui `window.__nexy_prefetch`.

> [!CATATAN]
> bentuk tag mengambil label sebagai `children`, bukan sebagai konten elemen: `<Link href="/about" children="About" />`. Untuk menempatkan markup di dalam tautan, gunakan formulir panggilan dengan komponen `children=` atau `.nexy` yang merender `<Slot />`.

## Audio dan Video

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` dan `Video(src, width=None, height=None, ...)` menampilkan pemain asli. `sources` menambahkan tag `<source>` dengan tipe MIME yang berasal dari setiap ekstensi.

## Komponen yang Anda tulis sendiri

Komponen `.nexy` yang dapat digunakan kembali adalah file di bawah `src/components/`: Python props di atas, HTML di bawah. Itu diimpor seperti modul Python lainnya.

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rute/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` tidak memiliki default, jadi halaman harus meneruskannya; `tone` kembali ke `"neutral"`. Markup di antara tag berada di dalam `<Slot />` (huruf kapital S). Lihat [.nexy files](README.md#components) untuk props, slot dan aturan bentuk tag.

## Mengimpor komponen klien

Dari file `.nexy`, impor komponen kerangka kerja berdasarkan jalur; kompiler memasangnya di klien dan meneruskan atribut sebagai props:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` melakukan hal yang sama di Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

Sintaks impor yang sama menyelesaikan `.json`, `.css` dan file gambar ke URL-nya.

## Templat dan Vite

`Template().render(path, context)` merender file templat (Jinja2, atau Markdown dirender ke HTML untuk rute `.md`). `Template().invalidate(path)` menghapusnya dari cache.

`Vite()` mengembalikan tag klien untuk mode saat ini: skrip HMR dalam pengembangan, bundel klien yang dibuat dalam produksi. Nexy menyebutnya untuk setiap halaman; Anda jarang membutuhkannya secara langsung.

## Belum dilaksanakan

`Form` dan `Script` adalah placeholder yang diekspor tanpa perilaku. Jangan bergantung pada mereka.

## Langkah selanjutnya

- [.nexy files](README.md): tempat pembantu ini digunakan
- [React](../react/differences.md): mengimpor komponen `.tsx`
- [Frontend](../../guides/frontend.md): bagaimana komponen klien digabungkan
