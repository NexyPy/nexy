# অন্য কাঠামো থেকে আসছে

Nexy হল FastAPI প্লাস ফাইল-ভিত্তিক রাউটিং, সার্ভার-রেন্ডার করা পৃষ্ঠা এবং ঐচ্ছিক React, Vue, Svelte, Solid বা Preact দ্বীপ। এই পৃষ্ঠাটি ম্যাপ করে যা আপনি ইতিমধ্যেই জানেন।

নীচের প্রতিটি ফ্রেমওয়ার্কের নিজস্ব একটি পৃষ্ঠা রয়েছে, কাজ অনুসারে কাজ, আপনার জানা কোড এবং তারপরে Nexy কোড সহ:

| Python | ব্যাকএন্ড | ফুলস্ট্যাক JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [এক্সপ্রেস](../coming-from/express.md), [ফাস্টফাই](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [এলিসিয়া](../coming-from/elysia.md), [হনো](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [স্প্রিং বুট](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [লারাভেল ](../coming-from/laravel.md), [রুবি অন রেল](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## থেকে FastAPI

| FastAPI | নেক্সি |
|---|---|
| `@app.get("/users")` আপনি আমদানি করেন এমন একটি মডিউলে | `GET` ফাংশন `src/routes/users.py` এ |
| `app.include_router(router)` | ফাইল পাথ হল URL; নিবন্ধন করার কিছু নেই |
| পথ পরম `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | এখনও `Depends(...)`: হ্যান্ডলাররা হল FastAPI হ্যান্ডলার |
| Jinja2 `TemplateResponse` | শেষবিন্দুর পাশে একটি `.nexy` পৃষ্ঠা |
| সঙ্গে চালান `uvicorn main:app` | `nx dev`, তারপর `nx build && nx start` |

`src/routes/*.py` এর অধীনে সবকিছুই সাধারণ FastAPI: নির্ভরতা, Pydantic মডেল, মিডলওয়্যার এবং `/docs` কাজ করে।

একই শেষ বিন্দু, আগে এবং পরে:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## থেকে Next.js

| Next.js | নেক্সি |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` বা `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (মালিক `<html>`) | `src/routes/layout.tsx` `useCSR = True` (React), অথবা `src/routes/layout.nexy` সার্ভার মোডে |
| নেস্টেড `layout.tsx` | ক্লায়েন্ট মোডে নেস্টেড `layout.tsx` / `layout.vue` / `layout.svelte`, সার্ভার মোডে নেস্টেড `layout.nexy` |
| `use client` একটি সার্ভার পৃষ্ঠায় উপাদান | [সার্ভার মোডে দ্বীপসমূহ](../rendering/islands.md) |
| রুট হ্যান্ডলার `route.ts` | `src/routes/api/x.py`, লেখা Python |
| `(group)` ফোল্ডার | একই: `(group)/` |
| সার্ভার অ্যাকশন | [`@Action`](../guides/actions.md) ফাংশনগুলি একটি ফর্ম থেকে বা টাইপ করা ক্লায়েন্ট ফাংশন হিসাবে বলা হয় |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

ব্যাকএন্ড হল Python, তাই আপনার API আপনার ডেটা এবং ML কাজের সাথে কোড শেয়ার করে। ক্লায়েন্ট উপাদানগুলি একটি সম্পূর্ণ-পৃষ্ঠা React গাছের পরিবর্তে দ্বীপ হিসাবে হাইড্রেট করে।

একটি Next.js পৃষ্ঠা প্রায় তার মতোই চলে যায় এবং এর `"use client"` উপাদানটি একটি সার্ভার পৃষ্ঠার একটি দ্বীপে পরিণত হয়:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```

## এক্সপ্রেস বা নোড ব্যাকএন্ড থেকে

| এক্সপ্রেস | নেক্সি |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` সাথে `async def GET(id)` |
| `app.use(middleware)` | FastAPI মিডলওয়্যার, `nexyconfig.py` থেকে নিবন্ধিত |
| `res.json(obj)` | একটি dict বা একটি Pydantic মডেল ফেরত দিন |
| ইজেএস/পগ ভিউ | `.nexy` (Jinja2) পৃষ্ঠা |
| `npm run dev` | `nx dev` |

`app.use(...)` `nexyconfig.py` এর একটি ক্ষেত্র হয়ে যায় এবং `res.json(...)` একটি রিটার্ন মান হয়ে যায়:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/routes/users/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```

## একটি রাউটার নির্বাচন করা হচ্ছে

| ব্যবহার করুন | কখন |
|---|---|
| ফাইল-ভিত্তিক রাউটার | ফাইল থেকে ম্যাপ করা পৃষ্ঠা এবং শেষ পয়েন্ট; ডিফল্ট |
| মডুলার রাউটার | কন্ট্রোলার, মডিউল এবং নির্ভরতা ইনজেকশন, নেস্টজেএস-স্টাইল |

দুটি ফাইলে মডুলার রাউটার: একটি নিয়ামক, এবং মডিউল `nexyconfig.py` পয়েন্টে `useRouter = AppModule`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

উভয়ই `nx new` দ্বারা ভারা এবং একই শেষ থেকে শেষ পরীক্ষা দ্বারা আচ্ছাদিত। [রাউটিং](../routing/README.md) এবং [মডুলার রাউটিং](../routing/modular/README.md) দেখুন।

## যেখানে পরের

- [দ্রুত শুরু ](quick-start.md): একটি প্রকল্প তৈরি করুন এবং এটি চালান
- [প্রজেক্ট স্ট্রাকচার](project-structure.md): যেখানে প্রতিটি ফাইল থাকে
- [রাউটিং ](../routing/README.md): রাউটার নির্বাচন করুন
