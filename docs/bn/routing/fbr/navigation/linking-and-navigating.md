# লিঙ্ক এবং নেভিগেট

ক্লায়েন্ট রাউটিং (`useCSR = True`) এর সাথে, দুটি পৃষ্ঠার মধ্যে একটি লিঙ্ক নথিটি পুনরায় লোড করার পরিবর্তে ব্রাউজারে পৃষ্ঠাটিকে অদলবদল করে। বিন্যাস তাদের রাষ্ট্র রাখা.

## প্লেইন লিঙ্ক ইতিমধ্যে কাজ

আপনার প্রোজেক্টের একটি পৃষ্ঠায় প্রতিটি `<a href>` ক্লায়েন্টে নেভিগেট করে, কোনো উপাদান এবং কোনো মার্কার ছাড়াই:

```html
<a href="/about">About</a>
```

একটি লিঙ্ক ব্রাউজারে রেখে দেওয়া হয় এবং পৃষ্ঠাটি সাধারণত লোড হয়, যখন:

- একটি সংশোধক কী রাখা হয়, বা বোতামটি প্রধান নয়;
- এর আছে `target` (`_self` ছাড়া), `download`, `rel="external"` বা `data-nexy-reload`;
- `href` হল অন্য একটি উৎস, একটি `mailto:` বা `tel:` লিঙ্ক, অথবা শুধুমাত্র একটি `#fragment`;
- পথটি কোন ক্লায়েন্ট রুটের সাথে মেলে না, তাই সার্ভার এটির উত্তর দেয়।

## `Link`

`Link` একই অ্যাঙ্কর যা একটি প্লেইন করতে পারে না: এটির `href` আপনার রুটের বিরুদ্ধে চেক করা হয়, এটি লক্ষ্য পৃষ্ঠাটিকে উষ্ণ করে, এবং এটি কখন বর্তমান পৃষ্ঠায় নির্দেশ করে তা জানে৷ আপনি যখন `nx dev` বা `nx build` চালান তখন Nexy আপনার কাঠামোর `Link` `__nexy__/src` মধ্যে তৈরি করে।

| ফ্রেমওয়ার্ক | আমদানি |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| প্রপ | অর্থ |
|---|---|
| `href` | প্রকল্পের একটি রুট (একটি টাইপো একটি টাইপ ত্রুটি), ঐচ্ছিকভাবে `?query` বা `#fragment`, বা একটি বহিরাগত URL সহ। |
| `replace` | একটি যোগ করার পরিবর্তে ইতিহাস এন্ট্রি প্রতিস্থাপন করুন। |
| `scroll` | `false` নেভিগেট করার পরে স্ক্রোল অবস্থান রাখে। ডিফল্ট: `true`। |
| `prefetch` | `'intent'` (ডিফল্ট) হোভার, ফোকাস বা স্পর্শে পৃষ্ঠা লোড করে; `'viewport'` যখন লিঙ্কটি ভিউতে স্ক্রোল করে; `false` কখনই না। |
| `activeClassName` | ক্লাসে যোগ করা হয়েছে যখন লিঙ্কটি বর্তমান পৃষ্ঠায় বা এটির নীচের একটি পৃষ্ঠায় নির্দেশ করে (`activeClass` Vue এবং Svelte)। |
| `exact` | শুধুমাত্র সঠিক পৃষ্ঠায় সক্রিয়। |

বর্তমান পৃষ্ঠায় যে লিঙ্কটি নির্দেশ করে সেটিও `aria-current="page"` পায়।

## হুকস

