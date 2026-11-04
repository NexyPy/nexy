# توثيق نكسي

**إطار عمل بايثون لتطبيقات الويب الكاملة.**

Nexy يدور حول التماس بين الواجهة الخلفية لـ Python والواجهة الأمامية للمتصفح. بدلا من خادمين، اثنان
بناء أنظمة وجدولين توجيه، تحصل على أصل واحد: FastAPI وStarlette يخدمان التطبيق،
يقوم Vite ببناء العميل، والملف الموجود ضمن `src/routes/` هو مسار - `.nexy` عبارة عن صفحة، `.py` عبارة عن
معالج واجهة برمجة التطبيقات.

- **بايثون أولاً.** الصفحات ونقاط النهاية والنماذج والإجراءات هي بايثون، وتحتاج الصفحة التي يعرضها الخادم
  لا يوجد إطار الواجهة الأمامية.
- **ثلاثة أجهزة توجيه، تكامل واحد.** مستند إلى ملف أو معياري أو FastAPI موجود `APIRouter`.
- **واجهة أمامية عندما تريد واحدة.** React أو Vue أو Svelte أو Solid أو Preact، لكل صفحة كجزر، أو لـ
  المشروع بأكمله في وضع العميل.
- **العرض، نموذج واحد.** يتم تحديد عرض الخادم والصفحات المخزنة مؤقتًا والجزر لكل صفحة؛ العميل
  التوجيه هو مفتاح المشروع.
- **الإجراءات المكتوبة.** يصل منشور النموذج ومكالمة العميل المكتوبة إلى نفس وظيفة بايثون.

ابدأ بملف واحد ضمن `src/routes/`، وأضف الهيكل عندما ينمو المشروع.

## البدء

### الخطوات الأولى
| صفحة | ماذا ستفعل |
|---|---|
| [التثبيت](getting-started/installation.md) | قم بتثبيت uv وNexy CLI، ثم قم بإنشاء مشروعك الأول |
| [البداية السريعة](getting-started/quick-start.md) | إنشاء مشروع وتشغيله مع إعادة التحميل المباشر وإنشاءه للإنتاج |
| [البرنامج التعليمي](getting-started/tutorial.md) | إنشاء صفحة ملاحظات بنقطة نهاية وبيانات مشتركة وبناء إنتاج في 10 دقائق |

### فهم النموذج
| الصفحة | ماذا ستفعل |
|---|---|
| [المفاهيم الأساسية](getting-started/core-concepts.md) | احصل على النموذج العقلي: المسار، الصفحة، العرض، المكون، المعالج، نقطة النهاية |
| [كيف يعمل Nexy](getting-started/how-nexy-works.md) | اتبع طلبًا واحدًا من عنوان URL إلى الملف الذي يجيب عليه |
| [الهندسة المعمارية](architecture.md) | تعرف على الطبقة التي تفعل ماذا، وما يتركه Nexy لتطبيقك |
| [بنية المشروع](getting-started/project-structure.md) | معرفة الغرض من كل مجلد وملف في المشروع |
| [اختر جهاز توجيه](routing/README.md) | اختر جهاز التوجيه المعتمد على الملف أو المعياري أو المخصص |
| [اختيار تنسيق عرض](views/README.md) | اختيار `.nexy` أو Markdown أو إطار عمل عميل لصفحة |

###  قادم من مكان آخر
| صفحة | ماذا ستفعل |
|---|---|
| [قادم من إطار عمل آخر](getting-started/coming-from-other-frameworks.md) | ترجمة عادات FastAPI وNext.js وExpress إلى Nexy |

## التوجيه

