# Perutean berbasis file

Rute adalah file. URL adalah jalur file yang berhubungan dengan `src/routes/`, tanpa ekstensi.

## File ke URL

| Berkas | URL |
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

## Dua mode

`useCSR` memutuskan halamannya. Keduanya tidak dapat digabungkan dalam satu proyek: Nexy menolak untuk memulai ketika halaman server berada di sebelah rute klien.

| Mode | Halaman | Tata letak akar | Lihat |
|---|---|---|---|
| Server (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Mode server dan mode klien](modes.md) |
| Klien (`useCSR = True`) | file kerangka kerja | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

File `.py` adalah penangan API di kedua mode.

## Apa yang bukan rute

- Nama file yang dicadangkan: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- File dan folder yang dimulai dengan `_` atau `.`: gunakan untuk sebagian dan draf.
- Ekstensi yang tidak aktif untuk proyek Anda. File yang ekstensinya tidak aktif dilewati dengan peringatan.

## Satu file per URL

Dua file yang diselesaikan ke URL yang sama keduanya terdaftar. Jangan membuat `blog.nexy` di samping `blog/index.nexy`, dan jangan mencampur `index.nexy` dan `index.py` untuk jalur yang sama. Pilih satu.

## Di bagian ini

| Folder | Cakupannya |
|---|---|
| [halaman/](pages/README.md) | halaman, [rute dinamis](pages/dynamic-routes.md), grup rute |
| [layouts/](layouts/README.md) | satu halaman per jenis file tata letak |
| [handlers/](handlers/README.md) | `.py` penangan, validasi dan kesalahan |
| [dependensi/](dependencies/README.md) | `dependencies.py`, penjaga |
| [perangkat tengah/](middleware/README.md) | `middleware.py` |
| [kesalahan/](errors/README.md) | halaman tidak ditemukan dan kesalahan |
| [navigasi/](navigation/linking-and-navigating.md) | tautan, kait |
| [waktu nyata/](realtime/websocket.md) | WebSocket |
| [warisan](inheritance.md) | aturan pewarisan dalam satu tabel |

## Langkah selanjutnya

- [Mode server dan mode klien](modes.md)
- [Tata Letak](layouts/README.md)
- [Perutean modular](../modular/README.md)
