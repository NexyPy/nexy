# Dokumentasi Nexy

**Kerangka kerja Python untuk aplikasi web fullstack.**

Nexy adalah tentang perpaduan antara backend Python dan frontend browser. Alih-alih dua server, dua sistem pembangunan dan dua tabel rute, Anda mendapatkan satu asal: FastAPI dan Starlette melayani aplikasi, Vite membangun klien, dan file di bawah `src/routes/` adalah rute - `.nexy` adalah halaman, `.py` adalah penangan API.

- **Python terlebih dahulu.** Halaman, titik akhir, formulir, dan tindakan adalah Python, dan halaman yang dirender oleh server tidak memerlukan kerangka kerja frontend.
- **Tiga router, satu integrasi.** Berbasis file, modular, atau yang sudah ada FastAPI `APIRouter`.
- **Frontend bila Anda menginginkannya.** React, Vue, Svelte, Solid atau Preact, per halaman sebagai pulau, atau untuk keseluruhan proyek dalam mode klien.
- **Rendering, satu model.** Render server, halaman cache, dan pulau ditentukan per halaman; perutean klien adalah peralihan proyek.
- **Tindakan yang diketik.** Postingan formulir dan panggilan klien yang diketik mencapai fungsi Python yang sama.

Mulailah dengan satu file di bawah `src/routes/`, dan tambahkan struktur saat proyek berkembang.

## Memulai

### Langkah pertama
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Instalasi](getting-started/installation.md) | Instal uv dan Nexy CLI, lalu buat proyek pertama Anda |
| [Mulai cepat](getting-started/quick-start.md) | Membuat proyek, menjalankannya dengan live reload, dan membangunnya untuk produksi |
| [Tutorial](getting-started/tutorial.md) | Membuat halaman catatan dengan titik akhir, data bersama, dan pembuatan produksi dalam 10 menit |

### Pahami modelnya
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Konsep inti](getting-started/core-concepts.md) | Dapatkan model mental: rute, halaman, tampilan, komponen, pengendali, titik akhir |
| [Cara kerja Nexy](getting-started/how-nexy-works.md) | Ikuti satu permintaan dari URL ke file yang menjawabnya |
| [Arsitektur](architecture.md) | Ketahui lapisan mana yang melakukan apa, dan apa yang diberikan Nexy pada aplikasi Anda |
| [Struktur proyek](getting-started/project-structure.md) | Ketahui kegunaan setiap folder dan file dalam suatu proyek |
| [Pilih router](routing/README.md) | Pilih router berbasis file, modular, atau kustom |
| [Pilih format tampilan](views/README.md) | Pilih `.nexy`, Markdown atau kerangka klien untuk halaman |

### Datang dari tempat lain
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Berasal dari kerangka lain](getting-started/coming-from-other-frameworks.md) | Terjemahkan FastAPI, Next.js dan Ekspresikan kebiasaan ke dalam Nexy |

## Perutean

### Berbasis file {fbr}
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Perutean berbasis file](routing/fbr/README.md) | Mengubah jalur file menjadi URL |
| [Halaman](routing/fbr/pages/README.md) | Tulis halaman |
| [Rute dinamis](routing/fbr/pages/dynamic-routes.md) | Gunakan `[slug]`, `[...path]` dan grup rute |
| [Metadata halaman](routing/fbr/pages/metadata.md) | Menetapkan judul, deskripsi, dan berbagi gambar halaman {new} |
| [Tata Letak](routing/fbr/layouts/README.md) | Berbagi bingkai antar halaman |
| [Warisan](routing/fbr/inheritance.md) | Membaca urutan resolusi tata letak, dependensi, dan halaman kesalahan |
| [Mode server dan mode klien](routing/fbr/modes.md) | `useCSR`, dan apa yang dimungkinkan oleh masing-masing mode |
| [Menautkan dan menavigasi](routing/fbr/navigation/linking-and-navigating.md) | Tautkan halaman, navigasi di klien, ambil terlebih dahulu |
| [Hook](routing/fbr/navigation/hooks.md) | Membaca jalur, kueri, cookie, dan sesi |

### Penangan dan kesalahan {fbr}
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Penanganan rute](routing/fbr/handlers/README.md) | Tambahkan titik akhir Python |
| [Validasi dan kesalahan](routing/fbr/handlers/validation-and-errors.md) | Jawab `422` dan `404`, dan naikkan `HTTPException` |
| [WebSocket penangan](routing/fbr/realtime/websocket.md) | Menangani koneksi `SOCKET` |
| [Dependensi dan penjaga](routing/fbr/dependencies/README.md) | Jalankan `dependencies.py` sebelum pengendali, dan mewarisinya |
| [File middleware](routing/fbr/middleware/README.md) | Bungkus permintaan dengan `middleware.py`, yang diwarisi berdasarkan direktori |
| [Halaman kesalahan](routing/fbr/errors/README.md) | Jawab dengan kesalahan `notfound.nexy`, `errors.nexy` dan JSON |
| [Halaman kesalahan per folder](routing/fbr/errors/folder-pages.md) | Kasus tepi: kesalahan dari sub-folder |

### Router modular {modular}
Pengontrol dan modul.
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Perutean modular](routing/modular/README.md) | Memasang pengontrol dan modul |
| [Injeksi ketergantungan](routing/modular/dependency-injection.md) | Tentukan layanan, cakupannya, dan wadahnya |
| [Penjaga dan metadata](routing/modular/guards-and-metadata.md) | Melindungi dan mendokumentasikan rute |
| [Router modular vs NestJS](routing/modular/vs-nestjs.md) | Perbandingan dengan NestJS |

