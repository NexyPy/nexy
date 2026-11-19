# আমি কিভাবে একটি Nexy সাইটে sitemap.xml এবং robots.txt যোগ করব?

`nexyconfig.py`-এ `useSiteUrl` সেট করুন: Nexy তারপর `/sitemap.xml` পরিবেশন করে, যা প্রকল্পের প্রতিটি স্ট্যাটিক পৃষ্ঠা তালিকাভুক্ত করে এবং একটি `/robots.txt` যা সার্চ ইঞ্জিনকে নির্দেশ করে।

## এটি `useSiteUrl` দিয়ে চালু করুন

`useSiteUrl` সাইটটির সর্বজনীন উত্স, একটি সার্চ ইঞ্জিন দেখতে পায়:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` এবং `nx start` তারপর উভয় ফাইলের উত্তর দিন। `useSiteUrl` ছাড়া কোনটিই বিদ্যমান নেই, তাই একটি প্রকল্প কখনই তার ডেভ সার্ভারের URL ভুল করে প্রকাশ করে না।

## সাইটম্যাপ তালিকা কি

সাইটম্যাপ প্রতিটি পৃষ্ঠাকে `useSiteUrl`-এ একটি সম্পূর্ণ URL হিসেবে দেয়:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

একটি রুট তালিকাভুক্ত করা হয় যখন এটি একটি নির্দিষ্ট পথে একটি `GET`-এর HTML-এর উত্তর দেয়:

<!-- router:fbr,custom -->
- একটি পৃষ্ঠা (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) তালিকাভুক্ত করা হয়েছে;
- একটি গতিশীল পৃষ্ঠা, যেমন `src/routes/users/[id].nexy`, বাদ পড়ে যায়: Nexy এর মান জানতে পারে না;
- একটি Python রুট হ্যান্ডলার JSON উত্তর দেয়, তাই এটি বাদ দেওয়া হয়।
<!-- /router -->

<!-- router:modular -->
- একটি নিয়ামক রুট যা HTML এর উত্তর দেয়, `@UseResponse(response_class=HTMLResponse)`, তালিকাভুক্ত করা হয়;
- পাথ প্যারামিটার সহ একটি রুট, যেমন `/users/{id}`, বাদ দেওয়া হয়: Nexy এর মানগুলি জানতে পারে না;
- JSON এর উত্তর দেয় এমন একটি রুট বাদ দেওয়া হয়েছে।
<!-- /router -->

API স্কিমা (`include_in_schema=False`) থেকে লুকানো একটি রুটও বাদ দেওয়া হয়েছে।

## এটি `robots.txt` পরিবেশন করে

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## পরিবর্তে আপনার নিজের লিখুন

আপনার নিজের ফাইল সর্বদা জয়ী হয়, এবং Nexy কখনই এটিকে ওভাররাইট করে না:

- `public/robots.txt` বা `public/sitemap.xml` যেমন পরিবেশন করা হয়, `public/` এর প্রতিটি ফাইল যেভাবে হয়;
- প্রকল্পের একটি রুট `/robots.txt` বা `/sitemap.xml` এর পথ ধরে রাখে।

ডায়নামিক পৃষ্ঠাগুলি তালিকাভুক্ত করতে আপনার নিজস্ব সাইটম্যাপ লিখুন, যেমন প্রতি ব্লগ পোস্টে একটি URL।

## পরবর্তী পদক্ষেপ

- [পৃষ্ঠা মেটাডেটা](../routing/fbr/pages/metadata.md): শিরোনাম এবং বর্ণনা সার্চ ইঞ্জিন দেখায়
- [কনফিগারেশন](../reference/config.md): প্রতিটি সেটিং এর `nexyconfig.py`
- [স্থাপন ](../deployment/README.md): উৎপাদনে প্রকল্প পরিবেশন
