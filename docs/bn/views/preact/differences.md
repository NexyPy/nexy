# Preact

Nexy সার্ভারে Preact 10টি উপাদান রেন্ডার করে, তারপর Preact সেগুলি ব্রাউজারে নিয়ে যায়। পৃষ্ঠা, বিন্যাস, দ্বীপ এবং ক্রিয়া প্রতিটি কাঠামোতে একই: এই পৃষ্ঠাটি সেটআপকে কভার করে, তারপর যে অংশগুলি [ভাগ করা চুক্তি](../frontend/pages.md) থেকে পৃথক।

| মোড | `nexyconfig.py` | পৃষ্ঠাগুলি হল | Preact হয় |
|---|---|---|---|
| সার্ভার (ডিফল্ট) | `useCSR = False` | `.nexy` ফাইল | [দ্বীপগুলি](../../rendering/islands.md) ঐ পৃষ্ঠাগুলির ভিতরে |
| ক্লায়েন্ট | `useCSR = True` | `.tsx` ফাইল | পুরো পৃষ্ঠা, [লেআউট](../frontend/layouts.md) এবং একটি ক্লায়েন্ট রাউটার সহ |

## একটি প্রকল্প শুরু করুন

```bash
nx new my-app --template web-fbr-preact
```

টেমপ্লেটটি একটি সার্ভার-মোড প্রকল্প যেখানে Preact দ্বীপ রয়েছে। পরিবর্তে প্রম্পটের উত্তর দেওয়ার জন্য একটি টেমপ্লেট ছাড়াই `nx new my-app` চালান: রাউটার, প্রকল্পের ধরন, ক্লায়েন্ট-সাইড রাউটিং ব্যবহার করবেন কিনা, তারপর ফ্রেমওয়ার্ক।

## একটি বিদ্যমান প্রকল্পে Preact সক্ষম করুন

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` এই ফাইলটি লেখেন; নেক্সি নিজে লিখে `__nexy__/vite.ts`, তাই এটি সম্পাদনা করবেন না।

| প্যাকেজ | সংস্করণ `nx new` লিখেছেন |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (দেব নির্ভরতা) |
| `preact-render-to-string` | `^6.7.0` (দেব নির্ভরতা, সার্ভারে রেন্ডার) |

## লিখুন Preact

একটি Preact উপাদান একটি প্রতিক্রিয়া-শৈলী ফাংশন। পার্থক্যগুলি এখানে গুরুত্বপূর্ণ:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- হুকগুলি `preact/hooks` থেকে এসেছে, যেমন `ComponentChildren` থেকে `preact`।
- HTML গুণাবলী লিখুন: `class`, `for`, `charset`। `Link` `class` থেকে এর ক্লাস পড়ে।

## নিয়ম

- **প্রতি একটি ফ্রেমওয়ার্ক প্রকল্প** `useFF` ঠিক একটি কাঠামো নেয়; `useFF = [preact(), react()]` স্টার্টআপে সার্ভার বন্ধ করে দেয়। `useFF = preact()` এর সাথে, প্রতিটি `.tsx` ফাইল হল Preact।
- **পৃষ্ঠাগুলি হল `.tsx`.** শুধুমাত্র একটি `.tsx` ফাইল `src/routes/` এর অধীনে একটি পৃষ্ঠা হয়ে যায়; `.jsx` একটি উপাদানের জন্য ঠিক আছে।
- **উপাদানগুলি বাইরে থাকে `src/routes/`**, সাধারণত `src/components/`-এ, তাই সেগুলি পৃষ্ঠা নয়।
- **একটি সার্ভার-মোড প্রকল্পের কোন `.tsx` নেই পৃষ্ঠা**, এবং একটি ক্লায়েন্ট-মোড প্রকল্পের কোনো `.nexy` পৃষ্ঠা নেই: Nexy শুরু করতে অস্বীকার করে এবং ফাইলের নাম দেয়। [মোডস](../../routing/fbr/modes.md) দেখুন।
- **একটি `.mdx` পৃষ্ঠা `"preact"` থেকে আমদানি করে।** Nexy একটি সংকলন করে `.mdx` ফাইলটি Preact দিয়ে শুধুমাত্র যখন এটি সেই আমদানি দেখতে পায়, উদাহরণস্বরূপ `import { h } from "preact"`, এবং অন্যথায় React সহ। [Markdown এবং MDX](../nexy/markdown.md) দেখুন।

## পাতা

ক্লায়েন্ট মোডে (`useCSR = True`), একটি পৃষ্ঠা হল একটি `.tsx` ফাইল।

### পৃষ্ঠা উপাদান

একটি পৃষ্ঠা হল ফাইলের ডিফল্ট এক্সপোর্ট। যদি কোনো ডিফল্ট রপ্তানি বিদ্যমান না থাকে, Nexy প্রথম নামযুক্ত রপ্তানি বেছে নেয়।

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### গতিশীল সেগমেন্ট

URL প্যারামিটারগুলি `useParams` হুকের মাধ্যমে উপলব্ধ:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## বিন্যাস

### বাস্তবায়ন

রুট লেআউট ডকুমেন্ট শেলকে সংজ্ঞায়িত করে। নেস্টেড লেআউট কন্টেন্ট মোড়ানো.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## দ্বীপপুঞ্জ

সার্ভার মোডে, একটি `.nexy` ফাইলে আমদানি করা একটি Preact উপাদান একটি দ্বীপ।

### আমদানি করা হচ্ছে

`.nexy` ফাইলের ফ্রন্টম্যাটারে উপাদান আমদানি করুন:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### হাইড্রেশন নির্দেশাবলী

যখন দ্বীপ হাইড্রেট হয় তখন নিয়ন্ত্রণ করতে `directive` প্রপ ব্যবহার করুন:

- `client:load` (ডিফল্ট): অবিলম্বে
- `client:idle`: যখন ব্রাউজার নিষ্ক্রিয় থাকে
- `client:visible`: যখন এটি দৃশ্যে স্ক্রোল করে
- `client:media`: যখন মিডিয়া কোয়েরি মেলে

## কর্ম এবং নেভিগেশন

### কলিং কর্ম

একটি অ্যাকশন কলের অবস্থা পরিচালনা করতে `useAction` হুক ব্যবহার করুন:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### নেভিগেশন

ক্লায়েন্ট-সাইড ট্রানজিশনের জন্য `Link` উপাদান ব্যবহার করুন। উল্লেখ্য যে Preact `className` এর পরিবর্তে `class` ব্যবহার করে:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

প্রোগ্রামেটিক নেভিগেশনের জন্য, `useRouter` হুক ব্যবহার করুন:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### ইউআরএল অ্যাক্সেস

- `usePathname()`: বর্তমান পথ
- `useParams()`: গতিশীল সেগমেন্ট
- `useSearchParams()`: কোয়েরি স্ট্রিং
- `useLocation()`: সম্পূর্ণ অবস্থান বস্তু

## পরবর্তী পদক্ষেপ

- [দর্শন](../README.md): একটি পৃষ্ঠা ব্যবহার করতে পারে এমন বিন্যাসের তুলনা করুন
- [ফ্রন্টেন্ড](../../guides/frontend.md): Vite এবং ক্লায়েন্ট বিল্ড
