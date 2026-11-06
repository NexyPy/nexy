# التوجيه المعياري

يستخدم التوجيه المعياري فئات ذات أدوات تزيين بدلاً من الملفات الموجودة ضمن `src/routes/`: تتعامل وحدات التحكم مع الطلبات، وتجميعها الوحدات، ويتم حقن الموفرين. قم بتركيب `APIRouter` الناتج مع `useRouter` في `nexyconfig.py`.

**قبل أن تبدأ:** مشروع Nexy وصفحة عمل واحدة. يحل جهاز التوجيه المعياري محل جهاز التوجيه المعتمد على الملفات، لذا اقرأ [التوجيه](../README.md) أولاً إذا لم تكن قد اخترت جهاز توجيه بعد.

| الصفحة | ما يغطيه |
|---|---|
| هذه الصفحة | تركيب وحدة، كتابة وحدة تحكم، وحدات تحكم المجموعة |
| [حقن التبعية](dependency-injection.md) | `@Injectable`، النطاقات، الحاوية |
| [الحراس والبيانات الوصفية](guards-and-metadata.md) | `@UseGuard`، `@Middleware`، `@UseRoute`، `@UseResponse` |
| [نكسي و NestJS](vs-nestjs.md) | ما يوافق NestJS وما لا يوافق |

## قم بإعداد جهاز التوجيه

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTE]
> يستمر التوجيه المستند إلى الملف في العمل. إذا كان `src/routes/` موجودًا، فسيتم مسحه ضوئيًا حتى عند ضبط `useRouter`.

## اكتب وحدة تحكم

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

تتم مطابقة الطرق بالاسم، بشكل غير حساس لحالة الأحرف: `get`، `post`، `put`، `patch`، `delete`، `options`، `head`، `trace`.

تعلن وحدة التحكم عن معالج واحد لكل طريقة HTTP؛ يثير نسخة مكررة عند بدء التشغيل. الوسيطة الأولى لـ `@Controller("/users")` هي المسار الذي يجيب عليه كل معالج، `/users/`. `async def SOCKET(...)` على وحدة التحكم يسجل WebSocket في نفس المسار.

## وحدات تحكم المجموعة في الوحدة النمطية

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` يرجع `APIRouter`. `controllers` مطلوب؛ `providers`، `imports` و `exports` اختيارية. يتم تثبيت الوحدات المستوردة كموجهات فرعية، ويتم حل موفريها المصدرين عند بدء التشغيل.

## وجهات النظر من وحدة تحكم

يمكن لوحدة التحكم إرجاع الصفحة. `useViews` يعرض عرض `.nexy`؛ قم بتداخل واحد داخل الآخر لتغليفه في تخطيط:

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
- [الحراس والبيانات الوصفية](guards-and-metadata.md): حماية وتوثيق المسارات
- [التوجيه](../README.md): جهاز التوجيه القائم على الملف
- [التكوين](../../reference/config.md): كل خيار، بما في ذلك `useRouter`
