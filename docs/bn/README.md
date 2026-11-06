# নেক্সি ডকুমেন্টেশন

**ফুলস্ট্যাক ওয়েব অ্যাপ্লিকেশনের জন্য একটি Python কাঠামো।**

Nexy আপনার পৃষ্ঠা এবং আপনার API একটি Python প্রকল্পে রাখে, একটি সার্ভার দ্বারা পরিবেশিত হয়। সংস্করণ 2.2 তৈরি করা হয়েছে FastAPI এর উপর: প্রতিটি API রুট হল একটি FastAPI রুট, একটি OpenAPI স্কিমাতে তালিকাভুক্ত যা স্কেলার `/docs` এ দেখায়।

- **Python প্রথম** পৃষ্ঠা, শেষবিন্দু, ফর্ম এবং ক্রিয়াগুলি হল Python, এবং একটি পৃষ্ঠার প্রয়োজন নেই JavaScript।
- **আপনি যখন চান একটি ফ্রন্টএন্ড এক** React, Vue, Svelte, Solid বা Preact, একটি উপাদান বা পুরো সাইটের জন্য।
- **এক ফাইল, এক URL** `src/routes/` এর অধীনে একটি ফাইল একটি রুট: `.nexy` একটি পৃষ্ঠা, `.py` একটি API শেষ পয়েন্ট।
- **বাড়তে রুম।** একটি ফাইল দিয়ে শুরু করুন মডিউলগুলিতে যান, অথবা একটি বিদ্যমান FastAPI রাউটারে প্লাগ ইন করুন, যখন প্রকল্পটি বৃদ্ধি পায়।

এখানে নতুন? পড়ুন [Nexy কি?](getting-started/what-is-nexy.md), তারপর [দ্রুত শুরু](getting-started/quick-start.md)।

## শুরু করা

### প্রথম পদক্ষেপ
| পাতা | আপনি কি করবেন |
|---|---|
| [নেক্সি কি?](getting-started/what-is-nexy.md) | Nexy কি, এটি কিসের উপর নির্মিত এবং আপনি কি পান তা জানুন |
| [ইনস্টলেশন](getting-started/installation.md) | uv এবং Nexy CLI ইনস্টল করুন, তারপর আপনার প্রথম প্রকল্প তৈরি করুন |
| [দ্রুত শুরু ](getting-started/quick-start.md) | একটি প্রকল্প তৈরি করুন, এটিকে লাইভ রিলোড দিয়ে চালান এবং উত্পাদনের জন্য এটি তৈরি করুন |
| [টিউটোরিয়াল](getting-started/tutorial.md) | 10 মিনিটের মধ্যে একটি এন্ডপয়েন্ট, শেয়ার করা ডেটা এবং একটি প্রোডাকশন বিল্ড সহ একটি নোট পৃষ্ঠা তৈরি করুন |

### মডেল বুঝুন
| পাতা | আপনি কি করবেন |
|---|---|
| [মূল ধারণা ](getting-started/core-concepts.md) | মানসিক মডেল পান: রুট, পৃষ্ঠা, দৃশ্য, উপাদান, হ্যান্ডলার, শেষ পয়েন্ট |
| [প্রকল্প কাঠামো ](getting-started/project-structure.md) | একটি প্রকল্পের প্রতিটি ফোল্ডার এবং ফাইল কি জন্য তা জানুন |
| [একটি রাউটার চয়ন করুন ](routing/README.md) | ফাইল-ভিত্তিক, মডুলার বা কাস্টম রাউটার চয়ন করুন |
| [একটি ভিউ ফরম্যাট বেছে নিন](views/README.md) | একটি পৃষ্ঠার জন্য `.nexy`, Markdown বা একটি ক্লায়েন্ট ফ্রেমওয়ার্ক বেছে নিন |

## রাউটিং

