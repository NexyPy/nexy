# লিঙ্ক এবং নেভিগেট

ক্লায়েন্ট রাউটিং (`useCSR = True`) এর সাথে, দুটি পৃষ্ঠার মধ্যে একটি লিঙ্ক নথিটি পুনরায় লোড করার পরিবর্তে ব্রাউজারে পৃষ্ঠাটিকে অদলবদল করে। বিন্যাস তাদের রাষ্ট্র রাখা.

## প্লেইন লিঙ্ক ইতিমধ্যে কাজ

প্রতিটি `<a href>` আপনার প্রকল্পের একটি পৃষ্ঠায় ক্লায়েন্টে নেভিগেট করে, কোন উপাদান এবং কোন মার্কার ছাড়াই:

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

| Prop | অর্থ |
|---|---|
| `href` | প্রকল্পের একটি রুট (একটি টাইপো একটি টাইপ ত্রুটি), ঐচ্ছিকভাবে `?query` বা `#fragment`, অথবা একটি বহিরাগত URL। |
| `replace` | একটি যোগ করার পরিবর্তে ইতিহাস এন্ট্রি প্রতিস্থাপন করুন। |
| `scroll` | `false` নেভিগেট করার পরে স্ক্রোল অবস্থান রাখে। ডিফল্ট: `true`। |
| `prefetch` | `'intent'` (ডিফল্ট) হোভার, ফোকাস বা স্পর্শে পৃষ্ঠা লোড করে; `'viewport'` যখন লিঙ্কটি ভিউতে স্ক্রোল করে; `false` কখনই না। |
| `activeClassName` | ক্লাসে যোগ করা হয়েছে যখন লিঙ্কটি বর্তমান পৃষ্ঠায় বা এটির নীচের একটি পৃষ্ঠায় নির্দেশ করে (`activeClass` Vue এবং Svelte)। |
| `exact` | শুধুমাত্র সঠিক পৃষ্ঠায় সক্রিয়. |

বর্তমান পৃষ্ঠায় যে লিঙ্কটি নির্দেশ করে সেটিও `aria-current="page"` পায়।

## হুকস

অবস্থান প্রতিটি কাঠামোর মধ্যে উপলব্ধ, সেই কাঠামোর বাগধারায়। প্রথম সময়ে, সার্ভার-সাইড অনুরোধের URL সহ হুক উত্তর রেন্ডার করে, তাই পৃষ্ঠাটি অমিল ছাড়াই হাইড্রেট করে।

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| পথ | `usePathname()` | `usePathname()` একটি অ্যাক্সেসর প্রদান করে | `usePathname()` একটি রেফ প্রদান করে | `$pathname` দোকান |
| রুট params | `useParams()` | `useParams()` অ্যাক্সেসর | `useParams()` রেফ | `$params` দোকান |
| প্রশ্ন | `useSearchParams()` | `useSearchParams()` অ্যাক্সেসর | `useSearchParams()` রেফারি | `$searchParams` দোকান |
| সবকিছু | `useLocation()` | `useLocation()` অ্যাক্সেসর | `useLocation()` রেফারি | `$location` দোকান |
| নেভিগেট করুন | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| ফ্লাইটে নেভিগেশন | `useTransition()` | `useTransition()` অ্যাক্সেসর | `useTransition()` রেফ | `useTransition()` দোকান |
| একটি পথ মেলে | `useMatch(path?)` | `useMatch(path?)` অ্যাক্সেসর | `useMatch(path?)` রেফারি | `useMatch(path?)` দোকান |
| যাওয়ার আগে জিজ্ঞাসা করুন | `useBlocker(dirty)` | `useBlocker(dirty())` `createEffect` মধ্যে | `useBlocker(dirtyRef)` | `useBlocker(dirty)` `$effect` মধ্যে |

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

## `useTransition` সহ একটি লোডিং অবস্থা দেখান

`useTransition()` ক্লায়েন্ট নেভিগেশন ফ্লাইটে আছে কিনা তা বলে। `pending` হল `true` ক্লিক থেকে পরবর্তী পৃষ্ঠাটি দেখানো পর্যন্ত, এবং `next` হল এটি যে অবস্থানে যাচ্ছে। একবার পৃষ্ঠাটি দেখানো হলে, যখন নেভিগেশন বন্ধ হয়ে যায়, বা যখন একটি নতুন এটি প্রতিস্থাপন করে তখন এটি `{ pending: false, next: null }` এ ফিরে যায়।

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## একটি পথের সাথে মেলান `useMatch`

`useMatch(path)` বলে যে `path` একটি ক্লায়েন্ট রুটের সাথে মেলে কিনা। এটি `{ match, found }` রিটার্ন করে, যেখানে `match` রুট ধরে রাখে `file`, তার `layouts` এবং তার `params`, বা `null`। একটি পথ ছাড়া এটি বর্তমান পৃষ্ঠার সাথে মেলে এবং প্রতিটি নেভিগেশন অনুসরণ করে। সার্ভার রেন্ডারের সময় এখনও কোন রাউটার নেই, তাই `match` হল `null` এবং `found` হল `false`।

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## এমন একটি পৃষ্ঠা ধরুন যা `ErrorBoundary` এর সাথে ব্যর্থ হয়

`ErrorBoundary` এর বাচ্চাদের পরিবর্তে একটি ফলব্যাক দেখায় যখন তাদের মধ্যে একজন ছুঁড়ে দেয় যখন এটি ব্রাউজারে রেন্ডার হয়। ফলব্যাক ত্রুটি পায় এবং `reset`, যা শিশুদের আবার রেন্ডার করে।

