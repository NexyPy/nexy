# توجيه معياري

يستخدم التوجيه المعياري الفئات ذات الديكورات بدلاً من الملفات الموجودة ضمن `src/routes/`: وحدات التحكم
التعامل مع الطلبات، والوحدات النمطية تجميعها، ويتم حقن مقدمي الخدمات. قم بتركيب الناتج `APIRouter`
مع `useRouter` في `nexyconfig.py`.

**قبل البدء:** مشروع Nexy وصفحة عمل واحدة. يحل جهاز التوجيه المعياري محل
جهاز يستند إلى ملف، لذا اقرأ [Routing](../README.md) أولاً إذا لم تكن قد اخترت جهاز توجيه بعد.

| الصفحة | ما يغطيه |
|---|---|
| هذه الصفحة | تركيب وحدة، كتابة وحدة تحكم، وحدات تحكم المجموعة |
| [حقن التبعية](dependency-injection.md) | `@Injectable`، النطاقات، الحاوية |
| [الحراس والبيانات الوصفية](guards-and-metadata.md) | `@UseGuard`، `@Middleware`، `@UseRoute`، `@UseResponse` |
| [Nexy وNestJS](vs-nestjs.md) | ما يطابق NestJS وما لا يطابق |

## إعداد جهاز التوجيه

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!ملاحظة]
> يستمر التوجيه المعتمد على الملف في العمل. إذا كان `src/routes/` موجودًا، فسيتم مسحه حتى
> عند ضبط `useRouter`.

## اكتب وحدة تحكم

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

تتم مطابقة الطرق بالاسم، بشكل غير حساس لحالة الأحرف: `get`، `post`، `put`، `patch`، `delete`، `options`،
`head`، `trace`.

تعلن وحدة التحكم عن معالج واحد لكل طريقة HTTP؛ يثير نسخة مكررة عند بدء التشغيل. أضف بادئة بـ
`@Controller(prefix="/users")` - كل معالج مثبت على `prefix/`. `async def SOCKET(...)` على أ
تقوم وحدة التحكم بتسجيل WebSocket في نفس المسار.

## وحدات تحكم المجموعة في الوحدة النمطية

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` يرجع `APIRouter`. `controllers` مطلوب؛ `providers`، `imports`
و`exports` اختيارية. يتم تركيب الوحدات المستوردة كموجهات فرعية وموفريها المصدرين
يتم حلها عند بدء التشغيل.

## مشاهدات من وحدة التحكم

يمكن لوحدة التحكم إرجاع الصفحة. `useViews` يعرض عرض `.nexy`؛ عش واحدًا داخل الآخر لتغليفه
في التخطيط:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

انظر [التخطيطات](../fbr/layouts/README.md).

## مثال

انظر `examples/Modular/api/minimal/`.

## الخطوات التالية

- [حقن التبعية](dependency-injection.md): الخدمات والنطاقات
- [الحراسات والبيانات الوصفية](guards-and-metadata.md): حماية وتوثيق المسارات
- [التوجيه](../README.md): جهاز التوجيه المعتمد على الملفات
- [التكوين](../../reference/config.md): كل خيار، بما في ذلك `useRouter`