### ফাইল-ভিত্তিক {fbr}
| পাতা | আপনি কি করবেন |
|---|---|
| [ফাইল-ভিত্তিক রাউটিং](routing/fbr/README.md) | একটি URL এ একটি ফাইল পাথ চালু করুন |
| [পৃষ্ঠাগুলি](routing/fbr/pages/README.md) | একটি পাতা লিখুন |
| [গতিশীল রুট](routing/fbr/pages/dynamic-routes.md) | `[slug]`, `[...path]` এবং রুট গ্রুপ ব্যবহার করুন |
| [পৃষ্ঠা মেটাডেটা](routing/fbr/pages/metadata.md) | একটি পৃষ্ঠার শিরোনাম, বিবরণ এবং শেয়ার ইমেজ সেট করুন {new} |
| [বিন্যাস](routing/fbr/layouts/README.md) | পৃষ্ঠাগুলির মধ্যে একটি ফ্রেম ভাগ করুন |
| [উত্তরাধিকার ](routing/fbr/inheritance.md) | লেআউট, নির্ভরতা এবং ত্রুটি পৃষ্ঠাগুলির রেজোলিউশন অর্ডার পড়ুন |
| [সার্ভার মোড এবং ক্লায়েন্ট মোড](routing/fbr/modes.md) | `useCSR`, এবং প্রতিটি মোড কি অনুমতি দেয় |
| [লিঙ্ক করা এবং নেভিগেট করা ](routing/fbr/navigation/linking-and-navigating.md) | পৃষ্ঠাগুলি লিঙ্ক করুন, ক্লায়েন্টে নেভিগেট করুন, প্রিফেচ করুন |
| [হুকস](routing/fbr/navigation/hooks.md) | পাথ, ক্যোয়ারী, কুকিজ এবং সেশন পড়ুন |

