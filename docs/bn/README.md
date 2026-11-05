# নেক্সি ডকুমেন্টেশন

**ফুলস্ট্যাক ওয়েব অ্যাপ্লিকেশনের জন্য একটি Python কাঠামো।**

Nexy হল একটি Python ব্যাকএন্ড এবং একটি ব্রাউজার ফ্রন্টএন্ডের মধ্যে সীম সম্পর্কে। দুটি সার্ভার, দুটি বিল্ড সিস্টেম এবং দুটি রুট টেবিলের পরিবর্তে, আপনি একটি মূল পাবেন: FastAPI এবং Starlette অ্যাপ্লিকেশনটি পরিবেশন করে, Vite ক্লায়েন্ট তৈরি করে, এবং `src/routes/` এর অধীনে একটি ফাইল একটি রুট - `.nexy` একটি পৃষ্ঠা, `.py` একটি API হ্যান্ডলার৷

- **Python প্রথম** পেজ, এন্ডপয়েন্ট, ফর্ম এবং অ্যাকশন হল Python, এবং একটি সার্ভার-রেন্ডার করা পেজের ফ্রন্টএন্ড ফ্রেমওয়ার্কের প্রয়োজন হয় না।
- **তিনটি রাউটার, একটি ইন্টিগ্রেশন।** ফাইল-ভিত্তিক, মডুলার বা একটি বিদ্যমান FastAPI `APIRouter`।
- **আপনি যখন চান একটি ফ্রন্টএন্ড এক** React, Vue, Svelte, Solid বা Preact, প্রতি পৃষ্ঠায় দ্বীপ হিসাবে, অথবা ক্লায়েন্ট মোডে পুরো প্রকল্পের জন্য।
- **রেন্ডারিং, এক মডেল** সার্ভার রেন্ডারিং, ক্যাশে করা পৃষ্ঠা এবং দ্বীপ প্রতি পৃষ্ঠায় নির্ধারিত হয়; ক্লায়েন্ট রাউটিং একটি প্রকল্প সুইচ.
- **টাইপ করা হয়েছে কর্ম** একটি ফর্ম পোস্ট এবং একটি টাইপ করা ক্লায়েন্ট কল একই Python ফাংশনে পৌঁছায়।

`src/routes/` এর অধীনে একটি ফাইল দিয়ে শুরু করুন, এবং যখন প্রকল্প বৃদ্ধি পায় তখন কাঠামো যোগ করুন।

## শুরু করা

### প্রথম পদক্ষেপ
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [ইনস্টলেশন](getting-started/installation.md) | uv এবং Nexy CLI ইনস্টল করুন, তারপর আপনার প্রথম প্রকল্প তৈরি করুন |
| [দ্রুত শুরু](getting-started/quick-start.md) | একটি প্রকল্প তৈরি করুন, লাইভ রিলোড দিয়ে চালান এবং উৎপাদনের জন্য এটি তৈরি করুন |
| [টিউটোরিয়াল](getting-started/tutorial.md) | একটি এন্ডপয়েন্ট, শেয়ার করা ডেটা এবং 10 মিনিটের মধ্যে একটি প্রোডাকশন বিল্ড সহ একটি নোট পৃষ্ঠা তৈরি করুন |

### মডেল বুঝুন
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [মূল ধারণাগুলি](getting-started/core-concepts.md) | মানসিক মডেল পান: রুট, পৃষ্ঠা, দৃশ্য, উপাদান, হ্যান্ডলার, শেষবিন্দু |
| [নেক্সি কীভাবে কাজ করে](getting-started/how-nexy-works.md) | URL থেকে একটি অনুরোধ অনুসরণ করুন যেটি ফাইলটির উত্তর দেয় |
| [আর্কিটেকচার](architecture.md) | জানুন কোন স্তরটি কী করে এবং Nexy আপনার অ্যাপ্লিকেশনে কী রেখে যায় |
| [প্রকল্প কাঠামো](getting-started/project-structure.md) | একটি প্রকল্পের প্রতিটি ফোল্ডার এবং ফাইল কী |
| [একটি রাউটার চয়ন করুন](routing/README.md) | ফাইল-ভিত্তিক, মডুলার বা কাস্টম রাউটার চয়ন করুন |
| [একটি ভিউ ফরম্যাট চয়ন করুন](views/README.md) | একটি পৃষ্ঠার জন্য `.nexy`, Markdown বা একটি ক্লায়েন্ট ফ্রেমওয়ার্ক বেছে নিন |

