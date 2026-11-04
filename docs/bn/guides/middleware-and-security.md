# মিডলওয়্যার এবং নিরাপত্তা

Nexy FastAPI এবং Starlette এ চলে, তাই তাদের মিডলওয়্যার প্রযোজ্য। সাধারণগুলো এক লাইনে
`nexyconfig.py`।

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

প্রতিটি `use*` অভিধানকে স্টারলেট মিডলওয়্যারের সাথে মিলে যাওয়া কীওয়ার্ড আর্গুমেন্ট হিসেবে পাস করা হয়:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`।

## আপনার নিজস্ব মিডলওয়্যার

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` ASGI মিডলওয়্যার ক্লাস নেয়।

## HTTPS

HTTPS সরাসরি `useSslKeyfile` এবং `useSslCertfile` দিয়ে পরিবেশন করুন, অথবা বিপরীত প্রক্সিতে TLS বন্ধ করুন
এবং সেট `useHTTPSRedirect`। বিকাশে Vite dev সার্ভার লুপব্যাক HTTP এর পিছনে থাকে
Nexy উত্স, তাই TLS কখনই এটিতে পৌঁছায় না।

## উৎপাদন চেকলিস্ট

- `useDocs = False` যদি OpenAPI স্কিমা সর্বজনীন হওয়া উচিত নয়।
- `useTrustedHost` হোস্ট-হেডার আক্রমণ ব্লক করতে আপনার ডোমেনে সেট করা হয়েছে।
- `useCORS` সুস্পষ্ট উত্স সহ, শংসাপত্রের সাথে কখনই `["*"]` একসাথে নয়।
- সেশনের জন্য একটি বাস্তব `secret_key`, পরিবেশ থেকে পড়া।
- ক্লায়েন্ট উপাদানগুলিতে প্রপস পাঠানো হয় নেক্সি দ্বারা HTML-এস্কেপড। ব্যবহারকারী ইনপুট `| safe` চিহ্নিত করবেন না
  টেমপ্লেট

## রক্ষী এবং নির্ভরতা

প্রতি-রুট সুরক্ষা FastAPI নির্ভরতা ব্যবহার করে। একটি রুট ডিরেক্টরিতে একটি `dependencies.py` প্রযোজ্য
এর নীচে সবকিছু: দেখুন [নির্ভরতা](../routing/fbr/dependencies/README.md)। মডুলার রাউটার ব্যবহার
[`@UseGuard`](../routing/modular/guards-and-metadata.md)।

## পরবর্তী ধাপ

- [কনফিগ](../reference/config.md): প্রতিটি মিডলওয়্যার ক্ষেত্র
- [মোতায়েন](../deployment/README.md)
- [পারফরম্যান্স](../deployment/performance.md)