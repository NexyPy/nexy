# কর্ম এবং নেভিগেশন

Nexy-এ ইন্টারঅ্যাকশন একটি ইউনিফাইড সিস্টেমের মাধ্যমে পরিচালিত হয় **Actions** এবং **নেভিগেশন**, নিশ্চিত করে যে ফ্রন্টএন্ড এবং ব্যাকএন্ড ম্যানুয়াল API আঠালো কোড ছাড়াই সিঙ্কে থাকে।

## অ্যাকশন চুক্তি

একটি **অ্যাকশন** হল একটি সার্ভার-সাইড ফাংশন যা একটি মিউটেশন পরিচালনা করে (যেমন, একটি ডাটাবেস আপডেট করা)। 

1.  **টাইপড ইনপুট**: টাইপ ইঙ্গিত সহ অ্যাকশনগুলি Python এ সংজ্ঞায়িত করা হয়েছে। Nexy একটি ম্যাচিং TypeScript ক্লায়েন্ট তৈরি করে, যাতে আপনি আপনার IDE-তে স্বয়ংসম্পূর্ণ এবং বৈধতা পান।
2.  **পারমাণবিক নির্বাহ**: একটি ক্রিয়া একটি একক `POST` অনুরোধ।
3.  **ফলাফল হ্যান্ডলিং**: অ্যাকশনগুলি একটি টাইপ করা ফলাফল প্রদান করে যা ক্লায়েন্ট UI আপডেট করতে ব্যবহার করতে পারে।

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

পৃষ্ঠাটি ঘোষিত ইনপুট Python সহ এটিকে কল করে এবং একটি টাইপ করা `Todo` ফিরে পায়:

<!-- router:fbr,custom -->
```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
উপাদানটি একটি দৃশ্যের একটি দ্বীপ, এবং একটি নিয়ামক দৃশ্যটি ফিরিয়ে দেয়:

```tsx filename="src/components/Todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

```nexy filename="src/apps/todos_view.nexy"
---
from "@/components/Todos.tsx" import Todos
---
<Todos directive="client:load" />
```
<!-- /router -->

## ক্লায়েন্ট-সাইড নেভিগেশন

নেক্সিতে নেভিগেশন "বুদ্ধিমান।" একটি সম্পূর্ণ ব্রাউজার পুনরায় লোড করার পরিবর্তে, সক্রিয় লেআউটগুলি মাউন্ট করার সময় Nexy বর্তমান পৃষ্ঠার বিষয়বস্তু অদলবদল করে।

- **`Link` কম্পোনেন্ট**: ক্লায়েন্ট-সাইড ট্রানজিশন সঞ্চালনের জন্য ফ্রেমওয়ার্ক-নির্দিষ্ট `Link` উপাদান ব্যবহার করুন।
- **প্রোগ্রাম্যাটিক নেভিগেশন**: যুক্তির প্রতিক্রিয়ায় পৃষ্ঠাগুলি পরিবর্তন করতে `@nexy/client` থেকে `useRouter()` ব্যবহার করুন এবং `push()` কল করুন (যেমন, একটি সফল লগইন করার পরে)।

```tsx filename="src/components/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## সমন্বয়: অ্যাকশন → নেভিগেশন

সবচেয়ে সাধারণ প্যাটার্ন হল একটি ক্রিয়া সম্পাদন করা এবং তারপর ব্যবহারকারীকে একটি নতুন পৃষ্ঠায় নেভিগেট করা।

**পুনর্বিবেচনা প্রবাহ:**
1.  ক্লায়েন্ট একটি অ্যাকশন কল.
2.  অ্যাকশন সার্ভারে সঞ্চালিত হয় এবং কল করে `revalidate("/path")`।
3.  সার্ভার একটি `x-nexy-revalidate` শিরোনাম দিয়ে বাসি পথের নামকরণ করে ফলাফল প্রদান করে।
4.  ক্লায়েন্ট নতুন অবস্থা প্রতিফলিত করতে পৃষ্ঠার বিষয়বস্তু আপডেট করে।

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

<!-- router:fbr,custom -->
```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

<!-- router:modular -->
```tsx filename="src/components/Login.tsx"
import { useAction } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export function Login() {
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) window.location.assign("/dashboard/");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```
<!-- /router -->

`check_password` মানে আপনার নিজের চেক। দেখুন [ত্রুটির জন্য কর্ম](../../guides/actions.md), ফর্ম ছাড়া JavaScript এবং নিরাপত্তা।

## ফ্রেমওয়ার্ক বাস্তবায়ন

কলিং অ্যাকশন এবং নেভিগেট করার জন্য API ফ্রেমওয়ার্ক অনুসারে পরিবর্তিত হয়। আপনার নির্বাচিত প্রযুক্তির জন্য **পার্থক্য** নির্দেশিকা দেখুন:

- [React পার্থক্য](../react/differences.md)
- [Vue পার্থক্য](../vue/differences.md)
- [Svelte পার্থক্য](../svelte/differences.md)
- [Solid পার্থক্য](../solid/differences.md)
- [Preact পার্থক্য](../preact/differences.md)
