# Warisan

Beberapa file di `src/routes/` berlaku untuk semua file di bawah direktorinya. Semuanya diselesaikan dengan cara yang sama: Nexy memulai dari direktori rute dan berjalan hingga `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Mengajukan | Aturan |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | setiap tata letak dari akar hingga halaman membungkusnya, **terluar dulu** |
| `middleware.py` | setiap file dari root hingga rute membungkus permintaan, **terluar terlebih dahulu**, sebelum dependensi |
| `dependencies.py` | setiap file dari root hingga rute berjalan, **yang terluar terlebih dahulu**, lalu penjaga pawangnya sendiri |
| `notfound.nexy`, `errors.nexy` | yang **terdekat** menang, per kode status |

Untuk halaman di atas, tata letak disarangkan sebagai `root layout > (shop) layout > cart layout > page`, dan dependensi dijalankan sebagai `root > (shop) > cart > handler guards`.

## Kenapa yang terluar dulu

Tata letak luar menggambar bingkai dan ketergantungan luar memutuskan siapa yang boleh masuk. Menempatkannya terlebih dahulu berarti bagian dalam dapat mengandalkannya: direktori yang memerlukan otentikasi dijalankan sebelum penangan yang membaca pengguna.

Ketergantungan `(shop)` pada pohon memeriksa cookie keranjang, sehingga ketergantungan keranjang di bawahnya dapat membaca keranjang tanpa memeriksa lagi:

```python filename="src/rute/(toko)/dependensi.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Tata Letak

Semua file tata letak tumpukan keluarga folder: lihat [Tata Letak](layouts/README.md). Keluarga yang berbeda tidak dapat digabungkan: `layout.vue` tidak pernah membungkus halaman `.tsx`, dan proyek memiliki tata letak `layout.nexy` atau klien, tidak pernah keduanya ([mode](modes.md)).

Tata letak pohon yang paling dalam hanya menambahkan bingkainya sendiri: tata letak akar di sekitarnya masih menggambar dokumen.

```nexy filename="src/routes/(toko)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## File perangkat tengah

Lihat [File Middleware](middleware/README.md): file tersebut dijalankan sebelum dependensi dan dapat menjawab tanpa mencapai rute.

Akar `middleware.py` membungkus setiap rute pohon, termasuk keretanya:

```python filename="src/rute/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Ketergantungan

Lihat [Dependensi](dependencies/README.md) untuk urutan dalam file handler, termasuk `@UseGuard` dan `@Middleware`.

## Halaman kesalahan

`notfound.nexy` dan `errors.nexy` dipasang satu kali pada root rute; salinan dalam subdirektori menyaring halaman untuk awalan tersebut. Lihat [Halaman kesalahan](errors/README.md).

Salinan di `cart/` menjawab 404 di bawah `/cart`, dan akarnya menyimpan sisanya:

```nexy filename="src/routes/(toko)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Langkah selanjutnya

- [Tata Letak](layouts/README.md)
- [Ketergantungan](dependencies/README.md)
- [Halaman kesalahan](errors/README.md)
