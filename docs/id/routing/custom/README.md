# Sertakan router FastAPI yang ada di Nexy

Untuk menyertakan router FastAPI yang ada di Nexy, setel `useRouter` ke `APIRouter` tersebut di kelas `NexyConfig` dari `nexyconfig.py`: rutenya disajikan apa adanya, di sebelah file `src/routes/`.

## Kapan menggunakan router khusus

- **Migrasi bertahap**: aplikasi FastAPI berpindah ke rute Nexy berdasarkan rute, dan sementara itu rute lamanya tetap menjawab.
- **Penggunaan kembali kode**: sebuah paket sudah mengekspos `APIRouter`, untuk otentikasi atau penagihan.
- **Backend yang Anda simpan**: API tetap biasa FastAPI, dan Nexy menambahkan halamannya.

## Atur `useRouter` di `nexyconfig.py`

Routernya adalah FastAPI `APIRouter` apa saja, ditulis seperti yang sudah Anda tulis:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` adalah bidang kelas `NexyConfig`, seperti setiap pengaturan proyek:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` lalu menjawab `GET /api/status` dan `GET /api/users/{id}`, dan `/docs` mencantumkannya.

> [!NOTE]
> `useRouter` di `nexyconfig.py` adalah sebuah pengaturan. `from nexy import useRouter` adalah hal lain: pengait yang digunakan halaman `.nexy` untuk membaca rute saat ini. Jangan mengimpornya untuk mengkonfigurasi router.

## Beberapa router

`useRouter` membutuhkan satu router. Kumpulkan beberapa di bawah satu orang tua dengan `include_router`:

```python filename="src/warisan/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Halaman dan rutekan file di sebelahnya

`src/routes/` masih dibaca ketika `useRouter` disetel: halaman `.nexy` atau jawaban file rute `.py` di sebelah rute yang disertakan.

```nexy filename="src/rute/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Dua batasan saat `useRouter` disetel:

- halaman tidak dibungkus oleh `layout.nexy`;
- `useCSR = True` ditolak: `nx dev` dan `nx build` jawaban `useCSR requires file-based routing`.

URL dijawab satu kali. Berikan awalan pada router yang disertakan, di sini `/api`, dan jauhkan file `src/routes/` dari jalur yang digunakannya.

## Seluruh aplikasi FastAPI

`useRouter` membutuhkan aplikasi `APIRouter`, bukan `FastAPI`. Rute aplikasi berada pada atribut `router`:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

Middleware, pengendali pengecualian, dan peristiwa startup milik aplikasi tetap berada di belakang: pindahkan ke `useMiddlewares` dan bidang lain di `nexyconfig.py`.

## Dependensi, autentikasi, dan database

Router berjalan dalam proses Nexy, jadi `Depends`, skema keamanan dan sesi database berfungsi seperti pada aplikasi asli:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Ujilah

```python filename="tes/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Langkah selanjutnya

- [Dari FastAPI ke Nexy](../../coming-from/fastapi.md): pindahkan rute ke file, satu per satu
- [Perutean berbasis file](../fbr/README.md)
- [Perutean modular](../modular/README.md): `useRouter = AppModule`
