# Nexy dan NestJS

Router modular terinspirasi oleh NestJS: pengontrol, modul, dan injeksi konstruktor. Ini adalah lapisan tipis di atas FastAPI, sehingga tidak mencoba mereproduksi seluruh NestJS. Halaman ini mencantumkan kedua sisi.

## Apa yang cocok

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` dengan empat atribut kelas yang sama |
| `@Injectable()` | `@Injectable()` |
| Injeksi konstruktor | `__init__` parameter diselesaikan dari anotasi tipe |
| Cakupan singleton, permintaan, dan sementara | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (ketergantungan FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Keangkuhan) | `@UseRoute`, `@UseResponse` (OpenAPI, disajikan di `/docs`) |
| WebSocket gerbang | `async def SOCKET(...)` pada pengontrol |
| Validasi DTO (`class-validator`) | Pydantic model, asli FastAPI |
| Deteksi ketergantungan melingkar | `RecursionError` memberi nama kelas |

Pengontrol yang sama dan layanan yang disuntikkan, NestJS terlebih dahulu:

```ts filename="pengguna.controller.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## Apa yang berbeda

- Penangan adalah metode yang diberi nama berdasarkan kata kerja HTTP (`get`, `post`...), satu per pengontrol.
- Penjaga dan dekorator middleware adalah FastAPI `Depends`, bukan kelas dengan `canActivate`.
- Parameter (`@Body`, `@Param`, `@Query`) adalah parameter FastAPI: anotasi tipe, `Query`, `Path`, `Body`.
- Pipa adalah Pydantic validasi dan FastAPI dependensi.

`@Query()`, DTO dan kelas penjaga menjadi anotasi, model Pydantic dan fungsi:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## Apa yang hilang

| NestJS fitur | Status di Nexy |
|---|---|
| Penyedia khusus (`useValue`, `useFactory`, `useClass`, token string) | tidak tersedia: hanya `@Injectable()` kelas |
| Menyuntikkan berdasarkan antarmuka atau kelas abstrak | tidak tersedia |
| Enkapsulasi modul | tidak diterapkan: container mencakup seluruh proses, `exports` hanya mengontrol resolusi yang diinginkan |
| Modul dinamis dan global (`forRoot`, `@Global`) | tidak tersedia |
| Kait siklus hidup (`onModuleInit`, `onApplicationShutdown`) | tidak tersedia |
| Pencegat | gunakan middleware ASGI (`useMiddlewares`) atau dependensi |
| Filter pengecualian | gunakan FastAPI penangan pengecualian |
| Modul pengujian dengan penggantian penyedia | tidak ada API publik; gunakan FastAPI `dependency_overrides` dan `TestClient` |
| Modul konfigurasi, penjadwalan, antrian, CQRS, layanan mikro, caching | bukan bagian dari Nexy; menggunakan ekosistem Python. |

Sebagai pengganti penyedia `useFactory`, fungsi biasa di belakang `Depends`, yang ditimpa oleh pengujian dengan `dependency_overrides`:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## Kapan harus mengambilnya

Pilih router modular bila Anda menginginkan struktur berbasis kelas dengan injeksi untuk API yang lebih besar. Pilih router berbasis file ketika struktur URL adalah prinsip pengorganisasiannya. Keduanya di-scaffold oleh `nx new`, dijalankan pada aplikasi FastAPI yang sama, dan dapat hidup berdampingan.

> [!NOTE]
> item yang hilang di atas adalah kesenjangan yang jujur. Jika Anda memerlukan penyedia `useFactory` atau penyedia yang dapat diganti dalam pengujian hari ini, pertahankan logika dalam fungsi biasa dan FastAPI `Depends`, yang menyusun dan mengganti secara alami.

## Langkah selanjutnya

- [Injeksi ketergantungan](dependency-injection.md)
- [Penjaga dan metadata](guards-and-metadata.md)
- [Pengujian](../../guides/testing.md)
