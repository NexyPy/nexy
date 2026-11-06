# কনফিগার

কনফিগারেশন হল প্রোজেক্ট রুটে `nexyconfig.py`-এ একটি ক্লাস। Nexy এটি যে ডিরেক্টরিতে চলে সেখান থেকে এটি লোড করে; ফাইল ছাড়া একটি প্রকল্প ডিফল্ট ব্যবহার করে।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## সার্ভার

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `usePort` | `3000` | `dev` এবং `start` এর জন্য পোর্ট |
| `useHost` | `"0.0.0.0"` | ঠিকানা বাঁধা |
| `useSslKeyfile`, `useSslCertfile` | `None` | সরাসরি HTTPS পরিবেশন করুন |
| `useDevTools` | `True` | টুলবার `nexy dev` প্রতিটি পৃষ্ঠায় যোগ করে (পৃষ্ঠার তথ্য, রুট, ত্রুটি, কনফিগার); `False` এটিকে সরিয়ে দেয়। উত্পাদনে উপস্থিত হয় না |
| `useWorkers` | `0` | প্রক্রিয়াগুলি `nx start` চলে; `0` লিনাক্স এবং ম্যাকওএস-এ প্রতি সিপিইউ একটি, উইন্ডোজে একটি |
| `useCSR` | `False` | ক্লায়েন্ট-সাইড রাউটিং মোড; `.nexy` রুট নিষ্ক্রিয় করা হয়েছে |

## রুট

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `useRouter` | `None` | ফাইল-ভিত্তিক রুটের পাশে মাউন্ট করা একটি `APIRouter` উদাহরণ বা ক্লাস; `None` মানে শুধুমাত্র ফাইল-ভিত্তিক |
| `excludeDirs` | `["templates", "extension", "docs"]` | রুট স্ক্যান করার সময় ডিরেক্টরিগুলি এড়িয়ে যায় |
| `useAliases` | `None` | আমদানি উপনাম, যেমন `{"@": "src"}` (`@/components/Counter.tsx` মানে `src/components/Counter.tsx`); `nx new` আপনি যাকে বেছে নিয়েছেন তা লেখেন এবং Vite এবং `tsconfig.json` এটি অনুসরণ করেন |

## ফ্রন্টেন্ড

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `useFF` | `None` | ক্লায়েন্ট ফ্রেমওয়ার্ক কারখানা: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Vite দিয়ে ক্লায়েন্ট বান্ডিল তৈরি এবং পরিবেশন করা |
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` রেন্ডারিংয়ের জন্য অতিরিক্ত এক্সটেনশন |
| `useWatchExtensions` | `None` | অতিরিক্ত এক্সটেনশন dev সার্ভার ঘড়ি |
| `useWatchExcludePatterns` | `None` | গ্লোব প্যাটার্ন যা ডেভ সার্ভার উপেক্ষা করে |

> **জেনে রাখা ভালো**: `NexyConfigModel` ঘোষণা করে `useVite = False`; রানটাইম `Config` ডিফল্ট হল `True`।

## সংরক্ষিত ফাইলের নাম

প্রতিটি ক্ষেত্র একটি সংরক্ষিত ভূমিকায় এক্সটেনশন যোগ করে। `useLayoutExtensions = ["md"]` `layout.md` সংরক্ষিত করে তোলে, ঠিক `layout.nexy` এর মতো।

| মাঠ | এ এক্সটেনশন যোগ করে |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API ডকুমেন্টেশন

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `useDocs` | `True` | স্কেলার রেফারেন্স পৃষ্ঠা পরিবেশন করুন; `/openapi.json` যে কোন উপায়ে পরিবেশন করা হয় |
| `useDocsUrl` | `"/docs"` | API রেফারেন্স পৃষ্ঠার পথ |
| `useRedocsUrl` | `"/redocs"` | ঘোষিত কিন্তু কোন রুট মাউন্ট করা হয় না |
| `useTitle` | `"Nexy App"` | OpenAPI শিরোনাম এবং পৃষ্ঠার শিরোনাম (`"Nexy"` `NexyConfigModel`]) |

### প্রকল্পের একটি পৃষ্ঠার জন্য বিনামূল্যে `/docs`

এপিআই রেফারেন্স কোন রুটের আগে `/docs` উত্তর দেয়, তাই `src/routes/docs.nexy` বা `src/routes/docs/[[...slug]].nexy` সেখানে কখনই পরিবেশন করা হয় না। `nx dev` এবং `nx start` শুরুতে এমন একটি পৃষ্ঠার নাম দিন। এর সাথে রেফারেন্স সরান `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

অথবা `useDocs = False` দিয়ে এটি বন্ধ করুন। `/openapi.json` উভয় ক্ষেত্রেই পরিবেশিত থাকে: প্রকল্পের রুটগুলিকে সেই পথ থেকে দূরে রাখুন।

## মিডলওয়্যার

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI মিডলওয়্যার ক্লাস |
| `useCORS` | `None` | জন্য kwargs `CORSMiddleware` |
| `useGZip` | `None` | জন্য kwargs `GZipMiddleware` |
| `useTrustedHost` | `None` | জন্য kwargs `TrustedHostMiddleware` |
| `useSession` | `None` | জন্য kwargs `SessionMiddleware` |
| `useAuth` | `None` | প্রমাণীকরণ মিডলওয়্যার কনফিগারেশন |
| `useHTTPSRedirect` | `False` | HTTPS-এ HTTP রিডাইরেক্ট করুন |

## Markdown

| মাঠ | ডিফল্ট | অর্থ |
|---|---|---|
| `useTocDepth` | `"2-6"` | শিরোনাম স্তর বিষয়বস্তু সারণী অন্তর্ভুক্ত |
| `useTocTitle` | `"Table of Contents"` | TOC শিরোনাম |
| `useTocAuto` | `True` | Markdown পৃষ্ঠাগুলির জন্য বিষয়বস্তুর সারণী তৈরি করুন |

## ফাইল গাছের বাইরের রুট

একটি FastAPI `APIRouter` তৈরি করুন এবং এটি `useRouter` দিয়ে মাউন্ট করুন। এটি ফাইল-ভিত্তিক রুটের পাশে পরিবেশিত হয়:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

উপরের ডিফল্টগুলি `nexy/core/config.py` থেকে পড়া হয়।

## ঘোষণা, এখনও পড়া হয়নি

এই ক্ষেত্রগুলি `NexyConfigModel`-এ বিদ্যমান কিন্তু কোনো কোড সেগুলি গ্রাস করে না। তাদের সেট করার কোন প্রভাব নেই:

`useViteDevUrl`, `useRTL`।

## পরবর্তী পদক্ষেপ

- [i18n](../guides/i18n.md): আন্তর্জাতিকীকরণ
- [ফ্রন্টএন্ড](../guides/frontend.md): `useFF` এবং ক্লায়েন্ট বিল্ড
- [স্থাপন ](../deployment/README.md): উত্পাদন বিকল্প
