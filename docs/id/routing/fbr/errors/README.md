# Halaman kesalahan

Permintaan yang gagal harus tetap menjawab seperti situs Anda lainnya: halaman dengan kata-kata Anda sendiri untuk pengunjung, kegagalan yang sama seperti JSON untuk klien API. Nexy menjawab keduanya, dan satu file menggantikan setiap jawaban.

Halaman ini adalah petanya: file mana yang menjawab status apa, dan bagaimana membuat status pertama Anda. Halaman-halaman folder mendapatkan [halamannya sendiri](folder-pages.md).

## Satu kegagalan, dua jawaban

```diagram filename="yang menjawab permintaan yang gagal"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Halaman pertama Anda

Buat `src/routes/notfound.nexy` dan tulis apa yang harus dibaca pengunjung:

```nexy filename="src/rute/tidak ditemukan.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Simpan, dan minta URL tidak ada yang berfungsi:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

File di root rute menjawab keseluruhan proyek; salinan dalam folder hanya menjawab folder itu dan [menyimpan sisanya sebagaimana adanya](folder-pages.md). Tanpa file apa pun, Nexy menyajikan halaman bergaya bawaannya.

## File mana yang menjawab

| File | Jawaban |
|---|---|
| `notfound.nexy` | `404` untuk direktorinya |
| `errors.nexy` | `500` untuk direktorinya |
| `forbidden.nexy` | `403` untuk direktorinya |
| `unauthorized.nexy` | `401` untuk direktorinya |
| `loading.nexy` | dilindungi undang-undang; belum ada efek runtime |

| Situasi | Jawaban |
|---|---|
| Tidak ada rute yang cocok | `404` |
| Segmen dinamis tidak dapat dikonversi ke anotasinya | `404` |
| Pengecualian yang tidak tertangani, di halaman atau pengendali API | `500` |
| `raise HTTPException(status_code=403)` | status yang Anda naikkan, sebagai HTML atau JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, dari mana saja dalam permintaan |
| `redirect()`, `permanentRedirect()` | pengalihan nyata tanpa halaman kesalahan |

## Tinggalkan halaman atau jawaban dari kode

`redirect`, `permanentRedirect`, `notFound`, `forbidden` dan `unauthorized` memunculkan pengecualian HTTP, sehingga panggilan yang sama berfungsi di halaman `.nexy`, penangan API, pengontrol modular, penjaga, dan `dependencies.py`. Mereka memiliki nama yang sama di klien (`@nexy/client`).

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Hubungi | Jawab |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` mengubah POST menjadi GET setelah formulir |
| `permanentRedirect(url)` | `308`; browser dan mesin pencari mengingatnya |
| `notFound(detail=None)` | `404`: halaman `notfound`, atau JSON untuk klien API |
| `forbidden(detail=None)` | `403`: pengunjung dikenal tetapi mungkin tidak melihatnya |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` menambahkan `WWW-Authenticate` |

Jawaban pengalihan dengan header `Location` dan tanpa halaman, juga ke klien API. Bangun tujuan dari nilai-nilai yang Anda percayai: `redirect(request.query_params["next"])` mengarahkan pengunjung ke mana pun yang disebutkan dalam tautan. Tujuan dengan jeda baris ditolak.

Seorang penjaga melindungi seluruh folder:

```python filename="src/rute/pribadi/dependensi.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML atau JSON

Pengecualian yang sama menjawab secara berbeda tergantung pada siapa yang bertanya:

- Browser (`Accept: text/html`) mendapat halaman HTML. Detailnya lolos dari HTML, sehingga pesan yang dibuat dari masukan pengguna tidak dapat memasukkan markup.
- Klien yang meminta JSON dan bukan halaman (`Accept: application/json`) mendapat `{"detail": "..."}` dengan kode status yang sama.

```python filename="src/routes/api/item/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!CATATAN]
> klien yang mengirimkan `Accept: */*` (default `curl` dan banyak perpustakaan HTTP) menerima halaman HTML. Setel `Accept: application/json` untuk kesalahan JSON.

## Pengecualian yang tidak tertangani

Pengecualian yang tidak ditangani apa pun dicatat satu kali, dengan pengecualian, dari mana asalnya dan kode di sekitarnya, dan dijawab sesuai dengan modenya.

| | `nx dev` | `nx start` |
|---|---|---|
| Browser | halaman dengan kesalahan, baris kode Anda yang memunculkannya dan penelusuran balik lengkap | halaman `500` bawaan (atau `errors.nexy`) Anda dengan referensi |
| Klien JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Log server | pengecualian dan baris kode Anda | pengecualian dan seluruh penelusuran balik, dengan referensi yang sama |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Referensinya adalah delapan karakter, baru untuk setiap kegagalan. Pengunjung dapat mengutipnya, dan Anda menemukan penelusuran baliknya dengan mencari lognya. Baik pengecualian maupun kode tidak sampai ke pengunjung dalam produksi. `errors.nexy` khusus hanya menggantikan halaman; garis log tetap ada.

## Kesalahan validasi

Header, parameter kueri, atau bidang isi yang hilang menjawab `422` dengan isi JSON FastAPI, untuk setiap klien. Lihat [Validasi dan kesalahan](../handlers/validation-and-errors.md).

## Langkah selanjutnya

- [Halaman kesalahan per folder](folder-pages.md): 404, 403 atau 401 milik Anda sendiri dalam satu folder
- [Rute dinamis](../pages/dynamic-routes.md)
- [Rute API](../handlers/README.md)
- [Pengujian](../../../guides/testing.md)
