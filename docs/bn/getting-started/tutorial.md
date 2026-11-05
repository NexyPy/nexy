# টিউটোরিয়াল: 10 মিনিটের মধ্যে একটি নোট পৃষ্ঠা তৈরি করুন

আপনি একটি প্রকল্প তৈরি করবেন, একটি পৃষ্ঠা যুক্ত করবেন, একটি Python এন্ডপয়েন্ট যোগ করবেন, তাদের মধ্যে ডেটা শেয়ার করবেন এবং উৎপাদনের জন্য তৈরি করবেন। আপনি একটি পৃষ্ঠা এবং JSON হিসাবে পরিবেশিত নোটগুলির একটি তালিকা দিয়ে শেষ করুন৷

Nexy এ নতুন? প্রথমে [দ্রুত শুরু](quick-start.md) করুন: এটি তিন মিনিট সময় নেয়।

```diagram filename="পুরো টিউটোরিয়াল এক লাইনে"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. প্রকল্প তৈরি করুন

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` [uv](https://docs.astral.sh/uv/) এর সাথে আসে এবং শুধুমাত্র প্রকল্প তৈরি করে। এর পরে প্রতিটি কমান্ড প্রজেক্টের ভার্চুয়াল পরিবেশে চলে (বা `uv run nexy dev` হিসাবে)।

ফাইল-ভিত্তিক রাউটার, একটি ওয়েব প্রজেক্ট এবং যেকোনো ক্লায়েন্ট ফ্রেমওয়ার্ক (বা কোনোটিই) বেছে নিন। খোলা
<http://localhost:3000>। দীর্ঘ পদক্ষেপগুলি তাদের সময়কাল সহ প্রতিটি লাইন মুদ্রণ করে, যেমনটি `uv` করে।

<!-- router:modular -->
ফাইল-ভিত্তিক রাউটার প্রম্পটে `No` উত্তর দিন: `nx new` মডুলার রাউটারটিকে `src/routes/`-এর পরিবর্তে `src/apps/`-এ স্ক্যাফোল্ড করে।
<!-- /router -->

<!-- router:custom -->
পৃষ্ঠাগুলির জন্য ফাইল-ভিত্তিক রাউটার প্রম্পটে `Yes` উত্তর দিন, তারপরে আপনার বিদ্যমান `APIRouter` কে `nexyconfig.py` এ মাউন্ট করুন: দুটি রাউটার একসাথে থাকে।
<!-- /router -->

## 2. লেআউট সম্পাদনা করুন

<!-- router:fbr,custom -->
`src/routes/layout.nexy` HTML নথির মালিক (React ক্লায়েন্ট রাউটিং সহ এটি `layout.tsx`)। পরিবর্তন করুন `<title>`:

```nexy
<title>Notes</title>
```

সংরক্ষণ করুন: ব্রাউজার পুনরায় লোড হয়। [লেআউট](../routing/fbr/layouts/README.md) দেখুন।
<!-- /router -->

<!-- router:modular -->
কন্ট্রোলার দৃশ্যের চারপাশে `src/apps/layout.nexy` রেন্ডার করে এবং সেই ফাইলটি HTML নথির মালিক। পরিবর্তন করুন `<title>`:

```nexy
<title>Notes</title>
```

সংরক্ষণ করুন: ব্রাউজার পুনরায় লোড হয়। [একটি কন্ট্রোলার থেকে দেখা](../routing/modular/README.md#views-from-a-controller) দেখুন।
<!-- /router -->

## 3. একটি পৃষ্ঠা যোগ করুন

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

খুলুন <http://localhost:3000/notes>: আপনি দুটি বুলেট দেখতে হবে. এটি `/notes` এ পরিবেশিত হয়। `---` এর মধ্যবর্তী অংশটি Python, বাকি অংশটি Jinja2।
<!-- /router -->

<!-- router:modular -->
একটি নিয়ামক একটি দৃশ্য প্রদান করে। তৈরি করুন `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

রুটটি `src/apps/app_controller.py` এ ঘোষণা করুন এবং মডিউলে নিয়ামক যোগ করুন:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

খুলুন <http://localhost:3000/notes>: আপনি দুটি বুলেট দেখতে হবে. `---` এর মধ্যবর্তী অংশটি Python, বাকি অংশটি Jinja2।
<!-- /router -->

## 4. একটি শেষ বিন্দু যোগ করুন

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

আপনার `[{"id":1,"text":"Buy milk"}]` পাওয়া উচিত। ফাংশনের নাম হল HTTP পদ্ধতি। ইন্টারেক্টিভ API ডক্স `/docs` এ রয়েছে।
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

`src/apps/app_module.py`-এ `NotesApiController` যোগ করুন `controllers`, তারপর চালান:

```bash
curl http://localhost:3000/api/notes
```

আপনার `[{"id":1,"text":"Buy milk"}]` পাওয়া উচিত। পদ্ধতির নাম হল HTTP পদ্ধতি। ইন্টারেক্টিভ API ডক্স `/docs` এ রয়েছে।
<!-- /router -->

## 5. ডেটা শেয়ার করুন

তালিকাটিকে একটি Python মডিউলে নিয়ে যান এবং উভয় ফাইলেই এটি ব্যবহার করুন:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. নির্মাণ এবং পরিবেশন

```bash
nx build
nx start
```

`nx build` প্রতিটি পর্যায় তার সময়কাল সহ মুদ্রণ করে। `nx start` কম্পাইল করা আউটপুটকে Uvicorn দিয়ে পরিবেশন করে: রানটাইমে কোনো নোড প্রক্রিয়া নেই।

## যেখানে পরের

- [রাউটিং](../routing/README.md): গতিশীল সেগমেন্ট এবং গ্রুপ
- [ক্রিয়াগুলি](../guides/actions.md): একটি ফর্ম বা ক্লায়েন্ট থেকে Python কল করুন
- [পরীক্ষা ](../guides/testing.md): পরীক্ষার পৃষ্ঠা এবং শেষ পয়েন্ট
- [মোতায়েন](../deployment/README.md): কন্টেইনার এবং বিপরীত প্রক্সি
