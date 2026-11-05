# WebSocket ہینڈلرز

ایک میں WebSocket کنکشن کو ہینڈل کریں۔ `.py` روٹ فائل `SOCKET` کی وضاحت کر کے۔

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## قواعد

- یو آر ایل فائل کا راستہ ہے، وہی قاعدہ جیسا کہ [روٹنگ](../../README.md)۔
- صرف `.py` روٹ فائلیں WebSocket ہینڈلرز کو `SOCKET` کے ذریعے رجسٹر کرتی ہیں۔
- یقینی بنائیں کہ آپ کی ریورس پراکسی آگے WebSocket اپ گریڈ کی درخواستیں ہیں۔

## اگلے اقدامات

- [API](../handlers/README.md): اسی فائلوں میں HTTP ہینڈلرز
- [تعینات](../../../deployment/README.md): پراکسی کنفیگریشن
- [ماڈیولر روٹنگ](../../modular/README.md): `SOCKET` ایک کنٹرولر پر
