# وثائق نيكسي

**إطار عمل Python لتطبيقات الويب الكاملة.**

يقوم Nexy بوضع صفحاتك وواجهة برمجة التطبيقات (API) الخاصة بك في مشروع واحد Python، يخدمه خادم واحد. الإصدار 2.2 مبني على FastAPI: كل مسار API هو مسار FastAPI، مدرج في مخطط OpenAPI الذي يعرضه Scalar في `/docs`.

- **Python أولاً.** الصفحات ونقاط النهاية والنماذج والإجراءات هي Python، والصفحة لا تحتاج إلى JavaScript.
- **واجهة أمامية عندما تريد واحدة.** React، Vue، Svelte، Solid أو Preact، لمكون واحد أو للموقع بأكمله.
- **ملف واحد، عنوان URL واحد.** الملف الموجود ضمن `src/routes/` هو مسار: `.nexy` عبارة عن صفحة، `.py` هي نقطة نهاية API.
- **مجال للنمو.** ابدأ بملف واحد؛ انتقل إلى الوحدات النمطية، أو قم بتوصيل جهاز توجيه FastAPI موجود، عندما ينمو المشروع.

جديد هنا؟ اقرأ [ما هو النكسي؟](getting-started/what-is-nexy.md)، ثم [البداية السريعة](getting-started/quick-start.md).

## البدء

### الخطوات الأولى
| الصفحة | ماذا ستفعل |
|---|---|
| [ما هو النكسي؟](getting-started/what-is-nexy.md) | تعرف على ما هو Nexy وما الذي بني عليه وما الذي تحصل عليه |
| [التثبيت](getting-started/installation.md) | قم بتثبيت uv وNexy CLI، ثم قم بإنشاء مشروعك الأول |
| [بداية سريعة](getting-started/quick-start.md) | أنشئ مشروعًا، وقم بتشغيله من خلال التحديث المباشر، ثم قم ببنائه للإنتاج |
| [البرنامج التعليمي](getting-started/tutorial.md) | أنشئ صفحة ملاحظات بنقطة نهاية وبيانات مشتركة وبناء إنتاج في 10 دقائق |

### فهم النموذج
| الصفحة | ماذا ستفعل |
|---|---|
| [المفاهيم الأساسية](getting-started/core-concepts.md) | احصل على النموذج العقلي: المسار، الصفحة، العرض، المكون، المعالج، نقطة النهاية |
| [هيكل المشروع](getting-started/project-structure.md) | تعرف على الغرض من كل مجلد وملف في المشروع |
| [اختيار جهاز التوجيه](routing/README.md) | اختر جهاز التوجيه المستند إلى الملف أو المعياري أو المخصص |
| [اختر تنسيق العرض](views/README.md) | اختر `.nexy`، Markdown أو إطار عمل عميل للصفحة |

### قادمة من مكان آخر
| الصفحة | ماذا ستفعل |
|---|---|
| [قادمة من إطار آخر](getting-started/coming-from-other-frameworks.md) | ترجمة FastAPI، Next.js والتعبير عن العادات إلى Nexy |

## التوجيه

### القائم على الملف {fbr}
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه القائم على الملف](routing/fbr/README.md) | تحويل مسار الملف إلى عنوان URL |
| [الصفحات](routing/fbr/pages/README.md) | اكتب صفحة |
| [المسارات الديناميكية](routing/fbr/pages/dynamic-routes.md) | استخدم `[slug]`، `[...path]` ومجموعات التوجيه |
| [البيانات التعريفية للصفحة](routing/fbr/pages/metadata.md) | تعيين عنوان ووصف ومشاركة صورة للصفحة {new} |
| [التخطيطات](routing/fbr/layouts/README.md) | مشاركة إطار بين الصفحات |
| [الميراث](routing/fbr/inheritance.md) | اقرأ ترتيب دقة التخطيطات والتبعيات وصفحات الخطأ |
| [وضع الخادم ووضع العميل](routing/fbr/modes.md) | `useCSR`، وما يسمح به كل وضع |
| [الارتباط والتنقل](routing/fbr/navigation/linking-and-navigating.md) | ربط الصفحات، والتنقل على العميل، والجلب المسبق |
| [خطافات](routing/fbr/navigation/hooks.md) | اقرأ المسار والاستعلام وملفات تعريف الارتباط والجلسة |

