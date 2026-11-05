# دوسرے فریم ورک سے آرہا ہے۔

Nexy FastAPI کے علاوہ فائل پر مبنی روٹنگ، سرور کے ذریعے پیش کردہ صفحات اور اختیاری React، Vue، Svelte، Solid یا Preact جزیرے ہیں۔ یہ صفحہ نقشہ بناتا ہے جو آپ پہلے سے جانتے ہیں۔

## سے FastAPI

| FastAPI | نیکسی |
|---|---|
| `@app.get("/users")` ایک ماڈیول میں جو آپ درآمد کرتے ہیں۔ | `GET` فنکشن `src/routes/users.py` میں |
| `app.include_router(router)` | فائل کا راستہ URL ہے؛ رجسٹر کرنے کے لئے کچھ نہیں |
| راہ پرم `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | اب بھی `Depends(...)`: ہینڈلرز FastAPI ہینڈلر ہیں۔ |
| Jinja2 `TemplateResponse` | اختتامی نقطہ کے ساتھ ایک `.nexy` صفحہ |
| کے ساتھ چلائیں `uvicorn main:app` | `nx dev`، پھر `nx build && nx start` |

`src/routes/*.py` کے تحت سب کچھ عام ہے FastAPI: انحصار، Pydantic ماڈل، مڈل ویئر اور `/docs` کام کرتے رہتے ہیں۔

## سے Next.js

| Next.js | نیکسی |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` یا `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (اپنے `<html>`] | `src/routes/layout.tsx` سرور موڈ میں `useCSR = True` (React)، یا `src/routes/layout.nexy` کے ساتھ |
| گھریلو `layout.tsx` | نیسٹڈ `layout.tsx` / `layout.vue` / `layout.svelte` کلائنٹ موڈ میں، نیسٹڈ `layout.nexy` سرور موڈ میں |
| سرور کے صفحے میں `use client` اجزاء | [جزیرے](../rendering/islands.md) سرور موڈ میں |
| روٹ ہینڈلرز `route.ts` | `src/routes/api/x.py`، Python میں لکھا گیا |
| `(group)` فولڈرز | وہی: `(group)/` |
| سرور کے اعمال | [`@Action`](../guides/actions.md) فنکشنز کو فارم سے بلایا جاتا ہے یا بطور ٹائپ شدہ کلائنٹ فنکشنز |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

پسدید Python ہے، لہذا آپ کا API آپ کے ڈیٹا اور ایم ایل کام کے ساتھ کوڈ کا اشتراک کرتا ہے۔ کلائنٹ کے اجزاء پورے صفحہ React کے درخت کے بجائے جزیروں کی طرح ہائیڈریٹ ہوتے ہیں۔

## ایکسپریس یا نوڈ بیک اینڈ سے

| ایکسپریس | نیکسی |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` کے ساتھ `async def GET(id)` |
| `app.use(middleware)` | FastAPI مڈل ویئر، `nexyconfig.py` سے رجسٹرڈ |
| `res.json(obj)` | ایک ڈکٹ یا Pydantic ماڈل واپس کریں۔ |
| ای جے ایس / پگ ویوز | `.nexy` (Jinja2) صفحات |
| `npm run dev` | `nx dev` |

## راؤٹر کا انتخاب

| استعمال کریں۔ | جب |
|---|---|
| فائل پر مبنی روٹر | فائلوں سے میپ کیے گئے صفحات اور اختتامی پوائنٹس؛ پہلے سے طے شدہ |
| ماڈیولر راؤٹر | کنٹرولرز، ماڈیولز اور انحصار انجیکشن، NestJS طرز |

دونوں کو `nx new` کے ذریعے ڈھانپ دیا گیا ہے اور ایک ہی آخر سے آخر تک ٹیسٹوں کے ذریعے احاطہ کیا گیا ہے۔ دیکھیں [روٹنگ](../routing/README.md) اور [ماڈیولر روٹنگ](../routing/modular/README.md)۔

## جہاں اگلا

- [فوری آغاز](quick-start.md): ایک پروجیکٹ بنائیں اور اسے چلائیں۔
- [پروجیکٹ ڈھانچہ](project-structure.md): جہاں ہر فائل کا تعلق ہے۔
- [روٹنگ](../routing/README.md): روٹر کا انتخاب کریں۔
