# কর্ম

একটি `@Action` একটি Python ফাংশনকে `POST` এন্ডপয়েন্টে পরিণত করে। একটি আদর্শ API হ্যান্ডলারের বিপরীতে, এটি একটি টাইপ করা যোগাযোগ সেতু হিসাবে ডিজাইন করা হয়েছে: Nexy স্বয়ংক্রিয়ভাবে TypeScript ক্লায়েন্ট তৈরি করে, ইনপুট যাচাই করে এবং প্রতিক্রিয়া পরিচালনা করে।

**আপনি শুরু করার আগে:** [দ্রুত শুরু](../getting-started/quick-start.md) দ্বারা তৈরি একটি প্রকল্প। অ্যাকশনগুলি পৃষ্ঠাগুলির পাশে, `src/actions/`-এ লাইভ।

```diagram filename="অ্যাকশন সাইকেল"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## অ্যাকশন সাইকেল

### 1. সংজ্ঞায়িত করুন
একটি ক্রিয়া হল একটি স্বাভাবিক Python ফাংশন যা `@Action` দিয়ে চিহ্নিত। API চুক্তি সংজ্ঞায়িত করতে Nexy তার স্বাক্ষর ব্যবহার করে।

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

পরামিতিগুলি হল ইনপুট, Pydantic দ্বারা যাচাইকৃত। `request` বা `response` নামের একটি প্যারামিটার ইনজেকশন করা হয় এবং ইনপুটের অংশ নয়।

### 2. যাচাই করুন
যখন অ্যাকশনটি কল করা হয়, Nexy ফাংশনের প্রকার ইঙ্গিতগুলির বিরুদ্ধে ইনপুটটিকে যাচাই করে। যদি একটি ক্ষেত্র অনুপস্থিত থাকে বা ভুল টাইপ থাকে, তাহলে কর্মটি কার্যকর করা হয় না এবং একটি `422 Unprocessable Entity` ফেরত দেওয়া হয়।

### 3. চালান
লজিক সার্ভারে চলে। যেহেতু এটি একটি স্ট্যান্ডার্ড Python ফাংশন, আপনি যেকোন লাইব্রেরি ব্যবহার করতে পারেন, ডাটাবেস অ্যাক্সেস করতে পারেন বা অন্য পরিষেবাগুলিতে কল করতে পারেন। এছাড়াও আপনি `revalidate()` ব্যবহার করে একটি পৃষ্ঠা রিফ্রেশ ট্রিগার করতে পারেন।

### 4. সিরিয়ালাইজ করুন
ফেরত মান স্বয়ংক্রিয়ভাবে JSON ক্রমিক করা হয়. Pydantic মডেলগুলি নেটিভভাবে পরিচালনা করা হয়, এবং স্ট্যান্ডার্ড Python প্রকারগুলি তাদের JSON সমমানের সাথে ম্যাপ করা হয়।

### 5. গ্রাস
ফ্রন্টএন্ড সম্পূর্ণ ধরনের নিরাপত্তা সহ ফলাফল পায়। Nexy আপনার স্বাক্ষর থেকে `__nexy__/src/actions.ts` লিখেছে, এবং `@nexy/actions` এটির সমাধান করেছে।

<!-- router:fbr,custom -->
```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
কম্পোনেন্ট হল একটি দ্বীপ যা একটি কন্ট্রোলার ফিরে আসে:

