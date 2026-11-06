# دوسرے فریم ورک سے آرہا ہے۔

Nexy FastAPI کے علاوہ فائل پر مبنی روٹنگ، سرور کے ذریعے پیش کردہ صفحات اور اختیاری React، Vue، Svelte، Solid یا Preact جزیرے ہیں۔ یہ صفحہ نقشہ بناتا ہے جو آپ پہلے سے جانتے ہیں۔

نیچے دیئے گئے ہر فریم ورک کا اپنا ایک صفحہ بھی ہوتا ہے، ٹاسک کے لحاظ سے، اس کوڈ کے ساتھ جو آپ جانتے ہیں اور پھر Nexy کوڈ:

| Python | بیک اینڈ | فل اسٹیک JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [ایکسپریس](../coming-from/express.md)، [فاسٹیفائی](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md)، [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [ایلیسیا](../coming-from/elysia.md)، [ہونو](../coming-from/hono.md) | [نکسٹ ](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md)، [اسپرنگ بوٹ](../coming-from/spring-boot.md) | [SvelteKit ](../coming-from/sveltekit.md) |
| | [لارویل](../coming-from/laravel.md)، [روبی آن ریلز](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## سے FastAPI

| FastAPI | نیکسی |
|---|---|
| `@app.get("/users")` ایک ماڈیول میں جو آپ درآمد کرتے ہیں۔ | `GET` فنکشن `src/routes/users.py` میں |
| `app.include_router(router)` | فائل کا راستہ URL ہے؛ رجسٹر کرنے کے لئے کچھ نہیں |
| راہ پرم `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | اب بھی `Depends(...)`: ہینڈلر FastAPI ہینڈلر ہیں۔ |
| Jinja2 `TemplateResponse` | اختتامی نقطہ کے ساتھ ایک `.nexy` صفحہ |
| کے ساتھ چلائیں `uvicorn main:app` | `nx dev`، پھر `nx build && nx start` |

`src/routes/*.py` کے تحت ہر چیز عام ہے FastAPI: انحصار، Pydantic ماڈل، مڈل ویئر اور `/docs` کام کرتے رہتے ہیں۔

ایک ہی اختتامی نقطہ، پہلے اور بعد:

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

## سے Next.js

| Next.js | نیکسی |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` یا `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (اپنے `<html>`] | `src/routes/layout.tsx` سرور موڈ میں `useCSR = True` (React)، یا `src/routes/layout.nexy` کے ساتھ |
| گھریلو `layout.tsx` | کلائنٹ موڈ میں نیسٹڈ `layout.tsx` / `layout.vue` / `layout.svelte`، سرور موڈ میں نیسٹڈ `layout.nexy` |
| `use client` سرور کے صفحے میں اجزاء | [سرور موڈ میں جزائر](../rendering/islands.md) |
| روٹ ہینڈلرز `route.ts` | `src/routes/api/x.py`، Python میں لکھا گیا |
| `(group)` فولڈرز | وہی: `(group)/` |
| سرور کے اعمال | [`@Action`](../guides/actions.md) فنکشنز کو فارم سے بلایا جاتا ہے یا بطور ٹائپ شدہ کلائنٹ فنکشنز |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

پسدید Python ہے، لہذا آپ کا API آپ کے ڈیٹا اور ایم ایل کام کے ساتھ کوڈ کا اشتراک کرتا ہے۔ کلائنٹ کے اجزاء پورے صفحہ React کے درخت کے بجائے جزیروں کی طرح ہائیڈریٹ ہوتے ہیں۔

ایک Next.js صفحہ تقریباً ویسا ہی آگے بڑھتا ہے جیسا کہ یہ ہے، اور اس کا `"use client"` جزو سرور صفحہ کا جزیرہ بن جاتا ہے۔

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

## ایکسپریس یا نوڈ بیک اینڈ سے

| ایکسپریس | نیکسی |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` کے ساتھ `async def GET(id)` |
| `app.use(middleware)` | FastAPI مڈل ویئر، `nexyconfig.py` سے رجسٹرڈ |
| `res.json(obj)` | ایک ڈکٹ یا Pydantic ماڈل واپس کریں۔ |
| ای جے ایس / پگ ویوز | `.nexy` (Jinja2) صفحات |
| `npm run dev` | `nx dev` |

`app.use(...)` `nexyconfig.py` کا فیلڈ بن جاتا ہے، اور `res.json(...)` واپسی کی قدر بن جاتا ہے:

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

## راؤٹر کا انتخاب

| استعمال کریں۔ | جب |
|---|---|
| فائل پر مبنی روٹر | فائلوں سے میپ کیے گئے صفحات اور اختتامی پوائنٹس؛ پہلے سے طے شدہ |
| ماڈیولر راؤٹر | کنٹرولرز، ماڈیولز اور انحصار انجیکشن، NestJS طرز |

ماڈیولر روٹر دو فائلوں میں: ایک کنٹرولر، اور ماڈیول `nexyconfig.py` پوائنٹس `useRouter = AppModule` کے ساتھ:

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

دونوں کو `nx new` کے ذریعے ڈھانپ دیا گیا ہے اور ایک ہی آخر سے آخر تک ٹیسٹ کے ذریعے احاطہ کیا گیا ہے۔ دیکھیں [روٹنگ](../routing/README.md) اور [ماڈیولر روٹنگ](../routing/modular/README.md)۔

## جہاں اگلا

- [فوری آغاز](quick-start.md): ایک پروجیکٹ بنائیں اور اسے چلائیں۔
- [پروجیکٹ کا ڈھانچہ](project-structure.md): جہاں ہر فائل کا تعلق ہے۔
- [روٹنگ ](../routing/README.md): روٹر کا انتخاب کریں۔
