# الإجراءات

يقوم `@Action` بتحويل الدالة Python إلى نقطة نهاية `POST`. على عكس معالج API القياسي، تم تصميمه كجسر اتصال مكتوب: يقوم Nexy تلقائيًا بإنشاء العميل TypeScript والتحقق من صحة الإدخال والتعامل مع الاستجابة.

**قبل أن تبدأ:** مشروع تم إنشاؤه بواسطة [البداية السريعة](../getting-started/quick-start.md). الإجراءات مباشرة بجوار الصفحات، في `src/actions/`.

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
الإجراء هو وظيفة Python عادية تحمل علامة `@Action`. يستخدم Nexy توقيعه لتحديد عقد API.

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

المعلمات هي المدخلات، ويتم التحقق من صحتها بواسطة Pydantic. يتم إدخال معلمة تسمى `request` أو `response` وهي ليست جزءًا من الإدخال.

### 2. التحقق من صحة
عندما يتم استدعاء الإجراء، يقوم Nexy بالتحقق من صحة الإدخال مقابل تلميحات نوع الوظيفة. إذا كان الحقل مفقودًا أو يحتوي على نوع خاطئ، فلن يتم تنفيذ الإجراء، وسيتم إرجاع `422 Unprocessable Entity`.

### 3. نفذ
يعمل المنطق على الخادم. نظرًا لأنها وظيفة Python قياسية، يمكنك استخدام أي مكتبة، أو الوصول إلى قاعدة البيانات، أو الاتصال بخدمات أخرى. يمكنك أيضًا تشغيل تحديث الصفحة باستخدام `revalidate()`.

### 4. إجراء تسلسل
يتم إجراء تسلسل لقيمة الإرجاع تلقائيًا إلى JSON. يتم التعامل مع النماذج Pydantic محليًا، ويتم تعيين الأنواع Python القياسية إلى مكافئاتها في JSON.

### 5. استهلك
تتلقى الواجهة الأمامية النتيجة بأمان كامل. يكتب نيكي `__nexy__/src/actions.ts` من توقيعاتك، ويقرر `@nexy/actions` ذلك.

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
| React، Preact | `{ pending, data, error, run, reset }` |
| Solid | نفس الشيء، مع `pending()`، `data()` و `error()` كموصلات |
| Vue | نفس الشيء، مع `pending`، `data` و `error` كمراجع |
| Svelte | متجر: `$save.pending`، `$save.data`، `$save.error`، بالإضافة إلى `save.run(input)` و `save.reset()` |

`useAction(action, { onSuccess, onError })` يأخذ أيضًا ردين اتصال. `run` لا يرمي أبدًا: الفشل يهبط في `error` و `run` يحل مع `undefined`.

الأنواع تأتي من Python: `str` هو `string`، `int` و `float` هي `number`، `list[T]` هو `T[]`، نموذج Pydantic أو `Enum` هو نوع مسمى، والحقل الافتراضي اختياري في الإدخال. النوع Pydantic الذي لا يمكن وصفه يصبح `unknown`.

## الأخطاء والفشل

يمكن أن يفشل الإجراء في مراحل مختلفة. يجب عليك التمييز بينهما في واجهة المستخدم الخاصة بك:

1.  **أخطاء التحقق من الصحة (422)**: الإدخال لم يتطابق مع التوقيع Python. `error.fields` يقوم بتعيين كل حقل غير صالح لرسالته.
2.  **أخطاء العمل (`HTTPException`)**: رمزك رفض الاتصال، على سبيل المثال `403 Forbidden` أو `409 Conflict`.
3.  **أخطاء الخادم (500)**: حدث استثناء غير معالج في كود Python الخاص بك.
4.  **أخطاء الشبكة**: لم يصل الطلب مطلقًا إلى الخادم، على سبيل المثال انتهاء المهلة أو فقدان الاتصال.
5.  **أخطاء التفويض (401، 403)**: الشيك الخاص بك رفض المتصل. Nexy لا يقرر هذا لك.

التحقق من الأصل الموضح أدناه هو حماية CSRF، وليس ترخيصًا: فهو يشير إلى مصدر المكالمة، ولا يشير مطلقًا إلى الشخص المسموح له بإجراءها.

## قم بتحديث الصفحة بعد الإجراء

يوضح الإجراء الصفحات التي أصبح تغييرها قديمًا، كما يفعل Next.js مع `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

الجواب يحمل المسارات في رأس `x-nexy-revalidate`. يقوم العميل بعد ذلك بإعادة جلب الصفحة الحالية من خلال جهاز التوجيه، أو يعيد تحميلها في حالة عدم وجود جهاز توجيه العميل.

## نماذج بدون JavaScript

يأخذ الإجراء أيضًا نموذج HTML قياسيًا، بحيث تعمل الصفحة قبل تحميل أي برنامج نصي:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

في قالب `.nexy` يكون `__actions_path["name"]` هو المسار، `__actions["name"]` الوظيفة، وتكون الوظيفة أيضًا في النطاق تحت اسمها الخاص.

عند النجاح، يتم إرسال الزائر مرة أخرى إلى الصفحة التي كان عليها النموذج، بالحالة `303`. للإجابة بشكل مختلف، قم بإرجاع كائن `Response` (على سبيل المثال، `RedirectResponse("/done", status_code=303)`).

## الأمن

### غموض المسار ليس إذنًا
مسار الإجراء هو `/_nx_` متبوعًا بتجزئة وحدة الوظيفة واسمها وسر المشروع. تم تعيينه بواسطة `NEXY_ACTION_SECRET`، أو الاحتفاظ به في `__nexy__/action.key`، والذي يقوم `nx build` بإنشائه، لذلك توافق حزمة العميل و `nx start` على: الاحتفاظ بهذا الملف مع البنية. يخفي المسار نقطة النهاية من الاكتشاف العرضي، و **المسار الذي تم إنشاؤه ليس آلية ترخيص**.

يمكن لأي شخص يعرف المسار أن يدعو إلى الإجراء. **يجب عليك** التحقق من هوية المستخدم وأذوناته داخل الإجراء:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### حماية الأصل
لمنع تزوير الطلبات عبر المواقع (CSRF)، يرفض Nexy الطلبات التي يكون `Origin` موقعًا آخر أو أن يقوم المتصفح بوضع علامة على `Sec-Fetch-Site: cross-site` بـ `403`. قم بإدراج المواقع التي قد تستدعي تصرفاتك في `NEXY_ALLOWED_ORIGINS`. يتم قبول المكالمات التي لا تحتوي على `Origin` (مثل `curl`).

## أخطاء الاستيراد

عند بدء التشغيل، يقوم Nexy باستيراد كل وحدة من `src/` للعثور على الإجراءات. يتم الإبلاغ عن الوحدة التي فشل استيرادها، ويستمر تحميل الوحدات الأخرى:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## الخطوات التالية

- [API](../routing/fbr/handlers/README.md): معالجات صريحة
- [الاختبار](testing.md#what-to-assert): كيفية اختبار الفعل
- [التكوين](../reference/config.md): خيارات البرامج الوسيطة والمصادقة
