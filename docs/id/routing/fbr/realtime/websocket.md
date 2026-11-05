# WebSocket penangan

Tangani koneksi WebSocket dalam file rute `.py` dengan mendefinisikan `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## Aturan

- URL adalah jalur file, aturannya sama seperti [routing](../../README.md).
- Hanya file rute `.py` yang mendaftarkan penangan WebSocket melalui `SOCKET`.
- Pastikan proksi terbalik Anda meneruskan WebSocket permintaan peningkatan.

## Langkah selanjutnya

- [API](../handlers/README.md): Penangan HTTP dalam file yang sama
- [Deploy](../../../deployment/README.md): konfigurasi proksi
- [Perutean modular](../../modular/README.md): `SOCKET` pada pengontrol
