# Dokumentasi Nexy

**Kerangka kerja Python untuk aplikasi web fullstack.**

Nexy menempatkan halaman dan API Anda dalam satu proyek Python, dilayani oleh satu server. Versi 2.2 dibangun di atas FastAPI: setiap rute API adalah rute FastAPI, tercantum dalam skema OpenAPI yang ditampilkan Scalar di `/docs`.

- **Python terlebih dahulu.** Halaman, titik akhir, formulir, dan tindakan adalah Python, dan sebuah halaman tidak memerlukan JavaScript.
- **Frontend bila Anda menginginkannya.** React, Vue, Svelte, Solid atau Preact, untuk satu komponen atau untuk keseluruhan situs.
- **Satu file, satu URL.** File di bawah `src/routes/` adalah rute: `.nexy` adalah halaman, `.py` adalah titik akhir API.
- **Ruang untuk berkembang.** Mulailah dengan satu file; pindah ke modul, atau colokkan router FastAPI yang ada, saat proyek berkembang.

Baru di sini? Baca [Apa itu Nexy?](getting-started/what-is-nexy.md), lalu [Mulai cepat](getting-started/quick-start.md).

## Memulai

### Langkah pertama
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Apa itu Nexy?](getting-started/what-is-nexy.md) | Ketahui apa itu Nexy, apa yang dibangunnya, dan apa yang Anda dapatkan |
| [Instalasi](getting-started/installation.md) | Instal uv dan Nexy CLI, lalu buat proyek pertama Anda |
| [Mulai cepat](getting-started/quick-start.md) | Buat proyek, jalankan dengan live reload, dan bangun untuk produksi |
| [Tutorial](getting-started/tutorial.md) | Buat halaman catatan dengan titik akhir, data bersama, dan build produksi dalam 10 menit |

### Pahami modelnya
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Konsep inti](getting-started/core-concepts.md) | Dapatkan model mental: rute, halaman, tampilan, komponen, penangan, titik akhir |
| [Struktur proyek](getting-started/project-structure.md) | Ketahui kegunaan setiap folder dan file dalam suatu proyek |
| [Pilih router](routing/README.md) | Pilih router berbasis file, modular, atau khusus |
| [Pilih format tampilan](views/README.md) | Pilih `.nexy`, Markdown atau kerangka klien untuk sebuah halaman |

### Datang dari tempat lain
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Berasal dari kerangka lain](getting-started/coming-from-other-frameworks.md) | Terjemahkan FastAPI, Next.js dan Ekspresikan kebiasaan ke dalam Nexy |

## Perutean

### Berbasis file {fbr}
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Perutean berbasis file](routing/fbr/README.md) | Ubah jalur file menjadi URL |
| [Halaman](routing/fbr/pages/README.md) | Tulis satu halaman |
| [Rute dinamis](routing/fbr/pages/dynamic-routes.md) | Gunakan `[slug]`, `[...path]` dan grup rute |
| [Metadata halaman](routing/fbr/pages/metadata.md) | Menetapkan judul, deskripsi, dan berbagi gambar halaman {new} |
| [Tata Letak](routing/fbr/layouts/README.md) | Bagikan bingkai antar halaman |
| [Warisan](routing/fbr/inheritance.md) | Baca urutan resolusi tata letak, dependensi, dan halaman kesalahan |
| [Mode server dan mode klien](routing/fbr/modes.md) | `useCSR`, dan apa yang dimungkinkan oleh setiap mode |
| [Menghubungkan dan menavigasi](routing/fbr/navigation/linking-and-navigating.md) | Tautkan halaman, navigasikan di klien, ambil terlebih dahulu |
| [Kait](routing/fbr/navigation/hooks.md) | Baca jalur, kueri, cookie, dan sesi |

### Penangan dan kesalahan {fbr}
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Pengendali rute](routing/fbr/handlers/README.md) | Tambahkan titik akhir Python |
| [Validasi dan kesalahan](routing/fbr/handlers/validation-and-errors.md) | Jawab `422` dan `404`, dan naikkan `HTTPException` |
| [WebSocket penangan](routing/fbr/realtime/websocket.md) | Tangani koneksi `SOCKET` |
| [Ketergantungan dan penjaga](routing/fbr/dependencies/README.md) | Jalankan `dependencies.py` sebelum seorang pengendali, dan mewarisinya |
| [File middleware](routing/fbr/middleware/README.md) | Bungkus permintaan dengan `middleware.py`, yang diwarisi berdasarkan direktori |
| [Halaman kesalahan](routing/fbr/errors/README.md) | Jawab dengan kesalahan `notfound.nexy`, `errors.nexy` dan JSON |
| [Halaman kesalahan per folder](routing/fbr/errors/folder-pages.md) | Kasus tepi: kesalahan dari sub-folder |

### Router modular {modular}
Pengontrol dan modul.
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Perutean modular](routing/modular/README.md) | Pasang pengontrol dan modul |
| [Injeksi ketergantungan](routing/modular/dependency-injection.md) | Tentukan layanan, cakupannya, dan wadahnya |
| [Penjaga dan metadata](routing/modular/guards-and-metadata.md) | Lindungi dan dokumentasikan rute |
| [Router modular vs NestJS](routing/modular/vs-nestjs.md) | Perbandingan dengan NestJS |

