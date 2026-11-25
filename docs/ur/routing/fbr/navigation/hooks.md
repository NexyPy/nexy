# کانٹے

ہکس موجودہ HTTP درخواست کو `.nexy` صفحہ، API ہینڈلر یا ماڈیولر کنٹرولر کے اندر سے پڑھتے ہیں۔ ان کے نام کلائنٹ روٹر (`@nexy/client`) کے ہکس سے ملتے ہیں جہاں وہ ایک ہی کام کرتے ہیں۔

> [!NOTE]
> ہکس صرف اس وقت کام کرتے ہیں جب درخواست کو سنبھالا جا رہا ہو۔ کسی کو کہیں اور پکارنے سے `RuntimeError` اضافہ ہوتا ہے۔

## ہکس

| ہک | واپسی |
|---|---|
| `usePathname()` | درخواست کا راستہ، جیسے `"/blog/post-1"` |
| `useSearchParams()` | استفسار کی تار بطور `dict[str, str]`، پہلی قدر فی کلید |
| `useParams()` | ڈائنامک پاتھ پیرامیٹرز، جیسے `{"slug": "post-1"}` |
| `useQuery()` | `useParams()` کا اصل نام، موجودہ صفحات کے لیے رکھا گیا ہے۔ |
| `useRequest()` | Starlette درخواست، جس کے لیے دوسرے ہکس کا احاطہ نہیں کرتے |
| `useHeaders()` | درخواست کے ہیڈر بطور `dict[str, str]`، چھوٹے کیس میں نام |
| `useUrl()` | مکمل URL: `.scheme`، `.hostname`، `.port`، `.path`، `.query` |
| `useIsActive(href, exact=False)` | چاہے `href` موجودہ صفحہ ہے یا اس کے والدین میں سے ایک ہے۔ |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | تمام کوکیز بطور `dict[str, str]` |
| `useSession()` | سیشن ڈکٹ، `{}` جب سیشنز فعال نہ ہوں۔ |
| `useToc(depth_range="2-6")` | مندرجات کا جدول موجودہ صفحہ کے لیے HTML، `""` جب کوئی نہیں۔ |
| `useViews(path, context=None)` | ایک اور نقطہ نظر پیش کرتا ہے اور ایک `HTMLResponse` واپس کرتا ہے |

## درخواست پڑھیں

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## نیویگیشن بار میں ایک فعال لنک

`useIsActive` اسی اصول کی پیروی کرتا ہے جو کلائنٹ پر ہے: استفسار کی تار، ٹکڑا اور ٹریلنگ سلیش کو نظر انداز کر دیا جاتا ہے، والدین کا لنک اس کے بچوں پر فعال ہوتا ہے جب تک کہ `exact` سیٹ نہ ہو، اور `/` صرف `/` پر فعال ہو۔

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## نوٹس

- `useQuery()` **path** پیرامیٹرز لوٹاتا ہے، استفسار کی تار نہیں، یہی وجہ ہے کہ `useParams()` موجود ہے۔ استفسار کی تار `useSearchParams()` ہے۔
- `useRouter()` یہاں درخواست ہک ہے۔ یہ `useRouter` کنفگ فیلڈ نہیں ہے جو ایک `APIRouter` کو ماؤنٹ کرتا ہے۔
- `useSession()` ضروریات `useSession = {...}` `nexyconfig.py` میں؛ اس کے بغیر ڈکٹ خالی ہے۔
- `useViews("about.tsx", {"title": "About"})` HTML واپس کرتا ہے: ایک `.nexy` منظر اس کے مرتب کردہ ماڈیول کے ذریعہ پیش کیا جاتا ہے، ایک `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` منظر کلائنٹ ماؤنٹ کنٹینر بن جاتا ہے۔

## اگلے اقدامات

- [صفحہ کی منتقلی کیسے کام کرتی ہے](page-transitions.md): جب کلائنٹ راؤٹر کسی صفحے کو تبدیل کرتا ہے تو کیا ہوتا ہے
- [صفحات](../pages/README.md): متحرک طبقات اور ترتیب
- [ترکیبیں](../../../guides/recipes.md): آزمائشی سائن ان فلو `useSession()` پر بنایا گیا
- [کنفیگ ](../../../reference/config.md): سیشنز اور لوکیلز کو فعال کریں۔
- [.nexy فائلیں](../../../views/nexy/README.md): جہاں ہکس کو عام طور پر کہا جاتا ہے۔
