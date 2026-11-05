# প্রকল্প কাঠামো

একটি Nexy প্রকল্পের প্রতিটি ফাইলের একটি কাজ আছে। এই পৃষ্ঠাটি যা বলে।

## শীর্ষ স্তর

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

একটি ফোল্ডার চয়ন করতে, ফাইলটি কী তা জিজ্ঞাসা করুন:

- **ব্রাউজার খুলতে পারে এমন কিছু** - একটি রুট: `src/routes/`।
- **বিভিন্ন রুট দ্বারা ব্যবহৃত একটি অংশ** - একটি উপাদান বা একটি মডিউল: `src/components/`, `src/`।
- **একটি ফাইল যেভাবে পরিবেশিত হয়** - `public/`।
- **মডুলার রাউটারের একটি নিয়ামক** - `src/apps/`।
- **উৎপন্ন** - `__nexy__/`; এটি সম্পাদনা করবেন না

> [!WARNING]
> `src/routes/` স্ক্যান করা হয়: সেখানে রাখা একজন সাহায্যকারী একটি রুট হয়ে যায়। একটি সাহায্যকারী রাখুন যেটি `src/routes/` এর বাইরে একটি রুট নয়, অথবা `_` দিয়ে এর নাম শুরু করুন।

## `src/routes/`

নীচের সংরক্ষিত নামগুলি ছাড়া প্রতিটি ফাইল একটি রুট হয়ে যায়। ফাইল পাথ বিয়োগ এক্সটেনশন হল URL - [রাউটিং](../routing/README.md) দেখুন।

| ফাইল | ভূমিকা |
|---|---|
| `layout.nexy` | ভাইবোন এবং শিশু পাতাগুলি মোড়ানো |
| `errors.nexy` | ডিরেক্টরির জন্য 500 পৃষ্ঠা |
| `notfound.nexy` | ডিরেক্টরির জন্য 404 পৃষ্ঠা |
| `dependencies.py` | ডিরেক্টরির জন্য FastAPI নির্ভরতা ভাগ করেছে |
| `__init__.py` | Python প্যাকেজ চিহ্নিতকারী |
| `loading.nexy` | সংরক্ষিত - রুটগুলি থেকে বাদ দেওয়া হয়েছে, তবে এটির এখনও কোন রানটাইম প্রভাব নেই |

প্রতিটি পৃষ্ঠার নামও ফ্রেমওয়ার্ক প্রতি বিদ্যমান। `react()` কনফিগার করা সহ, `layout.jsx` এবং `layout.tsx` ঠিক `layout.nexy` এর মতো সংরক্ষিত। তালিকা তৈরি করা হয় `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`)।

> [!NOTE]
> `notfound.nexy` এবং `errors.nexy` শুধুমাত্র তখনই ইনস্টল করা হয় যখন রুট রুটে একটি কপি বিদ্যমান থাকে। একটি সাবডিরেক্টরিতে একটি অনুলিপি তারপর সেই উপসর্গের জন্য পৃষ্ঠাটিকে পরিমার্জন করে।

## `src/apps/`

ডিরেক্টরিটি `nexy new` মডুলার রাউটারের জন্য ব্যবহার করে: কন্ট্রোলার, মডিউল এবং প্রদানকারীরা `nexy.decorators` থেকে ডেকোরেটরের মাধ্যমে তাদের রুট নিবন্ধন করে, তারপরে `nexyconfig.py` এ `useRouter` এর সাথে মোট `APIRouter` মাউন্ট করা হয়।

একটি প্রকল্পে উভয় রাউটার থাকতে পারে: `useRouter` মডুলার রাউটার মাউন্ট করে, এবং যখনই সেই ডিরেক্টরিটি বিদ্যমান থাকে তখন `src/routes/` স্ক্যান করা হয়। [মডুলার রাউটিং](../routing/modular/README.md) দেখুন।

## `public/`

এখানে ফাইলগুলি সাইট রুট থেকে দেওয়া হয়: `/favicon.ico`, `/robots.txt`, ছবি, ফন্ট।

## `__nexy__/`

`nx build` দ্বারা উত্পন্ন (এবং `nx dev` দ্বারা এটির প্রয়োজনীয় অংশগুলির জন্য)। এতে রয়েছে:

- সংকলিত রুট মডিউল, একটি Python প্যাকেজ হিসাবে (`__nexy__/src/routes/...`);
- উৎপন্ন ক্লায়েন্ট এন্ট্রি পয়েন্ট (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` একটি Vite বিল্ডের পরে - সম্পদ, ম্যানিফেস্ট, প্রি-রেন্ডার করা HTML;
- `build-cache.json`।

সম্পূর্ণ ডিরেক্টরিটিকে নিষ্পত্তিযোগ্য হিসাবে বিবেচনা করুন: এটি মুছুন, এটি পুনর্নির্মাণ করুন। এটি হাতে সম্পাদনা করা পরবর্তী বিল্ডে পরিবর্তন হারায়। এটি `.gitignore` এ যোগ করুন।

## পরবর্তী পদক্ষেপ

- [রাউটিং](../routing/README.md): কিভাবে একটি পাথ একটি URL হয়ে যায়
- [কনফিগ](../reference/config.md): প্রতিটি প্রকল্পের বিকল্প
- [ফ্রন্টেন্ড](../guides/frontend.md): Vite, স্টাইলিং এবং ক্লায়েন্ট বিল্ড
