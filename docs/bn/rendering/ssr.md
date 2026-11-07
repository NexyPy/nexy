# SSR (সার্ভার রেন্ডারিং)

## সংজ্ঞা

SSR হল ডিফল্ট: সার্ভার প্রতিটি অনুরোধের জন্য পৃষ্ঠাটিকে HTML-এ রেন্ডার করে। কিছুই এটি সক্রিয় করে না, এবং কোন পতাকা এটিকে বন্ধ করে না - একটি সার্ভার-মোড প্রকল্প প্রতিটি অনুরোধে রেন্ডার করে যদি না একটি পৃষ্ঠা `revalidate` ঘোষণা করে।

## এটা কিভাবে কাজ করে

<!-- router:fbr,custom -->
| রুট ফাইল | কি এইচটিএমএল উত্পাদন | কখন |
|---|---|---|
| `.nexy` | সংকলিত Python মডিউল, মাধ্যমে Jinja2 | প্রতিটি অনুরোধ |
| `.md` | Markdown, তারপর নিকটতম লেআউট | প্রতিটি অনুরোধ |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | ফ্রেমওয়ার্ক, নোডে রেন্ডার করা হয়েছে | বিল্ড এ যখন রুটের কোন লেআউট থাকে না, অন্যথায় ব্রাউজারে |
| `.py` | কিছুই না: এটি JSON বা একটি `Response` প্রদান করে | - |

একটি Markdown পৃষ্ঠা এবং একটি হ্যান্ডলার, একই প্রকল্পে পাশাপাশি:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

একটি উপাদান রুট হল একটি ক্ষেত্রে যার একটি দ্বিতীয় বাক্য প্রয়োজন। উৎপাদনে, একটি কম্পোনেন্ট রুট **ব্যতীত** একটি লেআউট বিল্ড করার সময় উত্পাদিত এইচটিএমএল দিয়ে পরিবেশন করা হয় এবং কম্পোনেন্ট এটিকে হাইড্রেট করে। একটি বিন্যাস সহ, বা বিকাশে, ধারকটি খালি থাকে এবং উপাদানটি ব্রাউজারে রেন্ডার হয় - পৃষ্ঠাটি তখন একটি শেল যা নিজেকে পূরণ করে।

টেবিলের কম্পোনেন্ট রুট, লেআউট ছাড়াই, তাই প্রোডাকশন বিল্ড থেকে তার HTML পরিবেশন করে:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| একটি নিয়ামক ফিরে আসে | কি এইচটিএমএল উত্পাদন | কখন |
|---|---|---|
| `useViews("....nexy")` | সংকলিত Python মডিউল, Jinja2 মাধ্যমে | প্রতিটি অনুরোধ |
| একটি `dict`, একটি তালিকা, একটি মডেল | কিছুই না: FastAPI JSON উত্তর দেয় | - |

একটি ভিউ এবং একটি JSON শেষ পয়েন্ট, একই মডিউলে পাশাপাশি:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## জীবনচক্র রেন্ডারিং

<!-- router:fbr,custom -->
1. অনুরোধটি ফাইল-ভিত্তিক রাউটারে পৌঁছায়। পাথ মিলে গেছে, এবং গতিশীল সেগমেন্টগুলি কম্পোনেন্ট যে ধরনের ঘোষণা করে তাতে কাস্ট করা হয়।

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: prop[int]
   ---
   <h1>অর্ডার #{{ আইডি + 1000 }</h1>
   ```

   `/orders/42` রেন্ডার `Order #1042`; `/orders/abc` উত্তর `404`।
2. কম্পোনেন্ট চলে। যেটি নোডে অপেক্ষা করে - একটি ক্লায়েন্ট নথি - একটি থ্রেড পুলে চলে, তাই এটি ইভেন্ট লুপকে আটকায় না।
3. দেহটি `text/html` হিসাবে প্রবাহিত হয়। একটি উপাদান যে খণ্ড ফলন তাদের স্ট্রিম হিসাবে এটি তাদের তৈরি.
4. ব্রাউজারটি HTML গ্রহণ করে। দ্বীপগুলি তাদের [নির্দেশ](islands.md) অনুসারে হাইড্রেট করে।

রেন্ডারিংয়ের সময় উত্থাপিত একটি ত্রুটি `errors.nexy` দ্বারা একটি পৃষ্ঠায় পরিণত হয় যখন প্রকল্পের একটি থাকে: [ত্রুটির পৃষ্ঠাগুলি](../routing/fbr/errors/README.md) দেখুন।
<!-- /router -->

<!-- router:modular -->
1. অনুরোধটি নিয়ন্ত্রকের কাছে পৌঁছায়। এর পাথ প্যারামিটারগুলি পদ্ধতিটি ঘোষণা করা প্রকারগুলিতে নিক্ষেপ করা হয় এবং ভিউতে প্রেরণ করা হয়:

   ```পাইথন ফাইলের নাম="src/apps/order_controller.py"
   থেকে nexy.decorators আমদানি কন্ট্রোলার
   nexy.hooks থেকে useViews আমদানি করুন


   @কন্ট্রোলার("/orders/{id}")
   ক্লাস অর্ডার কন্ট্রোলার:
       async def get(self, id: int):
           ইউজ ভিউ ("src/apps/order_view.nexy", প্রসঙ্গ={"id": id}) ফেরত দিন
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   id: prop[int]
   ---
   <h1>অর্ডার #{{ আইডি + 1000 }}</h1>
   ```

   `/orders/42/` রেন্ডারগুলি `Order #1042`; `/orders/abc/` উত্তর `404`।
