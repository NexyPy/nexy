# Kinerja

Apa yang dilakukan `nx start` secara default, apa yang harus diaktifkan, dan apa yang diukur.

## Default

| Kekhawatiran | Bawaan | Ubah itu |
|---|---|---|
| Proses | satu Uvicorn pekerja per CPU di Linux dan macOS, satu di Windows | `nx start` menjalankan aplikasi melalui Uvicorn |
| Kompresi | mati | `useGZip = {"minimum_size": 1000}` di [Konfigurasi](../reference/config.md), atau kompres di proksi terbalik |
| File statis | disajikan dengan `ETag` dan `Last-Modified`, tidak ada `Cache-Control` | mengatur caching yang berumur panjang di proksi terbalik atau CDN untuk bundel yang di-hash |
| halaman HTML | diberikan per permintaan, tanpa cache | [ISR](../rendering/isr.md) dengan `revalidate = N` |
| dokumen API | pada | `useDocs = False` dalam produksi |
| Node saat runtime | tidak ada | `nx build` melakukan pra-render komponen klien |

Dua saklar tabel di `nexyconfig.py`, dan ISR di halaman:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

## Diukur

Pengoperasian lokal, satu pekerja Uvicorn, Windows, Python 3.13, koneksi tetap hidup dari generator beban Python pada mesin yang sama. Perlakukan angka-angka tersebut sebagai dasar untuk membandingkan perubahan, bukan sebagai patokan terhadap kerangka kerja lainnya.

Rute tabel Nexy JSON adalah file ini:

```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```

| Rute | Konkurensi | Permintaan per detik | hal50 | hal99 |
|---|---|---|---|---|
| Telanjang FastAPI Rute JSON | 16 | ~4.500 | 3,4 ms | 5,1 ms |
| Rute Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2.900 | 5,2 ms | 9,8 ms |
| Halaman Nexy SSR (16 KB, 16 komponen) | 1 | ~500 | 1,9 ms | 3,0 mdtk |
| Halaman Nexy SSR (16 KB, 16 komponen) | 64 | ~670 | 94 ms | 126 ms |

Membaca tabel:

- Lapisan Nexy sendiri (konteks jalur, middleware) menghabiskan biaya sekitar sepertiga dari throughput rute kosong FastAPI.
- Halaman yang dirender di server membutuhkan CPU sekitar 2 ms, tersebar di sekitar 16 rendering template (satu per komponen). Halaman dengan komponen lebih sedikit secara proporsional lebih murah.
- Skala throughput dengan pekerja. Di Linux, `nx start` sudah memulai satu per CPU.

## Saran praktis

1. Tempatkan Nginx, Caddy atau keunggulan platform Anda: TLS, HTTP/2, Brotli, dan caching jangka panjang untuk aset `/__nexy__/client/` adalah kelebihannya. Lihat [Menerapkan](README.md).
2. Gunakan [ISR](../rendering/isr.md) untuk halaman yang berubah kurang dari sekali dalam satu menit.
3. Hidrasi dengan malas dengan [pulau](../rendering/islands.md) sehingga muatan pertama dikirimkan lebih sedikit JavaScript.
4. Jaga agar jumlah komponen `.nexy` per halaman masuk akal: masing-masing komponen merupakan render template terpisah.
5. Ukur rute Anda sendiri. Generator beban lokal yang menjaga koneksi tetap hidup sudah cukup untuk membandingkan dua versi halaman.

Saran 1 dengan Nginx: bundel klien yang di-hash di-cache selama satu tahun, sisanya masuk ke Nexy.

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Langkah selanjutnya

- [Menyebarkan](README.md)
- [Merender](../rendering/README.md)
- [Konfigurasi](../reference/config.md)
