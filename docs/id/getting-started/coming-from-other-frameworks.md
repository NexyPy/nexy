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

## Dari Next.js

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

Backendnya adalah Python, sehingga API Anda berbagi kode dengan data dan pekerjaan ML Anda. Komponen klien terhidrasi sebagai pulau, bukan pohon React satu halaman penuh.

Halaman Next.js berpindah hampir seperti semula, dan komponen `"use client"` menjadi sebuah pulau di halaman server:

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

## Dari backend Express atau Node

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