2. ভিউটি চলে, এবং `useViews` প্রতিক্রিয়া হিসাবে তার HTML ফেরত দেয়।
3. ব্রাউজারটি HTML গ্রহণ করে। দ্বীপগুলি তাদের [নির্দেশ](islands.md) অনুযায়ী হাইড্রেট করে।

রেন্ডার করার সময় উত্থাপিত একটি ত্রুটি ডিফল্ট ত্রুটি পৃষ্ঠার সাথে উত্তর দেওয়া হয়।
<!-- /router -->

## কখন ব্যবহার করতে হবে

- পৃষ্ঠাটি পাঠকের মালিকানাধীন কিছু দেখায়: একটি সেশন, একটি অ্যাকাউন্ট, একটি কার্ট৷
- প্রতিটি লোডে ডেটা অবশ্যই তাজা হতে হবে।
- বিষয়বস্তু অবশ্যই এইচটিএমএল-এ এমন ক্রলারের জন্য থাকতে হবে যা JavaScript চালায় না।
- পৃষ্ঠাটি রেন্ডার করার জন্য সস্তা: একটি প্রশ্ন, একটি টেমপ্লেট৷

প্রথম ক্ষেত্রে, একটি পাতা যে অধিবেশন থেকে পাঠক অভিবাদন. `useSession` `nexyconfig.py`-এ `useSession` এর অধিবেশন পড়ে, যা ছাড়া এটি ব্যর্থ হয়:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## কনফিগারেশন

<!-- router:fbr,custom -->
কোনোটিই নয়। দুটি উপায় আউট, এবং তাদের একই শস্য নেই:

| জন্য SSR ছেড়ে | এটা করো | শস্য |
|---|---|---|
| একটি পৃষ্ঠা, একটি ক্যাশে সহ | `revalidate = 60` এর ফ্রন্ট ম্যাটারে → [ISR](isr.md) | পৃষ্ঠা |
| পুরো প্রকল্প, ক্লায়েন্ট-রুটেড | `useCSR = True` `nexyconfig.py` → [CSR](csr.md) | প্রকল্প |

প্রকল্প ব্যাপী সুইচ, `nexyconfig.py` মধ্যে. ক্লায়েন্ট মোড একটি ক্লায়েন্ট ফ্রেমওয়ার্ক প্রয়োজন:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
কোনোটিই নয়। প্রতিটি ভিউ একটি কন্ট্রোলার রিটার্ন করে প্রতিটি অনুরোধে রেন্ডার করা হয়: [ISR](isr.md) এবং [CSR](csr.md) হল ফাইল-ভিত্তিক রাউটারের মোড।
<!-- /router -->

## উদাহরণ

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` একবার এই টেমপ্লেটটি চালায়, `slug` সেট করে `hello`। একটি দ্বিতীয় অনুরোধ এটি আবার চালায়: উভয়ের মধ্যে কিছুই রাখা হয় না। ক্যোয়ারী স্ট্রিং একটি প্রপ নয় - এটি [নেভিগেশন](../routing/fbr/navigation/hooks.md) এর হুক দিয়ে পড়ুন।
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` একবার এই ভিউ চালায়, `slug` সেট করে `hello`। একটি দ্বিতীয় অনুরোধ এটি আবার চালায়: উভয়ের মধ্যে কিছুই রাখা হয় না। ক্যোয়ারী স্ট্রিং একটি প্রপ নয় - এটি `useSearchParams` দিয়ে পড়ুন।
<!-- /router -->

## সীমাবদ্ধতা

- **প্রতি এক রেন্ডার অনুরোধ** একই সেকেন্ডে দুইজন দর্শক রেন্ডারের জন্য এবং এর পিছনে থাকা প্রশ্নের জন্য অর্থ প্রদান করে।
- **না ক্যাশে** উষ্ণ করার জন্য কোন শেয়ার্ড রেসপন্স ক্যাশে নেই: ফাইল রুট সহ, [ISR](isr.md) প্রতি ইউআরএলে একটি যোগ করে।
- **স্ট্রিমিং শুধুমাত্র একটি উপাদান যে সাহায্য করে ফলন** পৃষ্ঠার শীর্ষে একটি ধীর ক্যোয়ারী এখনও প্রথম বাইট বিলম্বিত করে।
- **কোন স্ট্যাটিক আউটপুট** সার্ভার মোডে বিল্ডে কিছুই হিমায়িত হয় না: কোনও SSG মোড নেই, এবং কোনও এক্সপোর্ট কমান্ড নেই। [রেন্ডারিং](README.md) দেখুন।
- **`.nexy` টেমপ্লেটে অটোএসকেপিং বন্ধ**। `| e` দিয়ে অবিশ্বস্ত মানগুলি এস্কেপ করুন।

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## পরবর্তী পদক্ষেপ

<!-- router:fbr,custom -->
- [ISR](isr.md): প্রতি ইউআরএলে এই পৃষ্ঠাটি ক্যাশে করুন
<!-- /router -->
- [দ্বীপপুঞ্জ](islands.md): SSR রাখুন এবং একটি উইজেটকে ইন্টারেক্টিভ করুন
<!-- router:fbr,custom -->
- [CSR](csr.md): ব্রাউজারে হ্যান্ড নেভিগেশন
<!-- /router -->
- [কর্মক্ষমতা](../deployment/performance.md)