### হ্যান্ডলার এবং ত্রুটি {fbr}
| পাতা | আপনি কি করবেন |
|---|---|
| [রুট হ্যান্ডলার ](routing/fbr/handlers/README.md) | একটি Python শেষ বিন্দু যোগ করুন |
| [বৈধতা এবং ত্রুটি](routing/fbr/handlers/validation-and-errors.md) | উত্তর দাও `422` এবং `404`, এবং একটি `HTTPException` বাড়াও |
| [WebSocket হ্যান্ডলার](routing/fbr/realtime/websocket.md) | একটি `SOCKET` সংযোগ পরিচালনা করুন |
| [নির্ভরতা এবং প্রহরী](routing/fbr/dependencies/README.md) | একটি হ্যান্ডলারের আগে `dependencies.py` চালান, এবং এটিকে উত্তরাধিকারী করুন |
| [মিডলওয়্যার ফাইল](routing/fbr/middleware/README.md) | ডিরেক্টরি দ্বারা উত্তরাধিকারসূত্রে প্রাপ্ত `middleware.py` সহ অনুরোধগুলি মোড়ানো |
| [ত্রুটি পৃষ্ঠাগুলি](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy` এবং JSON ত্রুটি সহ উত্তর দিন |
| [ফোল্ডার প্রতি ত্রুটি পৃষ্ঠাগুলি](routing/fbr/errors/folder-pages.md) | এজ কেস: সাব-ফোল্ডার থেকে ত্রুটি |

### মডুলার রাউটার {modular}
কন্ট্রোলার এবং মডিউল।
| পাতা | আপনি কি করবেন |
|---|---|
| [মডুলার রাউটিং](routing/modular/README.md) | মাউন্ট কন্ট্রোলার এবং মডিউল |
| [নির্ভরতা ইনজেকশন ](routing/modular/dependency-injection.md) | পরিষেবা, তাদের সুযোগ এবং ধারক সংজ্ঞায়িত করুন |
| [গার্ড এবং মেটাডেটা](routing/modular/guards-and-metadata.md) | সুরক্ষা এবং নথি রুট |
| [মডুলার রাউটার বনাম NestJS](routing/modular/vs-nestjs.md) | সাথে তুলনা NestJS |

### কাস্টম রাউটার ইন্টিগ্রেশন {custom}
| পাতা | আপনি কি করবেন |
|---|---|
| [কাস্টম রাউটিং ](routing/custom/README.md) | একটি বিদ্যমান FastAPI অ্যাপ অন্তর্ভুক্ত করুন |

## ফ্রন্টেন্ড

### শেয়ার করা চুক্তি
| পাতা | এটা কি সংজ্ঞায়িত করে |
|---|---|
| [কর্ম এবং নেভিগেশন](views/frontend/actions-and-navigation.md) | একটি টাইপ করা অ্যাকশন কল করুন, পৃষ্ঠাগুলি লিঙ্ক করুন, URL পড়ুন |

### নেক্সি ভিউ
| পাতা | আপনি কি করবেন |
|---|---|
| [.nexy ফাইল](views/nexy/README.md) | Python, Jinja2 এবং প্রপস সহ একটি পৃষ্ঠা লিখুন |
| [উপাদান ](views/nexy/components.md) | `Image`, `Link`, `Audio`, `Video` এবং `Import` ব্যবহার করুন |

### ফাইলে পৃষ্ঠা এবং বিন্যাস {fbr,custom}
| পাতা | এটা কি সংজ্ঞায়িত করে |
|---|---|
| [ফ্রন্টএন্ড পেজ](views/frontend/pages.md) | একটি ফাইল, একটি রুট: প্রপস, রেন্ডারিং, মেটাডেটা |
| [ফ্রন্টএন্ড লেআউট](views/frontend/layouts.md) | ডকুমেন্ট শেল, নেস্টিং এবং লেআউট কি করতে পারে না |
| [layout.nexy](views/nexy/layouts.md) | সার্ভার-মোড লেআউট লিখুন |
| [Markdown এবং MDX](views/nexy/markdown.md) | কন্টেন্ট পেজ লিখুন |

### ফ্রেমওয়ার্ক পার্থক্য
| পাতা | কি পরিবর্তন |
|---|---|
| [React পার্থক্য](views/react/differences.md) | উপাদান, হুক এবং `layout.tsx` {new} |
| [Vue পার্থক্য](views/vue/differences.md) | SFCs, refs এবং `layout.vue` {new} |
| [Svelte পার্থক্য](views/svelte/differences.md) | Runes, দোকান এবং `layout.svelte` {new} |
| [Solid পার্থক্য](views/solid/differences.md) | সংকেত, অ্যাক্সেসর এবং `layout.tsx` {new} |
| [Preact পার্থক্য](views/preact/differences.md) | হুক, সংকেত এবং `layout.tsx` {new} |

## রেন্ডারিং

### মোড
| পাতা | আপনি কি সিদ্ধান্ত নেবেন |
|---|---|
| [রেন্ডারিং ](rendering/README.md) | কোন রেন্ডারিং মোড একটি পৃষ্ঠার সাথে ফিট করে |
| [SSR](rendering/ssr.md) | সার্ভার রেন্ডারিং, ডিফল্ট |
| [দ্বীপপুঞ্জ](rendering/islands.md) | নিষ্ক্রিয়, দৃশ্যমান বা মিডিয়া ক্যোয়ারীতে হাইড্রেট করুন |

### ফাইল পৃষ্ঠার মোড {fbr,custom}
| পাতা | আপনি কি সিদ্ধান্ত নেবেন |
|---|---|
| [আইএসআর](rendering/isr.md) | stale-while-revalidate সহ ক্যাশে পৃষ্ঠা |
| [CSR](rendering/csr.md) | ক্লায়েন্ট-সাইড রাউটিং |

## গাইড

### ফর্ম এবং তথ্য
| পাতা | আপনি কি করবেন |
|---|---|
| [কর্ম](guides/actions.md) | একটি ফর্ম বা একটি টাইপ করা TypeScript ফাংশন থেকে একটি Python ফাংশন কল করুন |
| [ডাটাবেস](guides/databases.md) | একটি ORM বেছে নিন এবং মাইগ্রেশন চালান |

### নিরাপত্তা এবং স্থাপনা
| পাতা | আপনি কি করবেন |
|---|---|
| [মিডলওয়্যার এবং নিরাপত্তা ](guides/middleware-and-security.md) | CORS, GZip, বিশ্বস্ত হোস্ট এবং সেশন সেট আপ করুন |
| [স্থাপন ](deployment/README.md) | নির্মাণ, ধারক এবং পরিবেশন |
| [কর্মক্ষমতা](deployment/performance.md) | ডিফল্টগুলি পরিমাপ করুন এবং সুর করুন |

### নির্মাণ এবং পরীক্ষা
| পাতা | আপনি কি করবেন |
|---|---|
| [Vite এবং স্টাইলিং](guides/frontend.md) | সেট আপ Vite, স্টাইলিং এবং ক্লায়েন্ট বিল্ড |
| [পরীক্ষা ](guides/testing.md) | pytest, `TestClient` এবং ভিটেস্ট দিয়ে পরীক্ষা করুন |

### টুলিং এবং সাহায্য
| পাতা | আপনি কি করবেন |
|---|---|
| [দেব টুলবার](guides/devtools.md) | `nexy dev` এর টুলবার ব্যবহার করুন এবং এটি বন্ধ করুন |
| [কোডিং এজেন্ট](guides/ai-agents.md) | আপনার প্রকল্পের নিয়মগুলি Claude Code, Codex এবং OpenCode দিন |
| [সমস্যা সমাধান ](guides/troubleshooting.md) | মানুষ আঘাত প্রথম সমস্যা ঠিক করুন |

## ডাটাবেস

### এসকিউএল ডাটাবেস
| পাতা | আপনি কি করবেন |
|---|---|
| [SQLite](databases/sqlite.md) | একটি ফাইল ব্যবহার করুন, কোনো সার্ভার নেই: ইঞ্জিন, প্রগমাস, মাইগ্রেশন এবং পরীক্ষা |
| [PostgreSQL](databases/postgresql.md) | সাইকোপজির সাথে সংযোগ করুন, JSONB, অ্যারে, অনুসন্ধান এবং আপসার্ট ব্যবহার করুন |
| [নিয়ন ](databases/neon.md) | সার্ভারহীন PostgreSQL ব্যবহার করুন: পুল হোস্ট, অটোসাসপেন্ড এবং শাখা |
| [মাইএসকিউএল এবং মারিয়াডিবি](databases/mysql-mariadb.md) | pymysql এর সাথে সংযোগ করুন, utf8mb4 ব্যবহার করুন, আপসার্ট এবং পূর্ণ-পাঠ্য অনুসন্ধান করুন |

## থেকে আসছে

একই কাজ, আপনার জানা ফ্রেমওয়ার্ক এবং তারপর Nexy এ লেখা।

### ওভারভিউ
| পাতা | আপনি কি করবেন |
|---|---|
| [অন্য কাঠামো থেকে আসছে](getting-started/coming-from-other-frameworks.md) | অনুবাদ করুন FastAPI, Next.js এবং নেক্সিতে অভ্যাস প্রকাশ করুন |

### Python কাঠামো {fbr}
| পাতা | আপনি কি করবেন |
|---|---|
| [থেকে FastAPI](coming-from/fastapi.md) | আপনার FastAPI কোড রাখুন: শুধুমাত্র `@app.get` একটি ফাইল হয়ে যায় |
| [থেকে Flask](coming-from/flask.md) | ভিউ, ব্লুপ্রিন্ট, টেমপ্লেট এবং ফর্মগুলিকে Nexy রুটে পরিণত করুন৷ |
| [থেকে Django](coming-from/django.md) | নেক্সিতে মানচিত্র দৃশ্য, টেমপ্লেট, মডেল, ফর্ম এবং সেটিংস |

### JavaScript ব্যাকএন্ড {fbr}
| পাতা | আপনি কি করবেন |
|---|---|
| [এক্সপ্রেস থেকে](coming-from/express.md) | Python হ্যান্ডলারে রুট, মিডলওয়্যার এবং `req`/`res` অনুবাদ করুন |
| [Fastify](coming-from/fastify.md) থেকে | স্কিমা, প্লাগইন এবং হুকগুলিকে মডেল, ফোল্ডার এবং ফাইলে পরিণত করুন |
| [Elysia থেকে](coming-from/elysia.md) | ম্যাপ `t` স্কিমা, গার্ড এবং ইডেন থেকে Pydantic এবং টাইপ করা অ্যাকশন |
| [হোনো থেকে](coming-from/hono.md) | ম্যাপ রুট, মিডলওয়্যার এবং নেক্সিতে `hc` ক্লায়েন্ট |

### ফুলস্ট্যাক ফ্রেমওয়ার্ক {fbr}
| পাতা | আপনি কি করবেন |
|---|---|
| [থেকে Next.js](coming-from/nextjs.md) | আপনার React পৃষ্ঠাগুলি রাখুন এবং সার্ভার কোডকে Python এ সরান |
| [থেকে Remix](coming-from/remix.md) | লোডার এবং অ্যাকশনকে Python হ্যান্ডলার এবং অ্যাকশনে পরিণত করুন |
| [Nuxt ](coming-from/nuxt.md) থেকে | আপনার Vue পৃষ্ঠাগুলি রাখুন এবং `server/` থেকে Python এ সরান |
| [SvelteKit থেকে](coming-from/sveltekit.md) | আপনার Svelte পৃষ্ঠাগুলি রাখুন এবং লোড, অ্যাকশন এবং হুকগুলিকে Python এ সরান |
| [থেকে Astro](coming-from/astro.md) | একই দ্বীপের সাথে Astro পৃষ্ঠাগুলিকে `.nexy` পৃষ্ঠা হিসাবে লিখুন |
| [লারাভেল থেকে](coming-from/laravel.md) | মানচিত্র রুট, কন্ট্রোলার, ব্লেড, বাগ্মী এবং Nexy এর সারি |
| [রুবি অন রেল থেকে](coming-from/rails.md) | নেক্সিতে ম্যাপ রুট, কন্ট্রোলার, ERB, অ্যাক্টিভ রেকর্ড এবং চাকরি |

### কন্ট্রোলার ফ্রেমওয়ার্ক {modular}
| পাতা | আপনি কি করবেন |
|---|---|
| [থেকে NestJS](coming-from/nestjs.md) | মডুলার রাউটারে কন্ট্রোলার, মডিউল, প্রদানকারী এবং গার্ড সরান |
| [স্প্রিং বুট থেকে](coming-from/spring-boot.md) | মডুলার রাউটারে কন্ট্রোলার, পরিষেবা এবং ফিল্টারগুলি সরান |

## রেফারেন্স

### কমান্ড এবং কনফিগারেশন
| পাতা | এটা কি তালিকাভুক্ত |
|---|---|
| [CLI](reference/cli.md) | কমান্ড, পতাকা, প্রম্পট এবং প্রস্থান কোড |
| [কনফিগারেশন](reference/config.md) | প্রতিটি `nexyconfig.py` ক্ষেত্র এবং এর ডিফল্ট |

### Python API এবং ত্রুটি
| পাতা | এটা কি তালিকাভুক্ত |
|---|---|
| [Python API](reference/python-api.md) | প্রতিটি নাম Nexy রপ্তানি করে, মডিউল দ্বারা |
| [ব্যতিক্রম এবং ত্রুটি](reference/exceptions.md) | প্রতিটি ব্যর্থতা, তার স্থিতি, এবং ফাইল যা এটির উত্তর দেয় |

### ফাইল কনভেনশন {fbr,custom}
| পাতা | আপনি কি করবেন |
|---|---|
| [ফাইল কনভেনশন](reference/file-conventions.md) | সংরক্ষিত ফাইল এবং রাউটিং নিয়ম |

### কনভেনশন এবং ধারণা
| পাতা | আপনি কি করবেন |
|---|---|
| [শব্দকোষ](reference/glossary.md) | এই ডক্স ব্যবহার করে শব্দ |
| [নিরাপত্তা](reference/security.md) | সংস্করণ মেঝে, নিয়ম Nexy অনুসরণ করে, অডিট |

## লেআউট
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

## উন্নত

### উন্নত {advanced}

| পাতা | আপনি কি করবেন |
|---|---|
| [কিভাবে Nexy কাজ করে](getting-started/how-nexy-works.md) | একটি ফাইল এবং একটি পৃষ্ঠার মধ্যে কী ঘটে এবং Nexy আপনার কাছে কী রেখে যায় তা দেখুন৷ |
| [2.2 এ আপগ্রেড করা হচ্ছে](getting-started/upgrading.md) | 2.1 থেকে 2.2 পর্যন্ত স্থানান্তর করুন৷ |
| [আন্তর্জাতিকীকরণ (i18n)](guides/i18n.md) | আপনার পছন্দের লাইব্রেরির সাথে অনুবাদ যোগ করুন |
| [রেসিপি ](guides/recipes.md) | উদাহরণ এবং নিদর্শন, একটি টিউটোরিয়াল নয় |

*এই পৃষ্ঠাগুলি ডিফল্ট পড়ার পথের অংশ নয়। একটি "সমস্ত ডকুমেন্টেশন" লিঙ্ক আপনাকে সবকিছু দেখতে দেয়।*
