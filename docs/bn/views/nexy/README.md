# .nexy ফাইল

একটি `.nexy` ফাইল হল একটি উপাদান: উপরে Python, মাঝখানে HTML, নীচে CSS।

**আপনি শুরু করার আগে:** [দ্রুত শুরু](../../getting-started/quick-start.md) দ্বারা তৈরি একটি প্রকল্প। একটি `.nexy` ফাইলের কোনো বিল্ড কনফিগারেশনের প্রয়োজন হয় না: `nx dev` এটি সংরক্ষণে কম্পাইল করে।

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/blog/post_view.nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

নিয়ামক তার পথ থেকে `slug` পাস করে:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```
<!-- /router -->

## ফ্রন্টম্যাটার

দুটি `---` লাইনের মধ্যে সবকিছুই Python। কম্পোনেন্ট কম্পাইল করা হলে আমদানি সমাধান করা হয়; বাকি প্রতিটি অনুরোধের জন্য চলে, তাই এটি অনুরোধের অবস্থা পড়তে পারে।

| কি | উদাহরণ |
|---|---|
| একটি মডিউল আমদানি করুন | `import json`, `from datetime import datetime` |
| একটি উপাদান আমদানি করুন | `from "@/components/card.nexy" import Card` |
| একটি সম্পত্তি ঘোষণা | `title: prop[str] = "Default"` |
| একটি মান গণনা করুন | `year = datetime.now().year` |
| অনুরোধ পড়ুন | `pathname = usePathname()` |
| পৃষ্ঠা ক্যাশে করুন (ISR) | `revalidate = 60` |

## বৈশিষ্ট্য

বৈশিষ্ট্য হল উপাদান এর API. `prop[type]` প্রকার ঘোষণা করে, `= value` একটি ডিফল্ট দেয়। একটি ডিফল্ট ছাড়া একটি সম্পত্তি পিতামাতার দ্বারা পাস করা আবশ্যক.

একটি উপনাম দিয়ে শুরু হওয়া আমদানিগুলি `useAliases` এর মাধ্যমে সমাধান করা হয়। সেটআপ `nx new` মানচিত্র `@` থেকে `src` লেখে, যা `@/components/card.nexy` মানে `src/components/card.nexy` করে।

## টেমপ্লেট

ফ্রন্টম্যাটারের নীচে Jinja2 সহ এইচটিএমএল রয়েছে। ফ্রন্টম্যাটার থেকে ভেরিয়েবল এবং বৈশিষ্ট্যের সুযোগ রয়েছে।

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

অটোএসকেপিং হল **বন্ধ**: টেমপ্লেটগুলি হল প্রজেক্টের নিজস্ব HTML, তাই `{{ value }}` লিখিত হিসাবে সন্নিবেশ করা হয়েছে। `{{ value | e }}` দিয়ে অবিশ্বস্ত মানগুলিকে এড়িয়ে চলুন। `| safe` তাই কিছুই পরিবর্তন করে না।

> [!NOTE]
> মোড়ানো JavaScript যেটিতে `{{` বা `{%` আছে `{% raw %}...{% endraw %}`। ফ্রেমওয়ার্ক যেমন Vue এবং Svelte একই বন্ধনী ব্যবহার করে।

## উপাদান

যে কোনো আমদানি করা কলযোগ্য যার নাম একটি বড় হাতের অক্ষর দিয়ে শুরু হয় একটি ট্যাগ হিসাবে ব্যবহার করা যেতে পারে। কম্পাইলার এটিকে একটি Jinja কলে পুনর্লিখন করে: বৈশিষ্ট্যগুলি কীওয়ার্ড আর্গুমেন্টে পরিণত হয়।

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

শেষ লাইনটি ঠিক `{{ Audio("/theme.mp3", controls=True) }}`। উভয় সিনট্যাক্স অন্তর্নির্মিত `Image`, `Link`, `Audio` এবং `Video` সাহায্যকারীদের জন্য বৈধ - [উপাদানগুলি](components.md#two-syntaxes-one-function) দেখুন।

শিশুদেরকে শিশু উপাদানের ভিতরে `<Slot />` (ক্যাপিটাল এস) এবং লেআউটের ভিতরে `{{ children }}` মাধ্যমে রেন্ডার করা হয়।

অ্যাট্রিবিউটের ভিতরে Jinja দিয়ে একটি গণনা করা মান পাস করুন: `<Icon path="{{ icon }}" size="{{ size }}" />`। একটি খালি নাম যেমন `path=icon` পাঠ্য `icon`, পরিবর্তনশীল নয়। একটি উপাদানকে একটি CSS ক্লাস দিতে, একটি `class_name` প্রপ ঘোষণা করুন: `class` একটি Python কীওয়ার্ড।

> [!NOTE]
> একটি সহায়ক ট্যাগ সর্বদা স্ব-বন্ধ হয়। `Link`-এ কন্টেন্ট পাস করা তার `children` আর্গুমেন্ট (`<Link href="/about" children="About" />`) দিয়ে যায়, উপাদানের বিষয়বস্তুর মাধ্যমে নয়।

## শৈলী

`<style>` ব্লকগুলি পৃষ্ঠার সাথে নির্গত হয় যা তাদের ঘোষণা করে। সেগুলি ব্যাপ্ত নয়: দুটি উপাদানে ব্যবহৃত একটি শ্রেণির নাম হল একটি শ্রেণি। আপনার ক্লাসের উপসর্গ বা নামস্থান।

## নিয়ম যা সময় বাঁচায়

- ফাইল প্রতি একটি উপাদান. ফাইলের নাম হল উপাদানের নাম, PascalCase (`CopyChip.nexy`)। একটি `.nexy` উপাদান একটি Python মডিউল হিসাবে আমদানি করা হয়: নামের একটি হাইফেন (`copy-chip.nexy`) কম্পাইল করে না।
- তাদের ব্যবহার করার আগে প্রপস ঘোষণা করুন: একটি অঘোষিত পরিবর্তনশীল একটি খালি স্ট্রিং হিসাবে রেন্ডার করে, কারণ Jinja2 এর অনির্ধারিত এখানে নীরব।
- ফাংশনের ভিতরে পার্শ্ব প্রতিক্রিয়া রাখুন - প্রতিটি অনুরোধে সামনের বিষয়টি আবার চলে।

## পরবর্তী পদক্ষেপ

- [Markdown এবং MDX](markdown.md): বিষয়বস্তু পৃষ্ঠা
- [ISR](../../rendering/isr.md): প্রতি পাথে একটি পৃষ্ঠা ক্যাশে করুন
- [CSR](../../rendering/csr.md): ক্লায়েন্ট-সাইড রেন্ডারিং
