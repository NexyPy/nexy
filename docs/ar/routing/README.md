# التوجيه

لدى Nexy جهازي توجيه أصليين. يمكنك اختيار واحد لكل ميزة؛ يمكنهم التعايش في نفس التطبيق.

**لست متأكدا؟ استخدم التوجيه المستند إلى الملف.** وهو يغطي الصفحات ونقاط نهاية واجهة برمجة التطبيقات (API) بدون أي إعداد. أضف جهاز التوجيه المعياري عندما تحتاج الواجهة الخلفية إلى وحدات تحكم أو خدمات محقونة أو حراس.

| أنت تقوم بالبناء | استخدم |
|---|---|
| صفحات، محتوى، موقع به عدد قليل من نقاط النهاية | مستند إلى الملفات |
| واجهة برمجة تطبيقات كبيرة مع خدمات مشتركة عبر المسارات | معيارية |
| كلاهما: صفحات للأشخاص، وواجهة برمجة تطبيقات منظمة للأجهزة | قائمة على الملفات وموحدة معًا |

```diagram filename="جهاز التوجيه القائم على الملفات، في لمحة"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| جهاز التوجيه | المصدر | تم التمكين بواسطة |
|---|---|---|
| [المعتمد على الملف (FBR)](fbr/README.md) | كل ملف تحت `src/routes/` | الدليل موجود |
| [وحدات](modular/README.md) | وحدات تحكم ووحدات | `useRouter = AppModule` في `nexyconfig.py` |

يتم فحص FBR عند وجود `src/routes/`، حتى مع تركيب جهاز توجيه معياري.

##  التعايش والأولويات

يمكنك الجمع بين التكامل FBR والتكامل المعياري والمخصص. يقوم Nexy بتسجيل هذه المسارات بالترتيب الذي تم اكتشافها به. إذا قام جهازي توجيه بتحديد نفس مسار URL، فإن أول جهاز تم تسجيله يفوز. 

*ملاحظة: لا يوفر Nexy حاليًا تشخيصًا لتصادمات عناوين URL؛ إن الطريق الأول للمطالبة بمسار ما يؤدي ببساطة إلى تظليل المسارات الأخرى.*

## التوجيه القائم على الملف

الطريق هو ملف. عنوان URL هو المسار الخاص به ضمن `src/routes/`، بدون الامتداد. مثل Next.js، أ
يكون المشروع بأحد الوضعين المختارين بـ `useCSR`:

| | `useCSR = False` (افتراضي) | `useCSR = True` |
|---|---|---|
| صفحات | `.nexy`، `.md`، `.mdx` | ملفات إطار عمل العميل الخاص بك |
| تخطيط الجذر | `layout.nexy` | `layout.tsx` (رد الفعل) |
| مكونات العميل | المسموح بها، كجزر داخل الصفحات | الصفحات نفسها |
| مسارات واجهة برمجة التطبيقات | `.py` | `.py` |

انظر [وضع الخادم ووضع العميل](fbr/modes.md).

| قسم | ما يشمله |
|---|---|
| [fbr/pages](fbr/pages/README.md) | الصفحات و[المسارات الديناميكية](fbr/pages/dynamic-routes.md) ومجموعات المسار |
| [fbr/تخطيطات](fbr/layouts/README.md) | `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` معالجات المسار، [التحقق من الصحة والأخطاء](fbr/handlers/validation-and-errors.md) |
| [fbr/تبعيات](fbr/dependencies/README.md) | `dependencies.py` والحراس، الموروثة بالدليل |
| [fbr/البرامج الوسيطة](fbr/middleware/README.md) | `middleware.py`، ورثت بالدليل |
| [fbr/أخطاء](fbr/errors/README.md) | `notfound.nexy`، `errors.nexy`، أخطاء JSON |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | الارتباط، تنقل العميل، [الخطافات](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | معالجات WebSocket |
| [fbr/inheritance](fbr/inheritance.md) | كيف ترث التخطيطات والتبعيات وصفحات الخطأ |

## التوجيه المعياري

وحدات التحكم والوحدات النمطية وحقن التبعية بأسلوب NestJS. انظر
[التوجيه المعياري](modular/README.md) و [Nexy وNestJS](modular/vs-nestjs.md).

## التكامل المخصص

يمكنك أيضًا دمج جهاز توجيه FastAPI موجود في مشروع Nexy الخاص بك. راجع [تكامل التوجيه المخصص](custom/README.md).

## الخطوات التالية

-  [التوجيه القائم على الملف](fbr/README.md)
-  [التقديم](../rendering/README.md)
- [المشاهدات](../views/README.md): ما يدور داخل الملفات