# Bagaimana Nexy bekerja

Model mental dalam satu halaman: apa yang dibuat Nexy, apa yang Vite dibuat, dan apa yang terjadi antara file dan halaman di browser Anda. Bacalah sekali; dokumentasi lainnya kemudian berupa serangkaian detail.

## Arsitektur Nexy

Permintaan melewati lima lapisan: Uvicorn menerimanya, middleware menghiasinya, router mengambil file, penyaji mengubah file tersebut menjadi HTML atau JSON, dan lapisan klien mengambil alih jika halaman memiliki JavaScript. Nexy memiliki tiga pemain tengah; Vite dan kerangka kerja Anda memiliki klien; aplikasi Anda memiliki data, autentikasi, dan otorisasi.

Setiap lapisan, dan apa yang tidak dapat dilakukan, ada di [Arsitektur](../architecture.md). Untuk paket Nexy sendiri, lihat `ARCHITECTURE.md` di root repositori - ini ditulis untuk kontributor.

## Siklus hidup aplikasi

`nx dev` melakukan enam hal sebelum permintaan pertama:

1. memvalidasi `nexyconfig.py`, dan berhenti pada konfigurasi yang tidak valid;
2. memastikan paket Python proyek dapat diimpor;
3. menyelesaikan port, dan menghapus penanda basi `__nexy__/nexy.prod`;
4. menghasilkan file klien dan mengkompilasi rute, secara paralel;
5. memulai Vite dan menunggu hingga menjawab;
6. menginstal pengamat file, lalu mengizinkan uvicorn mengimpor `nexy.modules.routers.app:_server`.

Impor tersebut merakit aplikasi - middleware, Actions, router, penangan kesalahan - dan permintaan pertama dilayani oleh perakitan tersebut. Saat Anda menyimpan, pengamat memulai ulang uvicorn; halaman yang muncul, hilang atau dipindahkan juga membuat ulang daftar rute klien.

## Sistem perutean

Jalur di bawah `src/routes/` menjadi URL dengan empat aturan:

| Berkas | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

Ekstensi tidak pernah muncul; `index` adalah rute foldernya; folder dalam tanda kurung mengelompokkan file tanpa menambahkan segmen.

Ketika dua hal dapat menjawab URL yang sama, **yang pertama terdaftar menang**, dan Nexy selalu mendaftar dalam urutan ini:

1. titik akhir Tindakan;
2. file statis: `/public`, `/assets`, `/favicon.ico`;
3. sebuah modular `APIRouter` (`useRouter`);
4. rute file, yang paling spesifik terlebih dahulu: jalur statis, lalu jalur dinamis dengan segmen paling tetap, lalu jalur umum.

Dua rute file dengan spesifisitas yang sama didaftarkan dalam urutan jalur abjad, jadi `[id].nexy` menjawab sebelum `[slug].nexy`. Oleh karena itu, rute modular mengalahkan halaman dengan jalur yang sama. Ini adalah urutan prioritas yang dapat Anda andalkan, bukan aturan yang mengikat: berikan satu URL satu file.

## Sistem tampilan

Ekstensi file menentukan jenis filenya, dan konfigurasi proyek menentukan ekstensi mana yang aktif.

| Ekstensi | Aktif ketika | Dikompilasi oleh | Disajikan sebagai |
|---|---|---|---|
| `.nexy` | mode server | Nexy: materi depan menjadi Python, markup menjadi Jinja2 | halaman |
| `.md` | selalu | Nexy: rasa GitHub Markdown, id judul, daftar isi | satu halaman, di dalam tata letak terdekat |
| `.mdx` | selalu | Vite, dengan React atau Preact | rute komponen |
| `.tsx` | `useFF` adalah React, Solid atau Preact | Vite dan kerangka kerja | merupakan rute komponen |
| `.vue` | `useFF` adalah Vue | Vite dan Vue | merupakan rute komponen |
| `.svelte` | `useFF` adalah Svelte | Vite dan Svelte | merupakan rute komponen |
| `.py` | selalu | Python | penangan API: `GET`, `POST`, ... adalah metodenya |

File yang ekstensinya tidak aktif dilewati dengan peringatan, tidak disajikan. Dalam mode klien, `.nexy` ditolak sebelum server dimulai. Lihat [Konvensi file](../reference/file-conventions.md).

## Siklus hidup rendering

Tiga pertanyaan menentukan semua yang diperhatikan pembaca:

| Pertanyaan | Jawaban | Halaman |
|---|---|---|
| Siapa yang memproduksi HTML? | server, atau browser untuk rute klien | [Rendering](../rendering/README.md) |
| Kapan data dibaca? | pada setiap permintaan, pada setiap regenerasi, atau di browser | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Kapan JavaScript tiba? | hanya untuk sebuah pulau, atau untuk keseluruhan dokumen | [Pulau](../rendering/islands.md), [CSR](../rendering/csr.md) |

Dalam mode server, server merender setiap halaman, `revalidate` menyimpan satu halaman per URL, dan pulau menambahkan JavaScript ke satu komponen. Dalam mode klien, dokumen pertama dirender di Node dan navigasi kemudian terjadi di browser.

`__nexy__/` menampung semua yang dihasilkan: halaman yang dikompilasi, entri klien, keluaran build. Jangan pernah mengeditnya, jangan pernah melakukannya; hapus untuk memaksa pembangunan yang bersih.

## Integrasi frontend

**Vite tidak menggantikan Nexy.** Vite memaketkan dan menyajikan kode klien. Itu tidak merutekan permintaan, merender halaman `.nexy`, menjalankan Tindakan, atau memiliki asal. Browser berkomunikasi dengan satu asal - Nexy - dan dalam pengembangan, proksi Nexy Vite's titik akhir melaluinya, jadi tidak ada CORS yang harus dikonfigurasi.

**Nexy tidak menggantikan React.** Nexy memutuskan komponen mana yang dirender, kapan, dan dengan props yang mana; kerangka tersebut memiliki model komponen, reaktivitas, dan ekosistem. Halaman `.nexy` mengimpor komponen sebagai pulau; dalam mode klien, rute *adalah* sebuah komponen.

Untuk rute komponen, Python hanya menulis modul pembungkus tipis yang menunjuk ke file. Kompilasi dan rendering sisi server adalah tugas Vite.

## Pengembangan dan produksi

| | `nx dev` | `nx build` lalu `nx start` |
|---|---|---|
| Halaman | dikompilasi saat Anda menyimpan | dikompilasi satu kali, sebelumnya |
| Kode klien | Vite server pengembang dengan hot reload, di belakang bundel | asal Nexy sendiri di `__nexy__/client/`, HTML yang telah dirender sebelumnya |
| Node.js | berjalan di sebelah Python | tidak diperlukan untuk melakukan servis |
| Kesalahan | overlay di browser, toolbar di setiap halaman | halaman status tanpa detail |
| Asal | satu port, `3000` | satu port |

Apa yang tidak berubah: aturan routing yang sama, file halaman yang sama, `nexyconfig.py` yang sama. Halaman yang berperilaku berbeda antara keduanya adalah bug, bukan mode.

## Lebih dalam

- [Struktur proyek](project-structure.md): setiap folder proyek
- [Rendering](../rendering/README.md): SSR, ISR, CSR dan kepulauan
- [Frontend](../guides/frontend.md): Vite, gaya dan pembuatan klien
- [Perutean](../routing/README.md): router berbasis file, modular, dan khusus
