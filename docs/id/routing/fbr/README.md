# Perutean berbasis file

Rute adalah file. URL adalah jalur file yang berhubungan dengan `src/routes/`, tanpa ekstensi.

## File ke URL

| Mengajukan | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` memetakan ke direktorinya, bukan ke `/index`. Direktori dalam tanda kurung adalah **grup**: direktori ini mengatur file tanpa muncul di URL.

Dalam mode klien, file halaman adalah `.tsx`, `.vue` atau `.svelte` bukannya `.nexy`; aturan URL-nya sama.

Dua file dari tabel itu: halaman yang membaca segmennya, dan sebuah handler yang menjawab JSON.

```nexy filename="src/rute/blog/[siput].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}
```

## Dua mode

`useCSR` memutuskan halamannya. Keduanya tidak dapat digabungkan dalam satu proyek: Nexy menolak untuk memulai ketika halaman server berada di sebelah rute klien.

| Modus | Halaman | Tata letak akar | Lihat |
|---|---|---|---|
| Server (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Mode server dan mode klien](modes.md) |
| Klien (`useCSR = True`) | file kerangka | `layout.tsx` | [tata letak.tsx](../../views/react/differences.md) |

File `.py` adalah penangan API di kedua mode.

Sakelarnya adalah satu baris `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True  # client mode: src/routes/*.tsx are the pages
```

## Apa yang bukan rute

- Nama file yang dicadangkan: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- File dan folder yang dimulai dengan `_` atau `.`: gunakan untuk sebagian dan draf.
- Ekstensi yang tidak aktif untuk proyek Anda. File yang ekstensinya tidak aktif dilewati dengan peringatan.

```text
src/routes/
├─ layout.nexy          wraps the pages, not a route
├─ middleware.py        wraps the requests, not a route
├─ index.nexy           /
├─ _card.nexy           a partial: no URL
└─ .draft.nexy          a draft: no URL
```

## Satu file per URL

Dua file yang diselesaikan ke URL yang sama keduanya terdaftar. Jangan membuat `blog.nexy` di samping `blog/index.nexy`, dan jangan mencampur `index.nexy` dan `index.py` untuk jalur yang sama. Pilih satu.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: delete one of the two
```

## Di bagian ini

| Map | Apa yang dicakupnya |
|---|---|
| [halaman/](pages/README.md) | halaman, [rute dinamis](pages/dynamic-routes.md), grup rute |
| [tata letak/](layouts/README.md) | satu halaman per jenis file tata letak |
| [penangan/](handlers/README.md) | `.py` penangan, validasi dan kesalahan |
| [ketergantungan/](dependencies/README.md) | `dependencies.py`, penjaga |
| [perangkat tengah/](middleware/README.md) | `middleware.py` |
| [kesalahan/](errors/README.md) | halaman tidak ditemukan dan halaman kesalahan |
| [navigasi/](navigation/linking-and-navigating.md) | tautan, kait |
| [waktu nyata/](realtime/websocket.md) | WebSocket |
| [warisan](inheritance.md) | aturan pewarisan dalam satu tabel |

## Langkah selanjutnya

- [Mode server dan mode klien](modes.md)
- [Tata Letak](layouts/README.md)
- [Perutean modular](../modular/README.md)
