# सत्यापन और त्रुटियाँ

कैसे एक एपीआई हैंडलर खराब अनुरोध की रिपोर्ट करता है।

## मान्यता

हैंडलर पैरामीटर्स को उनके एनोटेशन के विरुद्ध FastAPI द्वारा मान्य किया जाता है।

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| समस्या | स्थिति | शरीर |
|---|---|---|
| गुम या अमान्य क्वेरी, हेडर, कुकी या बॉडी फ़ील्ड | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| अमान्य **पथ** खंड (`/api/users/abc` के लिए `id: int`) | `404` | नहीं मिला पृष्ठ, या `Accept: application/json` के लिए JSON |

एक पथ खंड जिसे परिवर्तित नहीं किया जा सकता वह `422` के बजाय `404` है: एक गतिशील मार्ग किसी भी यूआरएल को कैप्चर करता है, और एक यूआरएल जिसे परिवर्तित नहीं किया जा सकता वह मौजूद नहीं है।

`422` बॉडी FastAPI का मानक आकार है, इसलिए मौजूदा क्लाइंट और जेनरेट किए गए एसडीके काम करते रहते हैं।

## त्रुटियाँ उठाना

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| ग्राहक | प्रतिक्रिया भेजता है |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` स्थिति के साथ `404` |
| `Accept: text/html` | [त्रुटि पृष्ठ](../errors/README.md) |
| `Accept: */*` | त्रुटि पृष्ठ |

एपीआई क्लाइंट में `Accept: application/json` सेट करें। ब्राउज़रों को पेज मिलते रहते हैं.

## हैंडल न किए गए अपवाद

एक अपवाद यह है कि आपका हैंडलर समान HTML या JSON विकल्प के साथ उत्तर `500` नहीं पकड़ पाता है।

## कस्टम प्रतिक्रियाएँ

जब आप शरीर को नियंत्रित करते हैं तो एक प्रतिक्रिया वस्तु लौटाएँ:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## अगले चरण

- [एपीआई मार्ग](README.md)
- [त्रुटि पृष्ठ](../errors/README.md)
- [परीक्षण](../../../guides/testing.md)
