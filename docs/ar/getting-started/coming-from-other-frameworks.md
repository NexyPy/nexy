# قادمة من إطار عمل آخر

Nexy هو FastAPI بالإضافة إلى التوجيه المستند إلى الملفات والصفحات المعروضة بواسطة الخادم وReact وVue وSvelte الاختيارية.
جزر صلبة أو بريكت. تعرض هذه الصفحة ما تعرفه بالفعل.

##  من FastAPI

| FastAPI | نكسي |
|---|---|
| `@app.get("/users")` في الوحدة النمطية، يمكنك استيراد وظيفة | `GET` في `src/routes/users.py` |
| `app.include_router(router)` | مسار الملف هو عنوان URL؛ لا شيء للتسجيل |
| معلمة المسار `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | لا يزال `Depends(...)`: المعالجات هي معالجات FastAPI |
| Jinja2 `TemplateResponse` | صفحة `.nexy` بجوار نقطة النهاية |
| تشغيل مع `uvicorn main:app` | `nx dev`، ثم `nx build && nx start` |

كل شيء تحت `src/routes/*.py` هو FastAPI عادي: التبعيات، نماذج Pydantic، البرامج الوسيطة
و`/docs` الاستمرار في العمل.

## من Next.js

| Next.js | نكسي |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` أو `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (يمتلك `<html>`) | `src/routes/layout.tsx` مع `useCSR = True` (React)، أو `src/routes/layout.nexy` في وضع الخادم |
| متداخل `layout.tsx` | متداخل `layout.tsx` / `layout.vue` / `layout.svelte` في وضع العميل، متداخل `layout.nexy` في وضع الخادم |
| `use client` المكونات في صفحة الخادم | [الجزر](../rendering/islands.md) في وضع الخادم |
| معالجات الطريق `route.ts` | `src/routes/api/x.py`، مكتوبة بلغة بايثون |
| `(group)` المجلدات | نفسها: `(group)/` |
| إجراءات الخادم | [`@Action` ](../guides/actions.md) يتم استدعاء الوظائف من نموذج أو كوظائف عميل مكتوبة |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

الواجهة الخلفية هي Python، لذا تشارك واجهة برمجة التطبيقات (API) الخاصة بك التعليمات البرمجية مع بياناتك وعمل تعلم الآلة. مكونات العميل
هيدرات كجزر بدلاً من شجرة React ذات الصفحة الكاملة.

## من الواجهات الخلفية لـ Express أو Node

| اكسبريس | نكسي |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` مع `async def GET(id)` |
| `app.use(middleware)` | برنامج FastAPI الوسيط، مسجل من `nexyconfig.py` |
| `res.json(obj)` | إرجاع إملاء أو نموذج Pydantic |
| مشاهدات EJS / الصلصال | `.nexy` صفحات (Jinja2) |
| `npm run dev` | `nx dev` |

## اختيار الراوتر

| استخدم | عندما |
|---|---|
| صفحات جهاز التوجيه المستندة إلى الملف | ونقاط النهاية المعينة من الملفات؛ الافتراضي |
| وحدات التحكم في جهاز التوجيه المعياري | والوحدات النمطية وحقن التبعية، على طراز NestJS |

كلاهما مدعومان بـ `nx new` ومشمولان بنفس الاختبارات الشاملة. انظر
[التوجيه](../routing/README.md) و [التوجيه المعياري](../routing/modular/README.md).

## إلى أين بعد ذلك

- [البداية السريعة](quick-start.md): إنشاء مشروع وتشغيله
- [بنية المشروع](project-structure.md): حيث ينتمي كل ملف
- [التوجيه](../routing/README.md): اختر جهاز التوجيه