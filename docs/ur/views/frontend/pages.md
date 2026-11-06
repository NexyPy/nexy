# فرنٹ اینڈ پیجز

A **Page** Nexy ایپلی کیشن کی بنیادی اکائی ہے۔ یہ ایک URL ایڈریس ایبل وسیلہ ہے جسے `src/routes/` کے تحت فائل کے ذریعے بیان کیا گیا ہے۔ 

استعمال شدہ کلائنٹ فریم ورک سے قطع نظر، ہر صفحہ ایک ہی عالمگیر لائف سائیکل اور تعمیراتی رکاوٹوں کی پیروی کرتا ہے۔

## پیج لائف سائیکل

جب صارف کسی صفحہ پر جاتا ہے، Nexy مندرجہ ذیل اقدامات کرتا ہے:

1.  **روٹ میچنگ**: روٹر یو آر ایل سے متعلقہ فائل کی شناخت کرتا ہے۔
2.  **ڈیٹا بازیافت**: سرور صفحہ کے Python فرنٹ میٹر کو چلاتا ہے تاکہ اسے مطلوبہ ڈیٹا حاصل کیا جاسکے۔
3.  **کمپوزیشن**: صفحہ اپنے قریب ترین `layout.nexy` (یا فریم ورک لے آؤٹ) میں لپٹا ہوا ہے۔
4.  **رینڈرنگ**: نتیجہ ایچ ٹی ایم ایل میں پیش کیا جاتا ہے (بذریعہ Jinja2، Markdown، یا فریم ورک SSR)۔
5.  **ہائیڈریشن**: اگر صفحہ کلائنٹ فریم ورک کا استعمال کرتا ہے، تو براؤزر متعامل منطق کو جامد HTML سے منسلک کرتا ہے۔

ایک سرور موڈ صفحہ میں 2 سے 4 مراحل: فرنٹ میٹر بازیافت کرتا ہے، ٹیمپلیٹ پیش کرتا ہے، اور جڑ کی ترتیب نتیجہ کو لپیٹ دیتی ہے۔

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

## روٹنگ اور یو آر ایل

روٹنگ سختی سے فائل پر مبنی ہے۔ URL کا تعین فائل کے راستے سے `src/routes/`، مائنس ایکسٹینشن کے تحت ہوتا ہے۔

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### متحرک طبقات
ایک راستہ بنانے کے لیے جو پیرامیٹر کے لحاظ سے مختلف ہو (مثال کے طور پر، صارف کا پروفائل)، مربع بریکٹ استعمال کریں:
- `src/routes/user/[id].tsx` → `/user/123`

طبقہ (`123`) کی قدر `@nexy/client` سے `useParams()` ہک کے ذریعے صفحہ پر دستیاب ہے۔

```tsx filename="src/routes/user/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### روٹ گروپس
قوسین میں لپٹے فولڈرز کو روٹر کے ذریعے نظر انداز کیا جاتا ہے لیکن آپ کو تنظیمی مقاصد یا مشترکہ ترتیب کے لیے فائلوں کو گروپ کرنے کی اجازت دیتے ہیں:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## صفحہ میٹا ڈیٹا
ہر صفحہ میٹا ڈیٹا (عنوان، تفصیل، اوپن گراف ٹیگز) کی وضاحت کرسکتا ہے جسے Nexy دستاویز کے شیل میں داخل کرتا ہے۔ ایک `.nexy` صفحہ اسے اپنے فرنٹ میٹر میں متعین کرتا ہے، لفظی یا `setMetadata` کے ساتھ:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` ہے Python: a `.tsx`، `.vue` یا `.svelte` صفحہ کا کوئی `metadata` ایکسپورٹ نہیں ہے، لہٰذا کلائنٹ موڈ میں عنوان اور میٹا ٹیگز کو روٹ لے آؤٹ میں لکھیں۔ ہر فیلڈ کے لیے [صفحہ کا میٹا ڈیٹا](../../routing/fbr/pages/metadata.md) دیکھیں۔

## فریم ورک کا نفاذ
مندرجہ بالا تصورات عالمگیر ہیں۔ اپنے مخصوص فریم ورک میں کسی صفحہ کو کیسے نافذ کیا جائے یہ جاننے کے لیے، **اختلافات** گائیڈ دیکھیں:

- [React اختلافات](../react/differences.md)
- [Vue اختلافات](../vue/differences.md)
- [Svelte اختلافات](../svelte/differences.md)
- [Solid اختلافات](../solid/differences.md)
- [Preact اختلافات](../preact/differences.md)
