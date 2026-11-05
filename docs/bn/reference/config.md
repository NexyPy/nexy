# কনফিগার

কনফিগারেশন হল প্রোজেক্ট রুটে `nexyconfig.py`-এর একটি ক্লাস। Nexy এটি যে ডিরেক্টরিতে চলে সেখান থেকে এটি লোড করে; ফাইল ছাড়া একটি প্রকল্প ডিফল্ট ব্যবহার করে।

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

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `usePort` | `3000` | `dev` এবং `start` | এর জন্য পোর্ট
| `useHost` | `"0.0.0.0"` | ঠিকানা বাঁধাই |
| `useSslKeyfile`, `useSslCertfile` | `None` | সরাসরি HTTPS পরিবেশন করেন |
| `useDevTools` | `True` | টুলবার `nexy dev` প্রতিটি পৃষ্ঠায় যোগ করে (পৃষ্ঠার তথ্য, রুট, ত্রুটি, কনফিগার); `False` এটিকে সরিয়ে দেয়। উৎপাদনে কখনই উপস্থিত হয় না |
| `useWorkers` | `0` | প্রক্রিয়া `nx start` রান; `0` লিনাক্স এবং ম্যাকওএস-এ সিপিইউ প্রতি একটি, উইন্ডোজে একটি |
| `useCSR` | `False` | ক্লায়েন্ট-সাইড রাউটিং মোড; `.nexy` রুটগুলি নিষ্ক্রিয় |

## রুট

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `useRouter` | `None` | একটি `APIRouter` উদাহরণ বা ক্লাস ফাইল-ভিত্তিক রুটের পাশে মাউন্ট করা হয়েছে; `None` মানে শুধুমাত্র ফাইল-ভিত্তিক |
| `excludeDirs` | `["templates", "extension", "docs"]` | রুট স্ক্যান করার সময় ডিরেক্টরিগুলি এড়িয়ে যায় |
| `useAliases` | `None` | আমদানি উপনাম, যেমন `{"@": "src"}` (`@/components/Counter.tsx` মানে `src/components/Counter.tsx`); `nx new` আপনি যাকে বেছে নিয়েছেন তা লেখেন এবং Vite এবং `tsconfig.json` এটি অনুসরণ করেন |

## ফ্রন্টেন্ড

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `useFF` | `None` | ক্লায়েন্ট ফ্রেমওয়ার্ক কারখানা: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | Vite | এর সাথে ক্লায়েন্ট বান্ডিল তৈরি এবং পরিবেশন করা
| `useMarkdownExtensions` | `[]` | `.md`/`.mdx` রেন্ডারিংয়ের জন্য অতিরিক্ত এক্সটেনশন |
| `useWatchExtensions` | `None` | অতিরিক্ত এক্সটেনশন ডেভ সার্ভার দেখে |
| `useWatchExcludePatterns` | `None` | গ্লোব প্যাটার্ন যা ডেভ সার্ভার উপেক্ষা করে |

> **জেনে রাখা ভালো**: `NexyConfigModel` ঘোষণা করে `useVite = False`; রানটাইম `Config` ডিফল্ট হল `True`।

## সংরক্ষিত ফাইলের নাম

প্রতিটি ক্ষেত্র একটি সংরক্ষিত ভূমিকায় এক্সটেনশন যোগ করে। `useLayoutExtensions = ["md"]` `layout.md` সংরক্ষিত করে তোলে, ঠিক `layout.nexy` এর মতো।

| ক্ষেত্র | এক্সটেনশন যোগ করে |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## API ডকুমেন্টেশন

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `useDocs` | `True` | OpenAPI স্কিমা এবং এর স্কেলার রেফারেন্স পৃষ্ঠা | পরিবেশন করে
| `useDocsUrl` | `"/docs"` | API রেফারেন্স পৃষ্ঠার পথ |
| `useRedocsUrl` | `"/redocs"` | ঘোষণা করা হয়েছে কিন্তু কোনো রুট মাউন্ট করা হয়নি |
| `useTitle` | `"Nexy App"` | OpenAPI শিরোনাম এবং পৃষ্ঠার শিরোনাম (`"Nexy"` `NexyConfigModel`]] |

## মিডলওয়্যার

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `useMiddlewares` | `[]` | ASGI মিডলওয়্যার ক্লাস |
| `useCORS` | `None` | কোয়ার্গের জন্য `CORSMiddleware` |
| `useGZip` | `None` | কোয়ার্গের জন্য `GZipMiddleware` |
| `useTrustedHost` | `None` | কোয়ার্গের জন্য `TrustedHostMiddleware` |
| `useSession` | `None` | কোয়ার্গের জন্য `SessionMiddleware` |
| `useAuth` | `None` | প্রমাণীকরণ মিডলওয়্যার কনফিগারেশন |
| `useHTTPSRedirect` | `False` | HTTPS-তে HTTP পুনঃনির্দেশ |

## Markdown

| ক্ষেত্র | ডিফল্ট | অর্থ |
|---|---|---|
| `useTocDepth` | `"2-6"` | শিরোনামের স্তরগুলি বিষয়বস্তুর সারণীতে অন্তর্ভুক্ত |
| `useTocTitle` | `"Table of Contents"` | TOC শিরোনাম |
| `useTocAuto` | `True` | Markdown পৃষ্ঠাগুলির | জন্য বিষয়বস্তুর সারণী তৈরি করে

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
- [মোতায়েন](../deployment/README.md): উৎপাদন বিকল্প
