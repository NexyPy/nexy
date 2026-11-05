# Resep

Tiga hal yang dibutuhkan hampir setiap aplikasi, yaitu file lengkap yang dapat Anda salin. Setiap blok kode di bawah ini dengan `filename` ditulis ke dalam proyek baru dan dijalankan oleh rangkaian pengujian, jadi apa yang Anda baca itulah yang dijalankan.

Mereka menggunakan penangan API biasa; fungsi yang sama berfungsi di belakang halaman dalam [mode](../routing/fbr/modes.md).

## Masuk dengan sesi

Pengunjung memposting nama dan kata sandi, server mengingatnya dalam cookie yang ditandatangani, dan semua yang ada di bawah `/api/account` tertutup untuk orang lain.

Aktifkan sesi. Mereka membutuhkan `itsdangerous` (`uv add itsdangerous`):

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Masuk dan keluar:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

Jaga seluruh folder dengan satu [`dependencies.py`](../routing/fbr/dependencies/README.md):

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!CATATAN]
> jauhkan kata sandi asli dari sumbernya. Simpan hash (`argon2`, `bcrypt`) dan baca kunci rahasia dari lingkungan. Cookie sesi ditandatangani, tidak dienkripsi.

## API JSON dengan buat, baca, dan hapus

Penyimpanan dalam modul, rute pengumpulan, dan rute item. Ganti kamus dengan [a database](databases.md) ketika data harus bertahan jika dimulai ulang.

```python filename="src/catatan.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

Isi yang tidak cocok dengan `NewNote` ditolak dengan `422` sebelum kode Anda dijalankan, dan anotasi pengembalian menjadi respons yang terdokumentasi. Lihat [validasi dan kesalahan](../routing/fbr/handlers/validation-and-errors.md).

## Terima berkas

Upload membutuhkan `python-multipart` (`uv add python-multipart`). Periksa sendiri ukurannya, dan jangan pernah menggunakan nama file klien sebagai jalur:

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` menghapus folder apa pun yang diberi nama oleh klien, misalnya `../../etc/passwd`. Simpan byte dengan nama yang Anda hasilkan, bukan dengan nama ini.

## Langkah selanjutnya

- [Actions](actions.md): fungsi server yang diketik untuk formulir dan tombol
- [Middleware dan keamanan](middleware-and-security.md): CORS, host, sesi
- [Testing](testing.md): uji penangan Anda sendiri dengan cara yang sama
