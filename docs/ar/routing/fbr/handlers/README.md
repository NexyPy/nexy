# معالجات الطريق

الملف `.py` ضمن `src/routes/` هو معالج API. مسار الملف هو عنوان URL، وكل وظيفة مسماة على اسم أسلوب HTTP تصبح نقطة نهاية.

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

أسماء الوظائف المدعومة: `GET`، `POST`، `PUT`، `PATCH`، `DELETE`، `OPTIONS`، `HEAD`. `SOCKET` يفتح WebSocket في نفس المسار – انظر [WebSocket](../realtime/websocket.md).

## مفردات HTTP

استيراد ما يحتاجه المعالج من `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

يعرض فئات الطلب والاستجابة (`Request`، `Response`، `JSONResponse`، `HTMLResponse`، `PlainTextResponse`، `RedirectResponse`، `StreamingResponse`، `FileResponse`)، ومصادر المعلمات (`Header`، `Query`، `Cookie`، `Path`، `Body`)، `Depends`، `BackgroundTasks`، `HTTPException`، `status`. تعتمد المعالجات المكتوبة ضد هذه الوحدة على عقد Nexy، وليس على المحرك الذي يخدمها. Pydantic نماذج تصف الأجسام والاستجابات كالمعتاد.

## المعلمات

| المصدر | كيف يصل |
|---|---|
| مقطع المسار `[id]` | وسيطة الدالة `id`، تم تحويله إلى التعليق التوضيحي الخاص به |
| سلسلة الاستعلام | `page: int = 1` |
| نص JSON | Pydantic وسيطة النموذج |
| FastAPI البدائيات | `Depends`، `Header`، `Cookie`، `Form`، `UploadFile` - بدون تغيير |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

مقطع المسار هو `{id}`، لذا فإن FastAPI يتحقق من صحة `id: int`. القيمة التي ليست عددًا صحيحًا تجيب على `404`، لأن المسار الديناميكي يلتقط أي عنوان URL وعنوان URL الذي لا يمكن تحويله غير موجود. انظر [التصديق والأخطاء](validation-and-errors.md).

## الردود

| عودة | الرد |
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

رفع FastAPI الاستثناءات للعملاء. العميل الذي يرسل `Accept: application/json` يتلقى `{"detail": "..."}` بالحالة التي قمت برفعها؛ يتلقى المتصفح صفحة الخطأ. `notfound.nexy` يعرض `404` و `errors.nexy` يعرض `500`، كل منهما محدد بدليله. راجع [التحقق من الصحة والأخطاء](validation-and-errors.md) و[صفحات الخطأ](../errors/README.md).

## OpenAPI

يظهر كل مسار لواجهة برمجة التطبيقات (API) في المخطط الذي تم إنشاؤه، لأن المسارات هي مسارات FastAPI عادية. يتم تقديم المخطط في `/openapi.json` ويتم تقديمه بواسطة Scalar في `/docs`. قم بتعطيل كليهما باستخدام `useDocs = False` في `nexyconfig.py`.

## الخطوات التالية

- [التبعيات](../dependencies/README.md): مصادقة وإعداد مشتركين لكل معالج أو لكل دليل
- [التحقق من الصحة والأخطاء](validation-and-errors.md): `422`، `404` وأخطاء JSON
- [التوجيه](../../README.md): مسار الملف إلى URL
- [الإجراءات](../../../guides/actions.md): نقاط النهاية ذات المسارات التي تم إنشاؤها
- [التكوين](../../../reference/config.md): البرامج الوسيطة، CORS، الجلسات
