# التحقق والأخطاء

كيف يقوم معالج واجهة برمجة التطبيقات (API) بالإبلاغ عن طلب غير صالح.

## التحقق

يتم التحقق من صحة معلمات المعالج بواسطة FastAPI مقابل التعليقات التوضيحية الخاصة بها.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| المشكلة | الحالة | الجسم |
|---|---|---|
| استعلام أو رأس أو ملف تعريف ارتباط أو حقل نص مفقود أو غير صالح | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| مقطع **مسار** غير صالح (`/api/users/abc` لـ `id: int`) | `404` | الصفحة التي لم يتم العثور عليها، أو JSON لـ `Accept: application/json` |

مقطع المسار الذي لا يمكن تحويله هو `404` بدلاً من `422`: المسار الديناميكي يلتقط أي جزء
عنوان URL، وعنوان URL الذي لا يمكن تحويله غير موجود.

الجسم `422` هو الشكل القياسي لـ FastAPI، لذلك يستمر العملاء الحاليون ومجموعات SDK التي تم إنشاؤها في العمل.

## رفع الأخطاء

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| يرسل العميل | الرد |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` بالحالة `404` |
| `Accept: text/html` | [صفحة الخطأ](../errors/README.md) |
| `Accept: */*` | صفحة الخطأ |

قم بتعيين `Accept: application/json` في عملاء API. تستمر المتصفحات في الحصول على الصفحات.

## الاستثناءات غير المعالجة

استثناء هو أن المعالج الخاص بك لا يلتقط الإجابات `500`، بنفس اختيار HTML أو JSON.

## الردود المخصصة

قم بإرجاع كائن استجابة عندما تتحكم في الجسم:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## الخطوات التالية

- [مسارات واجهة برمجة التطبيقات](README.md)
- [صفحات الخطأ](../errors/README.md)
-  [الاختبار](../../../guides/testing.md)