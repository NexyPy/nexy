# Pengecualian dan kesalahan

Sebuah permintaan bisa gagal di empat tempat, dan Nexy menjawab masing-masing permintaan secara berbeda. Halaman ini adalah indeksnya: temukan status yang Anda lihat, lalu baris yang menghasilkannya, lalu file yang menentukan isi.

> [!CATATAN]
> Ada tiga hal yang terpisah dan mudah tercampur: **Jawaban HTTP** (status dan isi), **halaman kesalahan** (`notfound.nexy`, `errors.nexy`), dan **baris log** (apa yang Anda baca di terminal). Mengubah halaman tidak mengubah status, dan menyesuaikan halaman tidak menyembunyikan log.

## Versi pendek

| Apa yang terjadi | Status | Browser melihat | Klien API melihat |
|---|---|---|---|
| tidak ada rute yang cocok dengan URL | `404` | `notfound.nexy`, jika tidak, laman bawaan | `{"detail": "Not Found"}` |
| segmen jalur tidak sesuai dengan anotasinya | `404` | halaman yang sama | `{"detail": "Not Found"}` |
| bidang kueri, header, cookie, atau isi tidak ada atau tidak valid | `422` | FastAPI isi JSON | FastAPI isi JSON |
| `notFound()` | `404` | halaman | `{"detail": ...}` |
| `unauthorized()` | `401` | halaman bawaan | `{"detail": ...}` |
| `forbidden()` | `403` | halaman bawaan | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | halaman bawaan | `{"detail": ...}` |
| pengecualian tidak ada yang tertangkap | `500` | `errors.nexy`, selain itu halaman bawaan | `{"detail", "reference"}` |
| `redirect(url)` | `307` | tujuan, tanpa halaman | tujuan, tanpa isi |
| `permanentRedirect(url)` | `308` | tujuan, tidak ada halaman | tujuan |

Klien API adalah permintaan yang header `Accept`-nya meminta JSON dan bukan halaman:

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!PERINGATAN]
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

| Tahap | Apa yang bisa gagal | Jawabannya |
|---|---|---|
| Middleware | `middleware.py` Anda, CORS, sesi | status pengecualian, yang lain `500` |
| Router | URL tidak cocok dengan file | `404` |
| Validasi | segmen jalur tidak dapat dikonversi | `404` |
| Validasi | bidang kueri, header, cookie, atau isi | `422` |
| Halaman, pengendali, tindakan, penjaga | `HTTPException` | statusnya |
| Halaman, pengendali, tindakan, penjaga | apa pun yang lain | `500` |

## Berangkat dari mana saja

`redirect`, `permanentRedirect`, `notFound`, `forbidden` dan `unauthorized` memunculkan pengecualian HTTP, sehingga panggilan yang sama berfungsi di halaman `.nexy`, penangan API, pengontrol modular, penjaga, `dependencies.py` dan tindakan.

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

| Panggil | Jawab | Kapan |
|---|---|---|
| `notFound(detail=None)` | `404` | sumber daya tidak ada |
| `unauthorized(detail=None, scheme=None)` | `401` | pengunjung harus login terlebih dahulu |
| `forbidden(detail=None)` | `403` | pengunjung dikenal tetapi mungkin tidak melihatnya |
| `redirect(url, status=307)` | `307` | kirim ke tempat lain, pertahankan metodenya |
| `redirect(url, status=303)` | `303` | setelah formulir: permintaan berikutnya adalah `GET` |
| `permanentRedirect(url)` | `308` | halaman dipindahkan yang harus diingat oleh mesin pencari |

Bangun tujuan dari nilai-nilai yang Anda percayai. `redirect(request.query_params["next"])` mengarahkan pengunjung ke mana pun yang disebutkan dalam tautan; ini adalah pengalihan terbuka. Tujuan yang memiliki jeda baris ditolak.

## Validasi: 422, atau 404

Parameter handler divalidasi oleh FastAPI berdasarkan anotasinya.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Masalah | Status | Mengapa |
|---|---|---|
| kolom kueri, header, cookie, atau isi hilang atau tidak valid | `422` | permintaan sampai ke handler, data salah |
| segmen jalur tidak valid (`/api/users/abc` untuk `id: int`) | `404` | folder tidak memiliki rute untuk non-angka, sehingga URL tidak ada |

