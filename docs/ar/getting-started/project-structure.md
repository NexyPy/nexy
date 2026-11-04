# هيكل المشروع

كل ملف في مشروع Nexy له وظيفة واحدة. هذه الصفحة تقول التي.

## المستوى الأعلى

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

لاختيار مجلد، اسأل ما هو الملف:

- **شيء يمكن للمتصفح فتحه** - طريق: `src/routes/`.
- **قطعة تستخدم بعدة طرق** - مكون أو وحدة نمطية: `src/components/`، `src/`.
- **ملف تم تقديمه كما هو** - `public/`.
- **وحدة تحكم لجهاز التوجيه المعياري** - `src/apps/`.
- **تم الإنشاء** - `__nexy__/`؛ لا تقم بتحريره أبدًا.

> [!تحذير]
> `src/routes/` يتم مسحه ضوئيًا: يصبح المساعد الموجود هناك طريقًا. وضع المساعد الذي ليس الطريق
> خارج `src/routes/`، أو يبدأ اسمه بـ `_`.

## `src/routes/`

يصبح كل ملف مسارًا، باستثناء الأسماء المحجوزة أدناه. مسار الملف مطروحًا منه الامتداد هو
عنوان URL - راجع [التوجيه](../routing/README.md).

| الملف | الدور |
|---|---|
| `layout.nexy` | يلتف حول صفحات الأخوة والأبناء |
| `errors.nexy` | 500 صفحة للدليل |
| `notfound.nexy` | 404 صفحة للدليل |
| `dependencies.py` | شارك تبعيات FastAPI للدليل |
| `__init__.py` | علامة حزمة بايثون |
| `loading.nexy` | محجوز - مستبعد من المسارات، ولكن ليس له تأثير وقت التشغيل بعد |

كل اسم صفحة موجود أيضًا لكل إطار عمل. مع تكوين `react()`، `layout.jsx` و `layout.tsx`
محجوزة تمامًا مثل `layout.nexy`. تم إنشاء القوائم في `nexy/core/config.py`
(`LAYOUT_FILE_NAMES`، `ERROR_FILE_NAMES`، `NOTFOUND_FILE_NAMES`، `LOADING_FILE_NAMES`).

> [!ملاحظة]
>  `notfound.nexy` و `errors.nexy` يتم تثبيتها فقط عند وجود نسخة في
> طرق الجذر. ثم تقوم النسخة الموجودة في دليل فرعي بتحسين الصفحة لتلك البادئة.

## `src/apps/`

يستخدم الدليل `nexy new` لجهاز التوجيه المعياري: تسجيل وحدات التحكم والوحدات والموفرين
مساراتها عبر الزخارف من `nexy.decorators`، ثم يتم تركيب الركام `APIRouter`
مع `useRouter` في `nexyconfig.py`.

يمكن أن يحتوي المشروع على كلا الموجهين: يقوم `useRouter` بتثبيت جهاز التوجيه المعياري، ويتم فحص `src/routes/`
كلما كان هذا الدليل موجودا. انظر [التوجيه المعياري](../routing/modular/README.md).

## `public/`

يتم تقديم الملفات هنا من جذر الموقع: `/favicon.ico`، `/robots.txt`، الصور، الخطوط.

## `__nexy__/`

أنشئ بواسطة `nx build` (وبواسطة `nx dev` للأجزاء التي يحتاجها). أنه يحتوي على:

- وحدات المسار المترجمة، كحزمة بايثون (`__nexy__/src/routes/...`)؛
- نقاط دخول العميل التي تم إنشاؤها (`main.ts`، `vite.ts`، `*.auto.ts`)؛
- `client/` بعد إنشاء Vite - الأصول، والبيان، وHTML المعروض مسبقًا؛
- `build-cache.json`.

تعامل مع الدليل بأكمله على أنه يمكن التخلص منه: احذفه وأعد بنائه. تحريره يدويًا يفقد التغيير
على البناء القادم. أضفه إلى `.gitignore`.

## الخطوات التالية

- [التوجيه](../routing/README.md): كيف يصبح المسار عنوان URL
- [التكوين](../reference/config.md): كل خيار للمشروع
- [Frontend](../guides/frontend.md): Vite والتصميم وبناء العميل