# الربط والتنقل

باستخدام توجيه العميل (`useCSR = True`)، يؤدي الارتباط بين صفحتين إلى تبديل الصفحة في المستعرض بدلاً من إعادة تحميل المستند. تحافظ التخطيطات على حالتها.

## الروابط العادية تعمل بالفعل

يتم التنقل في كل `<a href>` إلى صفحة من مشروعك على العميل، بدون أي مكون أو علامة:

```html
<a href="/about">About</a>
```

يتم ترك رابط للمتصفح، ويقوم بتحميل الصفحة بشكل طبيعي، عندما:

- الضغط مع الاستمرار على مفتاح التعديل، أو أن الزر ليس هو المفتاح الرئيسي؛
- فيه `target` (غير `_self`) أو `download` أو `rel="external"` أو `data-nexy-reload`؛
- فإن `href` أصل آخر، أو رابط `mailto:`، أو `tel:`، أو `#fragment` فقط؛
- لا يتطابق المسار مع أي مسار للعميل، لذا يجيب الخادم عليه.

## `Link`

`Link` هو نفس المرساة مع ما لا يستطيع الشخص العادي فعله: يتم فحص `href` الخاص به مقابل مساراتك، ويقوم بتدفئة الصفحة المستهدفة، ويعرف متى يشير إلى الصفحة الحالية. يقوم Nexy بإنشاء `Link` لإطار العمل الخاص بك في `__nexy__/src` عند تشغيل `nx dev` أو `nx build`.

| الإطار | استيراد |
|---|---|
| React، Preact، Solid، Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Prop | معنى |
|---|---|
| `href` | مسار المشروع (الخطأ المطبعي هو خطأ في الكتابة)، اختياريًا مع `?query` أو `#fragment`، أو عنوان URL خارجي. |
| `replace` | استبدل إدخال السجل بدلاً من إضافة واحد. |
| `scroll` | `false` يحافظ على موضع التمرير بعد التنقل. الافتراضي: `true`. |
| `prefetch` | `'intent'` (افتراضي) يقوم بتحميل الصفحة عند التمرير أو التركيز أو اللمس؛ `'viewport'` عندما يتم تمرير الرابط إلى العرض؛ `false` أبدا. |
| `activeClassName` | تتم إضافتها إلى الفصل بينما يشير الارتباط إلى الصفحة الحالية أو الصفحة الموجودة أسفلها (`activeClass` في Vue و Svelte). |
| `exact` | نشط فقط على الصفحة المحددة. |

الرابط الذي يشير إلى الصفحة الحالية يحصل أيضًا على `aria-current="page"`.

## خطافات

الموقع متاح في كل إطار، في لغة ذلك الإطار. أثناء العملية الأولى، يقوم جانب الخادم بعرض إجابة الخطافات بعنوان URL للطلب، بحيث يتم ترطيب الصفحة دون عدم تطابق.

| | React، Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| المسار | `usePathname()` | `usePathname()` إرجاع ملحق | `usePathname()` يرجع مرجعا | `$pathname` مخزن |
| معلمات الطريق | `useParams()` | `useParams()` الواصل | `useParams()` المرجع | `$params` مخزن |
| الاستعلام | `useSearchParams()` | `useSearchParams()` الواصل | `useSearchParams()` المرجع | `$searchParams` مخزن |
| كل شيء | `useLocation()` | `useLocation()` الملحق | `useLocation()` المرجع | `$location` مخزن |
| انتقل | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| الملاحة في الرحلة | `useTransition()` | `useTransition()` الملحق | `useTransition()` المرجع | `useTransition()` مخزن |
| تطابق المسار | `useMatch(path?)` | `useMatch(path?)` الملحق | `useMatch(path?)` المرجع | `useMatch(path?)` مخزن |
| اسأل قبل المغادرة | `useBlocker(dirty)` | `useBlocker(dirty())` في `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` في `$effect` |

الاستعلام هو `URLSearchParams`. `useRouter()` و `router` يعطي `push(href)`، `replace(href)`، `back()`، `forward()`، `refresh()` و `prefetch(href)`؛ `push` و `replace` يقبل `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## إظهار حالة التحميل مع `useTransition`

`useTransition()` يخبرنا ما إذا كان نظام ملاحة العميل في حالة طيران. `pending` هو `true` من النقر حتى تظهر الصفحة التالية، و `next` هو الموقع الذي ستذهب إليه. ويعود إلى `{ pending: false, next: null }` بمجرد ظهور الصفحة، أو عند توقف التنقل، أو عند استبدالها بصفحة جديدة.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## مطابقة المسار مع `useMatch`

`useMatch(path)` يخبرنا ما إذا كان `path` يطابق مسار العميل. ترجع `{ match, found }`، حيث يحمل `match` المسار `file`، و `layouts` و `params`، أو هو `null`. بدون مسار، فإنه يطابق الصفحة الحالية ويتبع كل تنقل. أثناء تقديم الخادم، لا يوجد جهاز توجيه حتى الآن، لذا فإن `match` هو `null` و `found` هو `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## قبض على الصفحة التي تفشل مع `ErrorBoundary`

