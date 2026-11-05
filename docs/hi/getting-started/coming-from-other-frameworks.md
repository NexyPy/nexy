# दूसरे ढाँचे से आ रहा है

नेक्सी FastAPI प्लस फ़ाइल-आधारित रूटिंग, सर्वर-रेंडर किए गए पेज और वैकल्पिक React, Vue, Svelte, Solid या Preact द्वीप हैं। यह पृष्ठ वही दर्शाता है जो आप पहले से जानते हैं।

## से FastAPI

| FastAPI | नेक्सी |
|---|---|
| `@app.get("/users")` आपके द्वारा आयातित मॉड्यूल में | `GET` में फ़ंक्शन `src/routes/users.py` |
| `app.include_router(router)` | फ़ाइल पथ URL है; रजिस्टर करने के लिए कुछ भी नहीं |
| पथ परम `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | अभी भी `Depends(...)`: हैंडलर FastAPI हैंडलर हैं |
| Jinja2 `TemplateResponse` | समापन बिंदु के बगल में एक `.nexy` पृष्ठ |
| `uvicorn main:app` के साथ चलाएँ | `nx dev`, फिर `nx build && nx start` |

`src/routes/*.py` के अंतर्गत सब कुछ सामान्य है FastAPI: निर्भरताएं, Pydantic मॉडल, मिडलवेयर और `/docs` काम करते रहते हैं।

पहले और बाद में वही समापन बिंदु:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## से Next.js

| Next.js | नेक्सी |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` या `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (`<html>` का मालिक है) | `src/routes/layout.tsx` के साथ `useCSR = True` (React), या `src/routes/layout.nexy` सर्वर मोड में |
| नेस्टेड `layout.tsx` | नेस्टेड `layout.tsx` / `layout.vue` / `layout.svelte` क्लाइंट मोड में, नेस्टेड `layout.nexy` सर्वर मोड में |
| `use client` सर्वर पेज में घटक | [द्वीप](../rendering/islands.md) सर्वर मोड में |
| मार्ग संचालक `route.ts` | `src/routes/api/x.py`, Python में लिखा गया है |
| `(group)` फ़ोल्डर | वही: `(group)/` |
| सर्वर क्रियाएँ | [`@Action`](../guides/actions.md) फ़ंक्शंस को किसी फ़ॉर्म से या टाइप किए गए क्लाइंट फ़ंक्शंस के रूप में बुलाया जाता है |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

बैकएंड Python है, इसलिए आपका एपीआई आपके डेटा और एमएल कार्य के साथ कोड साझा करता है। क्लाइंट घटक पूरे पृष्ठ React पेड़ के बजाय द्वीपों के रूप में हाइड्रेट होते हैं।

एक Next.js पेज लगभग वैसे ही चलता रहता है, और इसका `"use client"` घटक एक सर्वर पेज का एक द्वीप बन जाता है:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```

## एक्सप्रेस या नोड बैकएंड से

| एक्सप्रेस | नेक्सी |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` के साथ `async def GET(id)` |
| `app.use(middleware)` | FastAPI मिडलवेयर, `nexyconfig.py` से पंजीकृत |
| `res.json(obj)` | एक आदेश या एक Pydantic मॉडल लौटाएँ |
| ईजेएस/पग दृश्य | `.nexy` (Jinja2) पृष्ठ |
| `npm run dev` | `nx dev` |

`app.use(...)` `nexyconfig.py` का फ़ील्ड बन जाता है, और `res.json(...)` रिटर्न मान बन जाता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```

## राउटर चुनना

| उपयोग करें | कब |
|---|---|
| फ़ाइल-आधारित राउटर | फ़ाइलों से मैप किए गए पृष्ठ और समापन बिंदु; डिफ़ॉल्ट |
| मॉड्यूलर राउटर | नियंत्रक, मॉड्यूल और निर्भरता इंजेक्शन, NestJS-शैली |

दो फाइलों में मॉड्यूलर राउटर: एक नियंत्रक, और मॉड्यूल `nexyconfig.py` `useRouter = AppModule` की ओर इशारा करता है:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

दोनों को `nx new` द्वारा तैयार किया गया है और अंत-से-अंत तक समान परीक्षणों द्वारा कवर किया गया है। [रूटिंग](../routing/README.md) और [मॉड्यूलर रूटिंग](../routing/modular/README.md) देखें।

## आगे कहाँ

- [त्वरित शुरुआत](quick-start.md): एक प्रोजेक्ट बनाएं और उसे चलाएं
- [परियोजना संरचना](project-structure.md): जहां प्रत्येक फ़ाइल संबंधित है
- [रूटिंग](../routing/README.md): राउटर चुनें
