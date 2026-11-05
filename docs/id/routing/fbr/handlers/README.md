# Pengendali rute

File `.py` di bawah `src/routes/` adalah pengendali API. Jalur file adalah URL, dan setiap fungsi yang diberi nama metode HTTP menjadi titik akhir.

## Buat titik akhir

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

File ini menjawab `GET /api/items` dan `POST /api/items`.

Nama fungsi yang didukung: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` membuka WebSocket di jalur yang sama - lihat [WebSocket](../realtime/websocket.md).

## Kosakata HTTP

Impor apa yang dibutuhkan penangan dari `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Ini memperlihatkan kelas permintaan dan respons (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), sumber parameter (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` dan `status`. Penangan yang ditulis pada modul ini bergantung pada kontrak Nexy, bukan pada mesin yang melayaninya. Pydantic model menggambarkan tubuh dan respons seperti biasa.

## Parameter

| Sumber | Bagaimana sampainya |
|---|---|
| Segmen jalur `[id]` | argumen fungsi `id`, dikonversi ke anotasinya |
| String kueri | `page: int = 1` |
| Argumen model badan JSON | Pydantic |
| FastAPI primitif | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - tidak berubah |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Segmen jalurnya adalah `{id}`, jadi FastAPI memvalidasi `id: int`. Nilai yang bukan bilangan bulat menjawab `404`, karena rute dinamis menangkap URL apa pun dan URL yang tidak dapat dikonversi tidak ada. Lihat [Validasi dan kesalahan](validation-and-errors.md).

## Tanggapan

| Kembali | Tanggapan |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, apa pun `Response` | persis seperti yang dinyatakan |
| `None` | respons kosong - kembalikan `Response` ketika statusnya penting |

Untuk kode status kustom atau tipe konten, kembalikan objek respons:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Kesalahan

Ajukan FastAPI pengecualian untuk klien. Klien yang mengirim `Accept: application/json` menerima `{"detail": "..."}` dengan status yang Anda naikkan; browser menerima halaman kesalahan. `notfound.nexy` merender `404` dan `errors.nexy` merender `500`, masing-masing tercakup dalam direktorinya. Lihat [Validasi dan kesalahan](validation-and-errors.md) dan [Halaman kesalahan](../errors/README.md).

## OpenAPI

Setiap rute API muncul dalam skema yang dihasilkan, karena rute tersebut adalah rute biasa FastAPI. Skema disajikan di `/openapi.json` dan dirender oleh Scalar di `/docs`. Nonaktifkan keduanya dengan `useDocs = False` di `nexyconfig.py`.

## Langkah selanjutnya

- [Dependensi](../dependencies/README.md): autentikasi dan pengaturan bersama per penangan atau per direktori
- [Validasi dan kesalahan](validation-and-errors.md): `422`, `404` dan kesalahan JSON
- [Perutean](../../README.md): jalur file ke URL
- [Aksi](../../../guides/actions.md): titik akhir dengan jalur yang dihasilkan
- [Konfigurasi](../../../reference/config.md): middleware, CORS, sesi
