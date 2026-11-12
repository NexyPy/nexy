# Python واجهة برمجة التطبيقات

كل اسم يصدره Nexy إلى كود Python الخاص بك، حسب الوحدة. يقوم الاختبار بفحص هذه الصفحة مقابل الكود في كلا الاتجاهين: الاسم المدرج هنا يجب أن يكون موجودًا، والاسم الذي يصدره الكود يجب أن يكون مدرجًا هنا.

## `nexy`

مكونات لقوالب `.nexy` وخطافات الطلب.

| الاسم | ما هو عليه |
|---|---|
| `Audio`، `Video` | اللاعبين الأصليين `<audio>` و `<video>`، راجع [المكونات](../views/nexy/components.md) |
| `Image` | `<img>` يتم تحميله ببطء بشكل افتراضي |
| `Link` | جانب العميل `<a>` مع الجلب المسبق الاختياري |
| `Import` | استيراد مكون العميل إلى صفحة `.nexy` |
| `Template` | تقديم Jinja2 و Markdown القوالب |
| `Vite` | علامة العميل Vite التي تحتاجها كل صفحة |
| `Form` | عنصر نائب بدون سلوك: استخدم `<form>` عادي مع [إجراء](../guides/actions.md) |
| `usePathname` | مسار الطلب الحالي |
| `useSearchParams` | سلسلة الاستعلام باعتبارها dict |
| `useParams` | معلمات المسار الديناميكي كإملاء، مثل `useParams()` على العميل |
| `useQuery` | الاسم الأصلي لـ `useParams`، المحتفظ به للصفحات الموجودة (لا يقرأ سلسلة الاستعلام) |
| `useRequest` | الطلب الحالي، لما لا تغطيه الخطافات الأخرى |
| `useHeaders` | رؤوس الطلب كإملاء بأسماء صغيرة |
| `useUrl` | عنوان URL الكامل: `.scheme`، `.hostname`، `.path`، `.query` |
| `useIsActive` | ما إذا كان الرابط يشير إلى الصفحة الحالية أو إلى أحد أصولها، لشريط التنقل |
| `useRouter` | `path`، `base_url`، `url_for` من الطلب الحالي |
| `useSession` | إملاء الجلسة، فارغ عند إيقاف الجلسات |
| `useCookies` | ملفات تعريف الارتباط الخاصة بالطلب بمثابة إملاء |
| `useToc` | جدول محتويات الصفحة الحالية، مثل HTML |
| `useViews` | تقديم ملف عرض مثل `about.tsx` من معالج |
| `setMetadata`، `useMetadata` | قم بتسمية العنوان وعلامات الرأس الخاصة بالصفحة، واكتبها في التخطيط |
| `redirect`، `permanentRedirect` | إرسال الزائر إلى مكان آخر (307، 308) وإيقاف الطلب |
| `notFound`، `forbidden`، `unauthorized` | الإجابة على 404 أو 403 أو 401 من أي مكان |

تعمل الخطافات داخل الطلب فقط: راجع [الخطافات](../routing/fbr/navigation/hooks.md).

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

مفردات HTTP للمعالج. قم بالاستيراد من هنا وليس من FastAPI، لذلك يعتمد معالجوك على عقد Nexy.

| الاسم | ما هو عليه |
|---|---|
| `Request`، `Response` | الطلب الوارد والاستجابة الصادرة |
| `HTTPException` | أوقف المعالج بالحالة و `detail` |
| `status` | رموز الحالة المسماة، مثل `status.HTTP_404_NOT_FOUND` |
| `Depends` | قم بتشغيل دالة أولاً وتمرير نتيجتها |
| `Header`، `Cookie`، `Query`، `Path`، `Body` | من أين تأتي المعلمة |
| `Form`، `File`، `UploadFile` | حقول النموذج والتحميلات (`python-multipart` فقط لـ `multipart/form-data`) |
| `BackgroundTasks` | العمل الذي يتم تشغيله بعد إرسال الإجابة |
| `JSONResponse`، `HTMLResponse`، `PlainTextResponse` | الإجابات بنوع محتوى ثابت |
| `RedirectResponse` | إعادة توجيه HTTP |
| `redirect`، `permanentRedirect` | رفع إعادة توجيه (307، 308) من صفحة أو معالج أو وحدة تحكم أو حارس |
| `notFound`، `forbidden`، `unauthorized` | ارفع 404 أو 403 أو 401 من نفس الأماكن |
| `FileResponse`، `StreamingResponse` | الإجابة مع ملف أو دفق |

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

قم بإدراج وحدة التحكم في `controllers` من الوحدة الجذرية.
<!-- /router -->

## `nexy.decorators`

| الاسم | ما هو عليه |
|---|---|
| `Action` | تحويل دالة إلى نقطة نهاية `POST`، راجع [الإجراءات](../guides/actions.md) |
| `revalidate` | أخبر المتصفح بالصفحات التي جعل الإجراء قديمًا |
| `Module`، `Controller` | أعلن عن وحدة ووحدة تحكم في [جهاز التوجيه المعياري](../routing/modular/README.md) |
| `Injectable`، `Container`، `Scope` | [حقن التبعية](../routing/modular/dependency-injection.md) وعمرها |
| `UseGuard`، `Middleware` | حراسة أو لف معالج واحد، راجع [الحراس](../routing/modular/guards-and-metadata.md) |
| `UseRoute`، `useRoute`، `RouteMeta` | قم بتسمية الطريق ووصفه لـ OpenAPI |
| `UseResponse`، `ResponseMeta` | وصف إجابة الطريق |
| `HTTP_METHODS` | طرق HTTP التي قد يحددها ملف المعالج |
| `ACTIONS_STORE` | سجل الإجراءات، للأدوات والاختبارات |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| الاسم | ما هو عليه |
|---|---|
| `render` | HTML لمكون `.nexy` لدعائم معينة، بدون خادم، راجع [اختبار](../guides/testing.md) |

```python filename="الاختبارات/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## أين التالي

- [التكوين](config.md): الحقول `use*` خلف هذه الأسماء
- [الاستثناءات والأخطاء](exceptions.md): ما يجيب عليه كل فشل
- [فهرس التوثيق](../README.md): الصفحة الخاصة بما تقوم ببنائه
