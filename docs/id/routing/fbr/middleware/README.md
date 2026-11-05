# File perangkat tengah

`middleware.py` dalam direktori rute membungkus permintaan yang ditangani oleh direktori tersebut. Seperti tata letak dan `dependencies.py`, file ditumpuk dari rute akar ke bawah, yang terluar terlebih dahulu.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

Fungsinya adalah `async def middleware(request, call_next)`: tanda tangan FastAPI dari `@app.middleware("http")`. Panggil `await call_next(request)` untuk melanjutkan rute, atau kembalikan respons untuk berhenti di sana. Kode setelah panggilan berjalan keluar dan dapat mengubah respons.

## Apa yang dibungkusnya

Middleware berlaku untuk **rute yang filenya ada di direktori** atau di bawahnya, baik halaman maupun penangan API, termasuk grup rute:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

Untuk request ke `/admin/users` urutannya adalah `root`, `admin`, `users`, lalu rutenya. Grup tidak memiliki URL sendiri, sehingga dicocokkan melalui rute yang melayani permintaan, bukan melalui URL.

URL yang tidak cocok dengan rute (404) hanya menerima middleware dari direktori yang bukan grup, dipilih berdasarkan awalan URL. `[slug]` cocok dengan satu segmen dan `[...rest]` cocok dengan sisanya.

## Apa yang tidak dibungkusnya

- URL kerangka dan aset: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` dan `/@...` (Vite).
- WebSocket penangan dan umur server: hanya permintaan HTTP.
- File dalam direktori dimulai dengan `_` atau `.`.

## Middleware, dependensi atau penjaga

| Gunakan | Saat |
|---|---|
| `middleware.py` | Anda memerlukan **respons** juga: header, pengalihan, pengaturan waktu, hubungan arus pendek untuk seluruh area |
| [`dependencies.py`](../dependencies/README.md) | Anda memerlukan parsing parameter atau memasukkan nilai (pengguna saat ini, sesi database) |
| `@UseGuard` pada handler | satu rute memerlukan pemeriksaan ekstra |
| `useMiddlewares` di [konfigurasi](../../../reference/config.md) | middleware ASGI untuk seluruh aplikasi (CORS, GZip, sesi) |

File middleware dijalankan **sebelum** dependensi: permintaan telah melewati setiap `middleware.py` direktorinya saat dependensi dimulai.

## Aturan

- File harus mendefinisikan `async def middleware(request, call_next)`. Jika tidak, Nexy berhenti saat startup dan memberi nama file tersebut.
- Ini adalah modul Python normal: impor apa yang Anda butuhkan. Itu dimuat sekali, ketika server dimulai.
- Ini tidak pernah menjadi rute: `/middleware` adalah 404.
- Pemeriksaan jalur dasar pada `request.scope["path"]`, tidak pernah pada `request.url.path` atau header `Host`: sejak CVE-2026-48710 objek URL boleh tidak sesuai dengan jalur yang diterima server. Lihat [Keamanan](../../../reference/security.md).

## Biaya

Sebuah proyek tanpa `middleware.py` tidak menghasilkan apa-apa: lapisan tersebut tidak diinstal. Dengan file, setiap middleware yang cocok menambahkan Starlette `BaseHTTPMiddleware`; jaga agar tetap kecil.

## Langkah selanjutnya

- [Warisan](../inheritance.md)
- [Ketergantungan](../dependencies/README.md)
- [Perangkat tengah dan keamanan](../../../guides/middleware-and-security.md)
