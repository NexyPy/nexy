# Apa itu Nexy?

Nexy adalah kerangka kerja Python untuk aplikasi web fullstack: halaman Anda dan API Anda berada dalam satu proyek dan dilayani oleh satu server.

## Apa yang Anda dapatkan

- **Halaman dalam Python.** File `.nexy` adalah HTML dengan beberapa baris Python di atasnya; file `.md` juga merupakan halaman. Tidak diperlukan JavaScript untuk merender halaman.
- **API dalam proyek yang sama.** File `.py` di bawah `src/routes/` menjawab permintaan HTTP: fungsi bernama `GET` menjawab `GET`, fungsi bernama `POST` menjawab `POST`.
- **Dokumentasi API gratis.** Setiap rute API muncul dalam skema OpenAPI, dan Scalar menampilkannya sebagai referensi interaktif di `/docs`.
- **Formulir yang memanggil Python.** Formulir, atau panggilan yang diketik dari browser, mencapai fungsi Python yang sama.
- **Kerangka kerja frontend bila Anda menginginkannya.** React, Vue, Svelte, Solid atau Preact, untuk satu komponen atau untuk keseluruhan situs.
- **Satu perintah untuk bekerja, satu untuk dikirim.** `nx dev` dimuat ulang saat Anda menyimpan; `nx build` menyiapkan produksi.

## Di atas apa itu dibangun

Versi saat ini, 2.2, menggunakan alat yang mungkin sudah Anda ketahui:

| Bagian | Dibangun | Apa artinya bagi Anda |
|---|---|---|
| Server dan API | [FastAPI](https://fastapi.tiangolo.com/) | rute API adalah rute FastAPI: validasi dan dependensi Pydantic berfungsi seperti biasa |
| Referensi API | OpenAPI dan [Skalar](https://scalar.com/) | skemanya ada di `/openapi.json`, referensinya ada di `/docs` |
| Halaman | Jinja2 | halaman `.nexy` menggunakan tag Jinja2 seperti `{{ title }}` |
| Bagian depan (opsional) | [Vite](https://vite.dev/) | hanya dengan kerangka frontend, yang juga membutuhkan Node.js |

## Halaman pertama dan titik akhir pertama

Sebuah halaman, di `/hello`:

```nexy filename="src/rute/halo.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Titik akhir, di `GET /api/items`, terdaftar di `/docs` tanpa kode tambahan apa pun:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## Apa yang Nexy serahkan padamu

Basis data, login, dan aturan tentang siapa yang boleh melakukan apa yang menjadi milik aplikasi Anda, jadi Anda memilih perpustakaannya. [Databases](../guides/databases.md) dan [Middleware dan keamanan](../guides/middleware-and-security.md) menunjukkan lokasi masing-masing plug-in.

## Langkah selanjutnya

- [Instalasi](installation.md): instal uv dan buat proyek
- [Mulai cepat](quick-start.md): jalankan, ubah halaman, buat
- [Konsep inti](core-concepts.md): beberapa kata yang digunakan dokumen lainnya
