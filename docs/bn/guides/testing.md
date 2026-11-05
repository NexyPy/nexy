# টেস্টিং

`nx test` সার্ভার পরীক্ষাগুলি pytest দিয়ে চালায়, এবং ক্লায়েন্ট ভিটেস্টের সাথে পরীক্ষা করে যখন আপনি তাদের জন্য জিজ্ঞাসা করেন।

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## কি রান

| অংশ | আদেশ | অবস্থা |
|---|---|---|
| সার্ভার | `pytest` | যখন এটি বিদ্যমান থাকে তখন `tests/` চলে, অন্যথায় প্রকল্প রুটে; যখন pytest ইনস্টল করা না থাকে তখন একটি সতর্কতা দিয়ে এড়িয়ে যায় |
| ক্লায়েন্ট | `npx vitest run` | শুধুমাত্র `--client` এর সাথে, এবং শুধুমাত্র যখন `vitest.config.ts` বিদ্যমান থাকে বা `vitest` `package.json` এ উপস্থিত হয় |

কোনো বিল্ট-ইন এন্ড-টু-এন্ড রানার নেই। সার্ভারটি `TestClient` দিয়ে চালান এবং ব্রাউজার আচরণের জন্য নিজেকে নাট্যকার বা সাইপ্রেস যোগ করুন।

## সার্ভার পরীক্ষা করুন

পরীক্ষার ক্লায়েন্ট প্রক্রিয়া চলাকালীন ASGI অ্যাপের সাথে কথা বলে: শুরু করার জন্য কোনও সার্ভার নেই, বাছাই করার জন্য কোনও পোর্ট নেই।

```python filename="tests/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` হল একত্রিত অ্যাপ্লিকেশন, এটি প্রথমবার পড়া হয়েছে। এটি ওয়ার্কিং ডিরেক্টরি থেকে `nexyconfig.py` পড়ে, তাই প্রজেক্ট রুট থেকে pytest চালান।

যখন একটি পরীক্ষা কনফিগারেশন বা রুট পরিবর্তন করে, মডিউল-স্তরের একটি পুনরায় ব্যবহার করার পরিবর্তে একটি নতুন অ্যাপ্লিকেশন তৈরি করুন:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` রুট, মিডলওয়্যার, সেশন এবং অনুবাদগুলি পুনরায় একত্রিত করে, তাই প্রতিটি কল প্রকল্প ডিরেক্টরির বর্তমান অবস্থা থেকে শুরু হয়।

## কি জাহির করা

একটি পৃষ্ঠা HTML প্রদান করে। স্ট্যাটাস জাহির করুন, তারপর আপনার পছন্দের বিষয়বস্তু:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

একটি API হ্যান্ডলার JSON প্রদান করে। একটি বৈধতা ব্যর্থতা হল একটি `422`, এবং একটি অনুপস্থিত রুট হল একটি `404` দ্বারা উত্তর দেওয়া `notfound.nexy` যখন সেই ফাইলটি বিদ্যমান থাকে:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

একটি কর্মের জন্য, ফাংশনটি সরাসরি পরীক্ষা করুন - এটি একটি স্বাভাবিক ফাংশন - এবং এটি প্রকাশ করে এমন পৃষ্ঠা থেকে এটির জেনারেট করা পথটি পড়ে HTTP এন্ডপয়েন্ট পরীক্ষা করুন:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

JSON এর সাথে একটি কল ফলাফল সহ উত্তর দেয় এবং `422` অবৈধ ক্ষেত্রগুলির সাথে।

> [!NOTE]
> কর্ম পথ প্রকল্পের জন্য নির্দিষ্ট এবং উত্পন্ন হয়. পরীক্ষায় কখনই হার্ডকোড `/_nx_<hash>` করবেন না।

## একটি `.nexy` উপাদান পরীক্ষা করুন

`nexy.testing.render` একটি কম্পোনেন্ট কম্পাইল করে, যে কম্পোনেন্ট ইম্পোর্ট করে এবং এর এইচটিএমএল রিটার্ন করে। প্রপস হল কীওয়ার্ড আর্গুমেন্ট এবং `children=` স্লট পূরণ করে:

```python filename="tests/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

প্রজেক্ট রুট থেকে pytest চালান: কম্পাইল করা ফাইলগুলি `__nexy__/`-এ যায়, যেমন `nx dev`। একটি উপাদান যা অনুরোধটি পড়ে (`usePathname`, `useSession`) এর পরিবর্তে `TestClient` সহ একটি পৃষ্ঠা পরীক্ষা প্রয়োজন।

## ক্লায়েন্ট পরীক্ষা করুন

`nx test --client` আপনার নিজের সেরা সেটআপ আশা করে। একটি ন্যূনতম উপাদান পরীক্ষা:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` এবং টেস্টিং লাইব্রেরি হল প্রকল্প নির্ভরতা: `nexy new` একটি টেস্ট স্ট্যাক ইনস্টল করে না। আপনার প্রয়োজনীয় পরিবেশের সাথে `vitest.config.ts` যোগ করুন (উপাদানের জন্য jsdom বা happy-dom)।

## ক্রমাগত একীকরণ

একটি প্রকল্প পাইপলাইনের জন্য দুটি কমান্ড যথেষ্ট:

```bash
nx build
nx test
```

`nx build` একটি সংকলন ত্রুটিতে ব্যর্থ হয়; `nx test` একটি ব্যর্থ দাবিতে ব্যর্থ হয় এবং অ-শূন্য থেকে বেরিয়ে যায়। `nx check` রানে mypy এবং `tsc` যোগ করে।

Nexy-এ কাজ করার জন্য নিজেই বিভিন্ন কমান্ড ব্যবহার করে: [কনট্রিবিউটিং](https://github.com/NexyPy/nexy/blob/main/CONTRIBUTING.md) দেখুন।

## পরবর্তী পদক্ষেপ

- [CLI](../reference/cli.md): `nx test` এর প্রতিটি পতাকা
- [এপিআই](../routing/fbr/handlers/README.md): কী একটি এন্ডপয়েন্ট রিটার্ন করে
- [মোতায়েন](../deployment/README.md): সিআই-তে পরীক্ষার আগে তৈরি করুন
