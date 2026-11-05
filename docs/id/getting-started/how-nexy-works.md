# Bagaimana Nexy bekerja

Apa yang terjadi antara file yang Anda tulis dan halaman di browser: lapisan yang dilintasi permintaan, siapa yang membuat apa, dan apa yang Nexy serahkan ke aplikasi Anda. Anda tidak memerlukan halaman ini untuk memulai; itu menjawab pertanyaan "mengapa cara kerjanya seperti itu" nanti.

## Lapisan

```diagram filename="Satu permintaan, lima lapisan"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Lapisan | Tanggung jawab | Tidak |
|---|---|---|
| Uvicorn | terima koneksinya, ucapkan ASGI | tahu apa itu halaman |
| Perangkat Tengah | hiasi permintaan: sesi, CORS, gzip, host tepercaya, pengalihan HTTPS, milik Anda | memilih rute |
| Perute | mencocokkan URL dengan file, dengan tata letak, dependensi, dan halaman kesalahannya | menghasilkan konten |
| penyaji | jalankan halaman dan ubah hasilnya menjadi HTML atau JSON | mengambil data Anda |
| Klien | Vite dan kerangka kerja Anda: bundel, hidrasi, navigasi klien | menjawab permintaan server |

## Siapa yang membangun apa

| Aktor | Milik | Tidak memiliki |
|---|---|---|
| Nexy | perutean, rendering server, Tindakan, kompilasi `.nexy`, satu asal | komponen, reaktivitas, data |
| Vite | bundel klien, server dev, hot reload | perutean, rendering server, Tindakan |
| Kerangka kerja Anda | komponen, reaktivitas, ekosistem | perutean, dokumen (Nexy menanyakan tata letaknya) |
| Aplikasi Anda | data, otentikasi, otorisasi, aturan bisnis | transportasi, rendering |

Aturan di balik tabel: **Nexy membangun apa yang dimilikinya, dan tidak pernah mengkompilasi apa yang Vite kompilasi.**

## Sistem perutean

Jalur di bawah `src/routes/` menjadi URL dengan empat aturan:

| Mengajukan | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

Ekstensi tidak pernah muncul; `index` adalah rute foldernya; folder dalam tanda kurung mengelompokkan file tanpa menambahkan segmen.

Ketika dua hal dapat menjawab URL yang sama, **yang pertama terdaftar menang**, dan Nexy selalu mendaftar dalam urutan ini:

1. titik akhir Tindakan;
2. file statis: `/public`, `/assets`, `/favicon.ico`;
3. modular `APIRouter` (`useRouter`);
4. rute file, yang paling spesifik terlebih dahulu: jalur statis, lalu jalur dinamis dengan segmen paling tetap, lalu jalur umum.

Dua rute file dengan spesifisitas yang sama didaftarkan dalam urutan jalur berdasarkan abjad, jadi `[id].nexy` menjawab sebelum `[slug].nexy`. Oleh karena itu, rute modular mengalahkan halaman dengan jalur yang sama. Ini adalah urutan prioritas yang dapat Anda andalkan, bukan aturan yang mengikat: berikan satu URL satu file.

## Sistem tampilan

Ekstensi file menentukan jenis filenya, dan konfigurasi proyek menentukan ekstensi mana yang aktif.

| Ekstensi | Aktif kapan | Disusun oleh | Berfungsi sebagai |
|---|---|---|---|
| `.nexy` | modus server | Nexy: frontmatter menjadi Python, markupnya menjadi Jinja2 | sebuah halaman |
| `.md` | selalu | Nexy: rasa GitHub Markdown, id judul, daftar isi | sebuah halaman, di dalam tata letak terdekat |
| `.mdx` | selalu | Vite, dengan React atau Preact | rute komponen |
| `.tsx` | `useFF` adalah React, Solid atau Preact | Vite dan kerangkanya | rute komponen |
| `.vue` | `useFF` adalah Vue | Vite dan Vue | rute komponen |
| `.svelte` | `useFF` adalah Svelte | Vite dan Svelte | rute komponen |
| `.py` | selalu | Python | penangan API: `GET`, `POST`, ... adalah metodenya |

File yang ekstensinya tidak aktif dilewati dengan peringatan, tidak disajikan. Dalam mode klien, `.nexy` ditolak sebelum server dimulai. Lihat [Konvensi file](../reference/file-conventions.md).

## Siklus hidup rendering

Tiga pertanyaan menentukan semua yang diperhatikan pembaca:

| Pertanyaan | Jawaban | Halaman |
|---|---|---|
| Siapa yang memproduksi HTML? | server, atau browser untuk rute klien | [Perenderan](../rendering/README.md) |
| Kapan data dibaca? | pada setiap permintaan, pada setiap regenerasi, atau di browser | [RSK](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Kapan JavaScript tiba? | hanya untuk satu pulau, atau untuk keseluruhan dokumen | [Pulau](../rendering/islands.md), [CSR](../rendering/csr.md) |

Dalam mode server, server merender setiap halaman, `revalidate` menyimpan satu halaman per URL, dan pulau menambahkan JavaScript ke satu komponen. Dalam mode klien, dokumen pertama dirender di Node dan navigasi kemudian terjadi di browser.

`__nexy__/` menampung semua yang dihasilkan: halaman yang dikompilasi, entri klien, keluaran build. Jangan pernah mengeditnya, jangan pernah melakukannya; hapus untuk memaksa pembangunan yang bersih.

## Integrasi frontend

**Vite tidak menggantikan Nexy.** Vite menggabungkan dan menyajikan kode klien. Itu tidak merutekan permintaan, merender halaman `.nexy`, menjalankan Tindakan, atau memiliki asal. Browser berkomunikasi dengan satu asal - Nexy - dan dalam pengembangan, proksi Nexy Vite's titik akhir melaluinya, jadi tidak ada CORS yang harus dikonfigurasi.

**Nexy tidak menggantikan React.** Nexy memutuskan komponen mana yang dirender, kapan, dan dengan props yang mana; kerangka tersebut memiliki model komponen, reaktivitas, dan ekosistem. Halaman `.nexy` mengimpor komponen sebagai pulau; dalam mode klien, rute *adalah* sebuah komponen.

Untuk rute komponen, Python hanya menulis modul pembungkus tipis yang menunjuk ke file. Kompilasi dan rendering sisi server adalah tugas Vite.

## Pengembangan dan produksi

`nx dev` memeriksa `nexyconfig.py`, mengkompilasi halaman, memulai Vite ketika proyek memiliki kerangka frontend, dan memulai ulang server saat Anda menyimpan. `nx build` melakukan pekerjaan yang sama satu kali, sebelumnya, dan `nx start` menyajikan hasilnya.

| | `nx dev` | `nx build` lalu `nx start` |
|---|---|---|
| Halaman | dikompilasi saat Anda menyimpan | dikompilasi sekali, sebelumnya |
| Kode klien | Vite server dev dengan hot reload, di belakang asal Nexy sendiri | bundel dalam `__nexy__/client/`, HTML yang telah dirender sebelumnya |
| Node.js | berjalan di sebelah Python | tidak diperlukan untuk melayani |
| Kesalahan | overlay di browser, toolbar di setiap halaman | halaman status tanpa detail |
| Asal | satu pelabuhan, `3000` | satu pelabuhan |

Apa yang tidak berubah: aturan routing yang sama, file halaman yang sama, `nexyconfig.py` yang sama. Halaman yang berperilaku berbeda antara keduanya adalah bug, bukan mode.

## Apa yang Nexy serahkan padamu

Nexy berhenti di tepi aplikasi Anda, dengan sengaja:

| Kekhawatiran | Apa yang Nexy sediakan | Apa yang Anda tulis |
|---|---|---|
| Otentikasi | middleware sesi, `AuthenticationMiddleware` ketika diaktifkan | login, pencarian pengguna, kebijakan cookie |
| Otorisasi | `dependencies.py`, penjaga, warisan per folder | aturan itu sendiri |
| Basis data | tidak ada ORM sendiri; `nx new` dapat menjalankan scaffold SQLModel, SQLAlchemy atau Tortoise, `nx migrate` menjalankan Alembic atau Aerich | model dan kueri ([Database](../guides/databases.md)) |
| Internasionalisasi | tidak ada apa pun untuk halaman Anda; hanya CLI yang diterjemahkan | perpustakaan dan pesan ([i18n](../guides/i18n.md)) |
| Pekerjaan latar belakang | tidak ada: tidak ada antrian, tidak ada penjadwal | sebuah proses pekerja |
| Email, pembayaran, pencarian | tidak ada apa-apa | layanan yang Anda pilih |

Alasannya sama untuk keenamnya: kerangka kerja yang memilih ORM atau perpustakaan autentikasi Anda memutuskan hal-hal yang hanya dapat diputuskan oleh aplikasi Anda. Biayanya jelas: tidak ada kabel untuk Anda, dan panduan yang tertaut dalam tabel menyatakan di mana harus menyambungkan masing-masing kabel.

## Langkah selanjutnya

- [Struktur proyek](project-structure.md): di mana setiap bagian berada dalam sebuah proyek
- [Perutean](../routing/README.md): router berbasis file, modular, dan khusus
- [Perenderan](../rendering/README.md): SSR, ISR, CSR dan pulau-pulau
- [Frontend](../guides/frontend.md): Vite, gaya dan pembuatan klien
