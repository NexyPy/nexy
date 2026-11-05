# त्रुटि पृष्ठ

एक अनुरोध जो विफल हो जाता है उसे अभी भी आपकी साइट के बाकी हिस्सों की तरह उत्तर देना चाहिए: एक विज़िटर के लिए आपके अपने शब्दों में एक पृष्ठ, एक एपीआई क्लाइंट के लिए JSON के समान विफलता। नेक्सी दोनों का उत्तर देती है, और एक फ़ाइल प्रत्येक उत्तर को प्रतिस्थापित कर देती है।

यह पृष्ठ मानचित्र है: कौन सी फ़ाइल किस स्थिति का उत्तर देती है, और अपना पहला कैसे बनाएं। किसी फ़ोल्डर के पेजों को [उनका अपना पेज](folder-pages.md) मिलता है।

## एक असफलता, दो उत्तर

```diagram filename="जो असफल अनुरोध का उत्तर देता है"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## आपका पहला पेज

`src/routes/notfound.nexy` बनाएं और लिखें कि एक आगंतुक को क्या पढ़ना चाहिए:

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

सहेजें, और एक यूआरएल मांगें जो कुछ भी काम नहीं करता:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

रूट रूट पर फ़ाइल पूरे प्रोजेक्ट का उत्तर देती है; किसी फ़ोल्डर में एक प्रतिलिपि केवल उस फ़ोल्डर का उत्तर देती है और [बाकी को वैसे ही रखती है](folder-pages.md)। बिना किसी फ़ाइल के, नेक्सी अपने अंतर्निर्मित स्टाइल पेज पर कार्य करता है।

## कौन सी फ़ाइल उत्तर देती है

| फ़ाइल | उत्तर |
|---|---|
| `notfound.nexy` | `404` इसकी निर्देशिका के लिए |
| `errors.nexy` | `500` इसकी निर्देशिका के लिए |
| `forbidden.nexy` | `403` इसकी निर्देशिका के लिए |
| `unauthorized.nexy` | `401` इसकी निर्देशिका के लिए |
| `loading.nexy` | आरक्षित; अभी तक कोई रनटाइम प्रभाव नहीं |

| स्थिति | उत्तर |
|---|---|
| कोई मार्ग मेल नहीं खाता | `404` |
| एक गतिशील खंड को उसके एनोटेशन में परिवर्तित नहीं किया जा सकता है | `404` |
| किसी पेज या एपीआई हैंडलर में एक हैंडल न किया गया अपवाद | `500` |
| `raise HTTPException(status_code=403)` | आपके द्वारा उठाया गया स्टेटस, HTML या JSON के रूप में |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, अनुरोध में कहीं से भी |
| `redirect()`, `permanentRedirect()` | बिना किसी त्रुटि वाला एक वास्तविक रीडायरेक्ट पृष्ठ |

## एक पेज छोड़ें या कोड से उत्तर दें

`redirect`, `permanentRedirect`, `notFound`, `forbidden` और `unauthorized` एक HTTP अपवाद उठाते हैं, इसलिए एक ही कॉल `.nexy` पेज, एक एपीआई हैंडलर, एक मॉड्यूलर नियंत्रक, एक गार्ड और एक `dependencies.py` में काम करता है। क्लाइंट पर उनके नाम समान हैं (`@nexy/client`)।

```nexy filename="src/routes/posts/[स्लग].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| कॉल करें | उत्तर दें |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` एक फॉर्म के बाद एक पोस्ट को जीईटी में बदल देता है |
| `permanentRedirect(url)` | `308`; ब्राउज़र और खोज इंजन इसे याद रखते हैं |
| `notFound(detail=None)` | `404`: `notfound` पेज, या एपीआई क्लाइंट के लिए JSON |
| `forbidden(detail=None)` | `403`: आगंतुक को पता है लेकिन वह इसे नहीं देख सकता है |
| `unauthorized(detail=None, scheme=None)` | `401`; `scheme="Bearer"` जोड़ता है `WWW-Authenticate` |

एक रीडायरेक्ट उत्तर `Location` हेडर और बिना किसी पेज के, एक एपीआई क्लाइंट को भी देता है। गंतव्य का निर्माण उन मूल्यों से करें जिन पर आप भरोसा करते हैं: एक `redirect(request.query_params["next"])` जहां भी लिंक कहता है वहां आगंतुकों को भेजता है। लाइन ब्रेक वाले गंतव्य को अस्वीकार कर दिया जाता है।

एक गार्ड पूरे फ़ोल्डर की सुरक्षा करता है:

```python filename="src/routes/private/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## एचटीएमएल या JSON

कौन पूछता है इसके आधार पर एक ही अपवाद अलग-अलग उत्तर देता है:

- एक ब्राउज़र (`Accept: text/html`) को एक HTML पेज मिलता है। विवरण HTML से बच गया है, इसलिए उपयोगकर्ता इनपुट से निर्मित संदेश मार्कअप इंजेक्ट नहीं कर सकता है।
- एक क्लाइंट जो JSON मांगता है न कि किसी पेज (`Accept: application/json`) के लिए, उसे समान स्टेटस कोड के साथ `{"detail": "..."}` मिलता है।

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!नोट]
> एक क्लाइंट जो `Accept: */*` भेजता है (`curl` और कई HTTP लाइब्रेरीज़ का डिफ़ॉल्ट) HTML पेज प्राप्त करता है। JSON त्रुटियों के लिए `Accept: application/json` सेट करें।

## हैंडल न किए गए अपवाद

एक अपवाद जिसे कुछ भी संभाला नहीं गया है उसे एक बार लॉग किया जाता है, अपवाद के साथ, यह कहां से आया है और इसके आसपास का कोड है, और मोड के अनुसार उत्तर दिया गया है।

| | `nx dev` | `nx start` |
|---|---|---|
| ब्राउज़र | त्रुटि वाला एक पृष्ठ, आपके कोड की पंक्तियाँ जिसने इसे उठाया और पूर्ण ट्रेसबैक | अंतर्निहित `500` पृष्ठ (या आपका `errors.nexy`) एक संदर्भ के साथ |
| JSON क्लाइंट | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| सर्वर लॉग | अपवाद और आपके कोड की पंक्तियाँ | अपवाद और संपूर्ण ट्रेसबैक, एक ही संदर्भ के साथ |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

संदर्भ आठ वर्णों का है, प्रत्येक विफलता के लिए नया। कोई विज़िटर इसे उद्धृत कर सकता है, और आप इसके लिए लॉग में खोजकर ट्रेसबैक ढूंढ सकते हैं। उत्पादन में न तो अपवाद और न ही कोड विज़िटर तक पहुंचता है। एक कस्टम `errors.nexy` केवल पृष्ठ को प्रतिस्थापित करता है; लॉग लाइन रहती है.

## सत्यापन त्रुटियाँ

प्रत्येक क्लाइंट के लिए एक गुम हेडर, क्वेरी पैरामीटर या बॉडी फ़ील्ड `422` को FastAPI के JSON बॉडी के साथ उत्तर देता है। [सत्यापन और त्रुटियाँ](../handlers/validation-and-errors.md) देखें।

## अगले चरण

- [त्रुटि पृष्ठ प्रति फ़ोल्डर](folder-pages.md): एक फ़ोल्डर में आपका स्वयं का 404, 403 या 401
- [गतिशील मार्ग](../pages/dynamic-routes.md)
- [एपीआई मार्ग](../handlers/README.md)
- [परीक्षण](../../../guides/testing.md)
