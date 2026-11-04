# معالجات WebSocket

التعامل مع اتصالات WebSocket في ملف توجيه `.py` عن طريق تحديد `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## القواعد

- عنوان URL هو مسار الملف، وهو نفس قاعدة [routing](../../README.md).
- فقط `.py` تسجل ملفات المسار معالجات WebSocket عبر `SOCKET`.
- تأكد من قيام الوكيل العكسي بإعادة توجيه طلبات ترقية WebSocket.

## الخطوات التالية

- [API](../handlers/README.md): معالجات HTTP في نفس الملفات
- [نشر](../../../deployment/README.md): تكوين الوكيل
- [التوجيه المعياري](../../modular/README.md): `SOCKET` على وحدة التحكم