# नेक्सी क्या है?

नेक्सी फुलस्टैक वेब अनुप्रयोगों के लिए एक Python ढांचा है: आपके पेज और आपका एपीआई एक प्रोजेक्ट में रहते हैं और एक सर्वर द्वारा परोसे जाते हैं।

## तुम्हें क्या मिलता है

- **Python में पृष्ठ।** एक `.nexy` फ़ाइल शीर्ष पर Python की कुछ पंक्तियों के साथ HTML है; एक `.md` फ़ाइल भी एक पृष्ठ है। किसी पृष्ठ को प्रस्तुत करने के लिए JavaScript की आवश्यकता नहीं है।
<!-- router:fbr -->
- **उसी प्रोजेक्ट में एक एपीआई।** `src/routes/` के अंतर्गत एक `.py` फ़ाइल HTTP अनुरोधों का उत्तर देती है: `GET` नाम का एक फ़ंक्शन उत्तर देता है `GET`, `POST` नामक एक फ़ंक्शन उत्तर देता है `POST`।
<!-- /router -->
<!-- router:modular -->
- **उसी प्रोजेक्ट में एक एपीआई।** एक नियंत्रक HTTP अनुरोधों का उत्तर देता है: इसकी विधि `get` उत्तर देती है `GET`, इसकी विधि `post` उत्तर देती है `POST`, और एक मॉड्यूल नियंत्रकों और उनकी सेवाओं को समूहित करता है।
<!-- /router -->
<!-- router:custom -->
- **उसी प्रोजेक्ट में एक एपीआई।** आपके पास पहले से मौजूद FastAPI राउटर उत्तर देता रहता है, और `src/routes/` के पेज और रूट फ़ाइलें उसके आगे उत्तर देती हैं।
<!-- /router -->
- **एपीआई दस्तावेज़ निःशुल्क।** प्रत्येक एपीआई मार्ग एक OpenAPI स्कीमा में दिखाई देता है, और स्केलर इसे `/docs` पर एक इंटरैक्टिव संदर्भ के रूप में दिखाता है।
- **फॉर्म जो Python को कॉल करते हैं।** एक फॉर्म, या ब्राउज़र से टाइप किया गया कॉल, उसी Python फ़ंक्शन तक पहुंचता है।
- **जब आप एक फ्रंटएंड फ्रेमवर्क चाहते हैं।** React, Vue, Svelte, Solid या Preact, एक घटक के लिए या पूरी साइट के लिए।
- **एक कमांड काम करने के लिए, एक शिप करने के लिए।** `nx dev` जैसे ही आप सेव करते हैं, पुनः लोड हो जाता है; `nx build` उत्पादन तैयार करता है।

## यह किस पर बनाया गया है

वर्तमान संस्करण, 2.2, उन उपकरणों पर आधारित है जिन्हें आप पहले से जानते होंगे:

| भाग | पर निर्मित | आपके लिए इसका क्या मतलब है |
|---|---|---|
| सर्वर और एपीआई | [FastAPI](https://fastapi.tiangolo.com/) | एक एपीआई मार्ग एक FastAPI मार्ग है: Pydantic सत्यापन और निर्भरताएं हमेशा की तरह काम करती हैं |
| एपीआई संदर्भ | OpenAPI और [अदिश](https://scalar.com/) | स्कीमा `/openapi.json` पर है, संदर्भ `/docs` पर है |
| पन्ने | Jinja2 | एक `.nexy` पृष्ठ Jinja2 टैग का उपयोग करता है जैसे `{{ title }}` |
| फ्रंटेंड (वैकल्पिक) | [Vite](https://vite.dev/) | केवल एक फ्रंटएंड फ्रेमवर्क के साथ, जिसकी भी आवश्यकता है Node.js |

## एक पहला पृष्ठ और एक पहला समापन बिंदु

<!-- router:fbr,custom -->
एक पृष्ठ, `/hello` पर:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

`GET /api/items` पर एक समापन बिंदु, बिना किसी अतिरिक्त कोड के `/docs` पर सूचीबद्ध है:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```
<!-- /router -->

<!-- router:modular -->
एक दृश्य, और नियंत्रक जो `/hello/` और `GET /api/items/` का उत्तर देते हैं। समापन बिंदु बिना किसी अतिरिक्त कोड के `/docs` पर सूचीबद्ध है, और इसके अंतिम स्लैश के बिना एक यूआरएल इसे रीडायरेक्ट करता है:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

```python filename="src/apps/hello_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews("src/apps/hello_view.nexy", context={"title": "Hello"})


@Controller("/api/items")
class ItemsController:
    async def get(self):
        return {"items": []}
```

रूट मॉड्यूल उन्हें सूचीबद्ध करता है, और `useRouter = AppModule` में `nexyconfig.py` इसे माउंट करता है:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .hello_controller import HelloController, ItemsController


@Module()
class AppModule:
    controllers = [HelloController, ItemsController]
```
<!-- /router -->

## नेक्सी आप पर क्या छोड़ती है

डेटाबेस, लॉगिन और कौन क्या कर सकता है इसके नियम आपके एप्लिकेशन से संबंधित हैं, इसलिए आप लाइब्रेरी चुनते हैं। [डेटाबेस](../guides/databases.md) और [मिडिलवेयर और सुरक्षा](../guides/middleware-and-security.md) दिखाते हैं कि प्रत्येक कहां प्लग इन करता है।

## अगले चरण

- [इंस्टालेशन](installation.md): uv इंस्टाल करें और एक प्रोजेक्ट बनाएं
- [त्वरित शुरुआत](quick-start.md): इसे चलाएं, एक पेज बदलें, इसे बनाएं
- [मूल अवधारणाएँ](core-concepts.md): कुछ शब्द जिनका उपयोग बाकी दस्तावेज़ करते हैं
