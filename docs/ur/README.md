# Nexy دستاویزات

**فل اسٹیک ویب ایپلیکیشنز کے لیے ایک Python فریم ورک۔**

Nexy ایک Python بیک اینڈ اور براؤزر فرنٹ اینڈ کے درمیان سیون کے بارے میں ہے۔ دو سرورز، دو بلڈ سسٹمز اور دو روٹ ٹیبلز کے بجائے، آپ کو ایک اصل ملتا ہے: FastAPI اور Starlette ایپلی کیشن کو پیش کرتا ہے، Vite کلائنٹ بناتا ہے، اور `src/routes/` کے نیچے فائل ایک روٹ ہے - `.nexy` ایک صفحہ ہے، `.py` ایک API ہینڈلر ہے۔

- **Python پہلے۔** صفحات، اختتامی نکات، شکلیں اور اعمال Python ہیں، اور سرور کے ذریعے پیش کردہ صفحہ کو فرنٹ اینڈ فریم ورک کی ضرورت نہیں ہے۔
- **تین راؤٹرز، ایک انضمام۔** فائل پر مبنی، ماڈیولر، یا موجودہ FastAPI `APIRouter`۔
- **ایک فرنٹ اینڈ جب آپ چاہتے ہیں** React، Vue، Svelte، Solid یا Preact، فی صفحہ جزائر کے طور پر، یا کلائنٹ موڈ میں پورے پروجیکٹ کے لیے۔
- **رینڈرنگ، ایک ماڈل** سرور رینڈرنگ، کیشڈ صفحات اور جزائر فی صفحہ طے کیے جاتے ہیں۔ کلائنٹ روٹنگ ایک پروجیکٹ سوئچ ہے۔
- **ٹائپ شدہ اعمال** ایک فارم پوسٹ اور ایک ٹائپ شدہ کلائنٹ کال اسی Python فنکشن تک پہنچتی ہے۔

`src/routes/` کے تحت ایک فائل سے شروع کریں، اور جب پروجیکٹ بڑھے تو ڈھانچہ شامل کریں۔

## شروع کرنا

### پہلے اقدامات
| صفحہ | آپ کیا کریں گے |
|---|---|
| [انسٹالیشن](getting-started/installation.md) | uv اور Nexy CLI انسٹال کریں، پھر اپنا پہلا پروجیکٹ بنائیں |
| [فوری آغاز](getting-started/quick-start.md) | ایک پروجیکٹ بنائیں، اسے لائیو ری لوڈ کے ساتھ چلائیں، اور اسے پروڈکشن کے لیے بنائیں |
| [ٹیوٹوریل](getting-started/tutorial.md) | ایک اختتامی نقطہ، مشترکہ ڈیٹا اور 10 منٹ میں پروڈکشن کی تعمیر کے ساتھ نوٹس کا صفحہ بنائیں |

### ماڈل کو سمجھیں۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [بنیادی تصورات](getting-started/core-concepts.md) | ذہنی ماڈل حاصل کریں: راستہ، صفحہ، منظر، جزو، ہینڈلر، اختتامی نقطہ |
| [Nexy کیسے کام کرتا ہے](getting-started/how-nexy-works.md) | URL سے اس فائل میں ایک درخواست پر عمل کریں جو اس کا جواب دیتی ہے |
| [آرکیٹیکچر](architecture.md) | جانیں کہ کون سی پرت کیا کرتی ہے، اور Nexy آپ کی ایپلی کیشن میں کیا چھوڑتا ہے |
| [پروجیکٹ ڈھانچہ](getting-started/project-structure.md) | جانیں کہ پروجیکٹ میں ہر فولڈر اور فائل کیا ہے |
| [ایک راؤٹر کا انتخاب کریں](routing/README.md) | فائل پر مبنی، ماڈیولر یا کسٹم راؤٹر کا انتخاب |
| [دیکھنے کا فارمیٹ منتخب کریں](views/README.md) | کسی صفحے کے لیے `.nexy`، Markdown یا کلائنٹ فریم ورک کا انتخاب کریں |

### کہیں اور سے آرہا ہے۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [ایک اور فریم ورک سے آرہا ہے](getting-started/coming-from-other-frameworks.md) | ترجمہ FastAPI، Next.js اور عادات کو Nexy میں ظاہر کریں |

## روٹنگ

