# Kinerja

Apa yang dilakukan `nx start` secara default, apa yang harus diaktifkan, dan apa yang diukur.

## Default

| Masalah | Default | Ubah |
|---|---|---|
| Memproses | satu Uvicorn pekerja per CPU di Linux dan macOS, satu di Windows | `nx start` menjalankan aplikasi melalui Uvicorn |
| Kompresi | nonaktif | `useGZip = {"minimum_size": 1000}` di [Konfigurasi](../reference/config.md), atau kompres di proksi terbalik |
| File statis | disajikan dengan `ETag` dan `Last-Modified`, tidak ada `Cache-Control` | yang menyetel cache jangka panjang di proksi terbalik atau CDN untuk bundel hash |
| Halaman HTML | dirender per permintaan, tanpa cache | [ISR](../rendering/isr.md) dengan `revalidate = N` |
| Dokumen API | pada | `useDocs = False` dalam produksi |
| Node saat runtime | tidak ada | `nx build` melakukan pra-render komponen klien |

## Diukur

Pengoperasian lokal, satu pekerja Uvicorn, Windows, Python 3.13, koneksi tetap hidup dari generator beban Python pada mesin yang sama. Perlakukan angka-angka tersebut sebagai dasar untuk membandingkan perubahan, bukan sebagai patokan terhadap kerangka kerja lainnya.

| Rute | Konkurensi | Permintaan per detik | p50 | p99 |
|---|---|---|---|---|
| Telanjang FastAPI Rute JSON | 16 | ~4,500 | 3,4 mdtk | 5,1 mdtk |
| Rute Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2,900 | 5,2 md | 9,8 md |
| Halaman Nexy SSR (16 KB, 16 komponen) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Halaman Nexy SSR (16 KB, 16 komponen) | 64 | ~670 | 94 ms | 126 ms |

Membaca tabel:

- Lapisan Nexy sendiri (konteks jalur, middleware) menghabiskan biaya sekitar sepertiga dari throughput rute kosong FastAPI.
- Halaman yang dirender di server membutuhkan CPU sekitar 2 ms, tersebar di sekitar 16 rendering template (satu per komponen). Halaman dengan komponen lebih sedikit secara proporsional lebih murah.
- Skala throughput dengan pekerja. Di Linux, `nx start` sudah memulai satu per CPU.

## Saran praktis

1. Tempatkan Nginx, Caddy atau keunggulan platform Anda: TLS, HTTP/2, Brotli, dan caching jangka panjang untuk aset `/__nexy__/client/` adalah kelebihannya. Lihat [Menerapkan](README.md).
2. Gunakan [ISR](../rendering/isr.md) untuk halaman yang berubah kurang dari sekali dalam satu menit.
3. Hidrasi secara malas dengan [pulau](../rendering/islands.md) sehingga muatan pertama dikirimkan lebih sedikit JavaScript.
4. Jaga agar jumlah `.nexy` komponen per halaman masuk akal: masing-masing komponen merupakan render template terpisah.
5. Ukur rute Anda sendiri. Generator beban lokal yang menjaga koneksi tetap hidup sudah cukup untuk membandingkan dua versi halaman.

## Langkah selanjutnya

- [Menyebarkan](README.md)
- [Render](../rendering/README.md)
- [Konfigurasi](../reference/config.md)
