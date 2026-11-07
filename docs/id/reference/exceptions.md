# Pengecualian dan kesalahan

Sebuah permintaan bisa gagal di empat tempat, dan Nexy menjawab masing-masing permintaan secara berbeda. Halaman ini adalah indeksnya: temukan status yang Anda lihat, lalu baris yang menghasilkannya, lalu file yang menentukan isi.

> [!NOTE]
> Ada tiga hal yang terpisah dan mudah tercampur: **Jawaban HTTP** (status dan isi), **halaman kesalahan** (`notfound.nexy`, `errors.nexy`), dan **baris log** (apa yang Anda baca di terminal). Mengubah halaman tidak mengubah status, dan menyesuaikan halaman tidak menyembunyikan log.

## Versi pendek

| Apa yang terjadi | Status | Peramban melihat | Klien API melihat |
|---|---|---|---|
| tidak ada rute yang cocok dengan URL | `404` | `notfound.nexy`, jika tidak, halaman bawaan | `{"detail": "Not Found"}` |
| segmen jalur tidak sesuai dengan anotasinya | `404` | halaman yang sama | `{"detail": "Not Found"}` |
| bidang kueri, header, cookie, atau isi tidak ada atau tidak valid | `422` | FastAPI badan JSON | FastAPI badan JSON |
| `notFound()` | `404` | halaman | `{"detail": ...}` |
| `unauthorized()` | `401` | halaman bawaan | `{"detail": ...}` |
| `forbidden()` | `403` | halaman bawaan | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | halaman bawaan | `{"detail": ...}` |
| pengecualian tidak ada yang tertangkap | `500` | `errors.nexy`, jika tidak, halaman bawaan | `{"detail", "reference"}` |
| `redirect(url)` | `307` | tujuan, tidak ada halaman | tujuannya, tidak ada tubuh |
| `permanentRedirect(url)` | `308` | tujuan, tidak ada halaman | tujuan |

