# वेबसॉकेट हैंडलर

`SOCKET` को परिभाषित करके `.py` रूट फ़ाइल में वेबसॉकेट कनेक्शन को संभालें।

```python filename="src/routes/ws/chat.py"
from fastapi import WebSocket


async def SOCKET(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("hello")
    await websocket.close()
```

## नियम

- यूआरएल फ़ाइल पथ है, [रूटिंग](../../README.md) के समान नियम।
- केवल `.py` रूट फ़ाइलें `SOCKET` के माध्यम से वेबसॉकेट हैंडलर को पंजीकृत करती हैं।
- सुनिश्चित करें कि आपका रिवर्स प्रॉक्सी वेबसॉकेट अपग्रेड अनुरोधों को अग्रेषित करता है।

## अगले चरण

- [एपीआई](../handlers/README.md): समान फ़ाइलों में HTTP हैंडलर
- [तैनाती](../../../deployment/README.md): प्रॉक्सी कॉन्फ़िगरेशन
- [मॉड्यूलर रूटिंग](../../modular/README.md): `SOCKET` एक नियंत्रक पर