### Integrasi router khusus {custom}
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Perutean khusus](routing/custom/README.md) | Sertakan aplikasi FastAPI yang sudah ada |

## Bagian depan

### Kontrak bersama
| Halaman | Apa yang didefinisikannya |
|---|---|
| [Halaman depan](views/frontend/pages.md) | Satu file, satu rute: props, rendering, metadata |
| [Tata letak bagian depan](views/frontend/layouts.md) | Shell dokumen, sarangnya, dan apa yang tidak bisa dilakukan oleh tata letak |
| [Tindakan dan navigasi](views/frontend/actions-and-navigation.md) | Panggil Tindakan yang diketik, tautkan halaman, baca URL-nya |

### Tampilan Nexy
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [file .nexy](views/nexy/README.md) | Tulis halaman dengan Python, Jinja2 dan alat peraga |
| [Komponen](views/nexy/components.md) | Gunakan `Image`, `Link`, `Audio`, `Video` dan `Import` |
| [tata letak.nexy](views/nexy/layouts.md) | Tulis tata letak mode server |
| [Markdown dan MDX](views/nexy/markdown.md) | Tulis halaman konten |

### Perbedaan kerangka
| Halaman | Perubahan apa |
|---|---|
| [React perbedaan](views/react/differences.md) | Komponen, pengait dan `layout.tsx` {new} |
| [Vue perbedaan](views/vue/differences.md) | SFC, referensi dan `layout.vue` {new} |
| [Svelte perbedaan](views/svelte/differences.md) | Rune, toko dan `layout.svelte` {new} |
| [Solid perbedaan](views/solid/differences.md) | Sinyal, pengakses dan `layout.tsx` {new} |
| [Preact perbedaan](views/preact/differences.md) | Kait, sinyal dan `layout.tsx` {new} |

## Render

### Mode
| Halaman | Apa yang akan Anda putuskan |
|---|---|
| [Merender](rendering/README.md) | Mode rendering mana yang sesuai dengan halaman |
| [RSK](rendering/ssr.md) | Render server, default |
| [ISR](rendering/isr.md) | Cache halaman dengan basi-saat-validasi ulang |
| [CSR](rendering/csr.md) | Perutean sisi klien |
| [Kepulauan](rendering/islands.md) | Hidrasi saat idle, terlihat, atau permintaan media |

## Panduan

### Formulir dan data
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Tindakan](guides/actions.md) | Panggil fungsi Python dari formulir atau fungsi TypeScript yang diketik |
| [Basis Data](guides/databases.md) | Pilih ORM dan jalankan migrasi |

### Keamanan dan penyebaran
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Middleware dan keamanan](guides/middleware-and-security.md) | Siapkan CORS, GZip, host dan sesi tepercaya |
| [Menyebarkan](deployment/README.md) | Bangun, masukkan ke dalam wadah, dan sajikan |
| [Pertunjukan](deployment/performance.md) | Ukur dan sesuaikan defaultnya |

### Bangun dan uji
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Vite dan penataan gaya](guides/frontend.md) | Siapkan Vite, penataan gaya, dan pembuatan klien |
| [Pengujian](guides/testing.md) | Uji dengan pytest, `TestClient` dan vitest |

### Perkakas dan bantuan
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Bilah alat pengembang](guides/devtools.md) | Gunakan toolbar `nexy dev`, dan matikan |
| [Agen pengkodean](guides/ai-agents.md) | Berikan Claude Code, Codex dan OpenCode aturan proyek Anda |
| [Pemecahan Masalah](guides/troubleshooting.md) | Perbaiki masalah pertama yang dialami orang |

## Referensi

### Perintah dan konfigurasi
| Halaman | Apa yang dicantumkannya |
|---|---|
| [CLI](reference/cli.md) | Perintah, bendera, petunjuk dan kode keluar |
| [Konfigurasi](reference/config.md) | Setiap bidang `nexyconfig.py` dan defaultnya |

### Python API dan kesalahan
| Halaman | Apa yang dicantumkannya |
|---|---|
| [API Python](reference/python-api.md) | Setiap nama yang diekspor Nexy, berdasarkan modul |
| [Pengecualian dan kesalahan](reference/exceptions.md) | Setiap kegagalan, statusnya, dan file yang menjawabnya |

### Konvensi dan konsep
| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Konvensi file](reference/file-conventions.md) | File cadangan dan aturan perutean |
| [Glosarium](reference/glossary.md) | Kata-kata yang digunakan dokumen ini |
| [Keamanan](reference/security.md) | Lantai versi, aturan yang diikuti Nexy, audit |

## Tata Letak
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
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

| Halaman | Apa yang akan kamu lakukan |
|---|---|
| [Cara kerja Nexy](getting-started/how-nexy-works.md) | Lihat apa yang terjadi antara file dan halaman, dan apa yang Nexy berikan kepada Anda |
| [Meningkatkan ke 2.2](getting-started/upgrading.md) | Bermigrasi dari 2.1 ke 2.2 |
| [Internasionalisasi (i18n)](guides/i18n.md) | Tambahkan terjemahan dengan perpustakaan pilihan Anda |
| [Resep](guides/recipes.md) | Contoh dan pola, bukan tutorial |

*Halaman ini bukan bagian dari jalur membaca default. Tautan "Semua dokumentasi" memungkinkan Anda melihat semuanya.*
