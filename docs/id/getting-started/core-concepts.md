# Konsep inti

Kata-kata yang digunakan dokumen lainnya - rute, halaman, tampilan, komponen, penangan, titik akhir - masing-masing dalam satu baris, dengan tautan ke halaman yang lebih dalam. Baru mengenal Nexy? Mulailah dengan [Apa itu Nexy?](what-is-nexy.md).

## Cara membaca dokumen ini

| Tingkat | Pertanyaan yang dijawabnya | Mulailah dengan |
|---|---|---|
| Arsitektur aplikasi | lapisan mana yang menjawab permintaan, dan apa yang ditolaknya | [Cara kerja Nexy](how-nexy-works.md) |
| Struktur aplikasi | di mana kode itu berada, dan menjadi apa sebuah file | [Struktur proyek](project-structure.md) |
| Presentasi dan rendering | apa yang dilihat pembaca, dan siapa yang menghasilkan HTML | [Penayangan](../views/README.md), [Perenderan](../rendering/README.md) |
| Interaksi aplikasi | apa yang dilakukan pembaca, dan apa tanggapannya | [Tindakan](../guides/actions.md) |

Level dibaca dalam urutan itu satu kali. Setelah itu, halaman yang Anda perlukan adalah pencarian, bukan kursus.

## Arsitektur aplikasi

Tiga cara untuk memutuskan kode mana yang menjawab URL. Itu adalah alternatif, bukan lapisan:

- **Perutean berbasis file (FBR)**: file di bawah `src/routes/` adalah rute. Standarnya.
- **Router modular**: pengontrol dan modul di bawah `src/apps/`, dideklarasikan dengan dekorator, untuk basis kode bergaya NestJS.
- **Router khusus**: FastAPI `APIRouter` yang sudah ada yang disertakan dalam aplikasi.

Memilih salah satu dari ketiganya adalah satu keputusan. Memilih kerangka frontend adalah hal lain yang terpisah: lihat [Memilih router](../routing/README.md) dan [Tampilan](../views/README.md).

## Struktur aplikasi

Lima gagasan yang berasal dari pembaca Next.js biasanya digabungkan menjadi satu. Keduanya bukanlah hal yang sama, dan perbedaannya menjelaskan sebagian besar pertanyaan "mengapa laman saya tidak dirender".

| Gagasan | Apa itu | Apa yang bukan |
|---|---|---|
| **Rute** | pola URL, dihasilkan oleh jalur file | satu file: satu file dapat menjawab beberapa URL (`[slug]`) |
| **Halaman** | file rute yang merender tampilan: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | titik akhir: ia menjawab dokumen, bukan data |
| **Lihat** | apa yang menghasilkan isi halaman: Jinja2 dan Python, Markdown, atau komponen klien | sebuah rute: tampilan yang sama dapat menyajikan beberapa halaman |
| **Komponen** | bagian yang dapat digunakan kembali yang diimpor halaman | sebuah rute: dalam mode server, sebuah komponen tidak pernah dilayani sendiri |
| **Pengendali rute** | fungsi file rute `.py`, dinamai berdasarkan metode HTTP (`GET`, `POST`, …) | halaman: ia mengembalikan JSON, file atau `Response` |
| **Titik akhir** | pasangan (URL, metode) yang dijawab oleh penangan | seorang penangan: satu file dapat menjawab beberapa titik akhir |

Dalam satu kalimat: **halaman adalah file rute, tampilan adalah apa yang merendernya, komponen adalah apa yang digunakan kembali oleh halaman, penangan menjawab titik akhir.**

Dua kata lagi yang muncul kembali di mana-mana:

- **Layout**: file `layout.*` yang membungkus halaman di bawah foldernya; yang root memiliki dokumen HTML. Lihat [Tata Letak](../routing/fbr/layouts/README.md).
- **Ketergantungan**: fungsi yang dijalankan sebelum penangan, diterapkan per rute atau per folder. Lihat [Ketergantungan](../routing/fbr/dependencies/README.md).

## Presentasi dan rendering

Dua keputusan independen, yang sering membingungkan:

- **Format** memutuskan file mana yang merender halaman: [Tampilan](../views/README.md).
- **Mode** memutuskan siapa yang memproduksi HTML dan kapan: [Perenderan](../rendering/README.md).

| Gagasan | Satu baris |
|---|---|
| Modus pelayan | server merender halaman `.nexy` dan `.md`; komponen adalah pulau ([mode](../routing/fbr/modes.md)) |
| Modus klien | `useCSR = True`: file kerangka adalah rutenya, dan navigasi terjadi di browser |
| SSR, ISR, CSR, kepulauan | empat mode rendering, ditentukan per halaman kecuali CSR, yaitu per proyek ([perenderan](../rendering/README.md)) |
| Hidrasi | browser yang melampirkan kerangka kerja ke HTML yang sudah dikirim server ([pulau](../rendering/islands.md)) |
| Alat peraga | nilai yang diberikan induk ke komponen, dideklarasikan `name: prop[type]` dalam file `.nexy` ([berkas .nexy](../views/nexy/README.md)) |

## Interaksi aplikasi

| Gagasan | Satu baris |
|---|---|
| Tindakan | fungsi Python yang ditandai `@Action`, berfungsi sebagai `POST`, dapat dipanggil dari formulir atau sebagai fungsi yang diketik ([tindakan](../guides/actions.md)) |
| Formulir | formulir HTML yang diposkan ke suatu Tindakan, dengan kesalahan validasi kembali ke halaman ([tindakan](../guides/actions.md)) |
| Navigasi | tautan yang mengambil terlebih dahulu, dan kait yang membaca jalur, kueri, cookie, dan sesi ([kait](../routing/fbr/navigation/hooks.md)) |
| Pengambilan data | dilakukan oleh halaman atau penangan yang memerlukannya; Nexy tidak mengirimkan lapisan data klien ([handler](../routing/fbr/handlers/README.md)) |

## Apa yang Nexy tidak lakukan

Otentikasi, otorisasi, database, internasionalisasi, pekerjaan latar belakang, email, pembayaran, dan pencarian adalah **tanggung jawab aplikasi Anda**, bukan tanggung jawab kerangka kerja. Nexy memberikan poin ekstensi dan mengatakan di mana harus memasang masing-masing poin: lihat [Apa yang diserahkan Nexy kepada Anda](how-nexy-works.md#what-nexy-leaves-to-you).

Alasannya bukan karena minimalisme itu sendiri: kerangka kerja yang memilih ORM atau perpustakaan autentikasi Anda telah memutuskan sesuatu yang hanya dapat diputuskan oleh aplikasi Anda.

## Langkah selanjutnya

- [Struktur proyek](project-structure.md): setiap folder dan file proyek
- [Glosarium](../reference/glossary.md): kata-kata yang sama, dalam satu indeks abjad
- [Cara kerja Nexy](how-nexy-works.md): lapisannya, siapa yang membangun apa, dan apa yang Nexy serahkan kepada Anda
