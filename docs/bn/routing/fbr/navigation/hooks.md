# হুকস

হুক একটি `.nexy` পৃষ্ঠা, একটি API হ্যান্ডলার বা একটি মডুলার কন্ট্রোলারের ভিতর থেকে বর্তমান HTTP অনুরোধটি পড়ে। তাদের নাম ক্লায়েন্ট রাউটারের হুকের সাথে মেলে (`@nexy/client`) যেখানে তারা একই কাজ করে।

> [!NOTE]
> হুক শুধুমাত্র কাজ করে যখন একটি অনুরোধ পরিচালনা করা হচ্ছে। অন্য কোথাও একজনকে ডাকলে `RuntimeError` হয়।

## হুক

| হুক | রিটার্নস |
|---|---|
| `usePathname()` | অনুরোধের পথ, যেমন `"/blog/post-1"` |
| `useSearchParams()` | ক্যোয়ারী স্ট্রিং হিসাবে `dict[str, str]`, প্রতি কী প্রথম মান |
| `useParams()` | ডায়নামিক পাথ প্যারামিটার, যেমন `{"slug": "post-1"}` |
| `useQuery()` | `useParams()` এর আসল নাম, বিদ্যমান পৃষ্ঠাগুলির জন্য রাখা হয়েছে |
| `useRequest()` | Starlette অনুরোধ, যা অন্যান্য হুকগুলি আবৃত করে না |
| `useHeaders()` | অনুরোধের শিরোনামগুলি `dict[str, str]` হিসাবে, ছোট হাতের নাম |
| `useUrl()` | সম্পূর্ণ URL: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | `href` বর্তমান পৃষ্ঠা বা এর পিতামাতার একজন কিনা |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | সমস্ত কুকিজ হিসাবে `dict[str, str]` |
| `useSession()` | সেশন ডিক্ট, `{}` যখন সেশন সক্রিয় করা হয় না |
| `useToc(depth_range="2-6")` | বর্তমান পৃষ্ঠার জন্য বিষয়বস্তুর সারণী HTML, `""` যখন কোনটি নেই |
| `useViews(path, context=None)` | অন্য ভিউ রেন্ডার করে এবং একটি `HTMLResponse` ফেরত দেয় |

## অনুরোধ পড়ুন

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## একটি নেভিগেশন বারে একটি সক্রিয় লিঙ্ক

`useIsActive` ক্লায়েন্টের মতো একই নিয়ম অনুসরণ করে: ক্যোয়ারী স্ট্রিং, ফ্র্যাগমেন্ট এবং একটি ট্রেলিং স্ল্যাশ উপেক্ষা করা হয়, `exact` সেট না করা পর্যন্ত পিতামাতার একটি লিঙ্ক তার সন্তানদের উপর সক্রিয় থাকে এবং `/` শুধুমাত্র `/` এ সক্রিয় থাকে।

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## নোট

- `useQuery()` **পথ** প্যারামিটার ফেরত দেয়, কোয়েরি স্ট্রিং নয়, যে কারণে `useParams()` বিদ্যমান। ক্যোয়ারী স্ট্রিং হল `useSearchParams()`।
- `useRouter()` এখানে অনুরোধ হুক. এটি `useRouter` কনফিগার ক্ষেত্র নয় যা একটি `APIRouter` মাউন্ট করে।
- `useSession()` প্রয়োজন `useSession = {...}` মধ্যে `nexyconfig.py`; এটা ছাড়া ডিকটি খালি।
- `useViews("about.tsx", {"title": "About"})` HTML প্রদান করে: একটি `.nexy` ভিউ তার সংকলিত মডিউল দ্বারা রেন্ডার করা হয়, একটি `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` ভিউ একটি ক্লায়েন্ট মাউন্ট কন্টেইনার হয়ে যায়।

## পরবর্তী পদক্ষেপ

- [পৃষ্ঠা](../pages/README.md): গতিশীল সেগমেন্ট এবং লেআউট
- [রেসিপি](../../../guides/recipes.md): একটি পরীক্ষিত সাইন-ইন প্রবাহ `useSession()` এর উপর নির্মিত
- [কনফিগ](../../../reference/config.md): সেশন এবং লোকেল সক্রিয় করুন
- [.nexy ফাইল](../../../views/nexy/README.md): যেখানে সাধারণত হুক বলা হয়
