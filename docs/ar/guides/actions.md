# الإجراءات

يقوم `@Action` بتحويل وظيفة بايثون إلى نقطة نهاية `POST`. على عكس معالج واجهة برمجة التطبيقات القياسي، فقد تم تصميمه كجسر اتصال مكتوب: يقوم Nexy تلقائيًا بإنشاء عميل TypeScript، والتحقق من صحة الإدخال، والتعامل مع الاستجابة.

**قبل البدء:** مشروع تم إنشاؤه بواسطة [البداية السريعة](../getting-started/quick-start.md).
الإجراءات مباشرة بجوار الصفحات، في `src/actions/`.

```diagram filename="دورة العمل"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## دورة العمل

### 1. تحديد
الإجراء هو دالة بايثون عادية تحمل علامة `@Action`. يستخدم Nexy توقيعه لتحديد عقد API.

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

المعلمات هي المدخلات، والتي تم التحقق من صحتها بواسطة Pydantic. يتم إدخال معلمة تسمى `request` أو `response` وهي ليست جزءًا من الإدخال.

### 2. التحقق من صحة
عندما يتم استدعاء الإجراء، يقوم Nexy بالتحقق من صحة الإدخال مقابل تلميحات نوع الوظيفة. إذا كان الحقل مفقودًا أو يحتوي على نوع خاطئ، فلن يتم تنفيذ الإجراء، وسيتم إرجاع `422 Unprocessable Entity`.

### 3. تنفيذ
يعمل المنطق على الخادم. وبما أنها وظيفة بايثون قياسية، يمكنك استخدام أي مكتبة، أو الوصول إلى قاعدة البيانات، أو الاتصال بخدمات أخرى. يمكنك أيضًا تشغيل تحديث الصفحة باستخدام `revalidate()`.

### 4. تسلسل
يتم إجراء تسلسل لقيمة الإرجاع تلقائيًا إلى JSON. يتم التعامل مع نماذج Pydantic محليًا، ويتم تعيين أنواع Python القياسية إلى مرادفات JSON الخاصة بها.

### 5. تستهلك
تتلقى الواجهة الأمامية النتيجة بأمان كامل. Nexy يكتب `__nexy__/src/actions.ts` من توقيعاتك، و `@nexy/actions` يعتزم عليه.

```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

بدون ربط، الإجراء هو مجرد وظيفة `async`: `const user = await create_user({ name: "Ada" })`.

| الإطار | ما `useAction` يعود |
|---|---|
| تفاعل، بادر | `{ pending, data, error, run, reset }` |
| الصلبة | نفس الشيء، مع `pending()`، `data()` و `error()` كموصلات |
| الرأي | هو نفسه، مع `pending`، `data` و `error` كمراجع |
| سفلتي | متجر: `$save.pending`، `$save.data`، `$save.error`، بالإضافة إلى `save.run(input)` و`save.reset()` |

`useAction(action, { onSuccess, onError })` يأخذ أيضًا ردين. `run` لا يرمي أبدًا: يسقط الفشل في `error` ويحل `run` مع `undefined`.

الأنواع تأتي من بايثون: `str` هو `string`، `int` و `float` هو `number`، `list[T]` هو `T[]`،
نموذج Pydantic أو `Enum` هو نوع مسمى، والحقل ذو الإعداد الافتراضي اختياري في الإدخال.
النوع الذي لا يستطيع Pydantic وصفه يصبح `unknown`.

## الأخطاء والإخفاقات

يمكن أن يفشل الإجراء في مراحل مختلفة. يجب عليك التمييز بينهما في واجهة المستخدم الخاصة بك:

1.  **أخطاء التحقق (422)**: الإدخال لم يتطابق مع توقيع بايثون. `error.fields` يقوم بتعيين كل حقل غير صالح لرسالته.
2.  **أخطاء العمل (`HTTPException`)**: رمزك رفض المكالمة، على سبيل المثال `403 Forbidden` أو `409 Conflict`.
3.  **أخطاء الخادم (500)**: حدث استثناء غير معالج في كود بايثون الخاص بك.
4.  **أخطاء الشبكة**: لم يصل الطلب مطلقًا إلى الخادم، على سبيل المثال انتهاء المهلة أو فقدان الاتصال.
5.  **أخطاء التفويض (401، 403)**: الشيك الخاص بك رفض المتصل. Nexy لا يقرر هذا لك.

التحقق من الأصل الموضح أدناه هو حماية CSRF، وليس ترخيصًا: فهو يوضح مكان المكالمة
جاء من، أبدا من يسمح له بذلك.

## تحديث الصفحة بعد إجراء ما

يوضح الإجراء الصفحات التي أصبح التغيير فيها قديمًا، كما يفعل Next.js مع `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

الجواب يحمل المسارات في رأس `x-nexy-revalidate`. يقوم العميل بعد ذلك بإعادة جلب الصفحة الحالية من خلال جهاز التوجيه، أو يعيد تحميلها في حالة عدم وجود جهاز توجيه العميل.

## نماذج بدون جافا سكريبت

يأخذ الإجراء أيضًا نموذج HTML قياسيًا، بحيث تعمل الصفحة قبل تحميل أي برنامج نصي:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

في قالب `.nexy` يكون `__actions_path["name"]` هو المسار، `__actions["name"]` الوظيفة، وتكون الوظيفة أيضًا في النطاق تحت اسمها الخاص.

عند النجاح، يتم إرسال الزائر مرة أخرى إلى الصفحة التي كان فيها النموذج، بالحالة `303`. للإجابة بشكل مختلف، قم بإرجاع كائن `Response` (على سبيل المثال، `RedirectResponse("/done", status_code=303)`).

## الأمن

### غموض المسار ليس ترخيصًا
مسار الإجراء هو `/_nx_` متبوعًا بتجزئة وحدة الوظيفة واسمها وسر الوحدة
مشروع. ويضبطه `NEXY_ACTION_SECRET`، أو يحفظه في `__nexy__/action.key`، وهو `nx build`
يتم إنشاؤه لذا توافق حزمة العميل و`nx start` على: احتفظ بهذا الملف مع البنية. المسار يخفي
نقطة النهاية من الاكتشاف العرضي، و**المسار الذي تم إنشاؤه ليس آلية ترخيص**.

يمكن لأي شخص يعرف المسار أن يدعو إلى الإجراء. **يجب عليك** التحقق من هوية المستخدم وأذوناته داخل الإجراء:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### حماية الأصل
لمنع تزوير الطلبات عبر المواقع (CSRF)، يرفض Nexy الطلبات التي يكون `Origin` موقعًا آخر أو أن يقوم المتصفح بوضع علامة على `Sec-Fetch-Site: cross-site` مع `403`. قم بإدراج المواقع التي قد تستدعي تصرفاتك في `NEXY_ALLOWED_ORIGINS`. يتم قبول المكالمات التي لا تحتوي على `Origin` (مثل `curl`).

## أخطاء الاستيراد

عند بدء التشغيل، يقوم Nexy باستيراد كل وحدة من `src/` للعثور على الإجراءات. يتم الإبلاغ عن الوحدة التي فشل استيرادها، ويستمر تحميل الوحدات الأخرى:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## الخطوات التالية

- [API](../routing/fbr/handlers/README.md): معالجات صريحة
- [الاختبار](testing.md#what-to-assert): كيفية اختبار إجراء ما
-  [التكوين](../reference/config.md): خيارات البرامج الوسيطة والمصادقة