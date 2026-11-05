# Penjaga dan metadata

Dekorator yang melindungi rute dan mendeskripsikannya dalam skema OpenAPI.

## Penjaga

`@UseGuard(*guards)` bekerja pada pengontrol (setiap metode) atau pada satu metode. Setiap penjaga ditambahkan sebagai FastAPI `Depends`, sehingga ia mendeklarasikan parameter yang diperlukan dan dimunculkan untuk menolak panggilan:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## Dekorator middleware

`@Middleware(*middlewares)` berperilaku dengan cara yang sama: ini adalah dependensi FastAPI, bukan middleware ASGI. Untuk middleware ASGI yang sebenarnya, gunakan `useMiddlewares` di [Config](../../reference/config.md) atau [Middleware dan keamanan](../../guides/middleware-and-security.md).

## Metadata rute

`@UseRoute(...)` menyetel metadata OpenAPI. Itu tidak mengubah jalur.

| Argumen | Arti |
|---|---|
| `name` | nama rute |
| `tags` | OpenAPI tag |
| `summary`, `description` | teks dalam referensi API |
| `deprecated` | tandai operasi tidak digunakan lagi |
| `include_in_schema` | menyembunyikan rute dari skema |
| `operation_id` | id operasi eksplisit |
| `openapi_extra` | kolom tambahan OpenAPI |

## Tanggapan

`@UseResponse(...)` mengatur `status_code`, `response_class`, `response_model`, `responses` dan opsi serialisasi.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

Referensi API yang dihasilkan disajikan di `/docs` kecuali `useDocs = False`.

## Langkah selanjutnya

- [Injeksi ketergantungan](dependency-injection.md)
- [Rute API](../fbr/handlers/README.md): opsi yang sama untuk penangan berbasis file
