# React

Nexy সার্ভারে React 19টি উপাদান রেন্ডার করে, তারপর React সেগুলিকে ব্রাউজারে হাইড্রেট করে। পৃষ্ঠা, বিন্যাস, দ্বীপ এবং ক্রিয়া প্রতিটি কাঠামোতে একই: এই পৃষ্ঠাটি সেটআপকে কভার করে, তারপর যে অংশগুলি [ভাগ করা চুক্তি](../frontend/pages.md) থেকে পৃথক।

| মোড | `nexyconfig.py` | পৃষ্ঠাগুলি হল | React হল |
|---|---|---|---|
| সার্ভার (ডিফল্ট) | `useCSR = False` | `.nexy` ফাইল | [দ্বীপগুলি](../../rendering/islands.md) ঐ পৃষ্ঠাগুলির ভিতরে |
| ক্লায়েন্ট | `useCSR = True` | `.tsx` ফাইল | পুরো পৃষ্ঠা, [লেআউট](../frontend/layouts.md) এবং একটি ক্লায়েন্ট রাউটার | সহ

## একটি প্রকল্প শুরু করুন

```bash
nx new my-app --template web-fbr-react
```

টেমপ্লেটটি একটি সার্ভার-মোড প্রকল্প যেখানে React দ্বীপ রয়েছে। পরিবর্তে প্রম্পটের উত্তর দেওয়ার জন্য একটি টেমপ্লেট ছাড়াই `nx new my-app` চালান: রাউটার, প্রকল্পের ধরন, ক্লায়েন্ট-সাইড রাউটিং ব্যবহার করবেন কিনা, তারপর ফ্রেমওয়ার্ক।

## একটি বিদ্যমান প্রকল্পে React সক্ষম করুন

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` এই ফাইলটি লেখেন; নেক্সি নিজে লিখে `__nexy__/vite.ts`, তাই এটি সম্পাদনা করবেন না।

| প্যাকেজ | সংস্করণ `nx new` লিখেছেন |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | দেব নির্ভরতা |

## নিয়ম

- **প্রতি একটি ফ্রেমওয়ার্ক প্রকল্প** `useFF` ঠিক একটি কাঠামো নেয়; `useFF = [react(), vue()]` স্টার্টআপে সার্ভার বন্ধ করে দেয়।
- **পৃষ্ঠাগুলি হল `.tsx`.** React উপাদানগুলির জন্য `.tsx` এবং `.jsx` এর মালিক, কিন্তু `src/routes/` এর অধীনে শুধুমাত্র একটি `.tsx` ফাইল একটি পৃষ্ঠা হয়ে যায়।
- **উপাদানগুলি বাইরে থাকে `src/routes/`**, সাধারণত `src/components/`-এ, তাই সেগুলি পৃষ্ঠা নয়।
- **একটি সার্ভার-মোড প্রকল্পের কোনো `.tsx` পৃষ্ঠা** নেই, এবং একটি ক্লায়েন্ট-মোড প্রকল্পের কোনো `.nexy` পৃষ্ঠা নেই: Nexy শুরু করতে অস্বীকার করে এবং ফাইলটির নাম দেয়। [মোডস](../../routing/fbr/modes.md) দেখুন।

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

রুট লেআউট ডকুমেন্ট শেলকে সংজ্ঞায়িত করে। নেস্টেড লেআউট তাদের নীচের বিষয়বস্তু মোড়ানো।

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## দ্বীপপুঞ্জ

সার্ভার মোডে, একটি `.nexy` ফাইলে আমদানি করা একটি React উপাদান হল একটি দ্বীপ।

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

ক্লায়েন্ট-সাইড ট্রানজিশনের জন্য `Link` উপাদান ব্যবহার করুন:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
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
- [ফ্রন্টএন্ড](../../guides/frontend.md): Vite এবং ক্লায়েন্ট বিল্ড
