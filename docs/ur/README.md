# Nexy دستاویزات

**فل اسٹیک ویب ایپلیکیشنز کے لیے ایک Python فریم ورک۔**

Nexy آپ کے صفحات اور آپ کے API کو ایک Python پروجیکٹ میں رکھتا ہے، جو ایک سرور کے ذریعے پیش کیا جاتا ہے۔ ورژن 2.2 FastAPI پر بنایا گیا ہے: ہر API روٹ ایک FastAPI روٹ ہے، ایک OpenAPI اسکیما میں درج ہے جسے اسکیلر `/docs` پر دکھاتا ہے۔

- **Python پہلے** صفحات، اختتامی نقطے، شکلیں اور اعمال Python ہیں، اور کسی صفحہ کو JavaScript کی ضرورت نہیں ہے۔
- **ایک فرنٹ اینڈ جب آپ چاہتے ہیں کہ** React، Vue، Svelte، Solid یا Preact، ایک جزو کے لیے یا پوری سائٹ کے لیے۔
- **ایک فائل، ایک URL** `src/routes/` کے تحت فائل ایک روٹ ہے: `.nexy` ایک صفحہ ہے، `.py` ایک API اینڈ پوائنٹ ہے۔
- **بڑھنے کے لیے کمرہ** ایک فائل سے شروع کریں۔ جب پروجیکٹ بڑھتا ہے تو ماڈیولز پر جائیں، یا موجودہ FastAPI روٹر میں پلگ ان کریں۔

یہاں نیا؟ پڑھیں [Nexy کیا ہے؟](getting-started/what-is-nexy.md)، پھر [کوئیک اسٹارٹ](getting-started/quick-start.md)۔

## شروع کرنا

### پہلے اقدامات
| صفحہ | آپ کیا کریں گے |
|---|---|
| [Nexy کیا ہے؟](getting-started/what-is-nexy.md) | جانیں کہ Nexy کیا ہے، یہ کس چیز پر بنایا گیا ہے اور آپ کو کیا ملتا ہے۔ |
| [تنصیب](getting-started/installation.md) | uv اور Nexy CLI انسٹال کریں، پھر اپنا پہلا پروجیکٹ بنائیں |
| [فوری آغاز](getting-started/quick-start.md) | ایک پروجیکٹ بنائیں، اسے لائیو ری لوڈ کے ساتھ چلائیں، اور اسے پروڈکشن کے لیے بنائیں |
| [سبق ](getting-started/tutorial.md) | 10 منٹ میں اختتامی نقطہ، مشترکہ ڈیٹا اور پروڈکشن کی تعمیر کے ساتھ نوٹس کا صفحہ بنائیں |

### ماڈل کو سمجھیں۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [بنیادی تصورات ](getting-started/core-concepts.md) | ذہنی ماڈل حاصل کریں: راستہ، صفحہ، منظر، جزو، ہینڈلر، اختتامی نقطہ |
| [منصوبے کا ڈھانچہ ](getting-started/project-structure.md) | جانیں کہ پروجیکٹ میں ہر فولڈر اور فائل کس کے لیے ہے۔ |
| [ایک راؤٹر کا انتخاب کریں ](routing/README.md) | فائل پر مبنی، ماڈیولر یا کسٹم راؤٹر کا انتخاب کریں۔ |
| [ویو فارمیٹ کا انتخاب کریں](views/README.md) | کسی صفحے کے لیے `.nexy`، Markdown یا کلائنٹ کا فریم ورک چنیں۔ |

## روٹنگ

### فائل پر مبنی {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [فائل پر مبنی روٹنگ](routing/fbr/README.md) | فائل کے راستے کو URL میں تبدیل کریں۔ |
| [صفحات](routing/fbr/pages/README.md) | ایک صفحہ لکھیں۔ |
| [متحرک راستے](routing/fbr/pages/dynamic-routes.md) | `[slug]`، `[...path]` اور روٹ گروپس کا استعمال کریں۔ |
| [صفحہ میٹا ڈیٹا ](routing/fbr/pages/metadata.md) | صفحہ کا عنوان، تفصیل اور تصویر شیئر کریں {new} |
| [لے آؤٹ](routing/fbr/layouts/README.md) | صفحات کے درمیان ایک فریم کا اشتراک کریں |
| [وراثت](routing/fbr/inheritance.md) | لے آؤٹ، انحصار اور خرابی والے صفحات کا ریزولوشن آرڈر پڑھیں |
| [سرور موڈ اور کلائنٹ موڈ](routing/fbr/modes.md) | `useCSR`، اور ہر موڈ جس کی اجازت دیتا ہے۔ |
| [لنک کرنا اور نیویگیٹ کرنا](routing/fbr/navigation/linking-and-navigating.md) | صفحات کو لنک کریں، کلائنٹ پر نیویگیٹ کریں، پری فیچ کریں۔ |
| [کانٹے](routing/fbr/navigation/hooks.md) | راستہ، استفسار، کوکیز اور سیشن پڑھیں |