### فائل پر مبنی {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [فائل پر مبنی روٹنگ](routing/fbr/README.md) | فائل کے راستے کو یو آر ایل میں تبدیل کریں |
| [صفحات](routing/fbr/pages/README.md) | ایک صفحہ لکھیں |
| [متحرک راستے](routing/fbr/pages/dynamic-routes.md) | `[slug]`، `[...path]` اور روٹ گروپس کا استعمال کریں |
| [صفحہ کا میٹا ڈیٹا](routing/fbr/pages/metadata.md) | صفحہ کا عنوان، تفصیل اور تصویر کا اشتراک کریں {new} |
| [لے آؤٹ](routing/fbr/layouts/README.md) | صفحات کے درمیان ایک فریم کا اشتراک کریں |
| [وراثت](routing/fbr/inheritance.md) | ترتیب، انحصار اور خرابی کے صفحات کے ریزولوشن آرڈر کو پڑھیں |
| [سرور موڈ اور کلائنٹ موڈ](routing/fbr/modes.md) | `useCSR`، اور ہر موڈ کیا اجازت دیتا ہے |
| [جوڑنا اور نیویگیٹ کرنا](routing/fbr/navigation/linking-and-navigating.md) | صفحات کو لنک کرنا، کلائنٹ پر نیویگیٹ کرنا، پیشگی بازیافت کرنا |
| [ہکس](routing/fbr/navigation/hooks.md) | راستہ، استفسار، کوکیز اور سیشن پڑھیں |

### ہینڈلر اور غلطیاں {fbr}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [روٹ ہینڈلرز](routing/fbr/handlers/README.md) | ایک Python اختتامی نقطہ شامل کریں |
| [تصدیق اور غلطیاں](routing/fbr/handlers/validation-and-errors.md) | جواب `422` اور `404`، اور ایک `HTTPException` |
| [WebSocket ہینڈلرز](routing/fbr/realtime/websocket.md) | ایک `SOCKET` کنکشن کو ہینڈل کریں |
| [انحصار اور محافظین](routing/fbr/dependencies/README.md) | ایک ہینڈلر سے پہلے `dependencies.py` چلائیں، اور اسے وارث بنائیں |
| [مڈل ویئر فائلیں](routing/fbr/middleware/README.md) | درخواستوں کو `middleware.py` کے ساتھ لپیٹنا، ڈائرکٹری | سے وراثت میں ملی۔
| [خرابی کے صفحات](routing/fbr/errors/README.md) | `notfound.nexy`، `errors.nexy` اور JSON کی غلطیوں کے ساتھ جواب دیں |
| [خرابی صفحات فی فولڈر](routing/fbr/errors/folder-pages.md) | ایج کیس: ذیلی فولڈرز سے غلطیاں |

### ماڈیولر راؤٹر {modular}
کنٹرولرز اور ماڈیولز۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [ماڈیولر روٹنگ](routing/modular/README.md) | ماؤنٹ کنٹرولرز اور ماڈیولز |
| [انحصار انجیکشن](routing/modular/dependency-injection.md) | خدمات، ان کے دائرہ کار اور کنٹینر کی وضاحت کریں |
| [گارڈز اور میٹا ڈیٹا](routing/modular/guards-and-metadata.md) | راستوں کی حفاظت اور دستاویز |
| [ماڈیولر روٹر بمقابلہ NestJS](routing/modular/vs-nestjs.md) | NestJS | کے ساتھ موازنہ

### حسب ضرورت روٹر انضمام {custom}
| صفحہ | آپ کیا کریں گے |
|---|---|
| [اپنی مرضی کے مطابق روٹنگ](routing/custom/README.md) | ایک موجودہ FastAPI ایپ شامل کریں |

## فرنٹ اینڈ

### مشترکہ معاہدے
| صفحہ | یہ کیا وضاحت کرتا ہے |
|---|---|
| [فرنٹ اینڈ پیجز](views/frontend/pages.md) | ایک فائل، ایک روٹ: پروپس، رینڈرنگ، میٹا ڈیٹا |
| [فرنٹ اینڈ لے آؤٹس](views/frontend/layouts.md) | دستاویز کا شیل، نیسٹنگ، اور لے آؤٹ کیا نہیں کر سکتا |
| [ایکشن اور نیویگیشن](views/frontend/actions-and-navigation.md) | ٹائپ کردہ ایکشن کو کال کریں، صفحات کو لنک کریں، یو آر ایل پڑھیں |

### Nexy نظارے۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [.nexy فائلز](views/nexy/README.md) | Python، Jinja2 اور پرپس | کے ساتھ ایک صفحہ لکھیں۔
| [اجزاء](views/nexy/components.md) | استعمال کریں `Image`، `Link`، `Audio`، `Video` اور `Import` |
| [layout.nexy](views/nexy/layouts.md) | سرور موڈ لے آؤٹ لکھیں |
| [Markdown اور MDX](views/nexy/markdown.md) | مواد کے صفحات لکھیں |

### فریم ورک کے اختلافات
| صفحہ | کیا تبدیلیاں |
|---|---|
| [React اختلافات](views/react/differences.md) | اجزاء، کانٹے اور `layout.tsx` {new} |
| [Vue اختلافات](views/vue/differences.md) | SFCs، refs اور `layout.vue` {new} |
| [Svelte اختلافات](views/svelte/differences.md) | رنز، اسٹورز اور `layout.svelte` {new} |
| [Solid اختلافات](views/solid/differences.md) | سگنلز، ایکسیسرز اور `layout.tsx` {new} |
| [Preact اختلافات](views/preact/differences.md) | کانٹے، سگنل اور `layout.tsx` {new} |