### Integrasi router khusus {custom}
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Perutean khusus](routing/custom/README.md) | Sertakan aplikasi FastAPI yang ada |

## Bagian depan

### Kontrak bersama
| Halaman | Definisinya |
|---|---|
| [Halaman depan](views/frontend/pages.md) | Satu file, satu rute: props, rendering, metadata |
| [Tata letak frontend](views/frontend/layouts.md) | Shell dokumen, sarangnya, dan apa yang tidak bisa dilakukan oleh tata letak |
| [Tindakan dan navigasi](views/frontend/actions-and-navigation.md) | Panggil Tindakan yang diketik, tautkan halaman, baca URL |

### Tampilan Nexy
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [berkas .nexy](views/nexy/README.md) | Tulis halaman dengan Python, Jinja2 dan props |
| [Komponen](views/nexy/components.md) | Gunakan `Image`, `Link`, `Audio`, `Video` dan `Import` |
| [layout.nexy](views/nexy/layouts.md) | Tulis tata letak mode server |
| [Markdown dan MDX](views/nexy/markdown.md) | Menulis halaman konten |

### Perbedaan kerangka
| Halaman | Apa yang berubah |
|---|---|
| [React perbedaan](views/react/differences.md) | Komponen, pengait dan `layout.tsx` {new} |
| [Vue perbedaan](views/vue/differences.md) | SFC, ref dan `layout.vue` {new} |
| [Svelte perbedaan](views/svelte/differences.md) | Rune, toko dan `layout.svelte` {new} |
| [Solid perbedaan](views/solid/differences.md) | Sinyal, pengakses dan `layout.tsx` {new} |
| [Preact perbedaan](views/preact/differences.md) | Kait, sinyal dan `layout.tsx` {new} |

## Render

### Mode
| Halaman | Apa yang akan Anda putuskan |
|---|---|
| [Perenderan](rendering/README.md) | Mode rendering mana yang sesuai dengan halaman |
| [SSR](rendering/ssr.md) | Render server, default |
| [ISR](rendering/isr.md) | Halaman cache dengan basi-saat-validasi ulang |
| [CSR](rendering/csr.md) | Perutean sisi klien |
| [Pulau](rendering/islands.md) | Hidrasi saat idle, terlihat, atau permintaan media |

## Panduan

### Formulir dan data
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Tindakan](guides/actions.md) | Memanggil fungsi Python dari formulir atau fungsi TypeScript yang diketik |
| [Database](guides/databases.md) | Pilih ORM dan jalankan migrasi |

### Keamanan dan penyebaran
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Middleware dan keamanan](guides/middleware-and-security.md) | Menyiapkan CORS, GZip, host dan sesi tepercaya |
| [Penerapan](deployment/README.md) | Bangun, masukkan ke dalam container, dan sajikan |
| [Kinerja](deployment/performance.md) | Mengukur dan menyetel default |

### Bangun dan uji
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Vite dan penataan gaya](guides/frontend.md) | Menyiapkan Vite, penataan gaya, dan pembuatan klien |
| [Pengujian](guides/testing.md) | Uji dengan pytest, `TestClient` dan vitest |

### Perkakas dan bantuan
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Toolbar pengembangan](guides/devtools.md) | Gunakan toolbar `nexy dev`, dan matikan |
| [Agen pengkodean](guides/ai-agents.md) | Berikan Claude Code, Codex dan OpenCode aturan proyek Anda |
| [Pemecahan masalah](guides/troubleshooting.md) | Memperbaiki masalah pertama yang dialami orang |

## Referensi

### Perintah dan konfigurasi
| Halaman | Apa yang dicantumkan |
|---|---|
| [CLI](reference/cli.md) | Perintah, tanda, perintah, dan kode keluar |
| [Konfigurasi](reference/config.md) | Setiap kolom `nexyconfig.py` dan defaultnya |

### Python API dan kesalahan
| Halaman | Apa yang dicantumkan |
|---|---|
| [API Python](reference/python-api.md) | Setiap nama yang diekspor Nexy, berdasarkan modul |
| [Pengecualian dan kesalahan](reference/exceptions.md) | Setiap kegagalan, statusnya, dan file yang menjawabnya |

### Konvensi dan konsep
| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Konvensi file](reference/file-conventions.md) | File cadangan dan aturan perutean |
| [Glosarium](reference/glossary.md) | Kata-kata yang digunakan dokumen ini |
| [Keamanan](reference/security.md) | Versi minimum, aturan yang diikuti Nexy, audit |

## Tata Letak
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Lanjutan

### Lanjutan {advanced}

| Halaman | Apa yang akan Anda lakukan |
|---|---|
| [Meningkatkan ke 2.2](getting-started/upgrading.md) | Bermigrasi dari 2.1 ke 2.2 |
| [Internasionalisasi (i18n)](guides/i18n.md) | Tambahkan terjemahan dengan perpustakaan pilihan Anda |
| [Resep](guides/recipes.md) | Contoh dan pola, bukan tutorial |

*Halaman ini bukan bagian dari jalur membaca default. Tautan "Semua dokumentasi" memungkinkan Anda melihat semuanya.*
