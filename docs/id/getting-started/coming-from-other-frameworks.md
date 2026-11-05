# Berasal dari kerangka lain

Nexy adalah FastAPI plus perutean berbasis file, halaman yang dirender oleh server, dan pulau opsional React, Vue, Svelte, Solid atau Preact. Halaman ini memetakan apa yang sudah Anda ketahui.

## Dari FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` dalam modul Anda mengimpor fungsi | `GET` di `src/routes/users.py` |
| `app.include_router(router)` | jalur file adalah URL; tidak ada yang perlu didaftarkan |
| Param jalur `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | masih `Depends(...)`: penangan adalah FastAPI penangan |
| Jinja2 `TemplateResponse` | halaman `.nexy` di sebelah titik akhir |
| Jalankan dengan `uvicorn main:app` | `nx dev`, lalu `nx build && nx start` |

Segala sesuatu di bawah `src/routes/*.py` biasa saja FastAPI: dependensi, model Pydantic, middleware, dan `/docs` tetap berfungsi.

## Dari Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` atau `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (memiliki `<html>`) | `src/routes/layout.tsx` dengan `useCSR = True` (React), atau `src/routes/layout.nexy` dalam mode server |
| bersarang `layout.tsx` | bersarang `layout.tsx` / `layout.vue` / `layout.svelte` dalam mode klien, bersarang `layout.nexy` dalam mode server |
| `use client` komponen di halaman server | [pulau](../rendering/islands.md) dalam mode server |
| Penangan rute `route.ts` | `src/routes/api/x.py`, ditulis dalam Python |
| `(group)` folder | sama: `(group)/` |
| Tindakan Server | [`@Action`](../guides/actions.md) fungsi yang dipanggil dari formulir atau seperti fungsi klien yang diketik |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Backendnya adalah Python, sehingga API Anda berbagi kode dengan data dan pekerjaan ML Anda. Komponen klien terhidrasi sebagai pulau, bukan pohon React satu halaman penuh.

## Dari backend Express atau Node

| Ekspres | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` dengan `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, didaftarkan dari `nexyconfig.py` |
| `res.json(obj)` | mengembalikan dict atau Pydantic model |
| Tampilan EJS / Pug | `.nexy` (Jinja2) halaman |
| `npm run dev` | `nx dev` |

## Memilih router

| Gunakan | Saat |
|---|---|
| Router berbasis file | halaman dan titik akhir dipetakan dari file; bawaan |
| Router modular | pengontrol, modul dan injeksi ketergantungan, gaya NestJS |

Keduanya dirangkai oleh `nx new` dan dicakup oleh pengujian end-to-end yang sama. Lihat [Perutean](../routing/README.md) dan [Perutean modular](../routing/modular/README.md).

## Dimana selanjutnya

- [Mulai cepat](quick-start.md): membuat proyek dan menjalankannya
- [Struktur proyek](project-structure.md): tempat setiap file berada
- [Perutean](../routing/README.md): pilih router
