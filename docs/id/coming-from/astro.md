# Dari Astro hingga Nexy

Halaman Nexy `.nexy` adalah halaman Astro dengan Python di bagian depan `---` dan bukan TypeScript: HTML pertama server yang sama, pulau yang sama, dan direktif `client:*`, yang dirender pada setiap permintaan.

Setiap bagian di bawah menunjukkan kebiasaan Astro, lalu hal yang sama di Nexy.

## Sebuah halaman

```astro filename="src/pages/about.astro"
---
const title = "About";
---
<h1>{title}</h1>
```

Materi depannya adalah Python dan templatnya adalah Jinja2:

```nexy filename="src/rute/tentang.nexy"
---
title = "About"
---
<h1>{{ title }}</h1>
```

`src/pages/` adalah `src/routes/`, dan `index.astro` adalah `index.nexy`.

## Loop dan kondisi

```astro filename="src/pages/users.astro"
---
const users = [{ name: "Ada", admin: true }, { name: "Alan", admin: false }];
---
<ul>
  {users.map((user) => <li>{user.name}{user.admin && <strong> admin</strong>}</li>)}
</ul>
```

```nexy filename="src/rute/pengguna.nexy"
---
users = [{"name": "Ada", "admin": True}, {"name": "Alan", "admin": False}]
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}{% if user.admin %}<strong> admin</strong>{% endif %}</li>
  {% endfor %}
</ul>
```

> [!WARNING]
> Astro lolos setiap `{value}`. Templat `.nexy` tidak: lolos dari apa yang diketik pengunjung dengan `{{ value | e }}`.

## Komponen dan `Astro.props`

```astro filename="src/components/Card.astro"
---
const { title, tone = "neutral" } = Astro.props;
---
<article class={`card card-${tone}`}>
  <h2>{title}</h2>
  <slot />
</article>
```

Props dideklarasikan dengan `prop[...]`, defaultnya adalah Python default, dan `<slot />` adalah `<Slot />`:

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/rute/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest" tone="warm">
  <p>This week</p>
</Card>
```

`@` adalah `src/`: `nx new` menulis `useAliases = {"@": "src"}` di `nexyconfig.py`.

## Tata Letak

```astro filename="src/layouts/Base.astro"
---
const { title } = Astro.props;
---
<html>
  <head><title>{title}</title></head>
  <body><slot /></body>
</html>
```

```astro filename="src/pages/about.astro"
---
import Base from "../layouts/Base.astro";
---
<Base title="About"><h1>About</h1></Base>
```

Sebuah halaman tidak mengimpor tata letaknya: `layout.nexy` terdekat di atasnya membungkusnya, dan halaman root memiliki dokumen tersebut.

```nexy filename="src/routes/layout.nexy"
---
from nexy import useMetadata

children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <head>{{ useMetadata().html() }}</head>
  <body>{{ children | safe }}</body>
</html>
```

## Judul dan meta tag

Prop `title` tata letak menjadi `metadata` di halaman, yang `useMetadata().html()` tulis di `<head>` tata letak di atas:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

## Rute dinamis dan `getStaticPaths`

```astro filename="src/pages/posts/[siput].astro"
---
export function getStaticPaths() {
  return [
    { params: { slug: "hello" }, props: { title: "Hello" } },
    { params: { slug: "world" }, props: { title: "World" } },
  ];
}
const { title } = Astro.props;
---
<h1>{title}</h1>
```

Halaman dinamis `.nexy` dirender berdasarkan permintaan, jadi tidak ada daftar jalur: segmen adalah prop, dan yang tidak diketahui adalah `404`.

```nexy filename="src/rute/postingan/[siput].nexy"
---
from nexy import notFound

POSTS = {"hello": "Hello", "world": "World"}

slug: prop[str]
if slug not in POSTS:
    notFound()
title = POSTS[slug]
---
<h1>{{ title }}</h1>
```

`[...path].astro` adalah `[...path].nexy`.

## Pulau dan `client:*`

```astro filename="src/pages/index.astro"
---
import Counter from "../components/Counter.tsx";
---
<h1>Static heading</h1>
<Counter start={3} client:visible />
```

Arahannya menjadi atribut `directive`, dengan nilai yang sama:

```nexy filename="src/routes/home.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter start=3 directive="client:visible" />
```

| Astro | Nexy |
|---|---|
| `client:load` | `directive="client:load"`, atau tidak ada arahan |
| `client:idle` | `directive="client:idle"` |
| `client:visible` | `directive="client:visible"` |
| `client:media="(min-width: 768px)"` | `directive="client:media" media="(min-width: 768px)"` |
| `client:only="react"` | diterima, tetapi tidak pernah terhidrasi: gunakan `client:load` |

Kerangka kerja ini ditetapkan satu kali dalam `nexyconfig.py`, dan sebuah proyek menggunakan salah satunya:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

## Markdown halaman

```md filename="src/halaman/changelog.md"
---
layout: ../layouts/Base.astro
---
# Changelog
```

File `.md` di bawah `src/routes/` adalah halaman, dibungkus dalam tata letak terdekat tanpa kunci `layout:`:

```md filename="src/rute/changelog.md"
# Changelog

