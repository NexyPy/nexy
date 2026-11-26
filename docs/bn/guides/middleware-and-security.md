# মিডলওয়্যার এবং নিরাপত্তা

Nexy FastAPI এবং Starlette এ চলে, তাই তাদের মিডলওয়্যার প্রযোজ্য। সাধারণগুলি `nexyconfig.py`-এ এক লাইন।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

প্রতিটি `use*` ডিকশনারি কিওয়ার্ড আর্গুমেন্ট হিসেবে মেলে Starlette মিডলওয়্যার: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`।

## আপনার নিজের মিডলওয়্যার

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` ASGI মিডলওয়্যার ক্লাস নেয়।

## হার সীমিত

`useRateLimit` একটি ক্লায়েন্টের ঠিকানায় `429 Too Many Requests` উত্তর দেয় যা `per` সেকেন্ডের একটি উইন্ডোতে `requests` এর বেশি অনুরোধ পাঠায়।

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy গ্যারান্টি দেয় যে সীমার বেশি অনুরোধ একটি `Retry-After` শিরোনাম সহ একটি `429` পাবে, উইন্ডোতে বাকি সেকেন্ড, এবং কখনই আপনার রুট, অ্যাকশন বা মিডলওয়্যারে পৌঁছাবে না।

Nexy গ্যারান্টি দেয় যে `useRateLimit` ছাড়া কোনো রেট লিমিট মিডলওয়্যার যোগ করা হয় না।

Nexy গ্যারান্টি দেয় যে `useHealth` প্রোবগুলি কখনই সীমাবদ্ধ নয়।

`paths` ঐচ্ছিক: এটি ছাড়া প্রতিটি পথ সীমিত। সার্ভার ক্রিয়াগুলি `/_nx_` এর অধীনে পরিবেশন করা হয়, যাতে উপসর্গ তাদের সকলকে সীমাবদ্ধ করে।

উইন্ডোটি সমস্ত ক্লায়েন্ট দ্বারা স্থির এবং ভাগ করা হয়েছে: গণনাগুলি `per` সেকেন্ডের প্রতিটি গুণে আবার শুরু হয়। একটি ক্লায়েন্ট তাই একটি উইন্ডোর প্রান্ত জুড়ে দুইবার `requests` পাঠাতে পারে।

গণনা প্রতিটি শ্রমিকের স্মৃতিতে বেঁচে থাকে। উপরে একটি `useWorkers` দিয়ে, একজন ক্লায়েন্ট প্রতিটি কর্মীকে `requests` পাঠাতে পারে এবং সার্ভার পুনরায় চালু হলে গণনা আবার শুরু হয়।

ক্লায়েন্ট ঠিকানা হল একটি ইউভিকর্ন অনুরোধ করে। একই মেশিনে একটি বিপরীত প্রক্সির পিছনে, ইউভিকর্ন এটি `X-Forwarded-For` থেকে পড়ে; অন্য মেশিনে প্রক্সির জন্য, `FORWARDED_ALLOW_IPS` এনভায়রনমেন্ট ভেরিয়েবলে এর ঠিকানা তালিকাভুক্ত করুন, অথবা প্রত্যেক ক্লায়েন্ট প্রক্সির ঠিকানা শেয়ার করে।

আপনার অ্যাপ্লিকেশনটি বেশ কয়েকটি কর্মী বা সার্ভার দ্বারা ভাগ করা একটি সীমার জন্য দায়ী: একটি বিপরীত প্রক্সি বা একটি স্টোর যেমন রেডিস।

## HTTPS

HTTPS-কে সরাসরি `useSslKeyfile` এবং `useSslCertfile` দিয়ে পরিবেশন করুন, অথবা বিপরীত প্রক্সিতে TLS বন্ধ করুন এবং `useHTTPSRedirect` সেট করুন। ডেভেলপমেন্টে Vite ডেভ সার্ভার নেক্সি অরিজিনের পিছনে লুপব্যাক HTTP-তে থাকে, তাই TLS কখনই এটিতে পৌঁছায় না।

## উত্পাদন চেকলিস্ট

- `useDocs = False` যদি OpenAPI স্কিমা সর্বজনীন হওয়া উচিত নয়।
- `useTrustedHost` হোস্ট-হেডার আক্রমণ ব্লক করতে আপনার ডোমেনে সেট করুন।
- `useCORS` সুস্পষ্ট উত্স সহ, শংসাপত্রের সাথে কখনই `["*"]` একসাথে নয়।
- সেশনের জন্য একটি বাস্তব `secret_key`, পরিবেশ থেকে পড়া।
- Props ক্লায়েন্ট উপাদানগুলিতে পাস করা হয় নেক্সি দ্বারা HTML-এস্কেপড। টেমপ্লেটগুলিতে ব্যবহারকারীর ইনপুট `| safe` চিহ্নিত করবেন না।

## গার্ড এবং নির্ভরতা

প্রতি-রুট সুরক্ষা FastAPI নির্ভরতা ব্যবহার করে। একটি রুট ডিরেক্টরিতে একটি `dependencies.py` এটির নীচের সমস্ত কিছুতে প্রযোজ্য: [নির্ভরতা](../routing/fbr/dependencies/README.md) দেখুন। মডুলার রাউটারে [`@UseGuard`](../routing/modular/guards-and-metadata.md) ব্যবহার করুন।

## পরবর্তী পদক্ষেপ

- [কনফিগ ](../reference/config.md): প্রতিটি মিডলওয়্যার ক্ষেত্র
- [স্থাপন ](../deployment/README.md)
- [কর্মক্ষমতা ](../deployment/performance.md)
