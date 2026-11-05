# وثائق نيكسي

**إطار عمل Python لتطبيقات الويب الكاملة.**

Nexy يدور حول التماس بين الواجهة الخلفية Python والواجهة الأمامية للمتصفح. بدلاً من خادمين ونظامي بناء وجدولي توجيه، تحصل على أصل واحد: FastAPI و Starlette يخدمان التطبيق، Vite يبني العميل، والملف الموجود تحت `src/routes/` هو مسار - `.nexy` هو صفحة، `.py` هو معالج API.

- **Python أولاً.** الصفحات ونقاط النهاية والنماذج والإجراءات هي Python، ولا تحتاج الصفحة المعروضة بواسطة الخادم إلى إطار عمل للواجهة الأمامية.
- **ثلاثة أجهزة توجيه، تكامل واحد.** قائم على الملفات، أو معياري، أو موجود FastAPI `APIRouter`.
- **واجهة أمامية عندما تريد واحدة.** React، Vue، Svelte، Solid أو Preact، لكل صفحة كجزر، أو للمشروع بأكمله في وضع العميل.
- **العرض، نموذج واحد.** يتم تحديد عرض الخادم والصفحات المخزنة مؤقتًا والجزر لكل صفحة؛ توجيه العميل هو مفتاح المشروع.
- **الإجراءات المكتوبة.** يصل منشور النموذج ومكالمة العميل المكتوبة إلى نفس الوظيفة Python.

ابدأ بملف واحد ضمن `src/routes/`، وأضف البنية عندما ينمو المشروع.

## البدء

### الخطوات الأولى
| صفحة | ماذا ستفعل |
|---|---|
| [التثبيت](getting-started/installation.md) | قم بتثبيت uv وNexy CLI، ثم أنشئ مشروعك الأول |
| [بداية سريعة](getting-started/quick-start.md) | إنشاء مشروع وتشغيله مع إعادة التحميل المباشر وإنشاءه للإنتاج |
| [البرنامج التعليمي](getting-started/tutorial.md) | إنشاء صفحة ملاحظات بنقطة نهاية وبيانات مشتركة وبناء إنتاج في 10 دقائق |

### فهم النموذج
| صفحة | ماذا ستفعل |
|---|---|
| [المفاهيم الأساسية](getting-started/core-concepts.md) | احصل على النموذج العقلي: المسار، الصفحة، العرض، المكون، المعالج، نقطة النهاية |
| [كيف يعمل Nexy](getting-started/how-nexy-works.md) | اتبع طلبًا واحدًا من عنوان URL إلى الملف الذي يجيب عليه |
| [الهندسة المعمارية](architecture.md) | تعرف على الطبقة التي تفعل ماذا، وما يتركه Nexy لتطبيقك |
| [بنية المشروع](getting-started/project-structure.md) | معرفة الغرض من كل مجلد وملف في المشروع |
| [اختيار جهاز توجيه](routing/README.md) | اختر جهاز توجيه قائم على الملف أو معياري أو مخصص |
| [اختيار تنسيق عرض](views/README.md) | اختيار `.nexy`، Markdown أو إطار عمل عميل لصفحة |

### قادمة من مكان آخر
| صفحة | ماذا ستفعل |
|---|---|
| [قادم من إطار آخر](getting-started/coming-from-other-frameworks.md) | ترجمة FastAPI، Next.js والتعبير عن العادات إلى نكسي |

## التوجيه

### القائم على الملف {fbr}
| صفحة | ماذا ستفعل |
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
| صفحة | ماذا ستفعل |
|---|---|
| [معالجات المسار](routing/fbr/handlers/README.md) | إضافة نقطة نهاية Python |
| [التصديق والأخطاء](routing/fbr/handlers/validation-and-errors.md) | الجواب `422` و `404`، ورفع `HTTPException` |
| [WebSocket معالجات](routing/fbr/realtime/websocket.md) | التعامل مع `SOCKET` اتصال |
| [التبعيات والحراس](routing/fbr/dependencies/README.md) | قم بتشغيل `dependencies.py` قبل المعالج، ويرثه |
| [ملفات البرامج الوسيطة](routing/fbr/middleware/README.md) | التفاف الطلبات مع `middleware.py`، الموروثة بالدليل |
| [صفحات الخطأ](routing/fbr/errors/README.md) | الإجابة مع `notfound.nexy`، `errors.nexy` وأخطاء JSON |
| [صفحات الخطأ لكل مجلد](routing/fbr/errors/folder-pages.md) | حالة الحافة: أخطاء من المجلدات الفرعية |

### جهاز التوجيه المعياري {modular}
وحدات التحكم والوحدات.
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه المعياري](routing/modular/README.md) | تركيب وحدات التحكم والوحدات |
| [حقن التبعية](routing/modular/dependency-injection.md) | تعريف الخدمات ونطاقاتها والحاوية |
| [الحراسات والبيانات الوصفية](routing/modular/guards-and-metadata.md) | حماية المسارات وتوثيقها |
| [جهاز التوجيه المعياري مقابل NestJS ](routing/modular/vs-nestjs.md) | مقارنة مع NestJS |

