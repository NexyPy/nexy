# Tata Letak Bagian Depan

**Layout** adalah pembungkus yang mendefinisikan struktur bersama di sekitar satu halaman atau lebih. Tata letak memungkinkan pengalaman "seperti aplikasi" dengan mempertahankan status dan menghindari pemuatan ulang halaman penuh selama navigasi.

## Logika Bersarang

Tata letak mengikuti struktur hierarki berdasarkan pohon direktori di bawah `src/routes/`.

1.  **Tata Letak Akar**: Setiap proyek memiliki tata letak akar (misalnya, `src/routes/layout.nexy`). Ini adalah satu-satunya tata letak yang bertanggung jawab untuk mendefinisikan shell dokumen: `<html>`, `<head>`, dan `<body>`.
2.  **Tata Letak Bersarang**: Folder apa pun dapat berisi file `layout.*` miliknya sendiri. Tata letak ini membungkus semua halaman dan sub-tata letak dalam folder itu.
3.  **Warisan**: Sebuah halaman dibungkus oleh semua tata letak dari akar hingga ke foldernya sendiri.

## Keadaan & Komposisi Bersama

Tata letak dirancang agar stabil. Saat bernavigasi di antara dua halaman yang berbagi tata letak yang sama, tata letak tersebut **tidak** dirender ulang; hanya konten anak yang berubah.

- **Slots**: Tata letak menyediakan "slot" (biasanya `children` di BEJ atau `{{ content }}` di Jinja2) tempat halaman bersarang dimasukkan.
- **Pelestarian Status**: Karena tata letak tetap terpasang, status apa pun yang ada di dalamnya (misalnya, kueri penelusuran di header) dipertahankan selama navigasi.

## Batasan Statis

Untuk rute yang telah dirender sebelumnya (SSG), tata letak root tidak dapat bergantung pada data waktu permintaan seperti cookie atau header. Itu harus dapat direpresentasikan sebagai cangkang statis yang kemudian dihidrasi oleh klien.

## Implementasi Kerangka

Penerapan slot dan nesting sedikit berbeda berdasarkan kerangka kerja. Lihat panduan **Perbedaan** untuk teknologi pilihan Anda:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
