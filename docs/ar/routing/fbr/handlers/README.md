# معالجات المسار

الملف `.py` ضمن `src/routes/` هو معالج API. مسار الملف هو عنوان URL، وكل وظيفة
اسمه بعد أسلوب HTTP يصبح نقطة النهاية.

## إنشاء نقطة نهاية

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

يجيب هذا الملف على `GET /api/items` و `POST /api/items`.

أسماء الوظائف المدعومة: `GET`، `POST`، `PUT`، `PATCH`، `DELETE`، `OPTIONS`، `HEAD`. `SOCKET` يفتح
WebSocket في نفس المسار - راجع [WebSocket](../realtime/websocket.md).

## مفردات HTTP

استيراد ما يحتاجه المعالج من `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

يعرض فئات الطلب والاستجابة (`Request`، `Response`، `JSONResponse`، `HTMLResponse`،
`PlainTextResponse`، `RedirectResponse`، `StreamingResponse`، `FileResponse`)، مصادر المعلمات
(`Header`، `Query`، `Cookie`، `Path`، `Body`)، `Depends`، `BackgroundTasks`، `HTTPException` و
`status`. المعالجات المكتوبة ضد هذه الوحدة تعتمد على عقد Nexy، وليس على المحرك الذي
يخدمهم. تصف نماذج Pydantic الأجسام والاستجابات كالمعتاد.

## المعلمات

| المصدر | كيف يصل |
|---|---|
| مقطع المسار `[id]` | وسيطة الدالة `id`، محولة إلى تعليقها |
| سلسلة الاستعلام | `page: int = 1` |
| نص JSON | حجة نموذج Pydantic |
| أساسيات FastAPI | `Depends`، `Header`، `Cookie`، `Form`، `UploadFile` - لم تتغير |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

مقطع المسار هو `{id}`، لذا يقوم FastAPI بالتحقق من صحة `id: int`. القيمة التي ليست عددًا صحيحًا تجيب
`404`، لأن المسار الديناميكي يلتقط أي عنوان URL وعنوان URL الذي لا يمكن تحويله غير موجود.
انظر [التصديق والأخطاء](validation-and-errors.md).

## الردود

| العودة | الرد |
|---|---|
| `dict`، `list`، `BaseModel` | JSON |
| `JSONResponse`، `HTMLResponse`، أي `Response` | تمامًا كما أعلن |
| `None` | استجابة فارغة - قم بإرجاع `Response` بدلاً من ذلك عندما تكون الحالة مهمة |

للحصول على رمز حالة مخصص أو نوع محتوى، قم بإرجاع كائن استجابة:

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## أخطاء

رفع استثناءات FastAPI للعملاء. العميل الذي يرسل `Accept: application/json` يستقبل
`{"detail": "..."}` بالمنزلة التي رفعتها؛ يتلقى المتصفح صفحة الخطأ. `notfound.nexy`
يعرض `404` و `errors.nexy` يعرض `500`، كل منهما محدد بدليله. انظر
[التصديق والأخطاء](validation-and-errors.md) و[صفحات الخطأ](../errors/README.md).

##  واجهة برمجة التطبيقات المفتوحة

يظهر كل مسار لواجهة برمجة التطبيقات (API) في المخطط الذي تم إنشاؤه، لأن المسارات عبارة عن مسارات FastAPI عادية. ال
يتم تقديم المخطط في `/openapi.json` ويتم تقديمه بواسطة Scalar في `/docs`. تعطيل كلاهما مع
`useDocs = False` في `nexyconfig.py`.

## الخطوات التالية

- [التبعيات](../dependencies/README.md): مصادقة وإعداد مشتركين لكل معالج أو لكل دليل
-  [التحقق من الصحة والأخطاء](validation-and-errors.md): `422`، `404` وأخطاء JSON
-  [التوجيه ](../../README.md)]: مسار الملف إلى عنوان URL
- [الإجراءات](../../../guides/actions.md): نقاط النهاية ذات المسارات التي تم إنشاؤها
-  [التكوين](../../../reference/config.md): البرامج الوسيطة، CORS، الجلسات