| ফ্রেমওয়ার্ক | আমদানি | ফলব্যাক |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | একটি `fallback` ফাংশন prop; শিশুরা ডিফল্ট স্লটে যায় |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | একটি `fallback` স্নিপেট |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

এটি ধরা পড়ে না:

- একটি ইভেন্ট হ্যান্ডলারে, একটি টাইমার বা একটি প্রতিশ্রুতিতে একটি ত্রুটি পরে নিক্ষেপ করা হয়েছে: এটি যেখানে ঘটে সেখানে ধরুন৷ Vue তার নিজস্ব ইভেন্ট হ্যান্ডলারদের জন্য ব্যতিক্রম, যাদের ত্রুটি সীমানায় পৌঁছেছে;
- একটি পৃষ্ঠা রাউটার লোড করতে পারে না: ব্রাউজার পরিবর্তে এটির জন্য সার্ভারকে জিজ্ঞাসা করে (দেখুন [রাউটারটি কী করে](#what-the-router-does))।

## অসংরক্ষিত পরিবর্তন সহ একটি পৃষ্ঠা ছেড়ে যাওয়ার আগে জিজ্ঞাসা করুন

`useBlocker(dirty, message?)` ভিজিটর চলে যাওয়ার আগে জিজ্ঞাসা করে যখন তারা `dirty` সত্য হয়: একটি লিঙ্ক, একটি `router.push`, পিছনে এবং সামনের বোতাম, একটি পুনরায় লোড এবং একটি বন্ধ ট্যাব। একটি ক্লায়েন্ট নেভিগেশন দেখায় `message` এ `confirm()`: হ্যাঁ যায়, পৃষ্ঠায় থাকে না। একটি পুনরায় লোড বা একটি বন্ধ ট্যাব ব্রাউজারের নিজস্ব প্রশ্ন দেখায়, যা কোন পৃষ্ঠা শব্দ করতে পারে না। একটি বার্তা ছাড়াই, প্রশ্ন হল "আপনার অসংরক্ষিত পরিবর্তনগুলি আছে৷ এই পৃষ্ঠাটি ছেড়ে যান?"৷

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

পতাকাটি যেখানে পরিবর্তিত হয় সেখানে পঠিত হয়, প্রতিটি কাঠামোর বাগধারায়:

| ফ্রেমওয়ার্ক | পতাকা অনুসরণ করুন |
|---|---|
| React, Preact | `useBlocker(dirty)` প্রতিটি রেন্ডারে |
| Vue | `useBlocker(dirty)` সাথে `dirty` একটি রেফ বা একটি গণনা করা হয়েছে |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` এছাড়াও একটি ফাংশন নেয়, একটি সিদ্ধান্তের জন্য যা দর্শক কোথায় যায় তার উপর নির্ভর করে। এটি পরবর্তী অবস্থান এবং বর্তমানটি গ্রহণ করে, এবং থাকার জন্য একটি কারণ (একটি স্ট্রিং) প্রদান করে, বা যাওয়ার কিছু নেই:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

একটি ফাংশন নিজেই জিজ্ঞাসা করে না এবং পুনরায় লোড ধরে না; জিজ্ঞাসা করার জন্য এটিতে `confirm()` কল করুন।

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
- `priority` ইমেজটিকে এখন উচ্চ অগ্রাধিকারে লোড করে, যেটি আগমনে দৃশ্যমান হয় তার জন্য।
- `fill` চিত্রটিকে তার অবস্থানগত অভিভাবককে কভার করে, `width` এবং `height` উপেক্ষা করে।
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
2. পৃষ্ঠা এবং এর [লেআউটগুলি](../layouts/README.md) **প্রথমে** আমদানি করে এবং রেন্ডার করে, এবং শুধুমাত্র তারপরে `history.pushState` দিয়ে ইউআরএল স্থানান্তরিত করে, তাই ঠিকানা বার কখনো ব্যর্থ হয়েছে এমন কোনো পৃষ্ঠা দেখায় না;
3. একটি `nexy:navigated` ইভেন্ট প্রেরণ করে `document`;
4. শীর্ষে স্ক্রোল করে, অথবা লক্ষ্যে `#fragment`।

পৃষ্ঠা অদলবদল ব্রাউজার ভিউ ট্রানজিশনের মধ্যে চলে যখন একটি উপলব্ধ থাকে: দেখুন [পেজ ট্রানজিশন কীভাবে কাজ করে](page-transitions.md)।

একটি নতুন নেভিগেশন একটি পুরানোটিকে বাতিল করে যা এখনও রেন্ডার হচ্ছে৷ যদি একটি পৃষ্ঠা রেন্ডার করতে না পারে, ব্রাউজার পরিবর্তে এটির জন্য সার্ভারকে জিজ্ঞাসা করে। পিছনে এবং ফরোয়ার্ড বোতামগুলি সেই এন্ট্রির পৃষ্ঠাটিকে রেন্ডার করে এবং এর স্ক্রোল অবস্থান পুনরুদ্ধার করে।

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

রাউটার শুধুমাত্র ক্লায়েন্ট রুট সহ একটি প্রকল্পে শুরু হয়, তাই একটি সার্ভার-রেন্ডার করা প্রকল্প ব্রাউজারের নিজস্ব ব্যাক বোতাম এবং স্ক্রোল পুনরুদ্ধার রাখে।

## পরবর্তী পদক্ষেপ

- [বিন্যাস](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [উপাদান ](../../../views/nexy/components.md)