### المعالجات والأخطاء {fbr}
| الصفحة | ماذا ستفعل |
|---|---|
| [معالجات المسار](routing/fbr/handlers/README.md) | أضف Python نقطة نهاية |
| [التحقق من الصحة والأخطاء](routing/fbr/handlers/validation-and-errors.md) | أجيب `422` و `404`، وارفع `HTTPException` |
| [WebSocket معالجات](routing/fbr/realtime/websocket.md) | التعامل مع اتصال `SOCKET` |
| [التبعيات والحراس](routing/fbr/dependencies/README.md) | قم بتشغيل `dependencies.py` قبل المعالج، ورثه |
| [ملفات الوسيطة](routing/fbr/middleware/README.md) | التفاف الطلبات مع `middleware.py`، ورثت عن طريق الدليل |
| [صفحات الخطأ](routing/fbr/errors/README.md) | أجب بأخطاء `notfound.nexy` و `errors.nexy` وJSON |
| [صفحات الخطأ لكل مجلد](routing/fbr/errors/folder-pages.md) | حالة الحافة: أخطاء من المجلدات الفرعية |

### جهاز التوجيه المعياري {modular}
وحدات التحكم والوحدات.
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه المعياري](routing/modular/README.md) | وحدات التحكم والوحدات |
| [حقن التبعية](routing/modular/dependency-injection.md) | تحديد الخدمات ونطاقاتها والحاوية |
| [الحراس والبيانات الوصفية](routing/modular/guards-and-metadata.md) | حماية وتوثيق المسارات |
| [جهاز التوجيه المعياري مقابل NestJS](routing/modular/vs-nestjs.md) | مقارنة مع NestJS |

### تكامل جهاز التوجيه المخصص {custom}
| الصفحة | ماذا ستفعل |
|---|---|
| [التوجيه المخصص](routing/custom/README.md) | تضمين تطبيق FastAPI موجود |

## الواجهة الأمامية

### العقود المشتركة
| الصفحة | ما يحدده |
|---|---|
| [صفحات الواجهة](views/frontend/pages.md) | ملف واحد، طريق واحد: الدعائم، العرض، البيانات الوصفية |
| [تخطيطات الواجهة الأمامية](views/frontend/layouts.md) | غلاف المستند والتداخل وما لا يستطيع التخطيط فعله |
| [الإجراءات والملاحة](views/frontend/actions-and-navigation.md) | قم باستدعاء إجراء مكتوب، وربط الصفحات، وقراءة عنوان URL |

### وجهات نظر نكسي
| الصفحة | ماذا ستفعل |
|---|---|
| [ملفات .nexy](views/nexy/README.md) | اكتب صفحة تحتوي على Python، Jinja2 والدعائم |
| [المكونات](views/nexy/components.md) | استخدم `Image`، `Link`، `Audio`، `Video` و `Import` |
| [تخطيط.nexy](views/nexy/layouts.md) | اكتب تخطيط وضع الخادم |
| [Markdown و MDX](views/nexy/markdown.md) | كتابة صفحات المحتوى |

### اختلافات الإطار
| الصفحة | ما يتغير |
|---|---|
| [React الاختلافات](views/react/differences.md) | المكونات والخطافات و `layout.tsx` {new} |
| [Vue الاختلافات](views/vue/differences.md) | SFCs والمراجع و `layout.vue` {new} |
| [Svelte الاختلافات](views/svelte/differences.md) | الرونية والمخازن و `layout.svelte` {new} |
| [Solid الاختلافات](views/solid/differences.md) | الإشارات والتوصيل و `layout.tsx` {new} |
| [Preact الاختلافات](views/preact/differences.md) | السنانير والإشارات و `layout.tsx` {new} |

## التقديم