```tsx filename="src/components/NewUser.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

একটি হুক ছাড়া, একটি কর্ম শুধুমাত্র একটি `async` ফাংশন: `const user = await create_user({ name: "Ada" })`।

| ফ্রেমওয়ার্ক | যা `useAction` ফেরত দেয় |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | একই, `pending()`, `data()` এবং `error()` অ্যাক্সেসর হিসাবে |
| Vue | একই, `pending`, `data` এবং `error` রেফ হিসাবে |
| Svelte | একটি দোকান: `$save.pending`, `$save.data`, `$save.error`, প্লাস `save.run(input)` এবং `save.reset()` |

`useAction(action, { onSuccess, onError })` এছাড়াও দুটি কলব্যাক লাগে। `run` কখনই নিক্ষেপ করে না: একটি ব্যর্থতা `error` এ ল্যান্ড করে এবং `run` `undefined` এর সাথে সমাধান করে।

প্রকারগুলি Python থেকে আসে: `str` হল `string`, `int` এবং `float` হল `number`, `list[T]` হল `T[]`, একটি Pydantic মডেল বা `Enum` একটি নামযুক্ত প্রকার, এবং একটি ডিফল্ট সহ একটি ক্ষেত্র ইনপুটে ঐচ্ছিক৷ একটি প্রকার Pydantic বর্ণনা করতে পারে না `unknown` হয়ে যায়।

## ত্রুটি এবং ব্যর্থতা

একটি ক্রিয়া বিভিন্ন পর্যায়ে ব্যর্থ হতে পারে। আপনার UI এ তাদের মধ্যে পার্থক্য করা উচিত:

1.  **বৈধতা ত্রুটি (422)**: ইনপুটটি Python স্বাক্ষরের সাথে মেলেনি। `error.fields` প্রতিটি অবৈধ ক্ষেত্রকে তার বার্তায় ম্যাপ করে।
2.  **ব্যবসায়িক ত্রুটি (`HTTPException`)**: আপনার কোড কলটি প্রত্যাখ্যান করেছে, উদাহরণস্বরূপ `403 Forbidden` বা `409 Conflict`।
3.  **সার্ভার ত্রুটি (500)**: আপনার Python কোডে একটি আন-হ্যান্ডেলড ব্যতিক্রম ঘটেছে।
4.  **নেটওয়ার্ক ত্রুটি**: অনুরোধটি কখনই সার্ভারে পৌঁছায়নি, উদাহরণস্বরূপ একটি সময়সীমা বা হারিয়ে যাওয়া সংযোগ।
5.  **অনুমোদনের ত্রুটি (401, 403)**: আপনার নিজের চেক কলকারীকে প্রত্যাখ্যান করেছে। Nexy আপনার জন্য এটি সিদ্ধান্ত নেয় না.

নীচে বর্ণিত অরিজিন চেকটি একটি CSRF সুরক্ষা, অনুমোদন নয়: এটি বলে যে কলটি কোথা থেকে এসেছে, কাকে এটি করার অনুমতি দেওয়া হয়নি।

## একটি কর্মের পরে পৃষ্ঠাটি রিফ্রেশ করুন

একটি ক্রিয়া বলে যে কোন পৃষ্ঠাগুলির পরিবর্তনটি বাসি হয়ে গেছে, যেমনটি Next.js `revalidatePath` এর সাথে করে:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

উত্তর একটি `x-nexy-revalidate` শিরোনামে পাথ বহন করে। ক্লায়েন্ট তারপর রাউটারের মাধ্যমে বর্তমান পৃষ্ঠাটি পুনরায় আনয়ন করে, বা ক্লায়েন্ট রাউটার না থাকলে এটি পুনরায় লোড করে।

## ফর্ম ছাড়া JavaScript

একটি অ্যাকশন একটি স্ট্যান্ডার্ড HTML ফর্মও নেয়, তাই কোনো স্ক্রিপ্ট লোড হওয়ার আগে পৃষ্ঠাটি কাজ করে:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

একটি `.nexy` টেমপ্লেটে `__actions_path["name"]` হল পথ, `__actions["name"]` ফাংশন, এবং ফাংশনটি তার নিজের নামেও রয়েছে।

সফল হলে, ভিজিটরকে স্ট্যাটাস সহ `303` ফর্মটি যে পৃষ্ঠায় ছিল সেখানে ফেরত পাঠানো হয়। ভিন্নভাবে উত্তর দিতে, একটি `Response` বস্তু ফেরত দিন (যেমন, `RedirectResponse("/done", status_code=303)`)।

একটি ফর্ম `application/x-www-form-urlencoded` হিসাবে পাঠানো হয়, যা একটি ব্রাউজার ডিফল্টভাবে করে, কোন অতিরিক্ত প্যাকেজের প্রয়োজন হয় না। যোগ করুন `enctype="multipart/form-data"` এবং কলের প্রয়োজন `python-multipart`: এটি ছাড়া অ্যাকশন উত্তর দেয় `500` কমান্ডের নামকরণ একটি বার্তা সহ, `uv add python-multipart`।

একটি ক্রিয়া ক্ষেত্রগুলি পড়ে, ফাইলগুলি নয়: একটি ফাইল ইনপুট একটি স্ট্রিং হিসাবে এটিতে পৌঁছায়। একটি আপলোড পেতে, একটি `File` বা `UploadFile` প্যারামিটার সহ `src/routes/api/` এ একটি রুট লিখুন।

## নিরাপত্তা

### পথের অস্পষ্টতা অনুমোদন নয়
অ্যাকশন পাথ হল `/_nx_` ফাংশনের মডিউলের একটি হ্যাশ, এর নাম এবং প্রকল্পের গোপনীয়তা। এটি `NEXY_ACTION_SECRET` দ্বারা সেট করা হয়, বা `__nexy__/action.key` এ রাখা হয়, যা `nx build` তৈরি করে যাতে ক্লায়েন্ট বান্ডিল এবং `nx start` সম্মত হয়: সেই ফাইলটিকে বিল্ডের সাথে রাখুন। পথটি নৈমিত্তিক আবিষ্কার থেকে শেষ বিন্দুকে লুকিয়ে রাখে এবং **উত্পন্ন পথটি অনুমোদনের প্রক্রিয়া নয়**।

যে কেউ পথ জানেন কর্ম কল করতে পারেন. আপনি **অবশ্যই** অ্যাকশনের ভিতরে ব্যবহারকারীর পরিচয় এবং অনুমতি যাচাই করতে হবে:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### মূল সুরক্ষা
ক্রস-সাইট অনুরোধ জালিয়াতি (CSRF) প্রতিরোধ করার জন্য, Nexy সেই অনুরোধগুলি প্রত্যাখ্যান করে যার `Origin` অন্য সাইট বা ব্রাউজার একটি `403` দিয়ে `Sec-Fetch-Site: cross-site` চিহ্নিত করে। `NEXY_ALLOWED_ORIGINS` এ আপনার ক্রিয়াকলাপগুলিকে কল করতে পারে এমন সাইটগুলির তালিকা করুন৷ একটি `Origin` (যেমন `curl`) ছাড়া কল গ্রহণ করা হয়.

## আমদানি ত্রুটি

স্টার্টআপে নেক্সি অ্যাকশন খোঁজার জন্য `src/` এর প্রতিটি মডিউল আমদানি করে। একটি মডিউল যা আমদানি করতে ব্যর্থ হয় তা রিপোর্ট করা হয় এবং অন্যগুলি এখনও লোড হয়:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## পরবর্তী পদক্ষেপ

- [API](../routing/fbr/handlers/README.md): স্পষ্ট হ্যান্ডলার
- [টেস্টিং](testing.md#what-to-assert): কিভাবে একটি ক্রিয়া পরীক্ষা করা যায়
- [কনফিগারেশন](../reference/config.md): মিডলওয়্যার এবং অথ অপশন
