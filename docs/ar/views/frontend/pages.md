# صفحات الواجهة الأمامية

**الصفحة** هي الوحدة الأساسية لتطبيق Nexy. إنه مورد يمكن عنونة عنوان URL محدد بواسطة ملف ضمن `src/routes/`. 

بغض النظر عن إطار عمل العميل المستخدم، تتبع كل صفحة نفس دورة الحياة العامة والقيود المعمارية.

## دورة حياة الصفحة

عندما ينتقل المستخدم إلى صفحة ما، يقوم Nexy بتنفيذ الخطوات التالية:

1.  **مطابقة المسار**: يقوم جهاز التوجيه بتعريف الملف المطابق لعنوان URL.
2.  **جلب البيانات**: يقوم الخادم بتشغيل الجزء الأمامي للصفحة Python لجلب البيانات التي يحتاجها.
3.  **التركيب**: يتم تغليف الصفحة بأقرب `layout.nexy` (أو تخطيط الإطار).
4.  **التقديم**: يتم تقديم النتيجة إلى HTML (عبر Jinja2 أو Markdown أو إطار عمل SSR).
5.  **الترطيب**: إذا كانت الصفحة تستخدم إطار عمل عميل، فسيقوم المتصفح بإرفاق المنطق التفاعلي بـ HTML الثابت.

الخطوات من 2 إلى 4 في صفحة واحدة في وضع الخادم: جلب المادة الأمامية، وعرض القالب، وتخطيط الجذر يغلف النتيجة.

```nexy filename="src/routes/users.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## التوجيه وعناوين URL

يعتمد التوجيه بشكل صارم على الملفات. يتم تحديد عنوان URL من خلال مسار الملف ضمن `src/routes/`، بدون الامتداد.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### القطاعات الديناميكية
لإنشاء مسار يختلف حسب المعلمة (على سبيل المثال، ملف تعريف المستخدم)، استخدم الأقواس المربعة:
- `src/routes/user/[id].tsx` → `/user/123`

قيمة المقطع (`123`) متاحة للصفحة عبر الخطاف `useParams()` من `@nexy/client`.

```tsx filename="src/routes/user/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### مجموعات الطريق
يتم تجاهل المجلدات الموجودة بين قوسين بواسطة جهاز التوجيه ولكنها تسمح لك بتجميع الملفات لأغراض تنظيمية أو تخطيطات مشتركة:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## البيانات التعريفية للصفحة
يمكن لكل صفحة تحديد البيانات الوصفية (العنوان والوصف وعلامات OpenGraph) التي يقوم Nexy بإدخالها في غلاف المستند. صفحة `.nexy` تضعها في مقدمتها بالحرف أو بـ `setMetadata`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` هو Python: صفحة `.tsx` أو `.vue` أو `.svelte` لا تحتوي على تصدير `metadata`، لذلك في وضع العميل، اكتب العنوان والعلامات الوصفية في التخطيط الجذر. راجع [بيانات تعريف الصفحة](../../routing/fbr/pages/metadata.md) لكل حقل.

## تنفيذ الإطار
المفاهيم المذكورة أعلاه عالمية. لمعرفة كيفية تنفيذ صفحة في إطار العمل الخاص بك، راجع دليل **الاختلافات**:

- [React الاختلافات](../react/differences.md)
- [Vue الاختلافات](../vue/differences.md)
- [Svelte الاختلافات](../svelte/differences.md)
- [Solid الاختلافات](../solid/differences.md)
- [Preact الاختلافات](../preact/differences.md)
