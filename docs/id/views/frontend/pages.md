# Halaman Depan

**Page** adalah unit dasar aplikasi Nexy. Ini adalah sumber daya beralamat URL yang ditentukan oleh file di bawah `src/routes/`. 

Terlepas dari kerangka klien yang digunakan, setiap halaman mengikuti siklus hidup universal dan batasan arsitektur yang sama.

## Siklus Hidup Halaman

Saat pengguna menavigasi ke suatu halaman, Nexy melakukan langkah-langkah berikut:

1.  **Pencocokan Rute**: Router mengidentifikasi file yang sesuai dengan URL.
2.  **Pengambilan Data**: Server mengeksekusi logika halaman (Python frontmatter atau framework loader) untuk mengambil data yang diperlukan.
3.  **Komposisi**: Halaman dibungkus dalam `layout.nexy` terdekat (atau tata letak kerangka kerja).
4.  **Rendering**: Hasilnya dirender ke HTML (melalui Jinja2, Markdown, atau framework SSR).
5.  **Hidrasi**: Jika halaman menggunakan kerangka klien, browser melampirkan logika interaktif ke HTML statis.

## Perutean & URL

Perutean sepenuhnya berbasis file. URL ditentukan oleh jalur file di bawah `src/routes/`, dikurangi ekstensi.

### Segmen Dinamis
Untuk membuat rute yang bervariasi berdasarkan parameter (misalnya profil pengguna), gunakan tanda kurung siku:
- `src/routes/user/[id].tsx` → `/user/123`

Nilai segmen (`123`) tersedia ke halaman melalui kait `useParams()` dari `@nexy/client`.

### Grup Rute
Folder yang dibungkus dalam tanda kurung diabaikan oleh router tetapi memungkinkan Anda mengelompokkan file untuk tujuan organisasi atau tata letak bersama:
- `src/routes/(auth)/login.tsx` → `/login`

## Metadata Halaman
Setiap halaman dapat menentukan metadata (judul, deskripsi, tag OpenGraph) yang dimasukkan Nexy ke dalam shell dokumen. Dalam file `.nexy`, ini dilakukan di frontmatter; dalam file kerangka kerja, ini disediakan melalui ekspor `metadata`.

## Implementasi Kerangka
Konsep-konsep di atas bersifat universal. Untuk melihat cara mengimplementasikan Halaman dalam kerangka spesifik Anda, lihat panduan **Perbedaan**:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
