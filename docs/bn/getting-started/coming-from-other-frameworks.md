# অন্য কাঠামো থেকে আসছে

Nexy হল FastAPI প্লাস ফাইল-ভিত্তিক রাউটিং, সার্ভার-রেন্ডার করা পৃষ্ঠা এবং ঐচ্ছিক React, Vue, Svelte, Solid বা Preact দ্বীপ। এই পৃষ্ঠাটি ম্যাপ করে যা আপনি ইতিমধ্যেই জানেন।

## থেকে FastAPI

| FastAPI | নেক্সি |
|---|---|
| `@app.get("/users")` একটি মডিউলে আপনি | `GET` ফাংশন আমদানি করেন `src/routes/users.py` |
| `app.include_router(router)` | ফাইল পাথ হল URL; নিবন্ধন করার কিছু নেই |
| পথ পরম `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | এখনও `Depends(...)`: হ্যান্ডলাররা হল FastAPI হ্যান্ডলার |
| Jinja2 `TemplateResponse` | শেষবিন্দুর পাশে একটি `.nexy` পৃষ্ঠা |
| `uvicorn main:app` | `nx dev` দিয়ে দৌড়ান, তারপর `nx build && nx start` |

`src/routes/*.py` এর অধীনে সবকিছুই সাধারণ FastAPI: নির্ভরতা, Pydantic মডেল, মিডলওয়্যার এবং `/docs` কাজ করে।

## থেকে Next.js

| Next.js | নেক্সি |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` বা `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (মালিক `<html>`) | `src/routes/layout.tsx` `useCSR = True` (React) সহ, অথবা `src/routes/layout.nexy` সার্ভার মোডে |
| নেস্টেড `layout.tsx` | নেস্টেড `layout.tsx` / `layout.vue` / `layout.svelte` ক্লায়েন্ট মোডে, নেস্টেড `layout.nexy` সার্ভার মোডে |
| একটি সার্ভার পৃষ্ঠায় `use client` উপাদানগুলি | [দ্বীপগুলি](../rendering/islands.md) সার্ভার মোডে |
| রুট হ্যান্ডলার `route.ts` | `src/routes/api/x.py`, লেখা Python |
| `(group)` ফোল্ডারগুলি | একই: `(group)/` |
| সার্ভার ক্রিয়াকলাপ [| [`@Action`](../guides/actions.md) ফাংশনগুলি একটি ফর্ম থেকে বা টাইপ করা ক্লায়েন্ট ফাংশনগুলি |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

ব্যাকএন্ড হল Python, তাই আপনার API আপনার ডেটা এবং ML কাজের সাথে কোড শেয়ার করে। ক্লায়েন্ট উপাদানগুলি একটি সম্পূর্ণ-পৃষ্ঠা React গাছের পরিবর্তে দ্বীপ হিসাবে হাইড্রেট করে।

## এক্সপ্রেস বা নোড ব্যাকএন্ড থেকে

| এক্সপ্রেস | নেক্সি |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` `async def GET(id)` | সহ
| `app.use(middleware)` | FastAPI মিডলওয়্যার, `nexyconfig.py` | থেকে নিবন্ধিত
| `res.json(obj)` | একটি ডিক্ট বা একটি Pydantic মডেল | ফেরত দিন
| EJS/Pug views | `.nexy` (Jinja2) পৃষ্ঠা |
| `npm run dev` | `nx dev` |

## একটি রাউটার নির্বাচন করা হচ্ছে

| ব্যবহার করুন | যখন |
|---|---|
| ফাইল-ভিত্তিক রাউটার | পৃষ্ঠা এবং ফাইল থেকে ম্যাপ করা শেষ পয়েন্ট; ডিফল্ট |
| মডুলার রাউটার | কন্ট্রোলার, মডিউল এবং নির্ভরতা ইনজেকশন, নেস্টজেএস-স্টাইল |

উভয়ই `nx new` দ্বারা ভারা এবং একই শেষ থেকে শেষ পরীক্ষা দ্বারা আচ্ছাদিত। [রাউটিং](../routing/README.md) এবং [মডুলার রাউটিং](../routing/modular/README.md) দেখুন।

## যেখানে পরের

- [দ্রুত শুরু](quick-start.md): একটি প্রকল্প তৈরি করুন এবং এটি চালান
- [প্রকল্প কাঠামো](project-structure.md): যেখানে প্রতিটি ফাইলের অন্তর্গত
- [রাউটিং](../routing/README.md): রাউটার নির্বাচন করুন
