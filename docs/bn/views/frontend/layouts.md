# ফ্রন্টএন্ড লেআউট

একটি **লেআউট** হল একটি মোড়ক যা এক বা একাধিক পৃষ্ঠার চারপাশে ভাগ করা কাঠামোকে সংজ্ঞায়িত করে। লেআউটগুলি স্থিতি সংরক্ষণ করে এবং নেভিগেশন চলাকালীন পূর্ণ-পৃষ্ঠা পুনরায় লোড এড়িয়ে "অ্যাপ-মতো" অভিজ্ঞতা সক্ষম করে৷

## নেস্টিং লজিক

লেআউটগুলি `src/routes/` এর অধীনে ডিরেক্টরি গাছের উপর ভিত্তি করে একটি শ্রেণিবদ্ধ কাঠামো অনুসরণ করে।

1.  **রুট লেআউট**: প্রতিটি প্রজেক্টের একটি রুট লেআউট থাকে (যেমন, `src/routes/layout.nexy`)। ডকুমেন্ট শেল সংজ্ঞায়িত করার জন্য এটিই দায়ী একমাত্র লেআউট: `<html>`, `<head>`, এবং `<body>`।
2.  **নেস্টেড লেআউটস**: যেকোনো ফোল্ডারের নিজস্ব `layout.*` ফাইল থাকতে পারে। এই লেআউটটি সেই ফোল্ডারের মধ্যে সমস্ত পৃষ্ঠা এবং সাব-লেআউটগুলিকে মোড়ানো হয়।
3.  **উত্তরাধিকার**: একটি পৃষ্ঠা রুট থেকে তার নিজস্ব ফোল্ডারে সমস্ত লেআউট দ্বারা মোড়ানো হয়।

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

একটি নেস্টেড লেআউট শুধুমাত্র তার UI এর অংশ আঁকে এবং পৃষ্ঠাটি রাখে যেখানে `children` যায়:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## শেয়ার্ড স্টেট এবং কম্পোজিশন

লেআউট স্থিতিশীল হতে ডিজাইন করা হয়েছে. ক্লায়েন্ট মোডে, একই লেআউট ভাগ করে এমন দুটি পৃষ্ঠার মধ্যে নেভিগেট করার সময়, লেআউটটি পুনরায় রেন্ডার করা হয় না **নয়**; শুধুমাত্র শিশু বিষয়বস্তু পরিবর্তন. সার্ভার মোডে প্রতিটি নেভিগেশন একটি নতুন নথি।

- **স্লট**: লেআউটগুলি একটি স্লট প্রদান করে যেখানে নেস্টেড পৃষ্ঠাটি ইনজেকশন করা হয়: JSX-এ `children`, এবং `children` একটি `.nexy` লেআউটে প্রপ।
- **রাষ্ট্রীয় সংরক্ষণ**: লেআউটটি মাউন্ট থাকার কারণে, এর মধ্যে থাকা যেকোনো অবস্থা (যেমন, একটি হেডারে একটি অনুসন্ধান প্রশ্ন) নেভিগেশনের সময় সংরক্ষিত হয়।

একটি `.nexy` বিন্যাসে একই স্লট:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

নীচের অনুসন্ধান ক্ষেত্রটি ব্যবহারকারীরা ড্যাশবোর্ড পৃষ্ঠাগুলির মধ্যে সরানোর সময় যা টাইপ করেছে তা রাখে, কারণ যে লেআউটটি এটি ধরে রাখে তা কখনও আনমাউন্ট হয় না:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## স্ট্যাটিক সীমাবদ্ধতা

প্রি-রেন্ডার করা (SSG) রুটের জন্য রুট লেআউট অনুরোধ-সময়ের ডেটা যেমন কুকিজ বা হেডারের উপর নির্ভর করতে পারে না। এটি অবশ্যই একটি স্ট্যাটিক শেল হিসাবে উপস্থাপনযোগ্য হতে হবে যা ক্লায়েন্ট তখন হাইড্রেট করে।

স্ট্যাটিক শেলের একটি স্ক্রিপ্টে পরিবর্তে ব্রাউজার থেকে থিমটি পড়ুন:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## ফ্রেমওয়ার্ক বাস্তবায়ন

ফ্রেমওয়ার্ক অনুসারে স্লট এবং নেস্টিং এর বাস্তবায়ন কিছুটা পরিবর্তিত হয়। আপনার নির্বাচিত প্রযুক্তির জন্য **পার্থক্য** নির্দেশিকা দেখুন:

- [React পার্থক্য](../react/differences.md)
- [Vue পার্থক্য](../vue/differences.md)
- [Svelte পার্থক্য](../svelte/differences.md)
- [Solid পার্থক্য](../solid/differences.md)
- [Preact পার্থক্য](../preact/differences.md)
