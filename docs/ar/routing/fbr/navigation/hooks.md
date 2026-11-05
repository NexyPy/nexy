# خطافات

تقرأ الخطافات طلب HTTP الحالي من داخل صفحة `.nexy` أو معالج API أو وحدة تحكم معيارية. تتطابق أسماؤهم مع خطافات جهاز توجيه العميل (`@nexy/client`) حيث يفعلون نفس الشيء.

> [!ملاحظة]
> تعمل الخطافات فقط أثناء معالجة الطلب. ونداء أحد في أي مكان آخر يرفع `RuntimeError`.

## السنانير

| الخطاف | يُرجع |
|---|---|
| `usePathname()` | مسار الطلب، على سبيل المثال: `"/blog/post-1"` |
| `useSearchParams()` | سلسلة الاستعلام كـ `dict[str, str]`، القيمة الأولى لكل مفتاح |
| `useParams()` | معلمات المسار الديناميكي، على سبيل المثال. `{"slug": "post-1"}` |
| `useQuery()` | الاسم الأصلي لـ `useParams()`، محفوظ للصفحات الموجودة |
| `useRequest()` | الطلب Starlette، لما لا تغطيه سائر الخطافات |
| `useHeaders()` | رؤوس الطلب كـ `dict[str, str]`، الأسماء بالأحرف الصغيرة |
| `useUrl()` | الرابط الكامل: `.scheme`، `.hostname`، `.port`، `.path`، `.query` |
| `useIsActive(href, exact=False)` | سواء كانت `href` هي الصفحة الحالية أو أحد أصولها |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | جميع ملفات تعريف الارتباط كـ `dict[str, str]` |
| `useSession()` | إملاء الجلسة، `{}` عندما لا يتم تمكين الجلسات |
| `useToc(depth_range="2-6")` | جدول محتويات HTML للصفحة الحالية، `""` عند عدم وجود شيء |
| `useViews(path, context=None)` | يعرض عرضًا آخر ويعيد `HTMLResponse` |

## اقرأ الطلب

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## رابط نشط في شريط التنقل

يتبع `useIsActive` نفس القاعدة كما هو الحال في العميل: يتم تجاهل سلسلة الاستعلام والجزء والشرطة المائلة اللاحقة، ويكون الارتباط إلى أحد الوالدين نشطًا على أبنائه ما لم يتم تعيين `exact`، ويكون `/` نشطًا فقط على `/`.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## ملاحظات

- `useQuery()` يُرجع معلمات **path**، وليس سلسلة الاستعلام، وهذا هو سبب وجود `useParams()`. سلسلة الاستعلام هي `useSearchParams()`.
- `useRouter()` هنا رابط الطلب. ليس حقل التكوين `useRouter` هو الذي يقوم بتثبيت `APIRouter`.
- `useSession()` يحتاج `useSession = {...}` في `nexyconfig.py`؛ بدونها الإملاء فارغ.
- `useViews("about.tsx", {"title": "About"})` يُرجع HTML: يتم تقديم عرض `.nexy` بواسطة الوحدة المترجمة الخاصة به، ويصبح العرض `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` حاوية تحميل عميل.

## الخطوات التالية

- [الصفحات](../pages/README.md): المقاطع والتخطيطات الديناميكية
- [الوصفات](../../../guides/recipes.md): تدفق تسجيل دخول تم اختباره مبني على `useSession()`
- [التكوين](../../../reference/config.md): تمكين الجلسات واللغات
- [.nexy files](../../../views/nexy/README.md): حيث يتم استدعاء الخطافات عادةً