### অন্য জায়গা থেকে আসছে
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [অন্য কাঠামো থেকে আসছে](getting-started/coming-from-other-frameworks.md) | অনুবাদ FastAPI, Next.js এবং নেক্সিতে অভ্যাস প্রকাশ করুন |

## রাউটিং

### ফাইল-ভিত্তিক {fbr}
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [ফাইল-ভিত্তিক রাউটিং](routing/fbr/README.md) | একটি ফাইল পাথকে একটি URL এ পরিণত করুন |
| [পৃষ্ঠাগুলি](routing/fbr/pages/README.md) | একটি পৃষ্ঠা লিখুন |
| [ডাইনামিক রুট](routing/fbr/pages/dynamic-routes.md) | ব্যবহার `[slug]`, `[...path]` এবং রুট গ্রুপ |
| [পৃষ্ঠা মেটাডেটা](routing/fbr/pages/metadata.md) | একটি পৃষ্ঠার শিরোনাম, বিবরণ এবং শেয়ারের ছবি সেট করুন {new} |
| [লেআউট](routing/fbr/layouts/README.md) | পৃষ্ঠাগুলির মধ্যে একটি ফ্রেম ভাগ করুন |
| [উত্তরাধিকার](routing/fbr/inheritance.md) | লেআউট, নির্ভরতা এবং ত্রুটি পৃষ্ঠাগুলির রেজোলিউশন অর্ডার পড়ুন |
| [সার্ভার মোড এবং ক্লায়েন্ট মোড](routing/fbr/modes.md) | `useCSR`, এবং প্রতিটি মোড কী অনুমতি দেয় |
| [লিঙ্ক করা এবং নেভিগেট করা](routing/fbr/navigation/linking-and-navigating.md) | পৃষ্ঠাগুলি লিঙ্ক করা, ক্লায়েন্টে নেভিগেট করা, প্রিফেচ করা |
| [হুকস](routing/fbr/navigation/hooks.md) | পাথ, ক্যোয়ারী, কুকিজ এবং সেশন পড়ুন |

