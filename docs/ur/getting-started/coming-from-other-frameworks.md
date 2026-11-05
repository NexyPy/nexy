# دوسرے فریم ورک سے آرہا ہے۔

Nexy FastAPI کے علاوہ فائل پر مبنی روٹنگ، سرور کے ذریعے پیش کردہ صفحات اور اختیاری React، Vue، Svelte، Solid یا Preact جزیرے ہیں۔ یہ صفحہ نقشہ بناتا ہے جو آپ پہلے سے جانتے ہیں۔

## سے FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` ایک ماڈیول میں جو آپ درآمد کرتے ہیں | `GET` فنکشن `src/routes/users.py` |
| `app.include_router(router)` | فائل کا راستہ URL ہے۔ رجسٹر کرنے کے لیے کچھ نہیں |
| راہ پرم `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | اب بھی `Depends(...)`: ہینڈلر FastAPI ہینڈلر ہیں |
| Jinja2 `TemplateResponse` | ایک `.nexy` نقطہ اختتام کے ساتھ |
| `uvicorn main:app` | `nx dev` کے ساتھ چلائیں، پھر `nx build && nx start` |

`src/routes/*.py` کے تحت سب کچھ عام ہے FastAPI: انحصار، Pydantic ماڈل، مڈل ویئر اور `/docs` کام کرتے رہتے ہیں۔

## سے Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` یا `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (مالک `<html>`) | `src/routes/layout.tsx` `useCSR = True` (React) کے ساتھ، یا `src/routes/layout.nexy` سرور موڈ میں |
| نیسٹڈ `layout.tsx` | نیسٹڈ `layout.tsx` / `layout.vue` / `layout.svelte` کلائنٹ موڈ میں، نیسٹڈ `layout.nexy` سرور موڈ میں |
| سرور کے صفحے میں `use client` اجزاء | [جزیرے](../rendering/islands.md) سرور موڈ میں |
| روٹ ہینڈلر `route.ts` | `src/routes/api/x.py`، Python | میں لکھا ہے۔
| `(group)` فولڈرز | ایک جیسے: `(group)/` |
| سرور ایکشنز | [`@Action`](../guides/actions.md) فنکشنز کو فارم سے بلایا جاتا ہے یا بطور ٹائپ کردہ کلائنٹ فنکشنز |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

پسدید Python ہے، لہذا آپ کا API آپ کے ڈیٹا اور ایم ایل کام کے ساتھ کوڈ کا اشتراک کرتا ہے۔ کلائنٹ کے اجزاء پورے صفحہ React کے درخت کے بجائے جزیروں کی طرح ہائیڈریٹ ہوتے ہیں۔

## ایکسپریس یا نوڈ بیک اینڈ سے

| ایکسپریس | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` `async def GET(id)` | کے ساتھ
| `app.use(middleware)` | FastAPI مڈل ویئر، `nexyconfig.py` | سے رجسٹرڈ
| `res.json(obj)` | ایک ڈکٹ یا ایک Pydantic ماڈل واپس کریں |
| ای جے ایس / پگ ویوز | `.nexy` (Jinja2) صفحات |
| `npm run dev` | `nx dev` |

## راؤٹر کا انتخاب

| استعمال کریں | جب |
|---|---|
| فائل پر مبنی روٹر | صفحات اور فائلوں سے میپ کیے گئے اختتامی نکات۔ پہلے سے طے شدہ |
| ماڈیولر روٹر | کنٹرولرز، ماڈیولز اور انحصار انجکشن، NestJS طرز |

دونوں کو `nx new` کے ذریعے ڈھانپ دیا گیا ہے اور ایک ہی آخر سے آخر تک ٹیسٹوں کے ذریعے احاطہ کیا گیا ہے۔ دیکھیں [روٹنگ](../routing/README.md) اور [ماڈیولر روٹنگ](../routing/modular/README.md)۔

## جہاں اگلا

- [فوری آغاز](quick-start.md): ایک پروجیکٹ بنائیں اور اسے چلائیں۔
- [پروجیکٹ ڈھانچہ](project-structure.md): جہاں ہر فائل کا تعلق ہے۔
- [روٹنگ](../routing/README.md): روٹر کا انتخاب کریں۔
