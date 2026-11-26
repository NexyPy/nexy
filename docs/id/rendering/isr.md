# ISR (basi-saat-validasi ulang)

## Definisi

ISR menyimpan cache HTML satu halaman, per URL, dan menyajikannya hingga jendelanya habis masa berlakunya. Salinan yang sudah habis masa berlakunya masih disajikan sementara salinan baru ditampilkan di latar belakang: yaitu *basi-sementara-validasi ulang*.

## Bagaimana cara kerjanya

`revalidate = N` di bagian depan halaman `.nexy` akan mengaktifkannya. `N` adalah jumlah detik; nilai yang hilang, nol atau negatif berarti tidak ada cache sama sekali.

Kunci cache adalah **jalur permintaan saja** - `request.scope["path"]`. String kueri bukan bagian darinya.

| Apa | Nilai |
|---|---|
| Kunci | jalur URL (`/blog/hello`) |
| Penyimpanan | dipilih oleh `useISRCache`: memori secara default, file, Redis, atau penyimpanan khusus |
| Terikat | 256 entri untuk penyimpanan memori, yang terakhir digunakan dikeluarkan; file dan Redis menyimpan entri hingga tidak valid |
| Tajuk respons | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Setiap respons ISR membawa header tersebut, termasuk render pertama dan render cadangan saat penyimpanan tidak aktif. CDN dapat menggunakannya untuk menyimpan salinan URL publik yang sama.

## Siklus hidup rendering

1. Permintaan tiba untuk halaman yang menyatakan `revalidate`.
2. Belum ada entri: halaman dirender, disimpan, dan dikembalikan.
3. Entri yang lebih muda dari `N` detik: dikembalikan apa adanya, halaman tidak dirender.
4. Entri yang lebih lama dari `N` detik: entri **basi** segera dikembalikan, dan tugas latar belakang menampilkan yang baru.
5. Jika perenderan latar belakang gagal, entri basi tetap ada dan permintaan basi berikutnya mencoba lagi.
6. Jika penyimpanan gagal, halaman dirender dan dikembalikan tanpa entri cache. Permintaannya masih berhasil.

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

## Pilih toko

Atur `useISRCache` di `nexyconfig.py`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Nilai | Toko | Dibagikan oleh |
|---|---|---|
| tidak disetel, `None`, atau `"memory"` | memori proses, dibatasi hingga 256 entri | satu pekerja |
| `"file"` | File JSON di `.nexy/isr` | pekerja di satu host |
| `{"type": "file", "directory": ".cache/isr"}` | File JSON di direktori yang diberikan | pekerja di satu host |
| `"redis"` | Redis di `redis://localhost:6379/0` | setiap pekerja yang mencapai server |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis di URL itu | setiap pekerja yang mencapai server |
| `{"type": "redis", "client": client}` | klien Redis yang Anda lewati | setiap pekerja yang mencapai server |
| sebuah objek dengan `get`, `set` dan `invalidate` | toko Anda sendiri | apa pun yang dibagikannya |

Toko Redis memerlukan paket klien: `uv add redis`. Itu tidak diinstal dengan Nexy. Penyimpanan khusus mengimplementasikan protokol `ISRCache` dari `nexy.modules.runtime.cache`; `get`-nya mengembalikan `CacheEntry` atau `None`.

Entri file ditulis secara atomik, sehingga pekerja tidak pernah membaca halaman setengah tertulis. Pekerja yang menggunakan direktori yang sama atau server Redis yang sama membaca entri yang sama. Penyimpanan yang rusak hanya membutuhkan biaya render: tidak pernah menjawab permintaan dengan kesalahan.

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

Permintaan pertama ke `/blog/hello` dirender dan disimpan. 300 detik berikutnya dilayani dari toko yang dipilih. `/blog/other` adalah entri terpisah, dirender dan disimpan sendiri. Dalam proyek nyata `posts` berasal dari database atau layanan, dipanggil satu kali per regenerasi.

## Apa yang bisa dan tidak bisa dibagikan oleh CDN

CDN yang menghormati `cache-control` dapat menyimpan satu salinan `/blog/hello` selama `s-maxage` detik dan menyajikannya saat divalidasi ulang. Itu membagikan salinan itu antara pengunjung dan pekerja karena tanggapannya mengatakan `public`.

CDN tidak mengetahui toko Nexy. `revalidate()` dalam [Aksi](../guides/actions.md) menghapus entri dari penyimpanan Nexy yang dikonfigurasi, tetapi tidak menghapus CDN. CDN menyimpan salinannya hingga jendelanya berakhir, atau hingga Anda mengonfigurasi pembersihannya.

Jangan berikan CDN halaman yang HTML-nya bergantung pada pengunjung. Responsnya mengatakan `public`, dan kunci Nexy adalah jalurnya saja: dua string kueri pada satu jalur berbagi satu entri. Sesi, cookie, atau id pengguna dalam HTML dapat disajikan kepada pengunjung lain.

## Keterbatasan

**Nexy menjamin** kunci cache adalah jalurnya, salinan basi disajikan selama regenerasi, dan kegagalan penyimpanan dikembalikan ke render.

**Berdasarkan konvensi**, halaman yang menyatakan `revalidate` adalah konten publik. Tulis seolah-olah setiap pengunjung melihat HTML yang sama.

**Aplikasi Anda bertanggung jawab untuk** hal lainnya:

| Batasi | Apa artinya |
|---|---|
| String kueri diabaikan | `/search?q=a` dan `/search?q=b` berbagi satu entri. Jangan menyimpan halaman pencarian dalam cache. |
| Sesi tidak terisolasi | Tanggapannya mengatakan `public`, dan HTML pengunjung pertama disajikan ke semua. Jangan pernah membaca sesi di halaman dengan `revalidate`. |
| CDN tidak dibersihkan | `revalidate()` membersihkan penyimpanan Nexy, bukan CDN atau proxy lain di depannya. |
| Tidak ada TTL di file dan penyimpanan Redis | Entri tetap ada sampai `revalidate()` atau pembersihan Anda sendiri menghapusnya. Penyimpanan memori mengeluarkan entri yang terakhir digunakan setelah 256. |
| Regenerasi secara bersamaan | Tidak ada yang menghapus duplikatnya: sepuluh permintaan basi dapat memulai sepuluh render. |
| Kesalahan diam | Operasi regenerasi atau penyimpanan yang gagal terus menayangkan halaman tersebut; kegagalan tidak dikembalikan. |

## Langkah selanjutnya

- [SSR](ssr.md): bagaimana halaman dirender sebelum di-cache
- [Aksi](../guides/actions.md): header `revalidate` dan pembatalan penyimpanan
- [Konfigurasi](../reference/config.md#server): `useISRCache`
- [Pertunjukan](../deployment/performance.md)
- [Halaman](../routing/fbr/pages/README.md): tata letak dan segmen dinamis