### وسائط
| الصفحة | ماذا ستقرر |
|---|---|
| [التقديم](rendering/README.md) | ما هو وضع العرض المناسب للصفحة |
| [إصلاحية القطاع الخاص](rendering/ssr.md) | تقديم الخادم، الافتراضي |
| [الاستخبارات والمراقبة](rendering/isr.md) | صفحات التخزين المؤقت التي لا معنى لها أثناء إعادة التحقق |
| [المسؤولية الاجتماعية للشركات](rendering/csr.md) | التوجيه من جانب العميل |
| [الجزر](rendering/islands.md) | هيدرات على الاستعلام الخامل أو المرئي أو الوسائط |

## أدلة

### النماذج والبيانات
| الصفحة | ماذا ستفعل |
|---|---|
| [الإجراءات](guides/actions.md) | استدعاء دالة Python من نموذج أو دالة مكتوبة TypeScript |
| [قواعد البيانات](guides/databases.md) | اختر ORM وقم بتشغيل عمليات الترحيل |

### الأمن والنشر
| الصفحة | ماذا ستفعل |
|---|---|
| [الوسيطة والأمن](guides/middleware-and-security.md) | قم بإعداد CORS وGZip والمضيفين والجلسات الموثوقة |
| [نشر](deployment/README.md) | بناء، حاويات وخدمة |
| [الأداء](deployment/performance.md) | قياس وضبط الإعدادات الافتراضية |

### بناء واختبار
| الصفحة | ماذا ستفعل |
|---|---|
| [Vite والتصميم](guides/frontend.md) | إعداد Vite والتصميم وبناء العميل |
| [الاختبار](guides/testing.md) | اختبار مع pytest، `TestClient` وفيتست |

### الأدوات والمساعدة
| الصفحة | ماذا ستفعل |
|---|---|
| [شريط أدوات التطوير](guides/devtools.md) | استخدم شريط الأدوات `nexy dev`، وقم بإيقاف تشغيله |
| [وكلاء الترميز](guides/ai-agents.md) | أعط Claude Code، Codex و OpenCode قواعد مشروعك |
| [استكشاف الأخطاء وإصلاحها](guides/troubleshooting.md) | إصلاح المشاكل الأولى التي يواجهها الناس |

## مرجع

### الأوامر والتكوين
| الصفحة | ما يسرد |
|---|---|
| [سطر الأوامر](reference/cli.md) | الأوامر والأعلام والمطالبات ورموز الخروج |
| [التكوين](reference/config.md) | كل `nexyconfig.py` الحقل والافتراضي الخاص به |

### Python API والأخطاء
| الصفحة | ما يسرد |
|---|---|
| [Python واجهة برمجة التطبيقات](reference/python-api.md) | كل اسم يصدره Nexy، حسب الوحدة |
| [الاستثناءات والأخطاء](reference/exceptions.md) | كل فشل وحالته والملف الذي يجيب عليه |

### الاتفاقيات والمفاهيم
| الصفحة | ماذا ستفعل |
|---|---|
| [اصطلاحات الملف](reference/file-conventions.md) | الملفات المحجوزة وقواعد التوجيه |
| [معجم](reference/glossary.md) | الكلمات التي تستخدمها هذه المستندات |
| [الأمن](reference/security.md) | طوابق الإصدار، والقواعد التي يتبعها Nexy، وعمليات التدقيق |

## التخطيط
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
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

| الصفحة | ماذا ستفعل |
|---|---|
| [كيف يعمل نيكسي](getting-started/how-nexy-works.md) | تعرف على ما يحدث بين الملف والصفحة، وما يتركه لك Nexy |
| [الترقية إلى 2.2](getting-started/upgrading.md) | الهجرة من 2.1 إلى 2.2 |
| [التدويل (i18n)](guides/i18n.md) | أضف الترجمات مع اختيارك للمكتبة |
| [وصفات](guides/recipes.md) | أمثلة وأنماط، وليس البرنامج التعليمي |

*هذه الصفحات ليست جزءًا من مسار القراءة الافتراضي. يتيح لك رابط "جميع الوثائق" رؤية كل شيء.*
