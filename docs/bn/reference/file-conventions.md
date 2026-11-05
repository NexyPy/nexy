# ফাইল কনভেনশন

`src/routes/` এর অধীনে সংরক্ষিত নাম এবং নিয়ম।

## রুট ফাইল

| ফাইল | হয়ে যায় |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | এর ডিরেক্টরির রুট |
| `about.nexy` | `/about` |
| `[slug].nexy` | গতিশীল সেগমেন্ট `{slug}` |
| `[...path].nexy` | ধরা-সব `{path:path}` |
| `(group)/page.nexy` | `/page`: গ্রুপটি URL-এ উপস্থিত হয় না |
| `name.py` | API হ্যান্ডলার; ফাংশনের নাম `GET`, `POST`, ... হল পদ্ধতি |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | ক্লায়েন্ট রুট যখন ফ্রেমওয়ার্ক সক্ষম করা হয় `useFF` |

## সংরক্ষিত ফাইল

| ফাইল | ভূমিকা | বিস্তারিত |
|---|---|---|
| `layout.nexy` | সার্ভার মোড: এর নীচে প্রতিটি পৃষ্ঠা মোড়ানো; এইচটিএমএল ডকুমেন্টের মালিক রুট | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | ক্লায়েন্ট মোড (React): রুট এইচটিএমএল ডকুমেন্টের মালিক, নেস্টেড পৃষ্ঠাগুলি মোড়ানো | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | ক্লায়েন্ট মোড: নেস্টেড লেআউট | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | এর ডিরেক্টরির জন্য 404 পৃষ্ঠা | [ত্রুটির পৃষ্ঠাগুলি](../routing/fbr/errors/README.md) |
| `errors.nexy` | এর ডিরেক্টরির জন্য 500 পৃষ্ঠা | [ত্রুটির পৃষ্ঠাগুলি](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | এর ডিরেক্টরির জন্য 403 পৃষ্ঠা | [ফোল্ডার প্রতি ত্রুটি পৃষ্ঠাগুলি](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | এর ডিরেক্টরির জন্য 401 পৃষ্ঠা | [ফোল্ডার প্রতি ত্রুটি পৃষ্ঠাগুলি](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | সংরক্ষিত এখনও রানটাইম প্রভাব নেই | [ত্রুটির পৃষ্ঠাগুলি](../routing/fbr/errors/README.md) |
| `middleware.py` | একটি `async def middleware(request, call_next)` ডিরেক্টরি এবং নীচের অনুরোধগুলি মোড়ানো | [মিডলওয়্যার ফাইল](../routing/fbr/middleware/README.md) |
| `dependencies.py` | ডিরেক্টরি এবং এর শিশুদের জন্য একটি `dependencies = [fn, ...]` তালিকা প্রয়োগ করা হয়েছে | [নির্ভরতা](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python প্যাকেজ চিহ্নিতকারী | |
| `favicon.ico` | পরিবেশিত `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` এবং `useLoadingExtensions` এই নামের জন্য আরও এক্সটেনশন সংরক্ষণ করে। [কনফিগ](config.md) দেখুন।

## উপেক্ষা করা ফাইল

- `_` বা `.` দিয়ে শুরু হওয়া একটি ফাইল বা ফোল্ডার: এটি আংশিক, খসড়া এবং সাহায্যকারীর জন্য ব্যবহার করুন।
- একটি ফাইল যার এক্সটেনশন প্রকল্পের জন্য সক্রিয় নয়: এটি একটি সতর্কতা সহ এড়িয়ে গেছে৷

## URL প্রতি একটি ফাইল

একই ইউআরএলে সমাধান করা দুটি ফাইল উভয় নিবন্ধন করে। `blog/index.nexy` এর পাশে `blog.nexy` রাখবেন না।

## বাইরে `src/routes/`

| ফোল্ডার | উদ্দেশ্য |
|---|---|
| `src/components/` | পৃষ্ঠা দ্বারা আমদানি করা উপাদান; কখনও রুট |
| `src/apps/` | [মডুলার রাউটারের](../routing/modular/README.md) কন্ট্রোলার এবং মডিউল |
| `public/` | স্ট্যাটিক ফাইল, রুটে পরিবেশিত: `public/logo.svg` হল `/logo.svg` (এছাড়াও `/public/`] এর অধীনে) |
| `__nexy__/` | উৎপন্ন আউটপুট; কমিট না |

## পরবর্তী পদক্ষেপ

- [রাউটিং](../routing/README.md)
- [প্রকল্প কাঠামো](../getting-started/project-structure.md)
