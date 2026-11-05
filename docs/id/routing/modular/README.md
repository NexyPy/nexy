# Perutean modular

Perutean modular menggunakan kelas dengan dekorator alih-alih file di bawah `src/routes/`: pengontrol menangani permintaan, modul mengelompokkannya, dan penyedia dimasukkan. Pasang `APIRouter` yang dihasilkan dengan `useRouter` di `nexyconfig.py`.

**Sebelum Anda memulai:** proyek Nexy dan satu halaman kerja. Router modular menggantikan router berbasis file, jadi bacalah [Routing](../README.md) terlebih dahulu jika Anda belum memilih router.

| Halaman | Cakupannya |
|---|---|
| Halaman ini | Pasang modul, tulis pengontrol, grup pengontrol |
| [Injeksi ketergantungan](dependency-injection.md) | `@Injectable`, cakupan, wadah |
| [Penjaga dan metadata](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy dan NestJS](vs-nestjs.md) | Apa yang cocok dengan NestJS dan apa yang tidak |

## Siapkan perute

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!CATATAN]
> perutean berbasis file tetap berfungsi. Jika `src/routes/` ada, itu dipindai bahkan ketika `useRouter` diatur.

## Tulis pengontrol

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Metode dicocokkan berdasarkan nama, tanpa membedakan huruf besar/kecil: `get`, `post`, `put`, `patch`, `delete`, `options`, `head`, `trace`.

Sebuah pengontrol mendeklarasikan satu penangan per metode HTTP; duplikat meningkat saat startup. Tambahkan awalan dengan `@Controller(prefix="/users")` - setiap penangan dipasang di `prefix/`. `async def SOCKET(...)` pada pengontrol mendaftarkan WebSocket di jalur yang sama.

## Pengontrol grup dalam sebuah modul

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` mengembalikan `APIRouter`. `controllers` diperlukan; `providers`, `imports` dan `exports` bersifat opsional. Modul yang diimpor dipasang sebagai sub-router, dan penyedia yang diekspor diselesaikan saat startup.

## Tampilan dari pengontrol

Pengontrol dapat mengembalikan halaman. `useViews` menampilkan tampilan `.nexy`; sarangkan satu di dalam yang lain untuk membungkusnya dalam tata letak:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

Lihat [Tata Letak](../fbr/layouts/README.md).

## Contoh

Lihat `examples/Modular/api/minimal/`.

## Langkah selanjutnya

- [Injeksi ketergantungan](dependency-injection.md): layanan dan cakupan
- [Penjaga dan metadata](guards-and-metadata.md): melindungi dan mendokumentasikan rute
- [Routing](../README.md): router berbasis file
- [Config](../../reference/config.md): setiap opsi, termasuk `useRouter`
