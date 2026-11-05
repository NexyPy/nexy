# WebSocket المعالجين

تعامل مع اتصالات WebSocket في ملف مسار `.py` عن طريق تعريف `SOCKET`.

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## القواعد

- عنوان URL هو مسار الملف، وهو نفس قاعدة [التوجيه](../../README.md).
- فقط `.py` تسجل ملفات المسار معالجات WebSocket عبر `SOCKET`.
- تأكد من أن الوكيل العكسي الخاص بك يقوم بإعادة توجيه WebSocket طلبات الترقية.

## الخطوات التالية

- [API](../handlers/README.md): معالجات HTTP في نفس الملفات
- [نشر](../../../deployment/README.md): تكوين الوكيل
- [التوجيه المعياري](../../modular/README.md): `SOCKET` على وحدة التحكم
