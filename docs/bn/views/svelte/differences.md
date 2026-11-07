# Svelte

Nexy সার্ভারে Svelte 5টি উপাদান রেন্ডার করে, তারপর Svelte সেগুলি ব্রাউজারে নিয়ে যায়। পৃষ্ঠা, বিন্যাস, দ্বীপ এবং ক্রিয়া প্রতিটি কাঠামোতে একই: এই পৃষ্ঠাটি সেটআপকে কভার করে, তারপর যে অংশগুলি [ভাগ করা চুক্তি](../frontend/pages.md) থেকে পৃথক।

<!-- router:fbr,custom -->
| মোড | `nexyconfig.py` | পৃষ্ঠাগুলি হল | Svelte হয় |
|---|---|---|---|
| সার্ভার (ডিফল্ট) | `useCSR = False` | `.nexy` ফাইল | [ঐ পৃষ্ঠাগুলির ভিতরে দ্বীপগুলি](../../rendering/islands.md) |
| ক্লায়েন্ট | `useCSR = True` | `.svelte` ফাইল | পুরো পৃষ্ঠা, [লেআউট](../frontend/layouts.md) এবং একটি ক্লায়েন্ট রাউটার সহ |
<!-- /router -->

<!-- router:modular -->
মডুলার রাউটারের সাথে, Svelte উপাদানগুলি হল [দ্বীপ](../../rendering/islands.md) `.nexy` ভিউগুলির ভিতরে একটি কন্ট্রোলার রিটার্ন করে: কোনও পৃষ্ঠা ফাইল নেই এবং কোনও ক্লায়েন্ট রাউটার নেই।
<!-- /router -->

## একটি প্রকল্প শুরু করুন

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-svelte
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-svelte
```
<!-- /router -->

টেমপ্লেটটি Svelte দ্বীপ সহ একটি সার্ভার-মোড প্রকল্প। পরিবর্তে প্রম্পটের উত্তর দিতে একটি টেমপ্লেট ছাড়াই `nx new my-app` চালান: রাউটার, প্রকল্পের ধরন, ক্লায়েন্ট-সাইড রাউটিং ব্যবহার করবেন কিনা, তারপর ফ্রেমওয়ার্ক।

## একটি বিদ্যমান প্রকল্পে Svelte সক্ষম করুন

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` এই ফাইলটি লিখেছেন; নেক্সি নিজেই লেখেন `__nexy__/vite.ts`, তাই এটি সম্পাদনা করবেন না।

| প্যাকেজ | সংস্করণ `nx new` লিখেছেন |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## নিয়ম

- **Svelte 5** উপাদানগুলি রুনস ব্যবহার করে: `$props()`, `$state()`, এবং শিশুদের জন্য স্নিপেট।
- **প্রতি একটি ফ্রেমওয়ার্ক প্রকল্প** `useFF` ঠিক একটি কাঠামো নেয়; `useFF = [svelte(), vue()]` স্টার্টআপে সার্ভার বন্ধ করে দেয়।
- **প্রতি একটি উপাদান ফাইল** আপনি একটি `.svelte` ফাইলের নিচে যে নামটি ইম্পোর্ট করেন তা শুধুমাত্র আপনার লেখা ট্যাগ।
<!-- router:fbr,custom -->
- **উপাদানগুলি বাইরে থাকে `src/routes/`**, সাধারণত `src/components/`-এ, তাই সেগুলি পৃষ্ঠা নয়।
- **একটি সার্ভার-মোড প্রকল্পের কোনো `.svelte` পৃষ্ঠা** নেই, এবং একটি ক্লায়েন্ট-মোড প্রকল্পের কোনো `.nexy` পৃষ্ঠা নেই: Nexy শুরু করতে অস্বীকার করে এবং ফাইলটির নাম দেয়। [মোডস](../../routing/fbr/modes.md) দেখুন।
<!-- /router -->
<!-- router:modular -->
- **উপাদানগুলি বসবাস করে `src/components/`**, এবং একটি দৃশ্য তাদের দ্বীপ হিসাবে আমদানি করে।
<!-- /router -->

<!-- router:fbr,custom -->
## পাতা

ক্লায়েন্ট মোডে (`useCSR = True`), একটি পৃষ্ঠা হল একটি `.svelte` ফাইল।

### পৃষ্ঠা উপাদান

পৃষ্ঠাটি `.svelte` ফাইলের স্ক্রিপ্ট ব্লক দ্বারা সংজ্ঞায়িত উপাদান।

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### গতিশীল সেগমেন্ট

URL প্যারামিটারগুলি `$props()` রুনের মাধ্যমে প্রপস হিসাবে পৃষ্ঠায় পৌঁছায়:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

বিকল্পভাবে, যেকোনো উপাদানে `@nexy/client` থেকে `$params` স্টোর ব্যবহার করুন।

## বিন্যাস

### বাস্তবায়ন

রুট লেআউট ডকুমেন্ট শেলকে সংজ্ঞায়িত করে। নেস্টেড লেআউটগুলি `children` স্নিপেট ব্যবহার করে বিষয়বস্তু মোড়ানো হয়।

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```
<!-- /router -->

## দ্বীপপুঞ্জ

সার্ভার মোডে, একটি `.nexy` ফাইলে আমদানি করা একটি Svelte উপাদান একটি দ্বীপ।

### আমদানি করা হচ্ছে

`.nexy` ফাইলের ফ্রন্টম্যাটারে উপাদান আমদানি করুন:

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.svelte" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### হাইড্রেশন নির্দেশাবলী

যখন দ্বীপ হাইড্রেট হয় তখন নিয়ন্ত্রণ করতে `directive` প্রপ ব্যবহার করুন:

- `client:load` (ডিফল্ট): অবিলম্বে
- `client:idle`: যখন ব্রাউজার নিষ্ক্রিয় থাকে
- `client:visible`: যখন এটি দৃশ্যে স্ক্রোল করে
- `client:media`: যখন মিডিয়া কোয়েরি মেলে

## কর্ম এবং নেভিগেশন

### কলিং কর্ম

একটি অ্যাকশন কলের অবস্থা পরিচালনা করতে `useAction` হুক ব্যবহার করুন। Svelte-এ, এটি একটি দোকান ফেরত দেয় (`$` দিয়ে পড়ুন)।

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### নেভিগেশন

ক্লায়েন্ট-সাইড ট্রানজিশনের জন্য `Link` উপাদান ব্যবহার করুন:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

প্রোগ্রামেটিক নেভিগেশনের জন্য, `@nexy/client` থেকে `router` অবজেক্ট ব্যবহার করুন:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### ইউআরএল অ্যাক্সেস

সমস্ত অবস্থান ডেটা স্টোর হিসাবে প্রদান করা হয়:

- `$pathname`: বর্তমান পথ
- `$params`: গতিশীল সেগমেন্ট
- `$searchParams`: কোয়েরি স্ট্রিং
- `$location`: সম্পূর্ণ অবস্থান বস্তু

## পরবর্তী পদক্ষেপ

- [ভিউ ](../README.md): একটি পৃষ্ঠা ব্যবহার করতে পারে এমন বিন্যাসের তুলনা করুন
- [ফ্রন্টএন্ড](../../guides/frontend.md): Vite এবং ক্লায়েন্ট বিল্ড
