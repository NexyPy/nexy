# मार्ग संचालक

`src/routes/` के अंतर्गत एक `.py` फ़ाइल एक एपीआई हैंडलर है। फ़ाइल पथ URL है, और HTTP विधि के नाम पर प्रत्येक फ़ंक्शन एक समापन बिंदु बन जाता है।

## एक समापन बिंदु बनाएँ

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

यह फ़ाइल `GET /api/items` और `POST /api/items` का उत्तर देती है।

समर्थित फ़ंक्शन नाम: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`। `SOCKET` उसी पथ पर एक WebSocket खोलता है - [WebSocket](../realtime/websocket.md) देखें।

## HTTP शब्दावली

एक हैंडलर को जो चाहिए वह आयात करें `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

यह अनुरोध और प्रतिक्रिया वर्गों (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), पैरामीटर स्रोतों (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends` को उजागर करता है। `BackgroundTasks`, `HTTPException` और `status`। इस मॉड्यूल के विरुद्ध लिखे गए हैंडलर नेक्सी के अनुबंध पर निर्भर करते हैं, न कि उस इंजन पर जो उन्हें सेवा प्रदान करता है। Pydantic मॉडल हमेशा की तरह शरीर और प्रतिक्रियाओं का वर्णन करते हैं।

## पैरामीटर्स

| स्रोत | यह कैसे आता है |
|---|---|
| पथ खंड `[id]` | फ़ंक्शन तर्क `id`, इसके एनोटेशन में परिवर्तित |
| क्वेरी स्ट्रिंग | `page: int = 1` |
| JSON बॉडी | Pydantic मॉडल तर्क |
| FastAPI आदिम | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - अपरिवर्तित |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

पथ खंड `{id}` है, इसलिए FastAPI `id: int` को मान्य करता है। एक मान जो पूर्णांक नहीं है, उत्तर देता है `404`, क्योंकि एक गतिशील मार्ग किसी भी यूआरएल को कैप्चर करता है और एक यूआरएल जिसे परिवर्तित नहीं किया जा सकता वह मौजूद नहीं है। [सत्यापन और त्रुटियाँ](validation-and-errors.md) देखें।

## प्रतिक्रियाएँ

| वापसी | प्रतिक्रिया |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, कोई भी `Response` | बिल्कुल वैसा ही जैसा घोषित किया गया है |
| `None` | खाली प्रतिक्रिया - जब स्थिति मायने रखती है तो इसके बजाय `Response` लौटाएं |

कस्टम स्थिति कोड या सामग्री प्रकार के लिए, एक प्रतिक्रिया ऑब्जेक्ट लौटाएँ:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## त्रुटियाँ

ग्राहकों के लिए FastAPI अपवाद बढ़ाएँ। एक ग्राहक जो `Accept: application/json` भेजता है उसे आपके द्वारा बढ़ाए गए स्टेटस के साथ `{"detail": "..."}` प्राप्त होता है; ब्राउज़र को त्रुटि पृष्ठ प्राप्त होता है. `notfound.nexy` प्रस्तुत करता है `404` और `errors.nexy` प्रस्तुत करता है `500`, प्रत्येक अपनी निर्देशिका के दायरे में आता है। [सत्यापन और त्रुटियां](validation-and-errors.md) और [त्रुटि पृष्ठ](../errors/README.md) देखें।

## OpenAPI

प्रत्येक एपीआई मार्ग जेनरेटेड स्कीमा में दिखाई देता है, क्योंकि मार्ग सादे FastAPI मार्ग हैं। स्कीमा `/openapi.json` पर परोसा जाता है और स्केलर द्वारा `/docs` पर प्रस्तुत किया जाता है। `useDocs = False` में `nexyconfig.py` दोनों को अक्षम करें।

## अगले चरण

- [निर्भरताएं](../dependencies/README.md): प्रति हैंडलर या प्रति निर्देशिका साझा प्रमाणीकरण और सेटअप
- [सत्यापन और त्रुटियां](validation-and-errors.md): `422`, `404` और JSON त्रुटियां
- [रूटिंग](../../README.md): यूआरएल के लिए फ़ाइल पथ
- [क्रियाएँ](../../../guides/actions.md): उत्पन्न पथों के साथ समापन बिंदु
- [कॉन्फ़िगर](../../../reference/config.md): मिडलवेयर, सीओआरएस, सत्र
