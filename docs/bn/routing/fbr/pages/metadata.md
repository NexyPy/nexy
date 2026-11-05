# পৃষ্ঠা মেটাডেটা

একটি পৃষ্ঠা তার শিরোনাম এবং এর হেড ট্যাগগুলির নাম দেয় এবং রুট লেআউট সেগুলি একবার লিখে।

## পাতায় বলুন

এমন একটি পৃষ্ঠার জন্য যা কখনও পরিবর্তন হয় না, সামনের বিষয়ের শীর্ষে একটি আক্ষরিক লিখুন:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

যখন শিরোনাম ডেটার উপর নির্ভর করে, পরিবর্তে `setMetadata` কল করুন:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

একটি মডুলার কন্ট্রোলার `setMetadata(...)` ফেরার আগে কল করে `useViews(...)`।

## লেআউটে এটি লিখুন

রুট লেআউটটি `<head>` এর মালিক। এক লাইন পৃষ্ঠাটি যা বলেছে তা লিখেছে, পালিয়ে গেছে:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

একটি পৃষ্ঠা তার লেআউটের আগে চলে, তাই লেআউটটি খুঁজে পায় যে পৃষ্ঠাটি কী চেয়েছে৷ একটি পৃষ্ঠা যা বলে যে কিছুই আপনার `nexyconfig.py` এর `useTitle` পায় না, এবং অন্য কোন ট্যাগ পায় না।

## ক্ষেত্রগুলি

| মাঠ | হিসেবে লেখা |
|---|---|
| `title` | `<title>`; `title_template="%s \| My site"` এর সাথে শিরোনামটি `%s` এ রাখা হয়েছে |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, উদাহরণস্বরূপ `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | প্রতি চাবিতে একটি `<meta property="og:...">`: `{"image": "/cover.png"}` দেয় `og:image` |
| `twitter` | প্রতি চাবিতে একটি `<meta name="twitter:...">` |
| `extra` | বৈশিষ্ট্য নির্দেশের একটি তালিকা, একটি `<meta>` প্রতিটি: `[{"name": "theme-color", "content": "#fff"}]` |

একটি পরবর্তী কল একটি মান প্রতিস্থাপন করে; `og`, `twitter` এবং `extra` যা আছে তাতে যোগ করুন। একটি ক্ষেত্র যা বিদ্যমান নেই তা উত্থাপন করে `TypeError`, তাই একটি টাইপো চুপচাপ কিছু করে না।

## ডিফল্টরূপে নিরাপদ

প্রতিটি মান HTML-এস্কেপড, তাই URL বা ডাটাবেস থেকে নির্মিত একটি শিরোনাম ট্যাগ বন্ধ করতে পারে না এবং একটি স্ক্রিপ্ট ইনজেক্ট করতে পারে না। একটি মান একবার এস্কেপ করা হয়, যখন লেআউটটি কল করে `html()`: নিজেকে এড়িয়ে যাবেন না।

## পরবর্তী পদক্ষেপ

- [পৃষ্ঠা](README.md)
- [লেআউট](../layouts/README.md)
- [ত্রুটির পৃষ্ঠাগুলি](../errors/README.md)
