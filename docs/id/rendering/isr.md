# ISR (basi-saat-validasi ulang)

## Definisi

ISR menyimpan cache HTML satu halaman, per URL, dan menyajikannya hingga jendelanya habis masa berlakunya. Salinan yang sudah habis masa berlakunya masih disajikan sementara salinan baru ditampilkan di latar belakang: yaitu *basi-sementara-validasi ulang*.

## Bagaimana cara kerjanya

`revalidate = N` di bagian depan halaman `.nexy` akan mengaktifkannya. `N` adalah jumlah detik; nilai yang hilang, nol atau negatif berarti tidak ada cache sama sekali.

Kunci cache adalah **jalur permintaan saja** - `request.scope["path"]`. String kueri bukan bagian darinya.

| Apa | Nilai |
|---|---|
| Kunci | jalur URL (`/blog/hello`) |
| Penyimpanan | di memori, dalam proses rendering halaman |
| Terikat | 256 entri per proses, paling sedikit digunakan baru-baru ini dikeluarkan |
| Header tanggapan | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Siklus hidup rendering

1. Permintaan tiba untuk halaman yang menyatakan `revalidate`.
2. Belum ada entri: halaman dirender, disimpan, dan dikembalikan.
3. Entri yang lebih muda dari `N` detik: dikembalikan apa adanya, halaman tidak dirender.
4. Entri yang lebih lama dari `N` detik: entri **basi** segera dikembalikan, dan tugas latar belakang menampilkan yang baru.
5. Jika render latar belakang tersebut meningkat, entri basi akan tetap ada dan permintaan basi berikutnya akan mencoba lagi.

## Kapan harus digunakan

- HTML yang sama untuk setiap pengunjung: postingan blog, halaman produk, halaman dokumentasi.
- Halaman ini sering dibaca dan jarang diubah.
- Datanya bisa berumur beberapa detik tanpa ada yang menyadarinya.

## Konfigurasi

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` adalah bilangan bulat biasa. Tidak ada penggantian per rute di tempat lain, dan penangan `.py` bukanlah halaman: mereka tidak pernah memasukkan cache ini.

## Contoh

Sebuah posting blog yang membaca database:

```nexy filename="src/rute/blog/[siput].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

Permintaan pertama untuk `/blog/hello` dirender dan disimpan. 300 detik berikutnya disajikan dari memori. `/blog/other` adalah entri terpisah, dirender dan disimpan sendiri. Dalam proyek nyata `posts` berasal dari database atau layanan, dipanggil satu kali per regenerasi.

## Keterbatasan

**Nexy menjamin** kunci cache adalah jalurnya, salinan basi disajikan selama regenerasi, dan penyimpanan dibatasi dan aman untuk thread.

**Berdasarkan konvensi**, halaman yang menyatakan `revalidate` adalah konten publik. Tulis seolah-olah setiap pengunjung melihat HTML yang sama.

**Aplikasi Anda bertanggung jawab untuk** hal lainnya:

| Batasan | Artinya |
|---|---|
| String kueri diabaikan | `/search?q=a` dan `/search?q=b` berbagi satu entri. Jangan menyimpan halaman pencarian dalam cache. |
| Sesi tidak terisolasi | Responsnya mengatakan `public`, dan HTML pengunjung pertama disajikan ke semua. Jangan pernah membaca sesi di halaman dengan `revalidate`. |
| Tidak ada pembatalan sisi server | Tidak ada yang membersihkan entri sebelum jendelanya berakhir. `revalidate(...)` di dalam [Aksi](../guides/actions.md) hanya memberitahu **browser** untuk memuat ulang jalur; itu tidak menyentuh cache ini. |
| Satu cache per proses | Beberapa pekerja menyimpan beberapa cache, dengan konten berbeda. |
| Regenerasi serentak | Tidak ada yang dapat menghapus duplikatnya: sepuluh permintaan basi dapat memulai sepuluh render. |
| Kesalahan tidak terdengar | Regenerasi yang gagal tetap menampilkan halaman lama; kegagalan dicatat, tidak dikembalikan. |

## Langkah selanjutnya

- [SSR](ssr.md): bagaimana halaman dirender sebelum di-cache
- [Aksi](../guides/actions.md): header `revalidate`, dan apa yang tidak dilakukannya
- [Kinerja](../deployment/performance.md)
- [Halaman](../routing/fbr/pages/README.md): tata letak dan segmen dinamis
