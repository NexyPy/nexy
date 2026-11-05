# Konvensi file

Nama dan aturan yang dicadangkan di bawah `src/routes/`.

## File rute

| Mengajukan | Menjadi |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | rute direktorinya |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmen dinamis `{slug}` |
| `[...path].nexy` | mencakup semua `{path:path}` |
| `(group)/page.nexy` | `/page`: grup tidak muncul di URL |
| `name.py` | Pengendali API; nama fungsi `GET`, `POST`, ... adalah metodenya |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | rute klien ketika kerangka kerja diaktifkan dengan `useFF` |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## File yang dicadangkan

| Mengajukan | Peran | Detail |
|---|---|---|
| `layout.nexy` | mode server: membungkus setiap halaman di bawahnya; yang root memiliki dokumen HTML | [tata letak.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | mode klien (React): yang root memiliki dokumen HTML, yang bersarang membungkus halaman | [tata letak.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | mode klien: tata letak bersarang | [tata letak.vue](../views/vue/differences.md), [tata letak.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404 halaman untuk direktorinya | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 halaman untuk direktorinya | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 halaman untuk direktorinya | [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 halaman untuk direktorinya | [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | dilindungi undang-undang; belum ada efek runtime | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `middleware.py` | sebuah `async def middleware(request, call_next)` membungkus permintaan direktori dan di bawahnya | [File middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | daftar `dependencies = [fn, ...]` diterapkan pada direktori dan turunannya | [Ketergantungan](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python penanda paket | |
| `favicon.ico` | disajikan di `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` dan `useLoadingExtensions` mencadangkan lebih banyak ekstensi untuk nama-nama ini. Lihat [Konfigurasi](config.md).

Dua file Python tabel, berdampingan dalam satu folder:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

Dan halaman yang menjawab 404 foldernya:

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## File yang diabaikan

- File atau folder yang dimulai dengan `_` atau `.`: gunakan untuk sebagian, draf, dan pembantu.
- File yang ekstensinya tidak aktif untuk proyek: dilewati dengan peringatan.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Satu file per URL

Dua file yang diselesaikan ke URL yang sama keduanya terdaftar. Jangan letakkan `blog.nexy` di sebelah `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Di luar `src/routes/`

| Map | Tujuan |
|---|---|
| `src/components/` | komponen yang diimpor berdasarkan halaman; tidak pernah rute |
| `src/apps/` | pengontrol dan modul [router modular](../routing/modular/README.md) |
| `public/` | file statis, disajikan di root: `public/logo.svg` adalah `/logo.svg` (juga di bawah `/public/`) |
| `__nexy__/` | keluaran yang dihasilkan; jangan berkomitmen |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Langkah selanjutnya

- [Perutean](../routing/README.md)
- [Struktur proyek](../getting-started/project-structure.md)