### ہینڈلر اور غلطیاں {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [روٹ ہینڈلر](routing/fbr/handlers/README.md) | ایک Python اختتامی نقطہ شامل کریں۔ |
| [توثیق اور غلطیاں](routing/fbr/handlers/validation-and-errors.md) | جواب دیں `422` اور `404`، اور بلند کریں `HTTPException` |
| [WebSocket ہینڈلر](routing/fbr/realtime/websocket.md) | ایک `SOCKET` کنکشن کو ہینڈل کریں۔ |
| [انحصار اور محافظ ](routing/fbr/dependencies/README.md) | ہینڈلر سے پہلے `dependencies.py` چلائیں، اور اسے وارث بنائیں |
| [مڈل ویئر فائلیں](routing/fbr/middleware/README.md) | درخواستوں کو `middleware.py` کے ساتھ لپیٹیں، جو ڈائرکٹری سے وراثت میں ملی ہیں۔ |
| [خرابی کے صفحات](routing/fbr/errors/README.md) | `notfound.nexy`، `errors.nexy` اور JSON کی غلطیوں کے ساتھ جواب دیں۔ |
| [خامی صفحات فی فولڈر](routing/fbr/errors/folder-pages.md) | ایج کیس: ذیلی فولڈرز سے غلطیاں |

### ماڈیولر راؤٹر {modular}
کنٹرولرز اور ماڈیولز۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [ماڈیولر روٹنگ](routing/modular/README.md) | ماؤنٹ کنٹرولرز اور ماڈیولز |
| [انحصار کا انجکشن](routing/modular/dependency-injection.md) | خدمات، ان کے دائرہ کار اور کنٹینر کی وضاحت کریں۔ |
| [گارڈز اور میٹا ڈیٹا](routing/modular/guards-and-metadata.md) | راستوں کی حفاظت اور دستاویز کریں۔ |
| [ماڈیولر روٹر بمقابلہ NestJS](routing/modular/vs-nestjs.md) | کے ساتھ موازنہ NestJS |

### حسب ضرورت روٹر انضمام {custom}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [حسب ضرورت روٹنگ](routing/custom/README.md) | ایک موجودہ FastAPI ایپ شامل کریں۔ |

## فرنٹ اینڈ

### مشترکہ معاہدے
| صفحہ | جو اس کی تعریف کرتا ہے۔ |
|---|---|
| [اعمال اور نیویگیشن](views/frontend/actions-and-navigation.md) | ٹائپ کردہ ایکشن کو کال کریں، صفحات کو لنک کریں، URL پڑھیں |

### Nexy نظارے۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [.nexy فائلیں](views/nexy/README.md) | Python، Jinja2 اور پرپس کے ساتھ ایک صفحہ لکھیں۔ |
| [اجزاء](views/nexy/components.md) | `Image`، `Link`، `Audio`، `Video` اور `Import` کا استعمال کریں۔ |

### فائلوں میں صفحات اور ترتیب {fbr,custom}
| صفحہ | جو اس کی تعریف کرتا ہے۔ |
|---|---|
| [فرنٹ اینڈ صفحات](views/frontend/pages.md) | ایک فائل، ایک راستہ: پرپس، رینڈرنگ، میٹا ڈیٹا |
| [فرنٹ اینڈ لے آؤٹ](views/frontend/layouts.md) | دستاویز کا شیل، گھوںسلا، اور لے آؤٹ کیا نہیں کر سکتا |
| [layout.nexy](views/nexy/layouts.md) | سرور موڈ لے آؤٹ لکھیں۔ |
| [Markdown اور MDX](views/nexy/markdown.md) | مواد کے صفحات لکھیں۔ |

### فریم ورک کے اختلافات
| صفحہ | کیا تبدیلیاں |
|---|---|
| [React اختلافات](views/react/differences.md) | اجزاء، ہکس اور `layout.tsx` {new} |
| [Vue اختلافات](views/vue/differences.md) | SFCs، refs اور `layout.vue` {new} |
| [Svelte اختلافات](views/svelte/differences.md) | رنز، اسٹورز اور `layout.svelte` {new} |
| [Solid اختلافات](views/solid/differences.md) | سگنلز، ایکسیسرز اور `layout.tsx` {new} |
| [Preact اختلافات](views/preact/differences.md) | ہکس، سگنلز اور `layout.tsx` {new} |

## رینڈرنگ

