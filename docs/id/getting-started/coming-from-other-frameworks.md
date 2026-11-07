# Berasal dari kerangka lain

Nexy adalah FastAPI plus perutean berbasis file, halaman yang dirender oleh server, dan pulau opsional React, Vue, Svelte, Solid atau Preact. Halaman ini memetakan apa yang sudah Anda ketahui.

Setiap kerangka kerja di bawah ini juga memiliki halamannya sendiri, tugas demi tugas, dengan kode yang Anda ketahui dan kemudian kode Nexy:

| Python | Bagian belakang | tumpukan penuh JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Ekspresikan](../coming-from/express.md), [Percepat](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Elysia](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Selanjutnya](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Sepatu Bot Musim Semi](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby di Rel](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## Dari FastAPI

<!-- router:fbr,custom -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` dalam modul yang Anda impor | `GET` berfungsi di `src/routes/users.py` |
| `app.include_router(router)` | jalur file adalah URL; tidak ada yang perlu didaftarkan |
| Parameter jalur `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | still `Depends(...)`: penangan adalah FastAPI penangan |
| Jinja2 `TemplateResponse` | halaman `.nexy` di sebelah titik akhir |
| Jalankan dengan `uvicorn main:app` | `nx dev`, lalu `nx build && nx start` |

Segala sesuatu di bawah `src/routes/*.py` adalah FastAPI biasa: dependensi, model Pydantic, middleware, dan `/docs` tetap berfungsi.

Titik akhir yang sama, sebelum dan sesudah:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/rute/pengguna/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` dalam modul yang Anda impor | `async def get(self)` di kelas `@Controller("/users")` |
| `app.include_router(router)` | pengontrol yang terdaftar di `controllers` dari `@Module` |
| Parameter jalur `/users/{id}` | `@Controller("/users/{id}")`, dengan `async def get(self, id: int)` |
| `Depends(...)` | still `Depends(...)`: metode pengontrol adalah titik akhir FastAPI |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, dikembalikan dengan metode |
| Jalankan dengan `uvicorn main:app` | `nx dev`, lalu `nx build && nx start` |

Dependensi, model Pydantic, middleware, dan `/docs` tetap berfungsi.

Titik akhir yang sama, sebelum dan sesudah:

```python filename="main.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## Dari Next.js

<!-- router:fbr,custom -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` atau `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (memiliki `<html>`) | `src/routes/layout.tsx` dengan `useCSR = True` (React), atau `src/routes/layout.nexy` dalam mode server |
| bersarang `layout.tsx` | bersarang `layout.tsx` / `layout.vue` / `layout.svelte` dalam mode klien, bersarang `layout.nexy` dalam mode server |
| `use client` komponen di halaman server | [pulau](../rendering/islands.md) dalam mode server |
| Pengendali rute `route.ts` | `src/routes/api/x.py`, ditulis dalam Python |
| `(group)` folder | sama: `(group)/` |
| Tindakan Server | [`@Action`](../guides/actions.md) fungsi dipanggil dari formulir atau seperti fungsi klien yang diketik |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Backendnya adalah Python, jadi API Anda berbagi kode dengan data dan pekerjaan ML Anda. Komponen klien terhidrasi sebagai pulau, bukan pohon React satu halaman penuh.

Halaman Next.js berpindah hampir seperti apa adanya, dan komponen `"use client"` menjadi sebuah pulau di halaman server:

```tsx filename="src/rute/blog/[siput].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/rute/blog/[siput].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | pengontrol yang mengembalikan `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, dengan `async def get(self, slug: str)` |
| `app/layout.tsx` (memiliki `<html>`) | tampilan tata letak yang dibungkus pengontrol di sekeliling tampilannya, melalui `children` |
| `use client` komponen di halaman server | [pulau](../rendering/islands.md) dalam tampilan |
| Pengendali rute `route.ts` | pengontrol yang mengembalikan dict, ditulis dalam Python |
| Tindakan Server | [`@Action`](../guides/actions.md) fungsi dipanggil dari formulir atau seperti fungsi klien yang diketik |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Backendnya adalah Python, sehingga API Anda berbagi kode dengan data dan pekerjaan ML Anda. Komponen klien terhidrasi sebagai pulau, bukan pohon React satu halaman penuh.

Halaman Next.js menjadi pengontrol dan tampilannya, dan komponen `"use client"` menjadi pulau tampilan:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## Dari backend Express atau Node

<!-- router:fbr,custom -->
| Ekspres | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` dengan `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, didaftarkan dari `nexyconfig.py` |
| `res.json(obj)` | mengembalikan dict atau model Pydantic |
| Tampilan EJS / Pug | `.nexy` (Jinja2) halaman |
| `npm run dev` | `nx dev` |

`app.use(...)` menjadi bidang `nexyconfig.py`, dan `res.json(...)` menjadi nilai kembalian:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/rute/pengguna/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| Ekspres | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, dengan `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI middleware, didaftarkan dari `nexyconfig.py` |
| `res.json(obj)` | mengembalikan dict atau model Pydantic |
| Tampilan EJS / Pug | `.nexy` (Jinja2) penayangan, dikembalikan oleh `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` menjadi bidang `nexyconfig.py`, dan `res.json(...)` menjadi nilai kembalian:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## Memilih router

| Gunakan | Kapan |
|---|---|
| Router berbasis file | halaman dan titik akhir dipetakan dari file; bawaannya |
| Perute modular | pengontrol, modul, dan injeksi ketergantungan, bergaya NestJS |

Router modular dalam dua file: pengontrol, dan modul `nexyconfig.py` menunjuk dengan `useRouter = AppModule`:

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

Keduanya di-scaffold oleh `nx new` dan dicakup oleh pengujian end-to-end yang sama. Lihat [Perutean](../routing/README.md) dan [Perutean modular](../routing/modular/README.md).

## Dimana selanjutnya

- [Mulai cepat](quick-start.md): membuat proyek dan menjalankannya
- [Struktur proyek](project-structure.md): tempat setiap file berada
- [Perutean](../routing/README.md): pilih router
