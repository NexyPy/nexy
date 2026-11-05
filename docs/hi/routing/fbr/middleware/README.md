# मिडलवेयर फ़ाइलें

रूट निर्देशिका में एक `middleware.py` उस निर्देशिका द्वारा संभाले गए अनुरोधों को लपेटता है। लेआउट और `dependencies.py` की तरह, फ़ाइलें रूट से नीचे, सबसे पहले सबसे बाहरी रूट से स्टैक होती हैं।

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

फ़ंक्शन `async def middleware(request, call_next)` है: FastAPI के `@app.middleware("http")` का हस्ताक्षर। मार्ग पर आगे बढ़ने के लिए `await call_next(request)` पर कॉल करें, या वहां रुकने के लिए प्रतिक्रिया दें। कॉल के बाद कोड रास्ते में चलता है और प्रतिक्रिया बदल सकता है।

## यह क्या लपेटता है

एक मिडलवेयर उन **मार्गों पर लागू होता है जिनकी फ़ाइल इसकी निर्देशिका में है** या नीचे, पेज और एपीआई हैंडलर समान रूप से, रूट समूह शामिल हैं:

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

`/admin/users` के अनुरोध के लिए आदेश है `root`, `admin`, `users`, फिर मार्ग। किसी समूह का अपना कोई यूआरएल नहीं होता है, इसलिए इसका मिलान उस रूट के माध्यम से किया जाता है जो अनुरोध को पूरा करता है, यूआरएल के माध्यम से नहीं।

एक यूआरएल जो बिना किसी रूट से मेल खाता है (एक 404) केवल उन निर्देशिकाओं के मिडलवेयर को प्राप्त करता है जो समूह नहीं हैं, यूआरएल उपसर्ग द्वारा चयनित होते हैं। `[slug]` एक खंड से मेल खाता है और `[...rest]` शेष से मेल खाता है।

## यह क्या नहीं लपेटता

- फ्रेमवर्क और एसेट यूआरएल: `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` और `/@...` (Vite)।
- WebSocket हैंडलर और सर्वर जीवनकाल: केवल HTTP अनुरोध।
- `_` या `.` से शुरू होने वाली निर्देशिकाओं में फ़ाइलें।

## मिडलवेयर, निर्भरता या गार्ड

| | का उपयोग करें जब |
|---|---|
| `middleware.py` | आपको **प्रतिक्रिया** की भी आवश्यकता है: पूरे क्षेत्र के लिए हेडर, रीडायरेक्ट, टाइमिंग, शॉर्ट-सर्किटिंग |
| [`dependencies.py`](../dependencies/README.md) | आपको पार्स किए गए पैरामीटर की आवश्यकता है या एक मान इंजेक्ट करने की आवश्यकता है (वर्तमान उपयोगकर्ता, डेटाबेस सत्र) |
| `@UseGuard` एक हैंडलर पर | एक मार्ग को अतिरिक्त जांच की आवश्यकता है |
| `useMiddlewares` [कॉन्फ़िगरेशन](../../../reference/config.md) में | पूरे एप्लिकेशन के लिए एक एएसजीआई मिडलवेयर (सीओआरएस, जीज़िप, सत्र) |

मिडलवेयर फ़ाइलें चलती हैं **before** निर्भरताएँ: निर्भरताएँ शुरू होने पर अनुरोध अपनी प्रत्येक `middleware.py` निर्देशिका को पार कर चुका होता है।

## नियम

- फ़ाइल को `async def middleware(request, call_next)` परिभाषित करना होगा। अन्यथा नेक्सी स्टार्टअप पर रुक जाती है और फ़ाइल को नाम देती है।
- यह एक सामान्य Python मॉड्यूल है: आपको जो चाहिए उसे आयात करें। सर्वर प्रारंभ होने पर इसे एक बार लोड किया जाता है।
- यह कभी भी एक मार्ग नहीं है: `/middleware` एक 404 है।
- बेस पथ की जाँच `request.scope["path"]` पर होती है, कभी भी `request.url.path` या `Host` हेडर पर नहीं: CVE-2026-48710 के बाद से यूआरएल ऑब्जेक्ट सर्वर द्वारा प्राप्त पथ से असहमत हो सकता है। [सुरक्षा](../../../reference/security.md) देखें।

## लागत

बिना किसी `middleware.py` के एक प्रोजेक्ट कुछ भी भुगतान नहीं करता है: परत स्थापित नहीं होती है। फ़ाइलों के साथ, प्रत्येक मिलान करने वाला मिडलवेयर एक Starlette `BaseHTTPMiddleware` जोड़ता है; उन्हें छोटा रखें.

## अगले चरण

- [विरासत](../inheritance.md)
- [निर्भरताएं](../dependencies/README.md)
- [मिडिलवेयर और सुरक्षा](../../../guides/middleware-and-security.md)
