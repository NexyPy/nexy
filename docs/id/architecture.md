# Arsitektur

## Definisi

Nexy terdiri dari lima lapisan, dan masing-masing lapisan mempunyai tugas yang tidak dapat dilakukan oleh lapisan lainnya. Mengetahui batas menjawab sebagian besar pertanyaan "mengapa berfungsi seperti itu": halaman yang lambat adalah pertanyaan penyaji, halaman yang salah adalah pertanyaan router, halaman yang tidak pernah muncul adalah pertanyaan klien.

Halaman ini untuk orang yang menulis lamaran. Paket Nexy itu sendiri, dan mekanisme di baliknya, dijelaskan di `ARCHITECTURE.md` di root repositori, untuk kontributor.

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

| Lapisan | Tanggung Jawab | Tidak |
|---|---|---|
| Uvicorn | terima koneksinya, ucapkan ASGI | ketahui apa itu halaman |
| Middleware | menghiasi permintaan: sesi, CORS, gzip, host tepercaya, pengalihan HTTPS, milik Anda | pilih rute |
| Router | mencocokkan URL ke suatu file, dengan tata letak, ketergantungan, dan halaman kesalahannya | menghasilkan konten |
| Renderer | menjalankan halaman dan mengubah hasilnya menjadi HTML atau JSON | mengambil data Anda |
| Klien | Vite dan kerangka kerja Anda: bundel, hidrasi, navigasi klien | menjawab permintaan server |

## Siapa yang membangun apa

| Aktor | Memiliki | Tidak memiliki |
|---|---|---|
| Perutean Nexy | rendering server, Tindakan, kompilasi `.nexy`, komponen satu asal | reaktivitas, data |
| Vite | bundel klien, server dev, hot reload | perutean, rendering server, Tindakan |
| Kerangka kerja Anda | komponen, reaktivitas, ekosistem | perutean, dokumen (Nexy meminta tata letaknya) |
| Aplikasi Anda | data, autentikasi, otorisasi, aturan bisnis | transportasi, rendering |

Aturan di balik tabel: **Nexy membangun apa yang dimilikinya, dan tidak pernah mengkompilasi apa yang Vite kompilasi.** Untuk rute komponen, Python menulis modul pembungkus tipis yang menunjuk ke file.

## Dimana permintaan diputuskan

1. Middleware berjalan, dan dapat mengubah permintaan atau menghentikannya.
2. Router mengambil satu file, dan tata letak di sekitarnya.
3. Penyaji menjalankan file itu dengan data yang dibacanya sendiri.
4. Responsnya kembali, dan lapisan klien mengambil alih jika halaman tersebut memiliki JavaScript.

Setiap langkah, dengan prioritas yang tepat antara router dan urutan `nx dev`, ada di [Cara kerja Nexy](getting-started/how-nexy-works.md). Halaman ini tidak mengulanginya.

## Pengembangan dan produksi

Lima lapisan yang sama, dirangkai dua kali:

| Lapisan | `nx dev` | `nx build` lalu `nx start` |
|---|---|---|
| Kompiler | berjalan ketika Anda menyimpan | berjalan sekali, sebelumnya |
| Vite | server dev, hot reload, diproksi melalui bundel | asal Nexy yang ditulis ke `__nexy__/client/`, tanpa server dev |
| Node | merender dokumen klien sesuai permintaan | merendernya saat build, bukan saat melayani |
| Pengamat | memulai ulang uvicorn saat perubahan | tidak ada |
| Asal | satu port | satu port |

Yang berubah adalah *kapan* pekerjaan dilakukan, bukan *siapa* yang melakukannya. Halaman yang berperilaku berbeda antara keduanya adalah bug di halaman tersebut, bukan properti mode.

## Batasan

Nexy berhenti di tepi aplikasi Anda, dengan sengaja:

| Kepedulian | Apa yang Nexy berikan | Apa yang Anda tulis |
|---|---|---|
| Otentikasi | middleware sesi, `AuthenticationMiddleware` ketika diaktifkan | login, pencarian pengguna, kebijakan cookie |
| Otorisasi | `dependencies.py`, penjaga, warisan per folder | aturan itu sendiri |
| Basis data | tidak ada: tidak ada ORM, tidak ada migrasi | lapisan model ([Database](guides/databases.md)) |
| Internasionalisasi | tidak ada apa pun untuk halaman Anda; hanya CLI yang diterjemahkan | perpustakaan dan pesan ([i18n](guides/i18n.md)) |
| Pekerjaan latar belakang | tidak ada: tidak ada antrian, tidak ada penjadwal | proses pekerja |
| Email, pembayaran, cari | tidak ada | layanan yang Anda pilih |

Alasannya sama untuk keenamnya: kerangka kerja yang memilih ORM atau perpustakaan autentikasi Anda memutuskan hal-hal yang hanya dapat diputuskan oleh aplikasi Anda. Biayanya jelas: tidak ada kabel untuk Anda, dan halaman panduan di atas menjelaskan di mana harus menyambungkannya.

## Langkah selanjutnya

- [Cara kerja Nexy](getting-started/how-nexy-works.md): satu permintaan, langkah demi langkah
- [Struktur proyek](getting-started/project-structure.md): tempat setiap lapisan berada dalam sebuah proyek
- [Routing](routing/README.md): tiga router, dan cara memilih
- [Rendering](rendering/README.md): dari mana HTML berasal
