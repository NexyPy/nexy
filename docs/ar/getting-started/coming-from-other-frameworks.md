# قادمة من إطار آخر

Nexy هو FastAPI بالإضافة إلى التوجيه المستند إلى الملف والصفحات المقدمة من الخادم والجزر الاختيارية React أو Vue أو Svelte أو Solid أو Preact. تعرض هذه الصفحة ما تعرفه بالفعل.

## من FastAPI

| FastAPI | نكسي |
|---|---|
| `@app.get("/users")` في الوحدة التي تقوم باستيراد وظيفة | `GET` في `src/routes/users.py` |
| `app.include_router(router)` | مسار الملف هو عنوان URL؛ لا شيء للتسجيل |
| معلمة المسار `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | لا يزال `Depends(...)`: المعالجات هي FastAPI معالجات |
| Jinja2 `TemplateResponse` | صفحة `.nexy` بجوار نقطة النهاية |
| تشغيل مع `uvicorn main:app` | `nx dev`، ثم `nx build && nx start` |

كل شيء ضمن `src/routes/*.py` عادي FastAPI: التبعيات، Pydantic النماذج، البرامج الوسيطة و `/docs` تستمر في العمل.

## من Next.js

| Next.js | نكسي |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` أو `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (تملك `<html>`) | `src/routes/layout.tsx` مع `useCSR = True` (React)، أو `src/routes/layout.nexy` في وضع الخادم |
| متداخل `layout.tsx` | متداخل `layout.tsx` / `layout.vue` / `layout.svelte` في وضع العميل، متداخل `layout.nexy` في وضع الخادم |
| `use client` المكونات في صفحة الخادم | [الجزر](../rendering/islands.md) في وضع الخادم |
| معالجات الطريق `route.ts` | `src/routes/api/x.py`، مكتوبة باللغة Python |
| `(group)` المجلدات | نفسها: `(group)/` |
| إجراءات الخادم | [`@Action` ](../guides/actions.md) يتم استدعاء الوظائف من نموذج أو كوظائف عميل مكتوبة |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

الواجهة الخلفية هي Python، لذا تشارك واجهة برمجة التطبيقات (API) الخاصة بك التعليمات البرمجية مع بياناتك وعمل تعلم الآلة. يتم ترطيب مكونات العميل كجزر بدلاً من شجرة React ذات صفحة كاملة.

## من الواجهات الخلفية Express أو Node

| اكسبريس | نكسي |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` مع `async def GET(id)` |
| `app.use(middleware)` | FastAPI البرامج الوسيطة، مسجلة من `nexyconfig.py` |
| `res.json(obj)` | إرجاع إملاء أو Pydantic نموذج |
| مشاهدات EJS / الصلصال | `.nexy` (Jinja2) الصفحات |
| `npm run dev` | `nx dev` |

## اختيار جهاز التوجيه

| استخدم | عندما |
|---|---|
| صفحات ونقاط نهاية جهاز التوجيه المستندة إلى الملف | المعينة من الملفات؛ الافتراضي |
| وحدات التحكم في جهاز التوجيه المعياري | والوحدات النمطية وحقن التبعية، على طراز NestJS |

كلاهما مدعومان بـ `nx new` ومشمولان بنفس الاختبارات الشاملة. انظر [التوجيه](../routing/README.md) و [التوجيه المعياري](../routing/modular/README.md).

## أين التالي

- [البداية السريعة](quick-start.md): إنشاء مشروع وتشغيله
- [بنية المشروع](project-structure.md): حيث ينتمي كل ملف
- [التوجيه](../routing/README.md): اختر جهاز التوجيه
