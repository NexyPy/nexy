# Python API

ہر نام Nexy آپ کے Python کوڈ کو ماڈیول کے ذریعے برآمد کرتا ہے۔ ایک ٹیسٹ اس صفحہ کو کوڈ کے خلاف دونوں سمتوں میں چیک کرتا ہے: یہاں درج ایک نام کا ہونا ضروری ہے، اور ایک نام جو کوڈ برآمد کرتا ہے یہاں درج ہونا چاہیے۔

## `nexy`

`.nexy` ٹیمپلیٹس اور درخواست کے ہکس کے اجزاء۔

| نام | یہ کیا ہے |
|---|---|
| `Audio`، `Video` | مقامی `<audio>` اور `<video>` کھلاڑی، دیکھیں [اجزاء](../views/nexy/components.md) |
| `Image` | ایک `<img>` جو پہلے سے طے شدہ طور پر سستی سے لوڈ ہوتا ہے۔ |
| `Link` | ایک کلائنٹ سائیڈ `<a>` اختیاری پری فیچ کے ساتھ |
| `Import` | ایک کلائنٹ کے جزو کو `.nexy` صفحہ میں درآمد کریں۔ |
| `Template` | رینڈر Jinja2 اور Markdown ٹیمپلیٹس |
| `Vite` | Vite کلائنٹ ٹیگ ہر صفحے کی ضرورت ہے۔ |
| `Form` | ایک پلیس ہولڈر جس میں کوئی رویہ نہیں ہے: ایک سادہ `<form>` ایک [ایکشن](../guides/actions.md) کے ساتھ استعمال کریں |
| `usePathname` | موجودہ درخواست کا راستہ |
| `useSearchParams` | استفسار کی تار بطور ڈکٹ |
| `useParams` | ڈائنامک پاتھ پیرامیٹرز بطور ڈیکٹ، جیسے کلائنٹ پر `useParams()` |
| `useQuery` | `useParams` کا اصل نام، موجودہ صفحات کے لیے رکھا گیا ہے (یہ استفسار کی تار نہیں پڑھتا ہے) |
| `useRequest` | موجودہ درخواست، جس کے لیے دوسرے ہکس کا احاطہ نہیں کیا گیا ہے۔ |
| `useHeaders` | درخواست کے ہیڈر کو کم کیس کے ناموں کے ساتھ ایک ڈکٹ کے طور پر |
| `useUrl` | مکمل URL: `.scheme`، `.hostname`، `.path`، `.query` |
| `useIsActive` | چاہے کوئی لنک موجودہ صفحہ پر یا اس کے والدین میں سے ایک پر، نیویگیشن بار کے لیے |
| `useRouter` | موجودہ درخواست کی `path`، `base_url` اور `url_for` |
| `useSession` | سیشن ڈکٹ، سیشن آف ہونے پر خالی |
| `useCookies` | ایک ڈکٹ کے طور پر درخواست کوکیز |
| `useToc` | موجودہ صفحہ کے مشمولات کا جدول، بطور HTML |
| `useViews` | ہینڈلر سے ایک ویو فائل رینڈر کریں جیسے `about.tsx` |
| `setMetadata`، `useMetadata` | کسی صفحہ کے عنوان اور ہیڈ ٹیگز کو نام دیں، اور انہیں ترتیب میں لکھیں۔ |
| `redirect`، `permanentRedirect` | وزیٹر کو کہیں اور بھیجیں (307, 308) اور درخواست روک دیں۔ |
| `notFound`، `forbidden`، `unauthorized` | کہیں سے بھی 404، 403 یا 401 جواب دیں۔ |

ہکس صرف درخواست کے اندر کام کرتے ہیں: دیکھیں [ہکس](../routing/fbr/navigation/hooks.md)۔

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

## `nexy.http`

ہینڈلر کی HTTP الفاظ۔ FastAPI کے بجائے یہاں سے درآمد کریں، لہذا آپ کے ہینڈلرز Nexy کے معاہدے پر منحصر ہیں۔

