# Halaman

File halaman mengembalikan HTML. Jenis file mana yang Anda gunakan akan mengubah cara pembuatannya: lihat [tampilan](../../../views/README.md). Bagian ini mencakup aturan perutean yang berlaku untuk setiap format halaman.

| Halaman | Cakupannya |
|---|---|
| [Rute dinamis](dynamic-routes.md) | `[slug]`, `[...path]`, grup rute, segmen yang diketik |
| [Halaman kesalahan](../errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON untuk klien API |
| [Tata Letak](../layouts/README.md) | Satu halaman per jenis file tata letak |
| [Warisan](../inheritance.md) | Bagaimana tata letak dan dependensi ditumpuk |

## Halaman minimal

```nexy filename="src/rute/tentang.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

Disajikan di `/about`. Materi depan di antara baris `---` adalah Python; markup di bawahnya adalah Jinja2. Lihat [file .nexy](../../../views/nexy/README.md).

## Format halaman

| Mode | File | Menghasilkan |
|---|---|---|
| Server | `.nexy` | HTML yang dirender server dari Python dan Jinja2 |
| Server | `.md`, `.mdx` | halaman konten |
| Komponen kerangka kerja klien | `.tsx`, `.jsx`, `.vue`, `.svelte` | dirender dan dinavigasi di browser |

Kedua mode tersebut tidak dapat digabungkan dalam satu proyek. Lihat [Mode server dan mode klien](../modes.md). Komponen klien masih dapat muncul dalam mode server, sebagai [pulau](../../../rendering/islands.md) di dalam halaman `.nexy`.

## Caching tambahan

Tambahkan `revalidate = 60` ke halaman `.nexy` untuk menyimpannya dalam cache dengan basi-sementara-validasi ulang. Lihat [ISR](../../../rendering/isr.md).

## Membaca permintaan

Sebuah halaman membaca jalur, string kueri, cookie, dan sesi melalui kait. Lihat [Kait](../navigation/hooks.md).

## Langkah selanjutnya

- [Rute dinamis](dynamic-routes.md)
- [Halaman kesalahan](../errors/README.md)
- [Perutean modular](../../modular/README.md): pengontrol, bukan file
