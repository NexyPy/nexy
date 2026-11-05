# Vue

Nexy সার্ভারে Vue 3টি একক-ফাইল উপাদান রেন্ডার করে, তারপর Vue সেগুলি ব্রাউজারে নিয়ে যায়। পৃষ্ঠা, বিন্যাস, দ্বীপ এবং ক্রিয়া প্রতিটি কাঠামোতে একই: এই পৃষ্ঠাটি সেটআপকে কভার করে, তারপর যে অংশগুলি [ভাগ করা চুক্তি](../frontend/pages.md) থেকে পৃথক।

| মোড | `nexyconfig.py` | পৃষ্ঠাগুলি হল | Vue হল |
|---|---|---|---|
| সার্ভার (ডিফল্ট) | `useCSR = False` | `.nexy` ফাইল | [দ্বীপগুলি](../../rendering/islands.md) ঐ পৃষ্ঠাগুলির ভিতরে |
| ক্লায়েন্ট | `useCSR = True` | `.vue` ফাইল | পুরো পৃষ্ঠা, [লেআউট](../frontend/layouts.md) এবং একটি ক্লায়েন্ট রাউটার | সহ

## একটি প্রকল্প শুরু করুন

```bash
nx new my-app --template web-fbr-vue
```

টেমপ্লেটটি একটি সার্ভার-মোড প্রকল্প যেখানে Vue দ্বীপ রয়েছে। পরিবর্তে প্রম্পটের উত্তর দেওয়ার জন্য একটি টেমপ্লেট ছাড়াই `nx new my-app` চালান: রাউটার, প্রকল্পের ধরন, ক্লায়েন্ট-সাইড রাউটিং ব্যবহার করবেন কিনা, তারপর ফ্রেমওয়ার্ক।

## একটি বিদ্যমান প্রকল্পে Vue সক্ষম করুন

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` এই ফাইলটি লেখেন; নেক্সি নিজে লিখে `__nexy__/vite.ts`, তাই এটি সম্পাদনা করবেন না।

| প্যাকেজ | সংস্করণ `nx new` লিখেছেন |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## নিয়ম

- **প্রতি একটি ফ্রেমওয়ার্ক প্রকল্প** `useFF` ঠিক একটি কাঠামো নেয়; `useFF = [vue(), react()]` স্টার্টআপে সার্ভার বন্ধ করে দেয়।
- **প্রতি একটি উপাদান ফাইল** একটি `.vue` ফাইল ডিফল্ট হিসাবে তার উপাদান রপ্তানি করে; আপনি যে নামটির অধীনে এটি আমদানি করেন তা শুধুমাত্র আপনার লেখা ট্যাগ।
- **উপাদানগুলি বাইরে থাকে `src/routes/`**, সাধারণত `src/components/`-এ, তাই সেগুলি পৃষ্ঠা নয়।
- **একটি সার্ভার-মোড প্রকল্পের কোনো `.vue` পৃষ্ঠা** নেই, এবং একটি ক্লায়েন্ট-মোড প্রকল্পের কোনো `.nexy` পৃষ্ঠা নেই: Nexy শুরু করতে অস্বীকার করে এবং ফাইলটির নাম দেয়। [মোডস](../../routing/fbr/modes.md) দেখুন।

## পাতা

ক্লায়েন্ট মোডে (`useCSR = True`), একটি পৃষ্ঠা হল একটি `.vue` ফাইল।

### পৃষ্ঠা উপাদান

পৃষ্ঠাটি `<script setup>` ব্লক দ্বারা সংজ্ঞায়িত উপাদান।

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### গতিশীল সেগমেন্ট

ইউআরএল প্যারামিটার প্রপ হিসাবে পৃষ্ঠায় পৌঁছায়। আপনি তাদের ব্যবহার করে ঘোষণা করতে পারেন `defineProps`:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

বিকল্পভাবে, যেকোনো উপাদানে `@nexy/client` থেকে `useParams` হুক ব্যবহার করুন।

## বিন্যাস

### বাস্তবায়ন

রুট লেআউট ডকুমেন্ট শেলকে সংজ্ঞায়িত করে। নেস্টেড লেআউট তাদের ডিফল্ট স্লটে বিষয়বস্তু মোড়ানো।

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## দ্বীপপুঞ্জ

সার্ভার মোডে, একটি `.nexy` ফাইলে আমদানি করা একটি Vue উপাদান হল একটি দ্বীপ।

### আমদানি করা হচ্ছে

`.nexy` ফাইলের ফ্রন্টম্যাটারে উপাদান আমদানি করুন:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

একটি অ্যাকশন কলের অবস্থা পরিচালনা করতে `useAction` হুক ব্যবহার করুন। Vue-এ, প্রত্যাবর্তিত অবস্থা (`pending`, `data`, `error`) গণনাকৃত রেফ।

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### নেভিগেশন

ক্লায়েন্ট-সাইড ট্রানজিশনের জন্য `Link` উপাদান ব্যবহার করুন:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

প্রোগ্রামেটিক নেভিগেশনের জন্য, `useRouter` হুক ব্যবহার করুন:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### ইউআরএল অ্যাক্সেস

সমস্ত অবস্থানের হুক গণনাকৃত রেফ প্রদান করে:

- `usePathname()`: বর্তমান পথ
- `useParams()`: গতিশীল সেগমেন্ট
- `useSearchParams()`: ক্যোয়ারী স্ট্রিং
- `useLocation()`: সম্পূর্ণ অবস্থান বস্তু

## পরবর্তী পদক্ষেপ

- [দর্শন](../README.md): একটি পৃষ্ঠা ব্যবহার করতে পারে এমন বিন্যাসের তুলনা করুন
- [ফ্রন্টেন্ড](../../guides/frontend.md): Vite এবং ক্লায়েন্ট বিল্ড
