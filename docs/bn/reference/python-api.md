# Python API

প্রতিটি নাম Nexy মডিউল দ্বারা আপনার Python কোডে রপ্তানি করে। একটি পরীক্ষা এই পৃষ্ঠাটিকে কোডের বিপরীতে উভয় দিক থেকে পরীক্ষা করে: এখানে তালিকাভুক্ত একটি নাম অবশ্যই বিদ্যমান থাকতে হবে এবং কোড রপ্তানি করে এমন একটি নাম এখানে তালিকাভুক্ত করা আবশ্যক৷

## `nexy`

`.nexy` টেমপ্লেট এবং অনুরোধ হুকগুলির জন্য উপাদান।

| নাম | এটা কি |
|---|---|
| `Audio`, `Video` | স্থানীয় `<audio>` এবং `<video>` খেলোয়াড়, [উপাদানগুলি](../views/nexy/components.md) দেখুন |
| `Image` | একটি `<img>` যা ডিফল্টরূপে অলসভাবে লোড হয় |
| `Link` | ঐচ্ছিক প্রিফেচ সহ একটি ক্লায়েন্ট-সাইড `<a>` |
| `Import` | একটি `.nexy` পৃষ্ঠায় একটি ক্লায়েন্ট উপাদান আমদানি করুন |
| `Template` | রেন্ডার Jinja2 এবং Markdown টেমপ্লেট |
| `Vite` | Vite ক্লায়েন্ট ট্যাগ প্রতিটি পৃষ্ঠার প্রয়োজন |
| `Form` | কোন আচরণ ছাড়া একটি স্থানধারক: একটি [ক্রিয়া](../guides/actions.md) সহ একটি প্লেইন `<form>` ব্যবহার করুন |
| `usePathname` | বর্তমান অনুরোধের পথ |
| `useSearchParams` | একটি dict হিসাবে ক্যোয়ারী স্ট্রিং |
| `useParams` | ডায়নামিক পাথ প্যারামিটারগুলি একটি ডিক্ট হিসাবে, যেমন ক্লায়েন্টে `useParams()` |
| `useQuery` | `useParams` এর আসল নাম, বিদ্যমান পৃষ্ঠাগুলির জন্য রাখা হয়েছে (এটি কোয়েরি স্ট্রিংটি পড়ে না) |
| `useRequest` | বর্তমান অনুরোধ, যা অন্যান্য হুক কভার করে না |
| `useHeaders` | অনুরোধ শিরোনাম একটি ছোট হাতের নাম সহ একটি dict হিসাবে |
| `useUrl` | সম্পূর্ণ URL: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | একটি লিঙ্ক বর্তমান পৃষ্ঠায় বা তার অভিভাবকদের একজনকে নির্দেশ করে, একটি নেভিগেশন বারের জন্য |
| `useRouter` | বর্তমান অনুরোধের `path`, `base_url` এবং `url_for` |
| `useSession` | সেশন ডিক্ট, যখন সেশন বন্ধ থাকে তখন খালি |
| `useCookies` | একটি ডিক্ট হিসাবে অনুরোধ কুকিজ |
| `useToc` | বর্তমান পৃষ্ঠার বিষয়বস্তুর সারণী, HTML হিসাবে |
| `useViews` | একটি হ্যান্ডলার থেকে একটি ভিউ ফাইল রেন্ডার করুন যেমন `about.tsx` |
| `setMetadata`, `useMetadata` | একটি পৃষ্ঠার শিরোনাম এবং হেড ট্যাগের নাম দিন এবং লেআউটে লিখুন |
| `redirect`, `permanentRedirect` | ভিজিটরকে অন্য কোথাও পাঠান (307, 308) এবং অনুরোধ বন্ধ করুন |
| `notFound`, `forbidden`, `unauthorized` | যেকোনো জায়গা থেকে 404, 403 বা 401 উত্তর দিন |

হুকগুলি শুধুমাত্র একটি অনুরোধের ভিতরে কাজ করে: [হুকস](../routing/fbr/navigation/hooks.md) দেখুন।

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## `nexy.http`

