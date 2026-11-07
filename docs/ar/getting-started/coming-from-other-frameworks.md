# قادمة من إطار آخر

Nexy هو FastAPI بالإضافة إلى التوجيه المستند إلى الملف والصفحات المقدمة من الخادم والجزر الاختيارية React أو Vue أو Svelte أو Solid أو Preact. تعرض هذه الصفحة ما تعرفه بالفعل.

يحتوي كل إطار أدناه أيضًا على صفحة خاصة به، مهمة بمهمة، تحتوي على الكود الذي تعرفه ثم كود Nexy:

| Python | الخلفية | المكدس الكامل JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [اكسبرس](../coming-from/express.md)، [فاستيفي](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md)، [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [إليسيا](../coming-from/elysia.md)، [هونو](../coming-from/hono.md) | [نوكست](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md)، [حذاء الربيع](../coming-from/spring-boot.md) | [سفيلتكيت](../coming-from/sveltekit.md) |
| | [لارافيل](../coming-from/laravel.md), [روبي أون ريلز](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## من FastAPI

<!-- router:fbr,custom -->
| FastAPI | نكسي |
|---|---|
| `@app.get("/users")` في الوحدة النمطية التي تقوم باستيرادها | `GET` الدالة في `src/routes/users.py` |
| `app.include_router(router)` | مسار الملف هو عنوان URL؛ لا شيء للتسجيل |
| معلمة المسار `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | لا يزال `Depends(...)`: المعالجات هي FastAPI معالجات |
| Jinja2 `TemplateResponse` | صفحة `.nexy` بجوار نقطة النهاية |
| تشغيل مع `uvicorn main:app` | `nx dev`، ثم `nx build && nx start` |

كل شيء تحت `src/routes/*.py` عادي FastAPI: التبعيات، Pydantic النماذج، البرامج الوسيطة و `/docs` تستمر في العمل.

نفس نقطة النهاية قبل وبعد:

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
<!-- /router -->

<!-- router:modular -->
| FastAPI | نكسي |
|---|---|
| `@app.get("/users")` في الوحدة النمطية التي تقوم باستيرادها | `async def get(self)` في فصل `@Controller("/users")` |
| `app.include_router(router)` | وحدة التحكم المدرجة في `controllers` من `@Module` |
| معلمة المسار `/users/{id}` | `@Controller("/users/{id}")`، مع `async def get(self, id: int)` |
| `Depends(...)` | لا يزال `Depends(...)`: طريقة التحكم هي نقطة نهاية FastAPI |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`، مردود بالطريقة |
| تشغيل مع `uvicorn main:app` | `nx dev`، ثم `nx build && nx start` |

التبعيات، Pydantic النماذج، البرامج الوسيطة و `/docs` تستمر في العمل.

نفس نقطة النهاية قبل وبعد:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## من Next.js

<!-- router:fbr,custom -->
| Next.js | نكسي |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` أو `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (يملك `<html>`) | `src/routes/layout.tsx` مع `useCSR = True` (React)، أو `src/routes/layout.nexy` في وضع الخادم |
| متداخلة `layout.tsx` | متداخل `layout.tsx` / `layout.vue` / `layout.svelte` في وضع العميل، متداخل `layout.nexy` في وضع الخادم |
| `use client` مكونات في صفحة الخادم | [الجزر](../rendering/islands.md) في وضع الخادم |
| معالجات الطريق `route.ts` | `src/routes/api/x.py`، مكتوب في Python |
| `(group)` المجلدات | نفسه: `(group)/` |
| إجراءات الخادم | [`@Action` ](../guides/actions.md) يتم استدعاء الوظائف من نموذج أو كوظائف عميل مكتوبة |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

الواجهة الخلفية هي Python، لذا تشارك واجهة برمجة التطبيقات (API) الخاصة بك التعليمات البرمجية مع بياناتك وعمل تعلم الآلة. يتم ترطيب مكونات العميل كجزر بدلاً من شجرة React ذات صفحة كاملة.

تتحرك صفحة Next.js كما هي تقريبًا، ويصبح مكونها `"use client"` بمثابة جزيرة لصفحة الخادم:

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
<!-- /router -->

<!-- router:modular -->
| Next.js | نكسي |
|---|---|
| `app/page.tsx` | وحدة تحكم تقوم بإرجاع `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`، مع `async def get(self, slug: str)` |
| `app/layout.tsx` (يملك `<html>`) | طريقة عرض تخطيطية تلتف وحدة التحكم حول طريقة العرض الخاصة بها، من خلال `children` |
| `use client` مكونات في صفحة الخادم | [الجزر](../rendering/islands.md) في طريقة عرض |
| معالجات الطريق `route.ts` | وحدة تحكم تقوم بإرجاع إملاء مكتوب باللغة Python |
| إجراءات الخادم | [`@Action` ](../guides/actions.md) يتم استدعاء الوظائف من نموذج أو كوظائف عميل مكتوبة |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

الواجهة الخلفية هي Python، لذا تشارك واجهة برمجة التطبيقات (API) الخاصة بك التعليمات البرمجية مع بياناتك وعمل تعلم الآلة. يتم ترطيب مكونات العميل كجزر بدلاً من شجرة React ذات صفحة كاملة.

تصبح صفحة Next.js وحدة تحكم وعرضها، ومكونها `"use client"` جزيرة للعرض:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## من الواجهات الخلفية Express أو Node

<!-- router:fbr,custom -->
| صريحة | نكسي |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` مع `async def GET(id)` |
| `app.use(middleware)` | FastAPI البرامج الوسيطة، مسجلة من `nexyconfig.py` |
| `res.json(obj)` | إرجاع إملاء أو نموذج Pydantic |
| مشاهدات EJS / الصلصال | `.nexy` (Jinja2) صفحة |
| `npm run dev` | `nx dev` |

يصبح `app.use(...)` حقلاً لـ `nexyconfig.py`، ويصبح `res.json(...)` قيمة مُرجعة:

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
<!-- /router -->

<!-- router:modular -->
| صريحة | نكسي |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`، مع `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI البرامج الوسيطة، مسجلة من `nexyconfig.py` |
| `res.json(obj)` | إرجاع إملاء أو نموذج Pydantic |
| مشاهدات EJS / الصلصال | `.nexy` (Jinja2) مشاهدات، تم إرجاعها بواسطة `useViews` |
| `npm run dev` | `nx dev` |

يصبح `app.use(...)` حقلاً لـ `nexyconfig.py`، ويصبح `res.json(...)` قيمة مُرجعة:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## اختيار جهاز التوجيه

| استخدم | متى |
|---|---|
| جهاز التوجيه القائم على الملف | الصفحات ونقاط النهاية المعينة من الملفات؛ الافتراضي |
| جهاز التوجيه المعياري | وحدات التحكم والوحدات وحقن التبعية، على غرار NestJS |

جهاز التوجيه المعياري في ملفين: وحدة تحكم، والوحدة النمطية `nexyconfig.py` تشير إلى `useRouter = AppModule`:

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

كلاهما مدعومان بـ `nx new` ومشمولان بنفس الاختبارات الشاملة. راجع [التوجيه](../routing/README.md) و [التوجيه المعياري](../routing/modular/README.md).

## أين التالي

- [البداية السريعة](quick-start.md): إنشاء مشروع وتشغيله
- [هيكل المشروع](project-structure.md): حيث ينتمي كل ملف
- [التوجيه](../routing/README.md): اختر جهاز التوجيه
