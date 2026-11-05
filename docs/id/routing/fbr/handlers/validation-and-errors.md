# Validasi dan kesalahan

Bagaimana pengendali API melaporkan permintaan yang buruk.

## Validasi

Parameter handler divalidasi oleh FastAPI berdasarkan anotasinya.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Masalah | Status | Badan |
|---|---|---|
| kolom kueri, header, cookie, atau isi tidak ada atau tidak valid | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| segmen **jalur** tidak valid (`/api/users/abc` untuk `id: int`) | `404` | halaman tidak ditemukan, atau JSON untuk `Accept: application/json` |

Segmen jalur yang tidak dapat dikonversi adalah `404` dan bukan `422`: rute dinamis menangkap URL apa pun, dan tidak ada URL yang tidak dapat dikonversi.

Isi `422` adalah bentuk standar FastAPI, sehingga klien yang sudah ada dan SDK yang dihasilkan tetap berfungsi.

## Meningkatkan kesalahan

```python filename="src/routes/api/item/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Klien mengirimkan | Respons |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` dengan status `404` |
| `Accept: text/html` | [halaman kesalahan](../errors/README.md) |
| `Accept: */*` | halaman kesalahan |

Setel `Accept: application/json` di klien API. Browser terus mendapatkan halaman.

## Pengecualian yang tidak tertangani

Pengecualian bahwa pengendali Anda tidak menangkap jawaban `500`, dengan pilihan HTML atau JSON yang sama.

## Respons khusus

Mengembalikan objek respons saat Anda mengontrol isi:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Langkah selanjutnya

- [Rute API](README.md)
- [Halaman kesalahan](../errors/README.md)
- [Pengujian](../../../guides/testing.md)
