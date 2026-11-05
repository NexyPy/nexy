# Konvensi file

Nama dan aturan yang dicadangkan di bawah `src/routes/`.

## File rute

| File | Menjadi |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | rute direktorinya |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmen dinamis `{slug}` |
| `[...path].nexy` | mencakup semua `{path:path}` |
| `(group)/page.nexy` | `/page`: grup tidak muncul di URL |
| `name.py` | pengendali API; nama fungsi `GET`, `POST`, ... adalah metodenya |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | rute klien ketika kerangka kerja diaktifkan dengan `useFF` |

## File yang dicadangkan

| File | Peran | Detail |
|---|---|---|
| `layout.nexy` | mode server: membungkus setiap halaman di bawahnya; yang root memiliki dokumen HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | mode klien (React): yang root memiliki dokumen HTML, yang bersarang membungkus halaman | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | mode klien: tata letak bersarang | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | 404 halaman untuk direktorinya | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 halaman untuk direktorinya | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | 403 halaman untuk direktorinya | [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 halaman untuk direktorinya | [Halaman kesalahan per folder](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | dicadangkan; belum ada efek runtime | [Halaman kesalahan](../routing/fbr/errors/README.md) |
| `middleware.py` | dan `async def middleware(request, call_next)` membungkus permintaan direktori dan di bawah | [Middleware files](../routing/fbr/middleware/README.md) |
| `dependencies.py` | daftar `dependencies = [fn, ...]` yang diterapkan pada direktori dan turunannya | [Dependensi](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python penanda paket | |
| `favicon.ico` | bertugas di `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` dan `useLoadingExtensions` mencadangkan lebih banyak ekstensi untuk nama-nama ini. Lihat [Konfigurasi](config.md).

## File yang diabaikan

- File atau folder yang dimulai dengan `_` atau `.`: gunakan untuk sebagian, draf, dan pembantu.
- File yang ekstensinya tidak aktif untuk proyek: dilewati dengan peringatan.

## Satu file per URL

Dua file yang diselesaikan ke URL yang sama keduanya terdaftar. Jangan letakkan `blog.nexy` di sebelah `blog/index.nexy`.

## Di luar `src/routes/`

| Map | Tujuan |
|---|---|
| `src/components/` | komponen yang diimpor berdasarkan halaman; tidak pernah merutekan |
| `src/apps/` | pengontrol dan modul dari [router modular](../routing/modular/README.md) |
| `public/` | file statis, disajikan di root: `public/logo.svg` adalah `/logo.svg` (juga di bawah `/public/`) |
| `__nexy__/` | menghasilkan keluaran; jangan melakukan |

## Langkah selanjutnya

- [Perutean](../routing/README.md)
- [Struktur proyek](../getting-started/project-structure.md)