Klien API adalah permintaan yang header `Accept`-nya meminta JSON dan bukan halaman:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` mengirimkan `Accept: */*` secara default, yang mendapatkan halaman HTML. Tambahkan `-H "Accept: application/json"` saat Anda menguji bentuk JSON. Browser terus mendapatkan halaman.

## Dari mana sebuah kegagalan berasal

```diagram filename="Satu permintaan, empat pintu keluar"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Panggung | Apa yang bisa gagal | Jawabannya |
|---|---|---|
| Perangkat Tengah | `middleware.py`, CORS, sesi Anda | status pengecualian, yang lain `500` |
| Perute | URL tidak cocok dengan file | `404` |
| Validasi | segmen jalur tidak dapat dikonversi | `404` |
| Validasi | bidang kueri, header, cookie, atau isi | `422` |
| Halaman, pawang, aksi, penjaga | `HTTPException` | statusnya |
| Halaman, pawang, aksi, penjaga | hal lain | `500` |

## Berangkat dari mana saja

`redirect`, `permanentRedirect`, `notFound`, `forbidden` dan `unauthorized` memunculkan pengecualian HTTP, sehingga panggilan yang sama berfungsi di halaman `.nexy`, penangan API, pengontrol modular, penjaga, `dependencies.py` dan tindakan.

<!-- router:fbr,custom -->
```python filename="src/rute/posting/[siput].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/posts/posts_by_slug_controller.py"
from nexy import notFound, redirect
from nexy.decorators import Controller

from src.posts import find


@Controller("/posts/{slug}")
class PostsBySlugController:
    async def get(self, slug: str):
        post = find(slug)
        if post is None:
            notFound("No such post")
        if post.moved_to:
            redirect(post.moved_to)
        return post
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

| Telepon | Jawaban | Kapan |
|---|---|---|
| `notFound(detail=None)` | `404` | sumber dayanya tidak ada |
| `unauthorized(detail=None, scheme=None)` | `401` | pengunjung harus login terlebih dahulu |
| `forbidden(detail=None)` | `403` | pengunjung diketahui tetapi mungkin tidak melihatnya |
| `redirect(url, status=307)` | `307` | kirim mereka ke tempat lain, pertahankan metodenya |
| `redirect(url, status=303)` | `303` | setelah formulir: permintaan berikutnya adalah `GET` |
| `permanentRedirect(url)` | `308` | halaman dipindahkan yang harus diingat oleh mesin pencari |

Bangun tujuan dari nilai-nilai yang Anda percayai. `redirect(request.query_params["next"])` mengarahkan pengunjung ke mana pun yang disebutkan dalam tautan; ini adalah pengalihan terbuka. Tujuan yang memiliki jeda baris ditolak.

## Validasi: 422, atau 404

Parameter handler divalidasi oleh FastAPI berdasarkan anotasinya.

<!-- router:fbr,custom -->
```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/search/search_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Header


@Controller("/api/search")
class SearchApiController:
    async def get(self, q: str, limit: int = 10, x_token: str = Header(...)):
        return {"q": q, "limit": limit}
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

| Masalah | Status | Mengapa |
|---|---|---|
| bidang kueri, header, cookie, atau isi tidak ada atau tidak valid | `422` | permintaan sampai ke handler, datanya salah |
| segmen jalur tidak valid (`/api/users/abc` untuk `id: int`) | `404` | folder tersebut tidak memiliki rute untuk non-angka, jadi URL-nya tidak ada |

Isi `422` adalah bentuk standar FastAPI, sehingga klien dan SDK yang dihasilkan tetap berfungsi:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Untuk formulir atau tindakan, klien menerima `ActionError` dengan `status` dan `detail`; a `422` juga mengisi `error.fields` dengan satu pesan per kolom. Lihat [Tindakan](../guides/actions.md#errors-and-failures).

> [!TIP]
> Validasi tanda tangan ketika aturannya tentang satu bidang (`limit: int = 10`). Validasi di isi ketika aturan memerlukan database atau bidang lain ("email ini sudah digunakan"): naikkan `HTTPException(409)` dan simpan pesan untuk klien.

## Halaman kesalahan khusus

<!-- router:fbr,custom -->
```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/route/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| Mengajukan | Status | Ruang lingkup |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | setiap rute proyek |
| `src/routes/errors.nexy` | `500` | setiap rute proyek |
| `src/routes/forbidden.nexy` | `403` | setiap rute proyek |
| `src/routes/unauthorized.nexy` | `401` | setiap rute proyek |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` dan di bawahnya |
| `src/routes/blog/errors.nexy` | `500` | `/blog` dan di bawahnya |
| `src/routes/loading.nexy` | - | sudah dipesan, belum ada efek runtime |

Satu file di suatu tempat di rute menginstal jawaban untuk statusnya: salinan di root menjawab keseluruhan proyek, salinan di folder menjawab folder itu, dan file terdalam yang cocok dengan URL menang. URL di luar setiap salinan, dan status tanpa file sama sekali, mendapatkan halaman bergaya bawaan. Lihat [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> Halaman `errors.nexy` menggantikan halaman `500`; itu tidak menangkap pengecualian dan tidak mengubah baris log. Jika pengendali yang dimunculkan adalah halaman itu sendiri, halaman tersebut tidak dapat menampilkan detail kesalahannya sendiri: pertahankan `errors.nexy` sederhana dan independen.
<!-- /router -->

<!-- router:modular -->
Router modular tidak memiliki halaman kesalahan dalam file: `404`, `500`, `403` atau `401` mendapatkan halaman gaya bawaan. Halaman kesalahan per folder adalah konvensi router berbasis file.
<!-- /router -->

## Pengecualian yang tidak tertangani

Pengecualian bahwa tidak ada yang tertangkap dicatat satu kali, dengan referensinya, dari mana asalnya, dan kode di sekitarnya. Statusnya adalah `500`, dan tubuhnya bergantung pada lingkungan.

| | `nexy dev` | `nexy build` lalu `nexy start` |
|---|---|---|
| Peramban | kesalahan, baris kode Anda, dan penelusuran balik | `errors.nexy`, jika tidak, halaman bawaan, dengan referensi |
| klien API | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | pengecualian dan baris kode Anda | pengecualian, keseluruhan penelusuran balik, dan referensi |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Referensinya adalah delapan karakter, baru untuk setiap kegagalan. Pengunjung dapat mengutipnya, dan Anda menemukan penelusuran baliknya dengan mencari lognya. Baik pengecualian maupun kode tidak sampai ke pengunjung dalam produksi.

> [!CAUTION]
> Jangan mengembalikan penelusuran balik ke pengunjung dalam produksi, dan jangan menaruh rahasia dalam pesan kesalahan: `detail` dari `HTTPException` dikirim ke klien, dengan lolos HTML. Letakkan rahasianya di log, bukan di jawabannya.

## Tindakan dan bentuk

Suatu tindakan adalah titik akhir `POST` dengan jalur yang dihasilkan. Kegagalannya mengikuti aturan yang sama:

| Situasi | Status | Klien |
|---|---|---|
| ada bidang yang hilang atau tidak valid | `422` | `ActionError` dengan `fields` |
| `HTTPException(403)` diangkat dalam aksi | `403` | `ActionError` dengan `status` dan `detail` |
| pengecualian yang tidak tertangani | `500` | `ActionError`; referensinya ada di log server |
| header `Origin` adalah situs lain | `403` | menolak sebelum aksi berjalan |

Formulir tanpa JavaScript memposting ke jalur tindakan; jika berhasil menjawab `303` kembali ke halaman, jika gagal menampilkan halaman kesalahan. Lihat [Tindakan](../guides/actions.md#forms-without-javascript).

## Daftar periksa ketika suatu halaman menjawab hal yang salah

1. **Lihat statusnya**, bukan halamannya. Sebuah kebiasaan `notfound.nexy` masih menjawab `404`.
2. **Baca terminal.** Halaman yang gagal diimpor tidak terdaftar, jadi URL-nya menjawab `404` selagi file ada. Kesalahan impor ada di log.
3. **Periksa ekstensinya.** Dengan `useCSR = True`, `.nexy` halaman termasuk dalam mode server; halaman dalam mode yang salah bukanlah rute.
4. **Periksa kedalamannya.** `notfound.nexy` atau `errors.nexy` hanya berfungsi jika salinan root ada.
5. **Minta JSON** dengan `Accept: application/json` untuk melihat bentuk yang diterima klien API Anda.
6. **Kutip referensi** dari `500` ketika Anda membuka terbitan atau mencari log.

## Langkah selanjutnya

- [Halaman kesalahan](../routing/fbr/errors/README.md): perilaku halaman penuh, dengan contoh
- [Validasi dan kesalahan](../routing/fbr/handlers/validation-and-errors.md): penangan API
- [Pemecahan masalah](../guides/troubleshooting.md): kesalahan yang sebenarnya terjadi
- [Pengujian](../guides/testing.md): menegaskan status dan isi