অবস্থান প্রতিটি কাঠামোর মধ্যে উপলব্ধ, সেই কাঠামোর বাগধারায়। প্রথম সময়, সার্ভার-সাইড অনুরোধের URL সহ হুক উত্তর রেন্ডার করে, তাই পৃষ্ঠাটি অমিল ছাড়াই হাইড্রেট করে।

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| পথ | `usePathname()` | `usePathname()` একটি অ্যাক্সেসর প্রদান করে | `usePathname()` একটি রেফ প্রদান করে | `$pathname` স্টোর |
| রুট প্যারামস | `useParams()` | `useParams()` অ্যাক্সেসর | `useParams()` রেফ | `$params` স্টোর |
| প্রশ্ন | `useSearchParams()` | `useSearchParams()` অ্যাক্সেসর | `useSearchParams()` রেফ | `$searchParams` স্টোর |
| সবকিছু | `useLocation()` | `useLocation()` অ্যাক্সেসর | `useLocation()` রেফ | `$location` স্টোর |
| নেভিগেট | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

প্রশ্নটি একটি `URLSearchParams`। `useRouter()` এবং `router` দাও `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` এবং `prefetch(href)`; `push` এবং `replace` গ্রহণ `{ scroll: false }`।

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` একটি `<img>` রেন্ডার করে যা ডিফল্টরূপে অলস এবং যখন এর আকার পরিচিত হয় তখন লেআউটটি পরিবর্তন করে না।

| ফ্রেমওয়ার্ক | আমদানি |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` প্রয়োজন; একটি আলংকারিক ছবির জন্য `alt=""` ব্যবহার করুন। Nexy যখন এটি অনুপস্থিত হয় একবার সতর্ক করে।
- `width` এবং `height` উভয়ের সাথে, বৈশিষ্ট্যগুলি ব্রাউজারকে আকৃতির অনুপাত দেয় এবং চিত্রটি তরল থাকে (`height: auto; max-width: 100%`)।
- `priority` এখন উচ্চ অগ্রাধিকারে ছবিটি লোড করে, যেটি আগমনের সময় দৃশ্যমান হয় তার জন্য।
- `fill` চিত্রটিকে তার অবস্থানগত অভিভাবক কভার করে, `width` এবং `height` উপেক্ষা করে।
- `sizes` এবং `srcSet` এর মধ্য দিয়ে যায়। Nexy ছবির আকার পরিবর্তন বা রূপান্তর করে না।

## একটি `.nexy` পৃষ্ঠা থেকে লিঙ্ক

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` রেন্ডার করে `<a href="/about" data-nexy-link="true">`। প্রতিটি বৈশিষ্ট্য এবং `href` HTML-এস্কেপড।

## রাউটার কি করে

একটি নেভিগেশন, রাউটার:

1. ক্লায়েন্ট রুটের বিপরীতে পাথ মেলে (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. পৃষ্ঠা এবং এর [লেআউটগুলি](../layouts/README.md) **প্রথমে** আমদানি করে এবং রেন্ডার করে, এবং শুধুমাত্র তারপর `history.pushState` এর সাথে ইউআরএল স্থানান্তরিত করে, তাই ঠিকানা বার কখনো ব্যর্থ হয়েছে এমন কোনো পৃষ্ঠা দেখায় না;
3. একটি `nexy:navigated` ইভেন্ট প্রেরণ করে `document`;
4. উপরের দিকে স্ক্রোল করে, অথবা `#fragment` লক্ষ্যে।

একটি নতুন নেভিগেশন একটি পুরানোটিকে বাতিল করে যা এখনও রেন্ডার হচ্ছে৷ যদি একটি পৃষ্ঠা রেন্ডার করতে না পারে, ব্রাউজার পরিবর্তে এটির জন্য সার্ভারকে জিজ্ঞাসা করে। পিছনে এবং ফরোয়ার্ড বোতামগুলি সেই এন্ট্রির পৃষ্ঠাটিকে রেন্ডার করে এবং এর স্ক্রোল অবস্থান পুনরুদ্ধার করে।

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

রাউটার শুধুমাত্র ক্লায়েন্ট রুট সহ একটি প্রকল্পে শুরু হয়, তাই একটি সার্ভার-রেন্ডার করা প্রকল্প ব্রাউজারের নিজস্ব ব্যাক বোতাম এবং স্ক্রোল পুনরুদ্ধার রাখে।

## পরবর্তী পদক্ষেপ

- [লেআউট](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [উপাদান](../../../views/nexy/components.md)
