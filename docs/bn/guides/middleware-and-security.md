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

## HTTPS

HTTPS-কে সরাসরি `useSslKeyfile` এবং `useSslCertfile` দিয়ে পরিবেশন করুন, অথবা বিপরীত প্রক্সিতে TLS বন্ধ করুন এবং `useHTTPSRedirect` সেট করুন। ডেভেলপমেন্টে Vite ডেভ সার্ভার নেক্সি অরিজিনের পিছনে লুপব্যাক HTTP-তে থাকে, তাই TLS কখনই এটিতে পৌঁছায় না।

## উত্পাদন চেকলিস্ট

- `useDocs = False` যদি OpenAPI স্কিমা সর্বজনীন হওয়া উচিত নয়।
- `useTrustedHost` হোস্ট-হেডার আক্রমণ ব্লক করতে আপনার ডোমেনে সেট করুন।
- `useCORS` স্পষ্ট উত্স সহ, শংসাপত্রের সাথে কখনই `["*"]` একসাথে নয়।
- সেশনের জন্য একটি বাস্তব `secret_key`, পরিবেশ থেকে পড়া।
- ক্লায়েন্ট উপাদানগুলিতে পাস করা প্রপগুলি Nexy দ্বারা HTML-এস্কেপ করা হয়৷ টেমপ্লেটগুলিতে ব্যবহারকারীর ইনপুট `| safe` চিহ্নিত করবেন না।

## প্রহরী এবং নির্ভরতা

প্রতি-রুট সুরক্ষা FastAPI নির্ভরতা ব্যবহার করে। একটি রুট ডিরেক্টরিতে একটি `dependencies.py` এটির নীচের সমস্ত কিছুতে প্রযোজ্য: [নির্ভরতা](../routing/fbr/dependencies/README.md) দেখুন। মডুলার রাউটারে [`@UseGuard`](../routing/modular/guards-and-metadata.md) ব্যবহার করুন।

## পরবর্তী পদক্ষেপ

- [কনফিগ](../reference/config.md): প্রতিটি মিডলওয়্যার ক্ষেত্র
- [মোতায়েন](../deployment/README.md)
- [কর্মক্ষমতা](../deployment/performance.md)
