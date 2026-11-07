# الإجراءات والملاحة

يتم التعامل مع التفاعل في Nexy من خلال نظام موحد من **الإجراءات** و **التنقل**، مما يضمن بقاء الواجهة الأمامية والخلفية متزامنتين بدون كود لاصق يدوي لواجهة برمجة التطبيقات.

## عقد العمل

**الإجراء** هو وظيفة من جانب الخادم تتعامل مع الطفرة (على سبيل المثال، تحديث قاعدة بيانات). 

1.  **الإدخال المكتوب**: يتم تعريف الإجراءات في Python مع تلميحات الكتابة. يقوم Nexy بإنشاء عميل TypeScript مطابق، بحيث تحصل على الإكمال التلقائي والتحقق من الصحة في IDE الخاص بك.
2.  **التنفيذ الذري**: الإجراء هو طلب واحد `POST`.
3.  **معالجة النتائج**: تُرجع الإجراءات نتيجة مكتوبة يمكن للعميل استخدامها لتحديث واجهة المستخدم.

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

تستدعيها الصفحة مع الإعلان عن الإدخال Python، وتحصل على رد مكتوب `Todo`:

<!-- router:fbr,custom -->
```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
المكون عبارة عن جزيرة عرض، وتقوم وحدة التحكم بإرجاع العرض:

```tsx filename="src/components/Todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

```nexy filename="src/apps/todos_view.nexy"
---
from "@/components/Todos.tsx" import Todos
---
<Todos directive="client:load" />
```
<!-- /router -->

## التنقل من جانب العميل

التنقل في Nexy "ذكي". بدلاً من إعادة تحميل المتصفح بالكامل، يقوم Nexy بتبديل محتوى الصفحة الحالية مع الحفاظ على تثبيت التخطيطات النشطة.

- **المكون `Link`**: استخدم المكون `Link` الخاص بالإطار لإجراء التحولات من جانب العميل.
- **التنقل البرمجي**: استخدم `useRouter()` من `@nexy/client` واتصل بـ `push()` لتغيير الصفحات استجابةً للمنطق (على سبيل المثال، بعد تسجيل دخول ناجح).

```tsx filename="src/components/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## التنسيق: العمل → الملاحة

النمط الأكثر شيوعًا هو تنفيذ إجراء ثم نقل المستخدم إلى صفحة جديدة.

**تدفق إعادة التحقق:**
1.  العميل يستدعي الإجراء.
2.  يتم تنفيذ الإجراء على الخادم ويستدعي `revalidate("/path")`.
3.  يقوم الخادم بإرجاع النتيجة برأس `x-nexy-revalidate` لتسمية المسارات القديمة.
4.  يقوم العميل بتحديث محتوى الصفحة ليعكس الحالة الجديدة.

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

<!-- router:fbr,custom -->
```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

<!-- router:modular -->
```tsx filename="src/components/Login.tsx"
import { useAction } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export function Login() {
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) window.location.assign("/dashboard/");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

`check_password` يعني الشيك الخاص بك. راجع [الإجراءات](../../guides/actions.md) لمعرفة الأخطاء والنماذج التي لا تحتوي على JavaScript والأمان.

## تنفيذ الإطار

تختلف واجهة برمجة التطبيقات (API) لاستدعاء الإجراءات والتنقل حسب إطار العمل. راجع دليل **الاختلافات** للتكنولوجيا التي اخترتها:

- [React الاختلافات](../react/differences.md)
- [Vue الاختلافات](../vue/differences.md)
- [Svelte الاختلافات](../svelte/differences.md)
- [Solid الاختلافات](../solid/differences.md)
- [Preact الاختلافات](../preact/differences.md)
