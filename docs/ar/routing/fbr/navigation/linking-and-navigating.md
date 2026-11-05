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

| الإطار | الاستيراد |
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

| الدعامة | المعنى |
|---|---|
| `href` | مسار المشروع (الخطأ المطبعي هو خطأ في النوع)، اختياريًا مع `?query` أو `#fragment`، أو عنوان URL خارجي. |
| `replace` | استبدل إدخال السجل بدلاً من إضافة واحد. |
| `scroll` | `false` يحافظ على موضع التمرير بعد التنقل. الافتراضي: `true`. |
| `prefetch` | `'intent'` (افتراضي) يقوم بتحميل الصفحة عند التمرير أو التركيز أو اللمس؛ `'viewport'` عندما يتم تمرير الرابط إلى العرض؛ `false` أبدا. |
| `activeClassName` | يضاف إلى الفصل بينما يشير الرابط إلى الصفحة الحالية أو صفحة أسفلها (`activeClass` في Vue و Svelte). |
| `exact` | نشط فقط على الصفحة المحددة. |

الرابط الذي يشير إلى الصفحة الحالية يحصل أيضًا على `aria-current="page"`.

## خطافات

الموقع متاح في كل إطار، في لغة ذلك الإطار. أثناء العملية الأولى، يقوم جانب الخادم بعرض إجابة الخطافات بعنوان URL للطلب، بحيث يتم ترطيب الصفحة دون عدم تطابق.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| المسار | `usePathname()` | `usePathname()` يُرجع موصلًا | `usePathname()` يُرجع مرجعًا | `$pathname` مخزن |
| معلمات المسار | `useParams()` | `useParams()` الوصول | `useParams()` المرجع | `$params` المتجر |
| الاستعلام | `useSearchParams()` | `useSearchParams()` الولوج | `useSearchParams()` المرجع | `$searchParams` المتجر |
| كل شيء | `useLocation()` | `useLocation()` ملحق | `useLocation()` المرجع | `$location` المتجر |
| التنقل | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

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

## `Image`

`Image` يعرض `<img>` كسولًا بشكل افتراضي ولا يغير التخطيط عندما يكون حجمه معروفًا.

| الإطار | الاستيراد |
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