### موڈز
| صفحہ | جو آپ فیصلہ کریں گے۔ |
|---|---|
| [انجام دینا ](rendering/README.md) | کون سا رینڈرنگ موڈ کسی صفحے پر فٹ بیٹھتا ہے۔ |
| [SSR](rendering/ssr.md) | سرور رینڈرنگ، ڈیفالٹ |
| [جزائر](rendering/islands.md) | غیر فعال، مرئی یا میڈیا کے استفسار پر ہائیڈریٹ کریں۔ |

### فائل کے صفحات کے طریقوں {fbr,custom}
| صفحہ | جو آپ فیصلہ کریں گے۔ |
|---|---|
| [آئی ایس آر](rendering/isr.md) | stale-while-revalidate کے ساتھ صفحات کیش کریں۔ |
| [CSR](rendering/csr.md) | کلائنٹ سائیڈ روٹنگ |

## رہنما

### فارم اور ڈیٹا
| صفحہ | آپ کیا کریں گے |
|---|---|
| [اعمال](guides/actions.md) | فارم یا ٹائپ شدہ TypeScript فنکشن سے Python فنکشن کو کال کریں۔ |
| [ڈیٹا بیس](guides/databases.md) | ایک ORM کا انتخاب کریں اور ہجرتیں چلائیں۔ |

### سیکیورٹی اور تعیناتی۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [مڈل ویئر اور سیکورٹی](guides/middleware-and-security.md) | CORS، GZip، قابل اعتماد میزبان اور سیشنز ترتیب دیں۔ |
| [تعیناتی](deployment/README.md) | بنائیں، کنٹینر بنائیں اور سرو کریں۔ |
| [کارکردگی](deployment/performance.md) | ڈیفالٹس کی پیمائش اور ٹیون کریں۔ |

### بنائیں اور ٹیسٹ کریں۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [Vite اور اسٹائلنگ](guides/frontend.md) | سیٹ اپ Vite، اسٹائلنگ اور کلائنٹ کی تعمیر |
| [جانچ](guides/testing.md) | pytest، `TestClient` اور vitest کے ساتھ ٹیسٹ کریں۔ |

### ٹولنگ اور مدد
| صفحہ | آپ کیا کریں گے |
|---|---|
| [دیو ٹول بار](guides/devtools.md) | `nexy dev` کا ٹول بار استعمال کریں، اور اسے آف کریں۔ |
| [کوڈنگ ایجنٹ](guides/ai-agents.md) | اپنے پروجیکٹ کے قواعد Claude Code، Codex اور OpenCode بتائیں |
| [خرابیوں کا سراغ لگانا](guides/troubleshooting.md) | لوگوں کے پہلے مسائل کو حل کریں۔ |

## ڈیٹا بیس

### ایس کیو ایل ڈیٹا بیس
| صفحہ | آپ کیا کریں گے |
|---|---|
| [SQLite](databases/sqlite.md) | ایک فائل استعمال کریں، کوئی سرور نہیں: انجن، پراگمس، منتقلی اور ٹیسٹ |
| [PostgreSQL](databases/postgresql.md) | psycopg کے ساتھ جڑیں، JSONB، arrays، تلاش اور upserts کا استعمال کریں۔ |
| [نیین ](databases/neon.md) | سرور لیس PostgreSQL کا استعمال کریں: پولڈ ہوسٹ، آٹو سسپینڈ اور برانچز |
| [MySQL اور MariaDB](databases/mysql-mariadb.md) | pymysql کے ساتھ جڑیں، utf8mb4، اپسرٹس اور مکمل متن کی تلاش کا استعمال کریں۔ |

## سے آرہا ہے۔

وہی کام، جو آپ جانتے ہیں اور پھر Nexy میں لکھے گئے فریم ورک میں۔

### جائزہ
| صفحہ | آپ کیا کریں گے |
|---|---|
| [دوسرے فریم ورک سے آرہا ہے](getting-started/coming-from-other-frameworks.md) | ترجمہ FastAPI، Next.js اور عادات کا اظہار Nexy میں کریں۔ |

### Python فریم ورک {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [سے FastAPI](coming-from/fastapi.md) | اپنا FastAPI کوڈ رکھیں: صرف `@app.get` فائل بن جاتی ہے۔ |
| [منجانب Flask](coming-from/flask.md) | نظارے، بلیو پرنٹس، ٹیمپلیٹس اور فارمز کو Nexy روٹس میں تبدیل کریں۔ |
| [منجانب Django](coming-from/django.md) | نقشہ کے نظارے، ٹیمپلیٹس، ماڈل، فارم اور ترتیبات Nexy پر |

