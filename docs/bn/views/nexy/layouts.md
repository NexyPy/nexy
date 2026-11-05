# layout.nexy

সার্ভার মোডের বিন্যাস ফাইল (`useCSR = False`)। HTML নথির মালিক রুট।

## রুট লেআউট

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` এবং `<body>` এখানে বাস করে আর কোথাও নেই।
- `<Vite />` ক্লায়েন্ট স্ক্রিপ্ট এবং শৈলী একবার ইনজেক্ট করে, `<head>`-এ।
- `{{ children | safe }}` হল যেখানে পৃষ্ঠা, বা পরবর্তী নেস্টেড লেআউট রেন্ডার হয়।

## নেস্টেড লেআউট

একটি সাবডিরেক্টরীতে একটি `layout.nexy` যা সাবট্রিকে মোড়ানো হয় এবং এর প্যারেন্টের ভিতরে রেন্ডার করে। এটি নথি ট্যাগ পুনরাবৃত্তি করে না:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` `layout.nexy > blog/layout.nexy > page` হিসাবে রেন্ডার করে।

## উপাদান এবং দ্বীপ

একটি লেআউট `.nexy` উপাদান (একটি শিরোনাম, একটি ফুটার) এবং ক্লায়েন্ট উপাদান আমদানি করতে পারে। একটি লেআউটের একটি ক্লায়েন্ট উপাদান হল একটি [দ্বীপ](../../rendering/islands.md) অন্য যে কোনোটির মতো:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## একটি বিন্যাস ছাড়া

`layout.nexy` ছাড়া একটি প্রকল্প এখনও একটি বৈধ নথির সাথে উত্তর দেয়: নেক্সি `<!DOCTYPE html>`, ভিউপোর্ট মেটা এবং Vite ট্যাগ সহ একটি ন্যূনতম শেল ফিরে আসে। আপনার একটি শিরোনাম, ফন্ট বা নেভিগেশন প্রয়োজনের সাথে সাথে একটি লেআউট যোগ করুন।

## মডুলার রাউটারে

কন্ট্রোলাররা তাদের মতামত বেছে নেয়, তাই তারা নিজেরাই লেআউট রচনা করে:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## এটা কি করতে পারে না

- এটি `layout.tsx`, `layout.vue` বা `layout.svelte` এর সাথে সহাবস্থান করতে পারে না: একটি সার্ভার-মোড প্রকল্পের কোনো ক্লায়েন্ট রুট নেই ([মোডস](../../routing/fbr/modes.md))।
- এটি ক্লায়েন্টে চলে না: ইন্টারঅ্যাক্টিভিটির জন্য একটি দ্বীপ ব্যবহার করুন।

## পরবর্তী পদক্ষেপ

- [লেআউট](../../routing/fbr/layouts/README.md)
- [উত্তরাধিকার](../../routing/fbr/inheritance.md)
- [.nexy ফাইল](README.md)
