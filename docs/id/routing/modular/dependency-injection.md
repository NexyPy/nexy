# Injeksi ketergantungan

Nexy menyelesaikan ketergantungan konstruktor untuk pengontrol dan layanan. Sebuah kelas ikut serta dengan `@Injectable()`.

## Suntikkan layanan

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller(prefix="/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

Daftarkan pengontrol dalam sebuah modul. Mencantumkan layanan di `providers` juga menyelesaikannya dengan mudah saat startup:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## Cara kerja resolusi

- Setiap parameter `__init__` diselesaikan dari **jenis anotasinya**. Anotasi harus berupa kelas `@Injectable()`, atau parameter harus memiliki nilai default; jika tidak, resolusi akan muncul `ValueError`.
- Pengontrol dipakai dengan `Container.resolve()` saat startup.
- Siklus ketergantungan memunculkan `RecursionError` penamaan kelas.
- Layanan dapat memasukkan layanan lain, hingga kedalaman apa pun.

## Lingkup

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Ruang Lingkup | Seumur Hidup |
|---|---|
| `Scope.SINGLETON` (default) | satu contoh untuk keseluruhan proses |
| `Scope.REQUEST` | satu contoh per konteks permintaan |
| `Scope.TRANSIENT` | contoh baru pada setiap resolusi |

## Wadahnya

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Membangun kelas `@Injectable()` sendiri akan memunculkan `TypeError`: container memiliki siklus hidupnya. Gunakan `Container.resolve(...)` atau terima kelas melalui konstruktor lain.

`Container.clear_request_scope()` menghapus instance permintaan saat ini.

## Parameter rute

FastAPI `Depends` berfungsi seperti biasa untuk parameter pengendali, di samping injeksi konstruktor:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Batasan

Wadah ini mencakup seluruh proses. Penyedia tidak diisolasi per modul, `exports` hanya memutuskan penyedia mana yang diselesaikan dengan penuh semangat oleh modul pengimpor, dan tidak ada API publik untuk menukar penyedia dalam pengujian. Lihat [Nexy dan NestJS](vs-nestjs.md) untuk perbandingan selengkapnya.

## Langkah selanjutnya

- [Penjaga dan metadata](guards-and-metadata.md)
- [Pengujian](../../guides/testing.md)
