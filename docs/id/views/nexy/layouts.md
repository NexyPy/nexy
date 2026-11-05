# tata letak.nexy

File tata letak mode server (`useCSR = False`). Yang root memiliki dokumen HTML.

## Tata letak akar

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` dan `<body>` tinggal di sini dan tidak di tempat lain.
- `<Vite />` memasukkan skrip dan gaya klien satu kali, ke dalam `<head>`.
- `{{ children | safe }}` adalah tempat halaman, atau tata letak bersarang berikutnya, dirender.

## Tata letak bersarang

`layout.nexy` dalam subdirektori membungkus subpohon tersebut dan merender di dalam induknya. Itu tidak mengulangi tag dokumen:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` diterjemahkan sebagai `layout.nexy > blog/layout.nexy > page`.

## Komponen dan pulau

Tata letak dapat mengimpor komponen `.nexy` (header, footer) dan komponen klien. Komponen klien dalam tata letak adalah [pulau](../../rendering/islands.md) seperti yang lainnya:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Tanpa tata letak

Sebuah proyek tanpa `layout.nexy` masih menjawab dengan dokumen yang valid: Nexy kembali ke shell minimal dengan `<!DOCTYPE html>`, meta viewport dan tag Vite. Tambahkan tata letak segera setelah Anda memerlukan judul, font, atau navigasi.

## Di router modular

Pengontrol memilih tampilannya, sehingga mereka membuat sendiri tata letaknya:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## Apa yang tidak bisa dilakukannya

- Itu tidak dapat hidup berdampingan dengan `layout.tsx`, `layout.vue` atau `layout.svelte`: proyek mode server tidak memiliki rute klien ([mode](../../routing/fbr/modes.md)).
- Itu tidak berjalan di klien: gunakan pulau untuk interaktivitas.

## Langkah selanjutnya

- [Tata Letak](../../routing/fbr/layouts/README.md)
- [Warisan](../../routing/fbr/inheritance.md)
- [file .nexy](README.md)
