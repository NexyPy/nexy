# Halaman kesalahan per folder

Sebuah folder dapat menjawab kesalahannya sendiri: sebuah blog dengan 404 dengan kata-katanya sendiri, sebuah area pribadi yang menawarkan formulir masuk alih-alih `401` kosong. Situs lainnya mempertahankan halaman yang sudah ada.

Halaman ini menambahkan salah satu file tersebut dan menunjukkan jawabannya.

## Aturannya

**File terdalam yang cocok dengan jawaban URL.** Segala sesuatu yang lain tetap apa adanya: kode status yang sama, JSON untuk klien API, dan halaman bawaan setelah tidak ada folder rantai yang memiliki file.

![Cakupan halaman kesalahan](../../../assets/error-page-scopes.svg)

Untuk `/blog/2024/hello` Nexy berjalan ke atas pohon: `/blog/2024`, lalu `/blog`, lalu `/`. Folder pertama yang menyimpan file menjawab. Folder cocok secara keseluruhan: `/blogger/hello` tidak berada di bawah `/blog`, jadi salinan di `blog/` tidak pernah menjawabnya.

## Keempat file

| File | Jawaban | Apa yang mencapainya |
|---|---|---|
| `notfound.nexy` | `404` | URL tidak ada rute yang cocok, `notFound()` |
| `errors.nexy` | `500` | pengecualian tidak ada yang ditangani |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` tetap dicadangkan: belum memiliki efek runtime.

Satu file di suatu tempat di `src/routes/` sudah cukup bagi Nexy untuk menjawab status itu: salinan di root menjawab keseluruhan proyek, salinan di folder menjawab folder itu, dan URL di luar setiap salinan mendapatkan halaman bawaan. Cadangan ekstensi lain untuk nama-nama ini di `nexyconfig.py` dengan `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` dan `useUnauthorizedExtensions`.

## Halaman folder pertama Anda

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Jalankan proyek dan minta postingan yang tidak ada:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

URL di luar folder menyimpan halaman yang sudah Anda miliki:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## Sebuah 401 yang mengarah ke suatu tempat

Folder kawasan lindung menjawab `401` dengan halaman yang menawarkan jalan masuk:

```nexy filename="src/routes/private/tidak sah.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/rute/pribadi/dependensi.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Setiap panggilan dan status menyimpan dua jawabannya:

| Siapa yang bertanya | `401` dengan file | `401` tanpa file |
|---|---|---|
| Browser (`Accept: text/html`) | halaman folder | halaman bawaan |
| Klien (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` menambahkan `WWW-Authenticate: Bearer` ke kedua jawaban. Detail yang dibuat dari masukan pengguna di-escape dalam HTML di halaman.

> [!TIP]
> `Accept: */*`, default `curl` dan banyak perpustakaan HTTP, tidak meminta keduanya dan menerima halaman HTML. Tambahkan `-H "Accept: application/json"` bila Anda menginginkan jawaban JSON.

## Periksa itu

```python filename="tes/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## Langkah selanjutnya

- [Halaman kesalahan](README.md): apa yang memicu setiap status, HTML atau JSON
- [Dependensi dan penjaga](../dependencies/README.md): melindungi seluruh folder
- [Pengujian](../../../guides/testing.md): `TestClient` dari pengujian pertama