### تكامل جهاز التوجيه المخصص {custom}
| صفحة | ماذا ستفعل |
|---|---|
| [توجيه مخصص](routing/custom/README.md) | تضمين تطبيق FastAPI موجود |

## الواجهة الأمامية

### العقود المشتركة
| صفحة | ما تحدده |
|---|---|
| [صفحات الواجهة](views/frontend/pages.md) | ملف واحد، مسار واحد: الدعائم، العرض، البيانات الوصفية |
| [تخطيطات الواجهة الأمامية](views/frontend/layouts.md) | غلاف المستند والتداخل وما لا يستطيع التخطيط فعله |
| [الإجراءات والتنقل](views/frontend/actions-and-navigation.md) | استدعاء إجراء مكتوب، ربط الصفحات، قراءة عنوان URL |

### وجهات نظر نكسي
| الصفحة | ماذا ستفعل |
|---|---|
| [.nexy files](views/nexy/README.md) | اكتب صفحة تحتوي على Python، Jinja2 والدعائم |
| [المكونات](views/nexy/components.md) | استخدم `Image`، `Link`، `Audio`، `Video` و `Import` |
| [layout.nexy](views/nexy/layouts.md) | كتابة تخطيط وضع الخادم |
| [Markdown و MDX](views/nexy/markdown.md) | كتابة صفحات المحتوى |

### اختلافات الإطار
| صفحة | ما يتغير |
|---|---|
| [React الاختلافات](views/react/differences.md) | المكونات والخطافات و `layout.tsx` {new} |
| [Vue الاختلافات](views/vue/differences.md) | SFCs والمراجع و `layout.vue` {new} |
| [Svelte الاختلافات](views/svelte/differences.md) | الأحرف الرونية والمخازن و `layout.svelte` {new} |
| [Solid الاختلافات](views/solid/differences.md) | الإشارات والوصلات و `layout.tsx` {new} |
| [Preact الفروق](views/preact/differences.md) | الخطافات والإشارات و `layout.tsx` {new} |

## التقديم

### وسائط
| صفحة | ماذا ستقرر |
|---|---|
| [العرض](rendering/README.md) | ما هو وضع العرض المناسب للصفحة |
| [SSR](rendering/ssr.md) | عرض الخادم، الافتراضي |
| [ISR](rendering/isr.md) | صفحات التخزين المؤقت التي لا معنى لها أثناء إعادة التحقق |
| [CSR](rendering/csr.md) | التوجيه من جانب العميل |
| [الجزر](rendering/islands.md) | الترطيب عند الاستعلام الخامل أو المرئي أو الوسائط |

## أدلة

### النماذج والبيانات
| صفحة | ماذا ستفعل |
|---|---|
| [الإجراءات](guides/actions.md) | استدعاء دالة Python من نموذج أو دالة TypeScript مكتوبة |
| [قواعد البيانات](guides/databases.md) | اختر ORM وقم بتشغيل عمليات الترحيل |

### الأمن والنشر
| صفحة | ماذا ستفعل |
|---|---|
| [البرامج الوسيطة والأمان](guides/middleware-and-security.md) | إعداد CORS وGZip والمضيفين والجلسات الموثوقة |
| [نشر](deployment/README.md) | البناء والحاويات والخدمة |
| [الأداء](deployment/performance.md) | قياس وضبط الإعدادات الافتراضية |

### بناء واختبار
| صفحة | ماذا ستفعل |
|---|---|
| [Vite والتصميم](guides/frontend.md) | إعداد Vite والتصميم وبناء العميل |
| [الاختبار](guides/testing.md) | الاختبار مع pytest، `TestClient` وفيتيست |

### الأدوات والمساعدة
| صفحة | ماذا ستفعل |
|---|---|
| [[شريط أدوات التطوير](guides/devtools.md) | استخدم شريط الأدوات `nexy dev`، وقم بإيقاف تشغيله |
| [وكلاء الترميز](guides/ai-agents.md) | أعطِ Claude Code و Codex و OpenCode قواعد مشروعك |
| [استكشاف الأخطاء وإصلاحها](guides/troubleshooting.md) | إصلاح المشاكل الأولى التي أصابت الناس |

## مرجع

### الأوامر والتكوين
| الصفحة | ما تتضمنه |
|---|---|
| [CLI](reference/cli.md) | الأوامر والإشارات والمطالبات ورموز الخروج |
| [التكوين](reference/config.md) | كل حقل `nexyconfig.py` وحقله الافتراضي |

### Python API والأخطاء
| صفحة | ما تتضمنه |
|---|---|
| [Python API](reference/python-api.md) | كل اسم يصدره Nexy، حسب الوحدة |
| [[الاستثناءات والأخطاء](reference/exceptions.md) | كل فشل وحالته والملف الذي يجيب عليه |

### الاتفاقيات والمفاهيم
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
| [وصفات](guides/recipes.md) | أمثلة وأنماط وليست دروسا |

*هذه الصفحات ليست جزءًا من مسار القراءة الافتراضي. يتيح لك رابط "جميع الوثائق" رؤية كل شيء.*
