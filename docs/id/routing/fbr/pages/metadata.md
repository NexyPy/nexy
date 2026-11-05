# Metadata halaman

Sebuah halaman memberi nama judul dan tag kepalanya, dan tata letak akar menuliskannya satu kali.

## Katakan di halaman

Untuk halaman yang tidak pernah berubah, tuliskan literal di bagian atas frontmatter:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Jika judul bergantung pada data, panggil `setMetadata` sebagai gantinya:

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Pengontrol modular memanggil `setMetadata(...)` sebelum mengembalikan `useViews(...)`.

## Tuliskan di tata letak

Tata letak root memiliki `<head>`. Satu baris menulis apa yang dikatakan halaman itu, lolos:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Sebuah halaman berjalan sebelum tata letaknya, sehingga tata letak menemukan apa yang diminta halaman tersebut. Halaman yang menyatakan tidak ada yang mendapatkan `useTitle` dari `nexyconfig.py` Anda, dan tidak ada tag lain.

## Ladang

| Bidang | Ditulis sebagai |
|---|---|
| `title` | `<title>`; dengan `title_template="%s \| My site"` judulnya dimasukkan ke dalam `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, misalnya `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | satu `<meta property="og:...">` per kunci: `{"image": "/cover.png"}` menghasilkan `og:image` |
| `twitter` | satu `<meta name="twitter:...">` per kunci |
| `extra` | daftar dikt atribut, masing-masing satu `<meta>`: `[{"name": "theme-color", "content": "#fff"}]` |

Panggilan selanjutnya menggantikan suatu nilai; `og`, `twitter` dan `extra` menambah apa yang ada di sana. Bidang yang tidak ada memunculkan `TypeError`, jadi kesalahan ketik tidak berarti apa-apa.

## Aman secara default

Setiap nilai lolos dari HTML, sehingga judul yang dibuat dari URL atau dari database tidak dapat menutup tag dan memasukkan skrip. Sebuah nilai di-escape satu kali, ketika tata letak memanggil `html()`: jangan meng-escape nilai tersebut sendiri.

## Langkah selanjutnya

- [Halaman](README.md)
- [Tata Letak](../layouts/README.md)
- [Halaman kesalahan](../errors/README.md)
