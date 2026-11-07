# Tutorial Nexy: membuat aplikasi catatan langkah demi langkah

Tutorial Nexy membuat satu aplikasi catatan dari folder kosong ke build produksi, satu bagian pada satu waktu, dan setiap bagian diakhiri dengan aplikasi yang berjalan.

Baru mengenal Nexy? [Mulai cepat](quick-start.md) menunjukkannya berjalan dalam tiga menit; kembali ke sini untuk mempelajari cara kerjanya.

## Bagaimana tutorialnya bekerja

- **Satu aplikasi yang berkembang.** Setiap bagian menambahkan satu fitur ke aplikasi catatan bagian sebelumnya.
- **Router Anda.** Bagian-bagiannya mengikuti router yang dipilih di bagian atas menu: berbasis file, modular, atau khusus. Pindahkan ke sana, dan file dari setiap bagian ikut berubah.
- **Kode yang berjalan.** Setiap file dengan nama di atasnya adalah keseluruhan file, dan rangkaian pengujian memutar ulang bagian-bagian tersebut secara berurutan pada proyek baru: apa yang Anda salin itulah yang dijalankan.
- **Berhenti di mana saja.** Setiap bagian membutuhkan waktu 10 hingga 20 menit dan diakhiri dengan apa yang harus diperiksa di browser.

## Bagian-bagiannya

### Unit 1: dasar-dasarnya

| Bagian | Apa yang Anda tambahkan | Apa yang Anda pelajari |
|---|---|---|
| [1. Buat proyek](../tutorial/create-the-project.md) | sebuah proyek yang berjalan | `nexy new`, `nexy dev` |
| [2. Halaman dan tata letak](../tutorial/pages-and-layouts.md) | halaman catatan | halaman, tampilan, tata letak |
| [3. Rute dinamis dan API](../tutorial/dynamic-routes.md) | `/notes/1` dan `/api/notes` | Segmen URL, rute JSON, `notFound` |
| [4. Komponen](../tutorial/components.md) | satu kartu per catatan | `.nexy` komponen dan alat peraganya |

### Satuan 2: data

| Bagian | Apa yang Anda tambahkan | Apa yang Anda pelajari |
|---|---|---|
| [5. Simpan catatan di SQLite](../tutorial/store-the-notes.md) | sebuah model, sebuah migrasi, sebuah benih | SQLModel, `nx migrate` |
| [6. Membuat catatan dari formulir](../tutorial/create-a-note.md) | formulir yang menyimpan catatan | Tindakan, bentuk tanpa JavaScript |
| [7. Tampilkan kesalahan validasi](../tutorial/validation-errors.md) | pesan di atas formulir | aturan dalam suatu Tindakan, `303`, `useSearchParams` |
| [8. Mengedit dan menghapus catatan](../tutorial/edit-and-delete.md) | bentuk-bentuk catatan | beberapa Tindakan per halaman, bidang tersembunyi |
| [9. Beri nomor halaman pada catatan](../tutorial/paginate-the-notes.md) | lima catatan per halaman | `offset` dan `limit`, penghubung antar halaman |

### Unit 3: pengguna

| Bagian | Apa yang Anda tambahkan | Apa yang Anda pelajari |
|---|---|---|
| [10. Buat akun dan masuk](../tutorial/accounts.md) | daftar, masuk, keluar | sesi, hashing kata sandi |
| [11. Berikan catatannya masing-masing kepada pengguna](../tutorial/own-notes.md) | catatan milik pengguna | kunci asing, `redirect`, `401` |
| [12. Reset password yang terlupa melalui email](../tutorial/password-reset.md) | tautan reset dikirim melalui email | `smtplib`, token bertanda tangan yang masa berlakunya habis |

### Unit 4: interaktivitas

| Bagian | Apa yang Anda tambahkan | Apa yang Anda pelajari |
|---|---|---|
| [13. Cari catatan saat Anda mengetik](../tutorial/search-the-notes.md) | kotak pencarian yang memfilter saat Anda mengetik | React pulau, alat peraga dari Python |
| [14. Centang catatan tanpa memuat ulang halaman](../tutorial/tick-a-note.md) | tombol Selesai di setiap not | peningkatan progresif, satu Tindakan untuk bentuk dan untuk `fetch` |

### Berikutnya

| Satuan | Apa keuntungan aplikasi |
|---|---|
| 5. Melampaui permintaan | catatan dibagikan melalui email di latar belakang, intisari harian, pembaruan langsung |
| 6. Kirim | pengujian, halaman dan log kesalahan, header keamanan, build Docker |

## Langkah selanjutnya

- [Bagian 1: membuat proyek](../tutorial/create-the-project.md)
- [Konsep inti](core-concepts.md): kata-kata yang digunakan tutorial