Isi `422` adalah bentuk standar FastAPI, sehingga klien dan SDK yang dihasilkan tetap berfungsi:

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Untuk formulir atau tindakan, klien menerima `ActionError` dengan `status` dan `detail`; a `422` juga mengisi `error.fields` dengan satu pesan per kolom. Lihat [Tindakan](../guides/actions.md#errors-and-failures).

> [!TIPS]
> Validasi tanda tangan ketika aturannya tentang satu bidang (`limit: int = 10`). Validasi di isi ketika aturan memerlukan database atau bidang lain ("email ini sudah digunakan"): naikkan `HTTPException(409)` dan simpan pesan untuk klien.

## Halaman kesalahan khusus

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/route/errors.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| File | Status | Cakupan |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | setiap rute proyek |
| `src/routes/errors.nexy` | `500` | setiap rute proyek |
| `src/routes/forbidden.nexy` | `403` | setiap rute proyek |
| `src/routes/unauthorized.nexy` | `401` | setiap rute proyek |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` dan di bawahnya |
| `src/routes/blog/errors.nexy` | `500` | `/blog` dan di bawahnya |
| `src/routes/loading.nexy` | - | sudah dipesan, belum ada efek runtime |

Satu file di suatu tempat di rute menginstal jawaban untuk statusnya: salinan di root menjawab keseluruhan proyek, salinan di folder menjawab folder itu, dan file terdalam yang cocok dengan URL menang. URL di luar setiap salinan, dan status tanpa file sama sekali, mendapatkan halaman bergaya bawaan. Lihat [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md).

> [!PENTING]
> Halaman `errors.nexy` menggantikan halaman `500`; itu tidak menangkap pengecualian dan tidak mengubah baris log. Jika pengendali yang dimunculkan adalah halaman itu sendiri, halaman tersebut tidak dapat menampilkan detail kesalahannya sendiri: pertahankan `errors.nexy` sederhana dan independen.

## Pengecualian yang tidak tertangani

Pengecualian bahwa tidak ada yang tertangkap dicatat satu kali, dengan referensinya, dari mana asalnya, dan kode di sekitarnya. Statusnya adalah `500`, dan tubuhnya bergantung pada lingkungan.

| | `nexy dev` | `nexy build` lalu `nexy start` |
|---|---|---|
| Browser | kesalahan, baris kode Anda dan traceback | `errors.nexy`, selain itu halaman bawaan, dengan referensi |
| Klien API | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | pengecualian dan baris kode Anda | pengecualian, seluruh penelusuran balik dan referensi |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

Referensinya adalah delapan karakter, baru untuk setiap kegagalan. Pengunjung dapat mengutipnya, dan Anda menemukan penelusuran baliknya dengan mencari lognya. Baik pengecualian maupun kode tidak sampai ke pengunjung dalam produksi.

> [!PERHATIAN]
> Jangan mengembalikan penelusuran balik ke pengunjung dalam produksi, dan jangan menaruh rahasia dalam pesan kesalahan: `detail` dari `HTTPException` dikirim ke klien, dengan lolos HTML. Letakkan rahasianya di log, bukan di jawabannya.

## Tindakan dan bentuk

Suatu tindakan adalah titik akhir `POST` dengan jalur yang dihasilkan. Kegagalannya mengikuti aturan yang sama:

| Situasi | Status | Klien |
|---|---|---|
| sebuah field hilang atau tidak valid | `422` | `ActionError` dengan `fields` |
| `HTTPException(403)` dimunculkan dalam aksi | `403` | `ActionError` dengan `status` dan `detail` |
| pengecualian yang tidak tertangani | `500` | `ActionError`; referensinya ada di log server |
| header `Origin` adalah situs lain | `403` | ditolak sebelum tindakan berjalan |

Formulir tanpa JavaScript memposting ke jalur tindakan; jika berhasil menjawab `303` kembali ke halaman, jika gagal menampilkan halaman kesalahan. Lihat [Tindakan](../guides/actions.md#forms-without-javascript).

## Daftar periksa ketika suatu halaman menjawab hal yang salah

1. **Lihat statusnya**, bukan halamannya. Sebuah kebiasaan `notfound.nexy` masih menjawab `404`.
2. **Baca terminal.** Halaman yang gagal diimpor tidak didaftarkan, jadi URL-nya menjawab `404` selagi file ada. Kesalahan impor ada di log.
3. **Periksa ekstensinya.** Dengan `useCSR = True`, `.nexy` halaman termasuk dalam mode server; halaman dalam mode yang salah bukanlah rute.
4. **Periksa kedalamannya.** `notfound.nexy` atau `errors.nexy` hanya berfungsi jika salinan root ada.
5. **Minta JSON** dengan `Accept: application/json` untuk melihat bentuk yang diterima klien API Anda.
6. **Kutip referensi** dari `500` ketika Anda membuka terbitan atau mencari log.

## Langkah selanjutnya

- [Halaman kesalahan](../routing/fbr/errors/README.md): perilaku halaman penuh, dengan contoh
- [Validasi dan kesalahan](../routing/fbr/handlers/validation-and-errors.md): penangan API
- [Pemecahan masalah](../guides/troubleshooting.md): kesalahan yang sebenarnya terjadi
- [Testing](../guides/testing.md): menegaskan status dan isi
