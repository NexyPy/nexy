# Rute dinamis

Segmen jalur yang ditulis dalam tanda kurung siku cocok dengan nilai apa pun dan menyerahkannya ke halaman atau pengendali.

## Segmen dinamis

`blog/[slug].nexy` melakukan servis `/blog/{slug}`. Di halaman, nyatakan segmen sebagai properti; dalam penangan Python, anggap itu sebagai argumen.

```nexy filename="src/rute/blog/[siput].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Segmen yang diketik

Anotasi menentukan jenisnya.

| Dimana | Konversi |
|---|---|
| `.py` handler | semua FastAPI jenis anotasi (`int`, `UUID`, `Enum`...) |
| `.nexy` halaman | `int` dan `float` dikonversi; yang lainnya tetap berupa string |

Nilai yang tidak cocok dengan anotasi adalah **tidak ditemukan**: `/api/users/abc` menjawab `404`, karena rute dinamis menangkap URL apa pun dan URL yang tidak dapat dikonversi sama sekali tidak ada. Lihat [Validasi dan kesalahan](../handlers/validation-and-errors.md).

## Segmen yang mencakup semua

`docs/[...path].nexy` melakukan servis `/docs/{path:path}`. Segmen yang tersisa tiba sebagai satu string, termasuk garis miring.

```nexy filename="src/rute/dokumen/[...jalan].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` memberi `path == "a/b/c"`.

## Grup rute

Direktori dalam tanda kurung mengatur file tanpa muncul di URL. Ia masih mengambil bagian dalam [warisan](../inheritance.md): `layout.*` dan `dependencies.py` berlaku pada apa yang ada di dalamnya.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Gunakan grup untuk memberikan tata letak berbeda pada bagian yang berbeda tanpa mengubah URL-nya.

## Prioritas

Rute statis menang atas rute dinamis, dan rute dinamis mengalahkan rute umum: `/blog/new` cocok dengan `blog/new.nexy` sebelum `blog/[slug].nexy`.

## Satu file per URL

Dua file yang diselesaikan ke URL yang sama keduanya terdaftar. Jangan letakkan `blog.nexy` di sebelah `blog/index.nexy`, atau gabungkan `index.nexy` dan `index.py` untuk jalur yang sama.

## Langkah selanjutnya

- [Halaman](README.md)
- [Halaman kesalahan](../errors/README.md)
- [Konvensi file](../../../reference/file-conventions.md)