## رینڈرنگ

### موڈز
| صفحہ | آپ کیا فیصلہ کریں گے |
|---|---|
| [رینڈرنگ](rendering/README.md) | کون سا رینڈرنگ موڈ کسی صفحے پر فٹ بیٹھتا ہے |
| [SSR](rendering/ssr.md) | سرور رینڈرنگ، ڈیفالٹ |
| [ISR](rendering/isr.md) | stale-while-revalidate کے ساتھ کیش صفحات |
| [CSR](rendering/csr.md) | کلائنٹ سائیڈ روٹنگ |
| [جزیرے](rendering/islands.md) | بیکار، مرئی یا میڈیا کے استفسار پر ہائیڈریٹ |

## رہنما

### فارم اور ڈیٹا
| صفحہ | آپ کیا کریں گے |
|---|---|
| [ایکشن](guides/actions.md) | فارم سے Python فنکشن کو کال کریں یا ٹائپ شدہ TypeScript فنکشن |
| [ڈیٹا بیسز](guides/databases.md) | ایک ORM کا انتخاب کریں اور ہجرتیں چلائیں |

### سیکیورٹی اور تعیناتی۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [مڈل ویئر اور سیکیورٹی](guides/middleware-and-security.md) | CORS، GZip، قابل اعتماد میزبان اور سیشنز | مرتب کریں
| [تعینات کریں](deployment/README.md) | بنائیں، کنٹینر بنائیں اور سرو کریں |
| [کارکردگی](deployment/performance.md) | ڈیفالٹس کی پیمائش اور ٹیون |

### بنائیں اور ٹیسٹ کریں۔
| صفحہ | آپ کیا کریں گے |
|---|---|
| [Vite اور اسٹائلنگ](guides/frontend.md) | سیٹ اپ Vite، اسٹائلنگ اور کلائنٹ کی تعمیر |
| [ٹیسٹنگ](guides/testing.md) | pytest، `TestClient` اور vitest | کے ساتھ ٹیسٹ

### ٹولنگ اور مدد
| صفحہ | آپ کیا کریں گے |
|---|---|
| [دیو ٹول بار](guides/devtools.md) | `nexy dev` کا ٹول بار استعمال کریں، اور اسے آف کریں |
| [کوڈنگ ایجنٹس](guides/ai-agents.md) | اپنے پروجیکٹ کے قواعد Claude Code، Codex اور OpenCode دیں |
| [ٹربل شوٹنگ](guides/troubleshooting.md) | لوگوں کے پہلے مسائل کو ٹھیک کریں |

## حوالہ

### کمانڈز اور تشکیل
| صفحہ | اس میں کیا درج ہے |
|---|---|
| [CLI](reference/cli.md) | کمانڈز، جھنڈے، اشارے اور ایگزٹ کوڈ |
| [تشکیل](reference/config.md) | ہر `nexyconfig.py` فیلڈ اور اس کا ڈیفالٹ |

### Python API اور غلطیاں
| صفحہ | اس میں کیا درج ہے |
|---|---|
| [Python API](reference/python-api.md) | ہر نام Nexy برآمد کرتا ہے، بذریعہ ماڈیول |
| [استثنیات اور غلطیاں](reference/exceptions.md) | ہر ناکامی، اس کی حیثیت، اور اس کا جواب دینے والی فائل |

### کنونشنز اور تصورات
| صفحہ | آپ کیا کریں گے |
|---|---|
| [فائل کنونشنز](reference/file-conventions.md) | محفوظ فائلیں اور روٹنگ کے قواعد |
| [ لغت ](reference/glossary.md) | وہ الفاظ جو یہ دستاویزات استعمال کرتے ہیں |
| [سیکیورٹی](reference/security.md) | ورژن کی منزلیں، قواعد Nexy کی پیروی، آڈٹ |

## لے آؤٹ
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

## اعلی درجے کی

### اعلی درجے کی {advanced}

| صفحہ | آپ کیا کریں گے |
|---|---|
| [2.2 تک اپ گریڈنگ](getting-started/upgrading.md) | 2.1 سے 2.2 تک منتقلی |
| [انٹرنیشنلائزیشن (i18n)](guides/i18n.md) | اپنی پسند کی لائبریری کے ساتھ ترجمہ شامل کریں |
| [ترکیبیں](guides/recipes.md) | مثالیں اور نمونے، سبق نہیں |

*یہ صفحات پہلے سے طے شدہ پڑھنے کے راستے کا حصہ نہیں ہیں۔ ایک "تمام دستاویزات" کا لنک آپ کو سب کچھ دیکھنے کی اجازت دیتا ہے۔*
