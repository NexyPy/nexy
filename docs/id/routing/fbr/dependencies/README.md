# Ketergantungan dan penjaga

Bagikan autentikasi, sesi database, dan pengaturan lainnya di seluruh rute dengan dependensi FastAPI. Mereka bekerja pada dua tingkat, dan tingkat direktori diwarisi seperti tata letak.

| Level | Dimana | Berlaku untuk |
|---|---|---|
| Direktori | `dependencies.py` | setiap rute dalam direktori dan di bawahnya, termasuk halaman |
| Penangan | `Depends`, `@UseGuard`, `@Middleware` | satu penangan |

## Per direktori: `dependencies.py`

A `dependencies.py` mendeklarasikan `dependencies` daftar fungsi biasa. Nexy membungkus masing-masing di `Depends`.

```python filename="src/rute/admin/dependensi.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!CATATAN]
> daftar fungsinya sendiri. Objek `Depends(...)` dalam daftar diabaikan.

Setiap rute di bawah `src/routes/admin/` sekarang memerlukan header, penangan `.py`, dan halaman `.nexy`.

## Warisan

Ketergantungan dikumpulkan dari root rute hingga ke direktori rute, **terluar pertama**, persis seperti tata letak, dan penjaga handler dijalankan terakhir:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Untuk `GET /admin/users` urutannya adalah `root`, `admin`, `users`, fungsi `@UseGuard` dari handler, fungsi `@Middleware`-nya, lalu handlernya. Grup rute (`(group)/`) adalah direktori seperti direktori lainnya, jadi `dependencies.py`-nya ikut ambil bagian.

## Per pawang

Gunakan `Depends` di tanda tangan, seperti di aplikasi FastAPI mana pun:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Penjaga dan middleware pada handler

`@UseGuard` dan `@Middleware` melampirkan dependensi FastAPI ke handler tanpa mengubah tanda tangannya. Keduanya merupakan dependensi, bukan middleware ASGI:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Untuk middleware ASGI yang sebenarnya (CORS, GZip, sesi, milik Anda sendiri) gunakan opsi `useMiddlewares` dan `use*` di [Middleware dan keamanan](../../../guides/middleware-and-security.md).

## Gagal dalam ketergantungan

Ketergantungan menolak permintaan dengan menaikkan. `HTTPException` menjawab dengan status yang Anda naikkan, sebagai JSON untuk klien API (`Accept: application/json`) dan sebagai halaman kesalahan untuk browser. Lihat [Validasi dan kesalahan](../handlers/validation-and-errors.md).

## Langkah selanjutnya

- [Warisan](../inheritance.md)
- [Penanganan](../handlers/README.md)
- [Perangkat tengah dan keamanan](../../../guides/middleware-and-security.md)
