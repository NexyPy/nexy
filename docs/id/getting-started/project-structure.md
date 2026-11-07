# Struktur proyek

Setiap file dalam proyek Nexy memiliki satu pekerjaan, dan kemana file tersebut pergi bergantung pada router: `src/routes/` untuk perutean berbasis file, `src/apps/` untuk router modular.

## Tingkat atas

<!-- router:fbr -->
```text
my-app/
├─ src/
│  ├─ routes/            every file is a route
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Untuk memilih folder, tanyakan file apa itu:

- **Sesuatu yang dapat dibuka oleh browser** - rute: `src/routes/`.
- **Sepotong yang digunakan oleh beberapa rute** - komponen atau modul: `src/components/`, `src/`.
- **File disajikan apa adanya** - `public/`.
- **Dihasilkan** - `__nexy__/`; jangan pernah mengeditnya.

> [!WARNING]
> `src/routes/` dipindai: pembantu yang ditempatkan di sana menjadi rute. Letakkan helper yang bukan merupakan rute di luar `src/routes/`, atau awali namanya dengan `_`.
<!-- /router -->

<!-- router:modular -->
```text
my-app/
├─ src/
│  ├─ apps/              controllers, modules and their views
│  │  ├─ app_module.py   the root module, given to useRouter
│  │  ├─ app_controller.py
│  │  ├─ app_view.nexy   a view a controller returns
│  │  ├─ layout.nexy     the frame the controllers pass their view to
│  │  └─ users/          one folder per feature: controller, module, service, model
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = AppModule
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Untuk memilih folder, tanyakan file apa itu:

- **URL** - metode pengontrol di `src/apps/`, didaftarkan oleh modulnya.
- **Halaman** - tampilan `.nexy` di sebelah pengontrolnya, dikembalikan dengan `useViews`.
- **Sepotong yang digunakan oleh beberapa tampilan** - `src/components/`.
- **File disajikan apa adanya** - `public/`.
- **Dihasilkan** - `__nexy__/`; jangan pernah mengeditnya.
<!-- /router -->

<!-- router:custom -->
```text
my-app/
├─ src/
│  ├─ legacy/            the FastAPI router you include
│  │  └─ api.py          router = APIRouter(prefix="/api")
│  ├─ routes/            pages and route files, served next to it
│  │  └─ index.nexy      → /
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration: useRouter = router
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Untuk memilih folder, tanyakan file apa itu:

- **Rute aplikasi yang disertakan** - yang sudah ada, di sini `src/legacy/`.
- **Halaman atau rute baru** - `src/routes/`, di sebelah router yang disertakan.
- **File disajikan apa adanya** - `public/`.
- **Dihasilkan** - `__nexy__/`; jangan pernah mengeditnya.
<!-- /router -->

<!-- router:fbr,custom -->
## `src/routes/`

Setiap file menjadi rute, kecuali nama yang dicadangkan di bawah. Jalur file dikurangi ekstensinya adalah URL - lihat [perutean berbasis file](../routing/fbr/README.md).

| Mengajukan | Peran |
|---|---|
| `layout.nexy` | membungkus halaman saudara dan anak |
| `errors.nexy` | 500 halaman untuk direktori |
| `notfound.nexy` | 404 halaman untuk direktori |
| `dependencies.py` | dependensi FastAPI bersama untuk direktori |
| `__init__.py` | Python penanda paket |
| `loading.nexy` | dicadangkan - dikecualikan dari rute, tetapi belum memiliki efek runtime |

Setiap nama halaman juga ada per kerangka. Dengan `react()` dikonfigurasi, `layout.jsx` dan `layout.tsx` dicadangkan persis seperti `layout.nexy`. Daftar dibuat di `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` dan `errors.nexy` hanya diinstal ketika salinan ada di root rute. Salinan dalam subdirektori kemudian menyaring halaman untuk awalan tersebut.
<!-- /router -->

<!-- router:modular -->
## `src/apps/`

Pengontrol menjawab URL, modul mengelompokkan pengontrol dan penyedia, dan modul root dipasang dengan `useRouter` di `nexyconfig.py`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller()
class AppController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/app_view.nexy")})
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
    useAliases = {"@": "src"}  # the views import @/components/...
```

Tidak ada file di `src/apps/` yang merupakan rute berdasarkan namanya: hanya pengontrol yang didaftarkan oleh modul yang menjawab. Lihat [perutean modular](../routing/modular/README.md).
<!-- /router -->

## `public/`

File di sini disajikan dari root situs: `/favicon.ico`, `/robots.txt`, gambar, font.

## `__nexy__/`

Dihasilkan oleh `nx build` (dan oleh `nx dev` untuk bagian-bagian yang dibutuhkannya). Ini berisi:

- file `.nexy` yang dikompilasi, sebagai paket Python (`__nexy__/src/...`);
- titik masuk klien yang dihasilkan (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` setelah Vite build - aset, manifes, HTML yang telah dirender sebelumnya;
- `build-cache.json`.

Perlakukan seluruh direktori sebagai sekali pakai: hapus, bangun kembali. Mengeditnya dengan tangan akan menghilangkan perubahan pada build berikutnya. Tambahkan ke `.gitignore`.

## Langkah selanjutnya

<!-- router:fbr -->
- [Perutean berbasis file](../routing/fbr/README.md): bagaimana jalur menjadi URL
<!-- /router -->
<!-- router:modular -->
- [Perutean modular](../routing/modular/README.md): pengontrol, modul, dan penyedia
<!-- /router -->
<!-- router:custom -->
- [Perutean khusus](../routing/custom/README.md): menyertakan router FastAPI yang ada
<!-- /router -->
- [Konfigurasi](../reference/config.md): setiap opsi proyek
- [Frontend](../guides/frontend.md): Vite, gaya dan pembuatan klien