### المستند إلى الملف {fbr}
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه المعتمد على الملف](routing/fbr/README.md) | تحويل مسار الملف إلى عنوان URL |
| [الصفحات](routing/fbr/pages/README.md) | اكتب صفحة |
| [المسارات الديناميكية](routing/fbr/pages/dynamic-routes.md) | استخدم `[slug]`، `[...path]` ومجموعات المسار |
| [البيانات الوصفية للصفحة](routing/fbr/pages/metadata.md) | تعيين عنوان ووصف ومشاركة صورة للصفحة {new} |
| [التخطيطات](routing/fbr/layouts/README.md) | مشاركة إطار بين الصفحات |
| [الميراث](routing/fbr/inheritance.md) | اقرأ ترتيب دقة التخطيطات والتبعيات وصفحات الأخطاء |
| [وضع الخادم ووضع العميل](routing/fbr/modes.md) | `useCSR`، وما يسمح به كل وضع |
| [الربط والتنقل](routing/fbr/navigation/linking-and-navigating.md) | ربط الصفحات، التنقل على العميل، الجلب المسبق |
| [الخطافات](routing/fbr/navigation/hooks.md) | قراءة المسار والاستعلام وملفات تعريف الارتباط والجلسة |

### المعالجات والأخطاء {fbr}
| الصفحة | ماذا ستفعل |
|---|---|
| [معالجات المسار](routing/fbr/handlers/README.md) | إضافة نقطة نهاية بايثون |
| [التصديق والأخطاء](routing/fbr/handlers/validation-and-errors.md) | الجواب `422` و `404`، ورفع `HTTPException` |
| [معالجات WebSocket](routing/fbr/realtime/websocket.md) | التعامل مع اتصال `SOCKET` |
| [التبعيات والحراس](routing/fbr/dependencies/README.md) | قم بتشغيل `dependencies.py` قبل المعالج، ويرثه |
| [ملفات البرامج الوسيطة](routing/fbr/middleware/README.md) | التفاف الطلبات مع `middleware.py`، الموروثة بالدليل |
| [صفحات الخطأ](routing/fbr/errors/README.md) | الإجابة مع `notfound.nexy`، `errors.nexy` وأخطاء JSON |
| [صفحات الخطأ في كل مجلد](routing/fbr/errors/folder-pages.md) | حالة الحافة: أخطاء من المجلدات الفرعية |

### جهاز التوجيه المعياري {modular}
وحدات التحكم والوحدات.
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه المعياري](routing/modular/README.md) | وحدات التحكم والوحدات النمطية |
| [حقن التبعية](routing/modular/dependency-injection.md) | تعريف الخدمات ونطاقاتها والحاوية |
| [الحراسات والبيانات الوصفية](routing/modular/guards-and-metadata.md) | حماية وتوثيق المسارات |
| [جهاز التوجيه المعياري مقابل NestJS](routing/modular/vs-nestjs.md) | المقارنة مع NestJS |

### تكامل جهاز التوجيه المخصص {custom}
| الصفحة | ماذا ستفعل |
|---|---|
| [توجيه مخصص](routing/custom/README.md) | تضمين تطبيق FastAPI موجود |

## الواجهة الأمامية

### العقود المشتركة
| الصفحة | ما تعريفه |
|---|---|
| [صفحات الواجهة](views/frontend/pages.md) | ملف واحد، مسار واحد: الدعائم، العرض، البيانات الوصفية |
| [تخطيطات الواجهة الأمامية](views/frontend/layouts.md) | غلاف المستند والتداخل وما لا يستطيع التخطيط فعله |
| [الإجراءات والتنقل](views/frontend/actions-and-navigation.md) | استدعاء إجراء مكتوب، ربط الصفحات، قراءة عنوان URL |

### مشاهدات نكسي
| الصفحة | ماذا ستفعل |
|---|---|
| [.nexy files](views/nexy/README.md) | اكتب صفحة باستخدام Python وJinja2 والدعائم |
| [المكونات](views/nexy/components.md) | استخدم `Image`، `Link`، `Audio`، `Video` و `Import` |
| [layout.nexy](views/nexy/layouts.md) | كتابة تخطيط وضع الخادم |
| [Markdown وMDX](views/nexy/markdown.md) | كتابة صفحات المحتوى |

### اختلافات الإطار
| الصفحة | ما يتغير |
|---|---|
| [اختلافات التفاعل](views/react/differences.md) | المكونات والخطافات و `layout.tsx` {new} |
| [اختلافات الرأي](views/vue/differences.md) | SFCs والمراجع و `layout.vue` {new} |
| [اختلافات رشيقة](views/svelte/differences.md) | الرونية والمخازن و `layout.svelte` {new} |
| [الاختلافات الصلبة](views/solid/differences.md) | الإشارات والموصلات و`layout.tsx` {new} |
| [الاختلافات المسبقة](views/preact/differences.md) | الخطافات والإشارات و `layout.tsx` {new} |

