# আমি কিভাবে Nexy এ সার্ভার কোড ডিবাগ করব?

টার্মিনালে `breakpoint()` বা ভিএস কোড এবং `debugpy` দিয়ে `nx dev`-এর সার্ভার কোড ডিবাগ করুন: ডেভ সার্ভার আপনার Python কে তার নিজস্ব প্রক্রিয়ায় চালায়, তাই এটির সাথে সংযুক্ত একটি ডিবাগার আপনার পৃষ্ঠা, API হ্যান্ডলার এবং অ্যাকশনে থামে।

## কিভাবে `nx dev` আপনার কোড চালায়

`nx dev` আলাদা কর্মী ছাড়াই নিজস্ব প্রক্রিয়ায় ইউভিকর্ন শুরু করে। যখন একটি Python ফাইল বা একটি `.nexy` পৃষ্ঠা পরিবর্তিত হয়, এটি আপনার প্রকল্পের মডিউলগুলি ভুলে যায় এবং একই প্রক্রিয়ায় সেগুলি আবার আমদানি করে। `nx dev` এর সাথে সংযুক্ত একটি ডিবাগার তাই পুনরায় লোড জুড়ে সংযুক্ত থাকে এবং একটি ফাইলে সেট করা একটি ব্রেকপয়েন্ট নতুন কোডে তার স্থান রাখে।

একটি `.nexy` ফাইল একই পথে `__nexy__/` এর অধীনে একটি Python মডিউলে সংকলিত হয়, যা চলে:

<!-- router:fbr,custom -->
| আপনি লিখুন | নেক্সি রান |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, ফাংশন `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | ফাইল নিজেই |
<!-- /router -->

<!-- router:modular -->
| আপনি লিখুন | নেক্সি রান |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | ফাইল নিজেই |
<!-- /router -->

একটি `.nexy` ফাইলের ফ্রন্ট ম্যাটার (দুটি `---` লাইনের মধ্যবর্তী Python সেই মডিউলের একটি ফাংশনের মূল অংশে পরিণত হয়। `__nexy__/` প্রতিটি পরিবর্তনের উপর আবার লেখা হয়: এটি কখনই সম্পাদনা করবেন না।

## `breakpoint()` দিয়ে টার্মিনালে থামুন

আপনি যেখানে থামতে চান সেখানে `breakpoint()` রাখুন, একটি `.py` ফাইলে বা একটি `.nexy` ফাইলের সামনের অংশে:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

পেজ খুলুন। অনুরোধটি অপেক্ষা করে এবং `nx dev` এর টার্মিনাল সংকলিত মডিউলে pdb দেখায়:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

খুলুন `/users`। অনুরোধটি অপেক্ষা করে এবং `nx dev` এর টার্মিনাল সেই লাইনে পিডিবি দেখায়। একটি ভিউ এর ফ্রন্ট ম্যাটারে, pdb `__nexy__/src/apps/` এর অধীনে কম্পাইল করা মডিউল দেখায়।
<!-- /router -->

একটি মান প্রিন্ট করার জন্য `p page` টাইপ করুন, পরবর্তী লাইনের জন্য `n`, অনুরোধটি চলতে দিন `c`। আপনার হয়ে গেলে লাইনটি সরান: পরবর্তী অনুরোধটি আবার সেখানে থামবে।

## VS কোড দিয়ে ডিবাগ করুন

প্রকল্পের পরিবেশে `debugpy` ইনস্টল করুন:

```bash
uv add --dev debugpy
```

তারপর একটি লঞ্চ কনফিগারেশন যোগ করুন। `nexy.modules.cli` হল `nx` কমান্ডের পিছনে মডিউল, তাই এটি Linux, macOS এবং Windows এ একই কাজ করে:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

F5 টিপুন। আপনার `.py` ফাইলে এবং `.nexy` ফাইলের জন্য `__nexy__/` এর অধীনে সংকলিত মডিউলে ব্রেকপয়েন্ট সেট করুন: VS কোড একটি `.nexy` ফাইলে থামতে পারে না, কারণ এটি সংকলিত না হওয়া পর্যন্ত Python নয়। কম্পাইল করা মডিউলের লাইন সংখ্যা সামনের ব্যাপারটিকে অনুসরণ করে, তাই আপনি পৃষ্ঠাটি সম্পাদনা করার পরে সেখানে একটি ব্রেকপয়েন্ট সরে যেতে পারে; `breakpoint()` ফ্রন্ট ম্যাটারে নেই।

## অন্য টার্মিনাল থেকে সংযুক্ত করুন

ডেভ সার্ভার নিজেই শুরু করতে এবং পরে একটি ডিবাগার সংযুক্ত করতে:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` একটি ডিবাগার সংযুক্ত না হওয়া পর্যন্ত স্টার্ট ধরে রাখে; একবারে শুরু করতে ছেড়ে দিন। ভিএস কোডে, `"request": "attach"` এবং `"connect": { "host": "127.0.0.1", "port": 5678 }` এর কনফিগারেশনের সাথে সংযুক্ত করুন।

debugpy সতর্ক করতে পারে যে "হিমায়িত মডিউল ব্যবহার করা হচ্ছে"। স্ট্যান্ডার্ড লাইব্রেরিতে একটি ব্রেকপয়েন্ট মিস হলে Python `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) দিয়ে শুরু করুন; আপনার নিজের কোডের ব্রেকপয়েন্ট প্রভাবিত হয় না।

## পরবর্তী পদক্ষেপ

- [সমস্যা সমাধান ](troubleshooting.md): প্রথম সমস্যা মানুষ আঘাত
- [টেস্টিং](testing.md): একবার আপনি এটি খুঁজে পেলে একটি পরীক্ষায় বাগটি পুনরুত্পাদন করুন
- [.nexy ফাইল](../views/nexy/README.md): ফ্রন্টম্যাটার, প্রপস এবং টেমপ্লেট
