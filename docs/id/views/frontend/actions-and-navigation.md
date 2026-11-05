# Tindakan dan Navigasi

Interaksi di Nexy ditangani melalui sistem terpadu **Tindakan** dan **Navigasi**, memastikan bahwa frontend dan backend tetap sinkron tanpa kode lem API manual.

## Kontrak Aksi

Sebuah **Action** adalah fungsi sisi server yang menangani mutasi (misalnya, memperbarui database). 

1.  **Input yang Diketik**: Tindakan ditentukan di Python dengan petunjuk tipe. Nexy menghasilkan klien TypeScript yang cocok, sehingga Anda mendapatkan pelengkapan otomatis dan validasi di IDE Anda.
2.  **Eksekusi Atom**: Suatu tindakan adalah permintaan `POST` tunggal.
3.  **Penanganan Hasil**: Tindakan mengembalikan hasil yang diketik yang dapat digunakan klien untuk memperbarui UI.

## Navigasi Sisi Klien

Navigasi di Nexy "cerdas". Alih-alih memuat ulang browser secara penuh, Nexy menukar konten halaman saat ini sambil tetap menjaga tata letak aktif tetap terpasang.

- **Komponen `Link`**: Gunakan komponen `Link` khusus kerangka kerja untuk melakukan transisi sisi klien.
- **Navigasi Terprogram**: Gunakan fungsi `navigate()` dari `@nexy/client` untuk mengubah halaman sebagai respons terhadap logika (misalnya, setelah login berhasil).

## Koordinasi: Tindakan → Navigasi

Pola yang paling umum adalah melakukan suatu tindakan dan kemudian mengarahkan pengguna ke halaman baru.

**Alur Validasi Ulang:**
1.  Klien memanggil Tindakan.
2.  Tindakan dijalankan di server dan memanggil `revalidate("/path")`.
3.  Server mengembalikan hasilnya bersama dengan sinyal untuk menyegarkan jalur yang ditentukan.
4.  Klien memperbarui konten halaman untuk mencerminkan keadaan baru.

## Implementasi Kerangka

API untuk memanggil tindakan dan bernavigasi bervariasi berdasarkan kerangka kerja. Lihat panduan **Perbedaan** untuk teknologi pilihan Anda:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