## التقديم

### أوضاع
| صفحة | ماذا ستقرر |
|---|---|
| [العرض](rendering/README.md) | ما هو وضع العرض المناسب للصفحة |
| [SSR](rendering/ssr.md) | عرض الخادم، الافتراضي |
| [ISR](rendering/isr.md) | صفحات التخزين المؤقت التي لا معنى لها أثناء إعادة التحقق |
| [CSR](rendering/csr.md) | التوجيه من جانب العميل |
| [الجزر](rendering/islands.md) | هيدرات عند الاستعلام الخامل أو المرئي أو الوسائط |

## الأدلة

### النماذج والبيانات
| صفحة | ماذا ستفعل |
|---|---|
| [الإجراءات](guides/actions.md) | استدعاء دالة بايثون من نموذج أو دالة TypeScript مكتوبة |
| [قواعد البيانات](guides/databases.md) | اختر ORM وقم بتشغيل عمليات الترحيل |

### الأمان والنشر
| الصفحة | ماذا ستفعل |
|---|---|
| [البرامج الوسيطة والأمان](guides/middleware-and-security.md) | إعداد CORS وGZip والمضيفين الموثوقين والجلسات |
| [نشر](deployment/README.md) | البناء والحاويات والخدمة |
| [الأداء](deployment/performance.md) | قياس وضبط الإعدادات الافتراضية |

### البناء والاختبار
| صفحة | ماذا ستفعل |
|---|---|
| [Vite والتصميم](guides/frontend.md) | إعداد Vite والتصميم وبناء العميل |
| [الاختبار](guides/testing.md) | الاختبار بالبيتست، `TestClient` وفيتيست |

### الأدوات والمساعدة
| صفحة | ماذا ستفعل |
|---|---|
| [شريط أدوات التطوير](guides/devtools.md) | استخدم شريط الأدوات `nexy dev`، وقم بإيقاف تشغيله |
| [وكلاء التشفير](guides/ai-agents.md) | أعط كلود كود، كوديكس وأوبن كود قواعد مشروعك |
| [استكشاف الأخطاء وإصلاحها](guides/troubleshooting.md) | إصلاح المشكلات الأولى التي يواجهها الأشخاص |

## المرجع

### الأوامر والتكوين
| الصفحة | ما تتضمنه |
|---|---|
| [CLI](reference/cli.md) | الأوامر والأعلام والمطالبات ورموز الخروج |
| [التكوين](reference/config.md) | كل حقل `nexyconfig.py` وحقله الافتراضي |

### واجهة برمجة تطبيقات بايثون والأخطاء
| الصفحة | ما تتضمنه |
|---|---|
| [Python API](reference/python-api.md) | كل اسم يصدره Nexy، حسب الوحدة |
| [الاستثناءات والأخطاء](reference/exceptions.md) | كل فشل وحالته والملف الذي يجيب عليه |

### الاصطلاحات والمفاهيم
| صفحة | ماذا ستفعل |
|---|---|
| [اصطلاحات الملفات](reference/file-conventions.md) | الملفات المحجوزة وقواعد التوجيه |
| [المسرد](reference/glossary.md) | الكلمات التي تستخدمها هذه المستندات |
| [الأمان](reference/security.md) | طوابق الإصدار، القواعد التي يتبعها Nexy، عمليات التدقيق |

## التخطيط
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## متقدم

### متقدم {advanced}

| صفحة | ماذا ستفعل |
|---|---|
| [الترقية إلى 2.2](getting-started/upgrading.md) | الترحيل من 2.1 إلى 2.2 |
| [التدويل (i18n)](guides/i18n.md) | إضافة الترجمات مع اختيارك للمكتبة |
| [وصفات](guides/recipes.md) | أمثلة وأنماط وليست تعليمية |

*هذه الصفحات ليست جزءًا من مسار القراءة الافتراضي. يتيح لك رابط "جميع الوثائق" رؤية كل شيء.*