`ErrorBoundary` يُظهر احتياطيًا بدلاً من أطفاله عندما يرمي أحدهم أثناء عرضه في المتصفح. يتلقى الإجراء الاحتياطي الخطأ و `reset`، مما يعرض الأطفال مرة أخرى.

| الإطار | استيراد | احتياطي |
|---|---|---|
| React، Preact، Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | `fallback` دالة prop؛ يذهب الأطفال إلى الفتحة الافتراضية |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | `fallback` مقتطف |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

لا يمسك:

- خطأ يتم طرحه لاحقًا، في معالج الحدث، أو المؤقت، أو الوعد: اكتشفه حيث يحدث. Vue هو الاستثناء لمعالجات الأحداث الخاصة به، والتي تصل أخطائها إلى الحدود؛
- صفحة لا يستطيع جهاز التوجيه تحميلها: يطلب المتصفح من الخادم بدلاً من ذلك (راجع [ما يفعله جهاز التوجيه](#what-the-router-does)).

## اسأل قبل مغادرة الصفحة التي تحتوي على تغييرات غير محفوظة

`useBlocker(dirty, message?)` يسأل الزائر قبل مغادرته بينما `dirty` صحيح: رابط، `router.push`، أزرار الرجوع والأمام، إعادة التحميل وعلامة تبويب مغلقة. يظهر تنقل العميل `message` في `confirm()`: نعم يستمر، لا يبقى في الصفحة. تعرض علامة التبويب المغلقة أو إعادة التحميل السؤال الخاص بالمتصفح، والذي لا يمكن لأي صفحة الإجابة عليه. بدون رسالة، يكون السؤال هو "لديك تغييرات غير محفوظة. هل تريد مغادرة هذه الصفحة؟".

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

تتم قراءة العلم حيث يتغير، في لغة كل إطار:

| الإطار | اتبع العلم |
|---|---|
| React، Preact | `useBlocker(dirty)` على كل تقديم |
| Vue | `useBlocker(dirty)` مع `dirty` مرجع أو محسوب |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` يتخذ أيضًا وظيفة، لقرار يعتمد على المكان الذي يذهب إليه الزائر. يتلقى الموقع التالي والموقع الحالي، ويعيد سببًا (سلسلة نصية) للبقاء، أو لا شيء للاستمرار:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

الوظيفة لا تسأل من تلقاء نفسها ولا تقوم بإعادة التحميل؛ اتصل بـ `confirm()` فيه للسؤال.

## `Image`

`Image` يعرض `<img>` كسولًا بشكل افتراضي ولا يغير التخطيط عندما يكون حجمه معروفًا.

| الإطار | استيراد |
|---|---|
| React، Preact، Solid، Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` مطلوب؛ استخدم `alt=""` لصورة زخرفية. يحذر Nexy مرة واحدة عندما يكون مفقودًا.
- مع كل من `width` و `height`، تمنح السمات المتصفح نسبة العرض إلى الارتفاع وتبقى الصورة سائلة (`height: auto; max-width: 100%`).
- `priority` يقوم بتحميل الصورة الآن بأولوية عالية، لتلك التي تكون مرئية عند الوصول.
- `fill` يجعل الصورة تغطي موقعها الأصلي، متجاهلاً `width` و `height`.
- `sizes` و `srcSet` يمرون. لا يقوم Nexy بتغيير حجم الصور أو تحويلها.

## رابط من صفحة `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` يجعل `<a href="/about" data-nexy-link="true">`. كل سمة و `href` تم تخطيها من HTML.

## ما يفعله جهاز التوجيه

أثناء التنقل، يقوم جهاز التوجيه بما يلي:

1. يطابق المسار مع مسارات العميل (`.tsx`، `.jsx`، `.vue`، `.svelte`)؛
2. يستورد ويعرض الصفحة و[تخطيطاتها](../layouts/README.md) **أولاً**، وبعدها فقط ينقل عنوان URL باستخدام `history.pushState`، بحيث لا يعرض شريط العناوين أبدًا صفحة فاشلة؛
3. يرسل حدث `nexy:navigated` على `document`؛
4. يتم التمرير إلى الأعلى، أو إلى الهدف `#fragment`.

يؤدي التنقل الأحدث إلى إلغاء التنقل الأقدم الذي لا يزال قيد العرض. إذا تعذر عرض الصفحة، يطلب المتصفح من الخادم بدلاً من ذلك. يعرض الزران الخلفي والأمامي صفحة هذا الإدخال ويستعيدان موضع التمرير الخاص به.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

يبدأ جهاز التوجيه فقط في مشروع به مسارات العميل، لذا يحتفظ المشروع المقدم من الخادم بزر الرجوع الخاص بالمتصفح واستعادة التمرير.

## الخطوات التالية

- [التخطيطات](../layouts/README.md)
- [المسؤولية الاجتماعية للشركات](../../../rendering/csr.md)
- [المكونات](../../../views/nexy/components.md)