### হ্যান্ডলার এবং ত্রুটি {fbr}
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [রুট হ্যান্ডলার](routing/fbr/handlers/README.md) | একটি Python শেষ বিন্দু যোগ করুন |
| [বৈধকরণ এবং ত্রুটিগুলি](routing/fbr/handlers/validation-and-errors.md) | উত্তর `422` এবং `404`, এবং একটি `HTTPException` | উত্থাপন করুন
| [WebSocket হ্যান্ডলারগুলি](routing/fbr/realtime/websocket.md) | একটি `SOCKET` সংযোগ হ্যান্ডেল |
| [নির্ভরতা এবং রক্ষক ](routing/fbr/dependencies/README.md) | একটি হ্যান্ডলারের আগে `dependencies.py` চালান এবং এটিকে উত্তরাধিকার সূত্রে পান |
| [মিডলওয়্যার ফাইলগুলি](routing/fbr/middleware/README.md) | `middleware.py` দিয়ে অনুরোধগুলি মোড়ানো, ডিরেক্টরি দ্বারা উত্তরাধিকারসূত্রে পাওয়া |
| [ত্রুটির পৃষ্ঠাগুলি](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy` এবং JSON ত্রুটি | সহ উত্তর
| [ফোল্ডার প্রতি ত্রুটি পৃষ্ঠাগুলি](routing/fbr/errors/folder-pages.md) | এজ কেস: সাব-ফোল্ডার থেকে ত্রুটি |

### মডুলার রাউটার {modular}
কন্ট্রোলার এবং মডিউল।
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [মডুলার রাউটিং](routing/modular/README.md) | মাউন্ট কন্ট্রোলার এবং মডিউল |
| [নির্ভরতা ইনজেকশন ](routing/modular/dependency-injection.md) | পরিষেবা, তাদের সুযোগ এবং ধারক সংজ্ঞায়িত করুন |
| [রক্ষী এবং মেটাডেটা](routing/modular/guards-and-metadata.md) | সুরক্ষা এবং নথির রুট |
| [মডুলার রাউটার বনাম NestJS](routing/modular/vs-nestjs.md) | NestJS | এর সাথে তুলনা

### কাস্টম রাউটার ইন্টিগ্রেশন {custom}
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [কাস্টম রাউটিং](routing/custom/README.md) | একটি বিদ্যমান FastAPI অ্যাপ অন্তর্ভুক্ত করুন |

## ফ্রন্টেন্ড

### শেয়ার করা চুক্তি
| পৃষ্ঠা | এটি কি সংজ্ঞায়িত করে |
|---|---|
| [ফ্রন্টেন্ড পেজ](views/frontend/pages.md) | একটি ফাইল, একটি রুট: প্রপস, রেন্ডারিং, মেটাডেটা |
| [ফ্রন্টেন্ড লেআউটস](views/frontend/layouts.md) | ডকুমেন্ট শেল, নেস্টিং এবং লেআউট কি করতে পারে না |
| [ক্রিয়া এবং নেভিগেশন](views/frontend/actions-and-navigation.md) | একটি টাইপ করা অ্যাকশন কল করুন, পৃষ্ঠাগুলি লিঙ্ক করুন, URL পড়ুন |

### নেক্সি ভিউ
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [.nexy ফাইল](views/nexy/README.md) | Python, Jinja2 এবং প্রপস | সহ একটি পৃষ্ঠা লিখুন
| [উপাদানগুলি](views/nexy/components.md) | ব্যবহার `Image`, `Link`, `Audio`, `Video` এবং `Import` |
| [layout.nexy](views/nexy/layouts.md) | সার্ভার-মোড লেআউট লিখুন |
| [Markdown এবং MDX](views/nexy/markdown.md) | বিষয়বস্তু পাতা লিখুন |

### ফ্রেমওয়ার্ক পার্থক্য
| পৃষ্ঠা | কি পরিবর্তন |
|---|---|
| [React পার্থক্য](views/react/differences.md) | উপাদান, হুক এবং `layout.tsx` {new} |
| [Vue পার্থক্য ](views/vue/differences.md) | SFC, রেফ এবং `layout.vue` {new} |
| [Svelte পার্থক্য ](views/svelte/differences.md) | রুনস, স্টোর এবং `layout.svelte` {new} |
| [Solid পার্থক্য](views/solid/differences.md) | সংকেত, অ্যাক্সেসর এবং `layout.tsx` {new} |
| [Preact পার্থক্য](views/preact/differences.md) | হুক, সংকেত এবং `layout.tsx` {new} |

## রেন্ডারিং

### মোড
| পৃষ্ঠা | আপনি কি সিদ্ধান্ত নেবেন |
|---|---|
| [রেন্ডারিং](rendering/README.md) | কোন রেন্ডারিং মোড একটি পৃষ্ঠার সাথে খাপ খায় |
| [SSR](rendering/ssr.md) | সার্ভার রেন্ডারিং, ডিফল্ট |
| [ISR](rendering/isr.md) | স্থির-যখন-পুনঃপ্রমাণিত সহ ক্যাশে পৃষ্ঠাগুলি |
| [CSR](rendering/csr.md) | ক্লায়েন্ট-সাইড রাউটিং |
| [দ্বীপগুলি](rendering/islands.md) | নিষ্ক্রিয়, দৃশ্যমান বা মিডিয়া প্রশ্নে হাইড্রেট |

## গাইড

### ফর্ম এবং তথ্য
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [ক্রিয়া ](guides/actions.md) | একটি ফর্ম বা একটি টাইপ করা TypeScript ফাংশন | থেকে একটি Python ফাংশন কল করুন
| [ডেটাবেস](guides/databases.md) | একটি ORM বেছে নিন এবং মাইগ্রেশন চালান |

### নিরাপত্তা এবং স্থাপনা
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [মিডলওয়্যার এবং নিরাপত্তা](guides/middleware-and-security.md) | সিওআরএস, জিজিপ, বিশ্বস্ত হোস্ট এবং সেশন সেট আপ করুন |
| [মোতায়েন](deployment/README.md) | নির্মাণ, ধারক এবং পরিবেশন |
| [কর্মক্ষমতা](deployment/performance.md) | ডিফল্টগুলি পরিমাপ করুন এবং সুর করুন |

### নির্মাণ এবং পরীক্ষা
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [Vite এবং স্টাইলিং](guides/frontend.md) | সেট আপ Vite, স্টাইলিং এবং ক্লায়েন্ট বিল্ড |
| [পরীক্ষা](guides/testing.md) | pytest, `TestClient` এবং ভিটেস্ট | সহ পরীক্ষা

### টুলিং এবং সাহায্য
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [দেব টুলবার](guides/devtools.md) | `nexy dev` এর টুলবার ব্যবহার করুন এবং এটি বন্ধ করুন |
| [কোডিং এজেন্ট ](guides/ai-agents.md) | Claude Code, Codex এবং OpenCode আপনার প্রকল্পের নিয়ম | দিন
| [সমস্যা নিবারণ](guides/troubleshooting.md) | মানুষের প্রথম সমস্যাগুলি ঠিক করুন |

## রেফারেন্স

### কমান্ড এবং কনফিগারেশন
| পৃষ্ঠা | এটি যা তালিকাভুক্ত করে |
|---|---|
| [CLI](reference/cli.md) | কমান্ড, পতাকা, প্রম্পট এবং এক্সিট কোড |
| [কনফিগ](reference/config.md) | প্রতিটি `nexyconfig.py` ক্ষেত্র এবং এর ডিফল্ট |

### Python API এবং ত্রুটি
| পৃষ্ঠা | এটি যা তালিকাভুক্ত করে |
|---|---|
| [Python API](reference/python-api.md) | প্রতিটি নাম Nexy রপ্তানি করে, মডিউল দ্বারা |
| [ব্যতিক্রম এবং ত্রুটিগুলি](reference/exceptions.md) | প্রতিটি ব্যর্থতা, তার স্থিতি, এবং ফাইল যা উত্তর দেয় |

### কনভেনশন এবং ধারণা
| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [ফাইল কনভেনশন](reference/file-conventions.md) | সংরক্ষিত ফাইল এবং রাউটিং নিয়ম |
| [শব্দকোষ ](reference/glossary.md) | এই নথিপত্রগুলি যে শব্দগুলি ব্যবহার করে |
| [নিরাপত্তা](reference/security.md) | সংস্করণ মেঝে, নিয়ম Nexy অনুসরণ করে, অডিট |

## লেআউট
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

## উন্নত

### উন্নত {advanced}

| পৃষ্ঠা | আপনি কি করবেন |
|---|---|
| [2.2 তে আপগ্রেড করা হচ্ছে](getting-started/upgrading.md) | 2.1 থেকে 2.2 এ স্থানান্তর করা |
| [আন্তর্জাতিককরণ (i18n)](guides/i18n.md) | আপনার পছন্দের লাইব্রেরির সাথে অনুবাদ যোগ করুন |
| [রেসিপি](guides/recipes.md) | উদাহরণ এবং প্যাটার্ন, টিউটোরিয়াল নয় |

*এই পৃষ্ঠাগুলি ডিফল্ট পড়ার পথের অংশ নয়। একটি "সমস্ত ডকুমেন্টেশন" লিঙ্ক আপনাকে সবকিছু দেখতে দেয়।*