একটি হ্যান্ডলারের HTTP শব্দভান্ডার। FastAPI থেকে না করে এখান থেকে আমদানি করুন, তাই আপনার হ্যান্ডলাররা Nexy এর চুক্তির উপর নির্ভর করে।

| নাম | এটা কি |
|---|---|
| `Request`, `Response` | আগত অনুরোধ এবং একটি বহির্গামী প্রতিক্রিয়া |
| `HTTPException` | একটি স্ট্যাটাস এবং একটি `detail` সহ হ্যান্ডলারকে থামান |
| `status` | নাম দেওয়া স্ট্যাটাস কোড, যেমন `status.HTTP_404_NOT_FOUND` |
| `Depends` | প্রথমে একটি ফাংশন চালান এবং এর ফলাফল পাস করুন |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | যেখান থেকে একটি প্যারামিটার আসে |
| `Form`, `File`, `UploadFile` | ফর্ম ক্ষেত্র এবং আপলোড (প্রয়োজন `python-multipart`) |
| `BackgroundTasks` | কাজ যা উত্তর পাঠানোর পরে চলে |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | একটি নির্দিষ্ট বিষয়বস্তুর প্রকার সহ উত্তর |
| `RedirectResponse` | একটি HTTP পুনর্নির্দেশ |
| `redirect`, `permanentRedirect` | একটি পৃষ্ঠা, একটি হ্যান্ডলার, একটি নিয়ামক বা একটি গার্ড থেকে একটি পুনঃনির্দেশ (307, 308) বাড়ান |
| `notFound`, `forbidden`, `unauthorized` | একই জায়গা থেকে একটি 404, 403 বা 401 বাড়ান |
| `FileResponse`, `StreamingResponse` | একটি ফাইল বা একটি স্ট্রিম দিয়ে উত্তর দিন |

```python filename="src/routes/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```

## `nexy.decorators`

| নাম | এটা কি |
|---|---|
| `Action` | একটি ফাংশনকে `POST` এন্ডপয়েন্টে পরিণত করুন, [কর্ম](../guides/actions.md) দেখুন |
| `revalidate` | ব্রাউজারকে বলুন কোন পৃষ্ঠাগুলি একটি অ্যাকশন বাসি হয়ে গেছে |
| `Module`, `Controller` | [মডুলার রাউটারে](../routing/modular/README.md) একটি মডিউল এবং একটি কন্ট্রোলার ঘোষণা করুন |
| `Injectable`, `Container`, `Scope` | [নির্ভরতা ইনজেকশন ](../routing/modular/dependency-injection.md) এবং এর জীবনকাল |
| `UseGuard`, `Middleware` | একটি হ্যান্ডলার গার্ড বা মোড়ানো, [গার্ডস](../routing/modular/guards-and-metadata.md) দেখুন |
| `UseRoute`, `useRoute`, `RouteMeta` | একটি পথের নাম দিন এবং OpenAPI এর জন্য এটি বর্ণনা করুন |
| `UseResponse`, `ResponseMeta` | একটি পথের উত্তর বর্ণনা কর |
| `HTTP_METHODS` | HTTP পদ্ধতি একটি হ্যান্ডলার ফাইল সংজ্ঞায়িত করতে পারে |
| `ACTIONS_STORE` | টুলিং এবং পরীক্ষার জন্য কর্মের রেজিস্ট্রি |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| নাম | এটা কি |
|---|---|
| `render` | প্রদত্ত প্রপসের জন্য একটি `.nexy` উপাদানের এইচটিএমএল, সার্ভার ছাড়াই, [টেস্টিং](../guides/testing.md) দেখুন |

```python filename="tests/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## যেখানে পরের

- [কনফিগ](config.md): এই নামের পিছনে `use*` ক্ষেত্র
- [ব্যতিক্রম এবং ত্রুটি](exceptions.md): প্রতিটি ব্যর্থতার উত্তর কি
- [ডকুমেন্টেশন ইনডেক্স](../README.md): আপনি যা তৈরি করছেন তার পৃষ্ঠা