### JavaScript پسدید {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [ایکسپریس سے ](coming-from/express.md) | روٹس، مڈل ویئر اور `req`/`res` کو Python ہینڈلرز میں ترجمہ کریں |
| [فاسٹائف ](coming-from/fastify.md) سے | اسکیموں، پلگ انز اور ہکس کو ماڈلز، فولڈرز اور فائلوں میں تبدیل کریں۔ |
| [ایلیسیا سے ](coming-from/elysia.md) | نقشہ `t` اسکیماس، گارڈز اور ایڈن سے Pydantic اور ٹائپ کردہ اعمال |
| [ہونو سے ](coming-from/hono.md) | نقشے کے راستوں، مڈل ویئر اور `hc` کلائنٹ کو Nexy تک |

### فل اسٹیک فریم ورک {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [منجانب Next.js](coming-from/nextjs.md) | اپنے React صفحات رکھیں اور سرور کوڈ کو Python پر منتقل کریں |
| [سے Remix](coming-from/remix.md) | لوڈرز اور اعمال کو Python ہینڈلرز اور ایکشنز میں تبدیل کریں۔ |
| [Nuxt ](coming-from/nuxt.md) سے | اپنے Vue صفحات رکھیں اور `server/` کو Python پر منتقل کریں۔ |
| [SvelteKit ](coming-from/sveltekit.md) سے | اپنے Svelte صفحات رکھیں اور بوجھ، اعمال اور ہکس کو Python پر منتقل کریں۔ |
| [سے Astro](coming-from/astro.md) | اسی جزیرے کے ساتھ Astro صفحات کو `.nexy` صفحات کے طور پر لکھیں |
| [لاراویل سے ](coming-from/laravel.md) | نقشے کے راستوں، کنٹرولرز، بلیڈ، فصاحت اور Nexy کے لیے قطاریں۔ |
| [روبی آن ریلز سے ](coming-from/rails.md) | نقشے کے راستے، کنٹرولرز، ERB، ایکٹو ریکارڈ اور Nexy کے لیے نوکریاں |

### کنٹرولر فریم ورک {modular}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [سے NestJS](coming-from/nestjs.md) | کنٹرولرز، ماڈیولز، پرووائیڈرز اور گارڈز کو ماڈیولر راؤٹر میں منتقل کریں۔ |
| [اسپرنگ بوٹ سے ](coming-from/spring-boot.md) | کنٹرولرز، سروسز اور فلٹرز کو ماڈیولر روٹر میں منتقل کریں۔ |

## حوالہ

### کمانڈز اور تشکیل
| صفحہ | اس میں کیا درج ہے۔ |
|---|---|
| [CLI](reference/cli.md) | کمانڈز، جھنڈے، پرامپٹس اور ایگزٹ کوڈز |
| [ترتیب ](reference/config.md) | ہر `nexyconfig.py` فیلڈ اور اس کا ڈیفالٹ |

### Python API اور غلطیاں
| صفحہ | اس میں کیا درج ہے۔ |
|---|---|
| [Python API](reference/python-api.md) | ہر نام Nexy برآمد کرتا ہے، بذریعہ ماڈیول |
| [مستثنیات اور غلطیاں](reference/exceptions.md) | ہر ناکامی، اس کی حیثیت، اور اس کا جواب دینے والی فائل |

### فائل کنونشنز {fbr,custom}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [فائل کنونشنز](reference/file-conventions.md) | محفوظ فائلیں اور روٹنگ کے اصول |

### کنونشنز اور تصورات
| صفحہ | آپ کیا کریں گے |
|---|---|
| [لغت ](reference/glossary.md) | الفاظ جو یہ دستاویزات استعمال کرتے ہیں۔ |
| [سیکورٹی](reference/security.md) | ورژن فرش، قواعد Nexy کی پیروی کرتا ہے، آڈٹ |

## لے آؤٹ
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
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

## اعلی درجے کی

### اعلیٰ {advanced}

| صفحہ | آپ کیا کریں گے |
|---|---|
| [Nexy کیسے کام کرتا ہے](getting-started/how-nexy-works.md) | دیکھیں کہ فائل اور صفحہ کے درمیان کیا ہوتا ہے، اور Nexy آپ کے لیے کیا چھوڑتا ہے۔ |
| [2.2 تک اپ گریڈ کرنا](getting-started/upgrading.md) | 2.1 سے 2.2 تک منتقل کریں۔ |
| [بین الاقوامی کاری (i18n)](guides/i18n.md) | اپنی پسند کی لائبریری کے ساتھ ترجمے شامل کریں۔ |
| [ترکیبیں](guides/recipes.md) | مثالیں اور نمونے، ٹیوٹوریل نہیں۔ |

*یہ صفحات پہلے سے طے شدہ پڑھنے کے راستے کا حصہ نہیں ہیں۔ ایک "تمام دستاویزات" کا لنک آپ کو سب کچھ دیکھنے کی اجازت دیتا ہے۔*
