# Glosarium

Kata-kata yang digunakan dokumen ini, masing-masing satu baris, disusun berdasarkan abjad. Istilah yang membutuhkan lebih dari satu baris memiliki halaman: ikuti tautannya. Untuk mengetahui kesesuaian gagasan-gagasan tersebut, bacalah [Konsep inti](../getting-started/core-concepts.md).

## Ketentuan

| Istilah | Dalam satu baris |
|---|---|
| Tindakan | fungsi Python bertanda `@Action`, berfungsi sebagai `POST` dan dapat dipanggil dari klien ([aksi](../guides/actions.md)) |
| ASGI | antarmuka Uvicorn berbicara, diimplementasikan oleh FastAPI dan Starlette |
| Modus klien | `useCSR = True`: file kerangka adalah rute dan navigasi browser ([mode](../routing/fbr/modes.md)) |
| Komponen | blok penyusun UI yang dapat digunakan kembali untuk membuat tampilan ([tampilan](../views/README.md)) |
| CSR | rendering sisi klien: browser merender halaman setelah dokumen pertama ([CSR](../rendering/csr.md)) |
| Ketergantungan | sebuah fungsi FastAPI berjalan sebelum seorang handler, per rute atau per folder ([dependensi](../routing/fbr/dependencies/README.md)) |
| Cangkang dokumen | `<html>`, `<head>` dan `<body>` di sekitar halaman, dimiliki oleh tata letak terdekat atau oleh Nexy ([tata letak](../routing/fbr/layouts/README.md)) |
| Titik akhir | kombinasi unik dari URL dan metode HTTP ([tampilan](../views/README.md)) |
| FBR | perutean berbasis file: file di bawah `src/routes/` adalah rute ([perutean](../routing/fbr/README.md)) |
| Masalah depan | blok Python di antara dua baris `---` dari file `.nexy` atau `.md` ([berkas .nexy](../views/nexy/README.md)) |
| Penjaga | ketergantungan yang menolak permintaan dengan menaikkan `HTTPException` ([penjaga](../routing/modular/guards-and-metadata.md)) |
| Penangan | fungsi Python yang menangani permintaan HTTP untuk metode tertentu ([tampilan](../views/README.md)) |
| HMR | penggantian modul panas: server pengembang menukar modul yang diubah, tanpa memuat ulang penuh ([frontend](../guides/frontend.md)) |
| Hidrasi | browser yang melampirkan kerangka kerja ke HTML yang sudah dikirim server ([pulau](../rendering/islands.md)) |
| Pulau | komponen klien dipasang di dalam halaman yang dirender server ([pulau](../rendering/islands.md)) |
| ISR | regenerasi statis tambahan: satu halaman cache per jalur, disegarkan di latar belakang ([ISR](../rendering/isr.md)) |
| Tata Letak | file `layout.*` yang membungkus halaman di bawah foldernya ([tata letak](../routing/fbr/layouts/README.md)) |
| Perute modular | rute dideklarasikan dengan `@Module` dan `@Controller` di bawah `src/apps/` ([modular](../routing/modular/README.md)) |
| Halaman | sumber daya beralamat URL yang ditentukan oleh file di bawah `src/routes/` ([tampilan](../views/README.md)) |
| Ambil terlebih dahulu | memuat halaman di belakang link sebelum pembaca mengkliknya ([tautan](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | nilai yang diberikan induk ke komponen ([berkas .nexy](../views/nexy/README.md)) |
| Validasi ulang | jumlah detik setelah halaman ISR dibuat ulang di latar belakang ([ISR](../rendering/isr.md)) |
| Rute | pola URL, dihasilkan oleh jalur file rute ([perutean](../routing/README.md)) |
| Grup rute | folder dalam tanda kurung yang mengelompokkan rute tanpa menambahkan segmen ([rute dinamis](../routing/fbr/pages/dynamic-routes.md)) |
| Pengendali rute | fungsi `GET`, `POST`, … dari file rute `.py` ([handler](../routing/fbr/handlers/README.md)) |
| Modus server | `useCSR = False`, default: server merender halaman `.nexy` dan `.md` ([mode](../routing/fbr/modes.md)) |
| Keterampilan | folder dengan `SKILL.md` yang mengajarkan agen pengkodean satu bagian dari Nexy ([agen pengkodean](../guides/ai-agents.md)) |
| SSG | pembuatan situs statis; **bukan mode Nexy**: HTML yang dibuat sebelumnya selalu dibaca kembali oleh server ([perenderan](../rendering/README.md)) |
| RSK | rendering sisi server: server merender setiap halaman untuk permintaannya, dan ini adalah default ([SSR](../rendering/ssr.md)) |
| Lihat | proses menghasilkan isi respons untuk suatu halaman ([tampilan](../views/README.md)) |

## File dan folder

| Nama | Dalam satu baris |
|---|---|
| `__nexy__/` | keluaran yang dihasilkan: halaman yang dikompilasi, entri klien dan klien tindakan; tidak pernah diedit, tidak pernah dilakukan |
| `nexyconfig.py` | konfigurasi proyek, kelas bidang `use*` ([konfigurasi](config.md)) |
| `public/` | file yang disajikan di root, seperti `public/logo.svg` → `/logo.svg` ([konvensi file](file-conventions.md)) |
| `src/apps/` | pengontrol dan modul router modular ([modular](../routing/modular/README.md)) |
| `src/components/` | komponen yang diimpor berdasarkan halaman; tidak pernah merutekan ([konvensi file](file-conventions.md)) |
| `src/routes/` | rute aplikasi ([konvensi file](file-conventions.md)) |

## Langkah selanjutnya

- [Konsep inti](../getting-started/core-concepts.md): model milik kata-kata ini
- [Indeks dokumentasi](../README.md): halaman untuk tugas yang ada
- [Konvensi file](file-conventions.md): nama khusus di balik definisi ini
- [Untuk agen AI](../guides/ai-agents.md): invarian yang sama, ditulis untuk agen