| نام | یہ کیا ہے |
|---|---|
| `Request`، `Response` | آنے والی درخواست اور باہر جانے والا جواب |
| `HTTPException` | ہینڈلر کو ایک حیثیت اور ایک `detail` کے ساتھ روکیں |
| `status` | نامزد اسٹیٹس کوڈز، جیسے `status.HTTP_404_NOT_FOUND` |
| `Depends` | پہلے ایک فنکشن چلائیں اور اس کا نتیجہ پاس کریں۔ |
| `Header`، `Cookie`، `Query`، `Path`، `Body` | جہاں سے ایک پیرامیٹر آتا ہے۔ |
| `Form`، `File`، `UploadFile` | فارم فیلڈز اور اپ لوڈز (ضرورت `python-multipart`) |
| `BackgroundTasks` | کام جو جواب بھیجے جانے کے بعد چلتا ہے۔ |
| `JSONResponse`، `HTMLResponse`، `PlainTextResponse` | ایک مقررہ مواد کی قسم کے ساتھ جوابات |
| `RedirectResponse` | ایک HTTP ری ڈائریکٹ |
| `redirect`، `permanentRedirect` | ایک صفحہ، ایک ہینڈلر، ایک کنٹرولر یا گارڈ سے ایک ری ڈائریکٹ (307، 308) اٹھائیں |
| `notFound`، `forbidden`، `unauthorized` | اسی جگہوں سے 404، 403 یا 401 بلند کریں۔ |
| `FileResponse`، `StreamingResponse` | فائل یا اسٹریم کے ساتھ جواب دیں۔ |

<!-- router:fbr,custom -->
```python filename="src/routes/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/items/items_by_id_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


@Controller("/api/items/{id}")
class ItemsByIdApiController:
    async def get(self, id: int, key: str = Depends(api_key)):
        return {"id": id}
```

روٹ ماڈیول کے `controllers` میں کنٹرولر کی فہرست بنائیں۔
<!-- /router -->

## `nexy.decorators`

| نام | یہ کیا ہے |
|---|---|
| `Action` | فنکشن کو `POST` اختتامی نقطہ میں تبدیل کریں، [ایکشنز](../guides/actions.md) دیکھیں |
| `revalidate` | براؤزر کو بتائیں کہ کون سے صفحات کو ایکشن نے باسی بنا دیا ہے۔ |
| `Module`، `Controller` | [ماڈیولر روٹر](../routing/modular/README.md) میں ایک ماڈیول اور ایک کنٹرولر کا اعلان کریں |
| `Injectable`، `Container`، `Scope` | [انحصار انجیکشن ](../routing/modular/dependency-injection.md) اور اس کی زندگی بھر |
| `UseGuard`، `Middleware` | ایک ہینڈلر کی حفاظت یا لپیٹنا، دیکھیں [گارڈز](../routing/modular/guards-and-metadata.md) |
| `UseRoute`، `useRoute`، `RouteMeta` | راستے کا نام دیں اور اس کی وضاحت کریں OpenAPI |
| `UseResponse`، `ResponseMeta` | راستے کا جواب بیان کریں۔ |
| `HTTP_METHODS` | HTTP طریقے جن کی ایک ہینڈلر فائل وضاحت کر سکتی ہے۔ |
| `ACTIONS_STORE` | ٹولنگ اور ٹیسٹ کے لیے اعمال کی رجسٹری |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| نام | یہ کیا ہے |
|---|---|
| `render` | دیئے گئے پرپس کے لیے ایک `.nexy` جزو کا HTML، بغیر سرور کے، دیکھیں [ٹیسٹنگ](../guides/testing.md) |

```python filename="tests/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## جہاں اگلا

- [ترتیب ](config.md): ان ناموں کے پیچھے `use*` فیلڈز
- [مستثنیات اور غلطیاں](exceptions.md): ہر ناکامی کا کیا جواب ہوتا ہے۔
- [دستاویزی اشاریہ](../README.md): وہ صفحہ جو آپ بنا رہے ہیں۔
