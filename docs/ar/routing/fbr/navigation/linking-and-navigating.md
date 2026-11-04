# الربط والتنقل

باستخدام توجيه العميل (`useCSR = True`)، يؤدي الارتباط بين صفحتين إلى تبديل الصفحة في المتصفح بدلاً من ذلك
من إعادة تحميل الوثيقة. تحافظ التخطيطات على حالتها.

## الروابط العادية تعمل بالفعل

يتم التنقل في كل `<a href>` إلى صفحة من مشروعك على العميل، بدون أي مكون أو علامة:

```html
<a href="/about">About</a>
```

يتم ترك رابط للمتصفح، ويقوم بتحميل الصفحة بشكل طبيعي، عندما:

- يتم الضغط باستمرار على مفتاح التعديل، أو أن الزر ليس هو المفتاح الرئيسي؛
- له `target` (غير `_self`)، `download`، `rel="external"` أو `data-nexy-reload`؛
- إن `href` أصل آخر، أو `mailto:` أو `tel:` صلة، أو `#fragment` فقط؛
- لا يتطابق المسار مع أي مسار للعميل، لذا يجيب عليه الخادم.

## `Link`

`Link` هو نفس المرساة مع ما لا يستطيع الشخص العادي فعله: يتم فحص `href` الخاص به مقابل مساراتك،
يقوم بتدفئة الصفحة المستهدفة، ويعرف متى يشير إلى الصفحة الحالية. يقوم Nexy بإنشاء `Link`
إطار العمل الخاص بك في `__nexy__/src` عند تشغيل `nx dev` أو `nx build`.

| الإطار | الاستيراد |
|---|---|
| رد فعل، بريكت، صلب، رؤية | `import { Link } from "@nexy/client"` |
| رشيقة | `import Link from "@nexy/Link.svelte"` |

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
| `activeClassName` | تتم إضافته إلى الفصل بينما يشير الرابط إلى الصفحة الحالية أو صفحة أسفلها (`activeClass` في Vue وSvelte). |
| `exact` | نشط فقط على الصفحة المحددة. |

الرابط الذي يشير إلى الصفحة الحالية يحصل أيضًا على `aria-current="page"`.

## خطافات

الموقع متاح في كل إطار، في لغة ذلك الإطار. خلال الفترة الأولى،
يعرض جانب الخادم إجابة الخطافات بعنوان URL للطلب، بحيث يتم ترطيب الصفحة بدون ملف
عدم تطابق.

| | تفاعل، تفاعل | صلب | رؤية | رفيع |
|---|---|---|---|---|
| المسار | `usePathname()` | `usePathname()` يُرجع موصل | `usePathname()` يُرجع مرجعًا | `$pathname` مخزن |
| معلمات الطريق | `useParams()` | `useParams()` الوصول | `useParams()` المرجع | `$params` المتجر |
| الاستعلام | `useSearchParams()` | `useSearchParams()` الولوج | `useSearchParams()` المرجع | `$searchParams` المتجر |
| كل شيء | `useLocation()` | `useLocation()` الولوج | `useLocation()` المرجع | `$location` المتجر |
| التنقل | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

الاستعلام هو `URLSearchParams`. `useRouter()` و `router` يعطي `push(href)`، `replace(href)`،
`back()`، `forward()`، `refresh()`، `prefetch(href)`؛ `push` و`replace` يقبل
`{ scroll: false }`.

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

`Image` يعرض `<img>` كسولًا بشكل افتراضي ولا يغير التخطيط عندما يكون حجمه
معروف.

| الإطار | الاستيراد |
|---|---|
| رد فعل، بريكت، صلب، رؤية | `import { Image } from "@nexy/client"` |
| رشيقة | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` مطلوب؛ استخدم `alt=""` لصورة زخرفية. يحذر Nexy مرة واحدة عندما يكون مفقودًا.
- مع كل من `width` و `height`، تمنح السمات المتصفح نسبة العرض إلى الارتفاع والصورة
  يبقى سائلاً (`height: auto; max-width: 100%`).
- `priority` يقوم بتحميل الصورة الآن بأولوية عالية، لتلك التي تكون مرئية عند الوصول.
- `fill` يجعل الصورة تغطي موقعها الأصلي، متجاهلاً `width` و `height`.
-  `sizes` و `srcSet` يمرون. لا يقوم Nexy بتغيير حجم الصور أو تحويلها.

## رابط من صفحة `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` يعرض
`<a href="/about" data-nexy-link="true">`. كل سمة و`href` تم تخطيها من HTML.

## ما يفعله جهاز التوجيه

أثناء التنقل، يقوم جهاز التوجيه بما يلي:

1. يطابق المسار مع مسارات العميل (`.tsx`، `.jsx`، `.vue`، `.svelte`)؛
2. يستورد ويعرض الصفحة و[تخطيطاتها](../layouts/README.md) **أولاً**، وعندها فقط
   ينقل عنوان URL باستخدام `history.pushState`، بحيث لا يعرض شريط العناوين أبدًا صفحة فاشلة؛
3. يرسل `nexy:navigated` حدثًا على `document`؛
4. للتمرير إلى الأعلى، أو إلى الهدف `#fragment`.

يؤدي التنقل الأحدث إلى إلغاء التنقل الأقدم الذي لا يزال قيد العرض. إذا تعذر عرض الصفحة، فسيقوم المتصفح
يطلب من الخادم ذلك بدلاً من ذلك. يعرض الزران الخلفي والأمام صفحة هذا الإدخال و
استعادة موضع التمرير الخاص به.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

يبدأ جهاز التوجيه فقط في مشروع يحتوي على مسارات العميل، لذا يحتفظ المشروع المقدم من الخادم
زر الرجوع الخاص بالمتصفح واستعادة التمرير.

## الخطوات التالية

- [التخطيطات](../layouts/README.md)
-  [المسؤولية الاجتماعية للشركات](../../../rendering/csr.md)
- [المكونات](../../../views/nexy/components.md)