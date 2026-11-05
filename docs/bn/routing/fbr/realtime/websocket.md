# WebSocket হ্যান্ডলার

`SOCKET` সংজ্ঞায়িত করে একটি `.py` রুট ফাইলে WebSocket সংযোগগুলি পরিচালনা করুন।

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## নিয়ম

- URL হল ফাইল পাথ, একই নিয়ম [রাউটিং](../../README.md)।
- শুধুমাত্র `.py` রুট ফাইলগুলি WebSocket হ্যান্ডলারদের `SOCKET` মাধ্যমে নিবন্ধন করে।
- নিশ্চিত করুন যে আপনার বিপরীত প্রক্সি ফরোয়ার্ড WebSocket আপগ্রেড অনুরোধ।

## পরবর্তী পদক্ষেপ

- [API](../handlers/README.md): একই ফাইলে HTTP হ্যান্ডলার
- [মোতায়েন](../../../deployment/README.md): প্রক্সি কনফিগারেশন
- [মডুলার রাউটিং](../../modular/README.md): `SOCKET` একটি কন্ট্রোলারে
