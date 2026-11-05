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

| File | Aturan |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | setiap tata letak dari akar hingga halaman membungkusnya, **terluar dulu** |
| `middleware.py` | setiap file dari root hingga rute membungkus permintaan, **terluar dulu**, sebelum dependensi |
| `dependencies.py` | setiap file dari root hingga rute berjalan, **yang terluar terlebih dahulu**, lalu penjaga pawangnya sendiri |
| `notfound.nexy`, `errors.nexy` | yang **terdekat** menang, per kode status |

Untuk halaman di atas, tata letak disarangkan sebagai `root layout > (shop) layout > cart layout > page`, dan dependensi dijalankan sebagai `root > (shop) > cart > handler guards`.

## Kenapa yang terluar dulu

Tata letak luar menggambar bingkai dan ketergantungan luar memutuskan siapa yang boleh masuk. Menempatkannya terlebih dahulu berarti bagian dalam dapat mengandalkannya: direktori yang memerlukan otentikasi dijalankan sebelum penangan yang membaca pengguna.

## Tata Letak

Semua file tata letak tumpukan keluarga folder: lihat [Tata Letak](layouts/README.md). Keluarga yang berbeda tidak dapat digabungkan: `layout.vue` tidak pernah membungkus halaman `.tsx`, dan proyek memiliki tata letak `layout.nexy` atau klien, tidak pernah keduanya ([mode](modes.md)).

## File perangkat tengah

Lihat [File Middleware](middleware/README.md): file tersebut dijalankan sebelum dependensi dan dapat menjawab tanpa mencapai rute.

## Ketergantungan

Lihat [Dependensi](dependencies/README.md) untuk urutan dalam file handler, termasuk `@UseGuard` dan `@Middleware`.

## Halaman kesalahan

`notfound.nexy` dan `errors.nexy` dipasang satu kali pada root rute; salinan dalam subdirektori menyaring halaman untuk awalan tersebut. Lihat [Halaman kesalahan](errors/README.md).

## Langkah selanjutnya

- [Tata Letak](layouts/README.md)
- [Ketergantungan](dependencies/README.md)
- [Halaman kesalahan](errors/README.md)