Version 2.2 is out.
```

Halaman `.mdx` juga bisa digunakan, dengan React atau Preact sebagai kerangkanya. Lihat [Markdown dan MDX](../views/nexy/markdown.md).

## Titik akhir API

```ts filename="src/pages/api/items/[id].ts"
export function GET({ params }) {
  return Response.json({ id: Number(params.id) });
}
```

```python filename="src/routes/api/item/[id].py"
async def GET(id: int):
    return {"id": id}
```

Badan adalah model Pydantic, yang divalidasi sebelum fungsi dijalankan:

```python filename="src/routes/api/items/index.py"
from pydantic import BaseModel

from nexy.http import JSONResponse


class NewItem(BaseModel):
    name: str


async def POST(item: NewItem):
    return JSONResponse({"created": item.name}, status_code=201)
```

## `Astro.redirect`, `Astro.cookies` dan `Astro.url`

```astro filename="src/pages/account.astro"
---
const theme = Astro.cookies.get("theme")?.value ?? "light";
if (!Astro.cookies.has("session")) return Astro.redirect("/login");
const page = Astro.url.searchParams.get("page") ?? "1";
---
<p>{theme} theme, page {page}</p>
```

Bacaan yang sama adalah kait, dan pengalihan adalah sebuah fungsi:

```nexy filename="src/routes/akun.nexy"
---
from nexy import redirect, useCookies, useSearchParams

cookies = useCookies()
if "session" not in cookies:
    redirect("/login")
theme = cookies.get("theme", "light")
page = useSearchParams().get("page", "1")
---
<p>{{ theme }} theme, page {{ page }}</p>
```

## Perangkat Tengah

```ts filename="src/middleware.ts"
export function onRequest(context, next) {
  return next().then((response) => {
    response.headers.set("x-app", "demo");
    return response;
  });
}
```

```python filename="src/rute/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-app"] = "demo"
    return response
```

`middleware.py` dalam subfolder hanya membungkus rute di bawahnya, yang menggantikan pemeriksaan jalur di dalam `onRequest`.

## Astro Tindakan

```ts filename="src/aksi/index.ts"
import { defineAction } from "astro:actions";
import { z } from "astro:schema";

export const server = {
  addNote: defineAction({
    accept: "form",
    input: z.object({ title: z.string() }),
    handler: async ({ title }) => ({ title }),
  }),
};
```

```astro filename="src/halaman/catatan.astro"
---
import { actions } from "astro:actions";
---
<form method="POST" action={actions.addNote}>
  <input name="title" />
  <button>Add</button>
</form>
```

Suatu tindakan adalah fungsi Python di `src/actions/`; formulir memposting ke jalurnya:

```python filename="src/aksi/catatan.py"
from nexy.decorators import Action

NOTES: list[str] = []


@Action
async def add_note(title: str) -> None:
    NOTES.append(title)
```

```nexy filename="src/rute/catatan.nexy"
---
from src.actions.notes import NOTES
---
<form method="post" action="{{ __actions_path['add_note'] }}">
  <input name="title">
  <button type="submit">Add</button>
</form>
<ul>
  {% for note in NOTES %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Dari sebuah pulau, `useAction(add_note)` di `@nexy/client` memanggil fungsi yang sama dengan input yang diketik.

## `<Image />`

```astro
---
import { Image } from "astro:assets";
import logo from "../assets/logo.png";
---
<Image src={logo} alt="Logo" width={128} height={32} />
```

```nexy filename="src/rute/merek.nexy"
---
from nexy import Image
---
<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

## `404.astro`

```astro filename="src/pages/404.astro"
<h1>Not found</h1>
```

```nexy filename="src/rute/tidak ditemukan.nexy"
<h1>Not found</h1>
```

Klien API masih mendapatkan `{"detail": "Not Found"}`.

## Output statis dan rendering sesuai permintaan

Astro membuat HTML statis secara default dan merender sesuai permintaan dengan `output: "server"` atau `export const prerender = false`. Nexy merender setiap halaman berdasarkan permintaan, dan menyimpan halaman yang Anda pilih per URL:

```nexy filename="src/rute/berita.nexy"
---
revalidate = 60
---
<h1>News</h1>
```

Tidak ada ekspor statis: `nx start` melayani situs. Lihat [Render](../rendering/README.md).

## Berlari

| Astro | Nexy |
|---|---|
| `npm create astro@latest` | `nx new` |
| `astro dev` | `nx dev` |
| `astro build` dan `astro preview` | `nx build`, lalu `nx start` |
| `public/` | `public/`, bertugas di `/` |
| `astro add react` | `nx new` dengan kerangka, atau `useFF = react()` |

## Langkah selanjutnya

- [file .nexy](../views/nexy/README.md)
- [Kepulauan](../rendering/islands.md)
- [Markdown dan MDX](../views/nexy/markdown.md)
- [Dari Next.js hingga Nexy](nextjs.md)
