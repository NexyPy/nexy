# Bagaimana cara kerja transisi halaman?

Nexy menggunakan View Transitions API browser untuk navigasi klien, sehingga browser yang didukung menganimasikan pertukaran halaman kecuali pengunjung lebih memilih gerakan yang dikurangi.

## Saat transisi berjalan

Dokumen pertama adalah respons server normal dan tidak memiliki transisi. Sejak saat itu, setiap navigasi yang ditangani oleh router klien menukar halaman di dalam `document.startViewTransition()`: link ke rute klien, `router.push()` atau `router.replace()`, dan tombol mundur dan maju. Router merender halaman berikutnya dan tata letaknya terlebih dahulu, lalu memindahkan URL-nya, sehingga halaman baru siap sebelum ditampilkan.

React, Preact, Solid, Vue dan Svelte berbagi router yang sama, sehingga perilakunya sama di kelima adaptor. Tidak ada pengaturan untuk mengaktifkan transisi.

## Ketika jatuh kembali

- Browser tanpa `startViewTransition()` merender halaman secara langsung.
- Dengan `prefers-reduced-motion: reduce`, router merender halaman secara langsung.
- Transisi yang dilewati oleh navigasi yang lebih baru tidak mencatat kesalahan: halaman masih benar.

URL, riwayat, posisi gulir, dan peristiwa `nexy:navigated` berperilaku sama dengan atau tanpa transisi.

## Gaya transisinya

Nexy tidak mengirimkan CSS animasi. Browser menerapkan cross-fade defaultnya, yang dapat Anda ganti di stylesheet Anda sendiri:

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Langkah selanjutnya

- [Menghubungkan dan menavigasi](linking-and-navigating.md)
- [Kait](hooks.md)
