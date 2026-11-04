# واجهة برمجة تطبيقات بايثون

كل اسم يصدره Nexy إلى كود Python الخاص بك، حسب الوحدة. يقوم الاختبار بفحص هذه الصفحة مقابل الكود الموجود
كلا الاتجاهين: الاسم المدرج هنا يجب أن يكون موجودًا، والاسم الذي يصدره الكود يجب أن يكون مدرجًا هنا.

## `nexy`

مكونات لقوالب `.nexy` وخطافات الطلب.

| الاسم | ما هو |
|---|---|
| `Audio`، `Video` | اللاعبين الأصليين `<audio>` و `<video>`، انظر [المكونات](../views/nexy/components.md) |
| `Image` | وهو `<img>` يتم التحميل ببطء بشكل افتراضي |
| `Link` | من جانب العميل `<a>` مع جلب مسبق اختياري |
| `Import` | استيراد مكون العميل إلى صفحة `.nexy` |
| `Template` | عرض قوالب Jinja2 وMarkdown |
| `Vite` | علامة عميل Vite التي تحتاجها كل صفحة |
| `Form` | عنصر نائب بدون سلوك: استخدم `<form>` عادي مع [إجراء](../guides/actions.md) |
| `usePathname` | مسار الطلب الحالي |
| `useSearchParams` | سلسلة الاستعلام كإملاء |
| `useParams` | معلمات المسار الديناميكي كإملاء، مثل `useParams()` على العميل |
| `useQuery` | الاسم الأصلي لـ `useParams`، محفوظ للصفحات الموجودة (لا يقرأ سلسلة الاستعلام) |
| `useRequest` | الطلب الحالي، لما لا تغطيه الخطافات الأخرى |
| `useHeaders` | رؤوس الطلب كإملاء بأسماء صغيرة |
| `useUrl` | الرابط الكامل: `.scheme`، `.hostname`، `.path`، `.query` |
| `useIsActive` | سواء كان الرابط يشير إلى الصفحة الحالية أو أحد أصولها، لشريط التنقل |
| `useRouter` | `path` و `base_url` و `url_for` من الطلب الحالي |
| `useSession` | إملاء الجلسة، فارغ عند إيقاف الجلسات |
| `useCookies` | ملفات تعريف الارتباط للطلب كإملاء |
| `useToc` | جدول محتويات الصفحة الحالية، بتنسيق HTML |
| `useViews` | عرض ملف عرض مثل `about.tsx` من معالج |
| `setMetadata`، `useMetadata` | تسمية العنوان وعلامات الرأس للصفحة، وكتابتها في التخطيط |
| `redirect`، `permanentRedirect` | أرسل الزائر إلى مكان آخر (307، 308) وأوقف الطلب |
| `notFound`، `forbidden`، `unauthorized` | الإجابة على 404 أو 403 أو 401 من أي مكان |

تعمل الخطافات داخل الطلب فقط: راجع [الخطافات](../routing/fbr/navigation/hooks.md).

## `nexy.http`

مفردات HTTP للمعالج. قم بالاستيراد من هنا بدلاً من FastAPI، بحيث يعتمد المعالجون لديك
على عقد Nexy.

| الاسم | ما هو |
|---|---|
| `Request`، `Response` | الطلب الوارد والرد الصادر |
| `HTTPException` | إيقاف المعالج بالحالة و `detail` |
| `status` | رموز الحالة المسماة، مثل `status.HTTP_404_NOT_FOUND` |
| `Depends` | قم بتشغيل دالة أولاً وتمرير نتيجتها إلى |
| `Header`، `Cookie`، `Query`، `Path`، `Body` | حيث تأتي المعلمة من |
| `Form`، `File`، `UploadFile` | حقول النموذج والتحميلات (تحتاج إلى `python-multipart`) |
| `BackgroundTasks` | العمل الذي يتم بعد إرسال الإجابة |
| `JSONResponse`، `HTMLResponse`، `PlainTextResponse` | إجابات ذات نوع محتوى ثابت |
| `RedirectResponse` | إعادة توجيه HTTP |
| `redirect`، `permanentRedirect` | رفع إعادة توجيه (307، 308) من صفحة أو معالج أو وحدة تحكم أو حارس |
| `notFound`، `forbidden`، `unauthorized` | جمع 404 أو 403 أو 401 من نفس الأماكن |
| `FileResponse`، `StreamingResponse` | الجواب بملف أو دفق |

## `nexy.decorators`

| الاسم | ما هو |
|---|---|
| `Action` | تحويل دالة إلى نقطة نهاية `POST`، راجع [الإجراءات](../guides/actions.md) |
| `revalidate` | أخبر المتصفح بالصفحات التي أصبح الإجراء قديمًا |
| `Module`، `Controller` | يعلن عن وحدة ووحدة تحكم في [جهاز التوجيه المعياري](../routing/modular/README.md) |
| `Injectable`، `Container`، `Scope` | [حقن التبعية](../routing/modular/dependency-injection.md) وعمرها |
| `UseGuard`، `Middleware` | حراسة أو لف معالج واحد، انظر [الحراس](../routing/modular/guards-and-metadata.md) |
| `UseRoute`، `useRoute`، `RouteMeta` | قم بتسمية المسار ووصفه لـ OpenAPI |
| `UseResponse`، `ResponseMeta` | وصف جواب الطريق |
| `HTTP_METHODS` | طرق HTTP التي قد يحددها ملف المعالج |
| `ACTIONS_STORE` | سجل الإجراءات للأدوات والاختبارات |

## `nexy.testing`

| الاسم | ما هو |
|---|---|
| `render` | HTML لمكون `.nexy` لدعائم معينة، بدون خادم، راجع [اختبار](../guides/testing.md) |

## إلى أين بعد ذلك

- [التكوين](config.md): الحقول `use*` خلف هذه الأسماء
- [الاستثناءات والأخطاء](exceptions.md): ما يجيب عليه كل فشل
- [فهرس التوثيق](../README.md): الصفحة الخاصة بما تقوم ببنائه