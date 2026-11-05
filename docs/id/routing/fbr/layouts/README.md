# Tata Letak

Tata letak membungkus setiap halaman di bawah direktorinya. Sarang tata letak: halaman dirender di dalam tata letak direktorinya, yang dirender di dalam tata letak direktori induk, hingga tata letak akar.

Ada satu halaman per jenis file tata letak:

| File | Mode | Memiliki dokumen HTML | Halaman |
|---|---|---|---|
| `layout.nexy` | server (`useCSR = False`) | ya, di root | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | klien (`useCSR = True`) | ya, di root (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | klien | ya, di root | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | klien | ya, di root | [layout.svelte](../../../views/svelte/differences.md) |

Sebuah proyek menggunakan satu keluarga. `layout.nexy` dan `layout.tsx` tidak dapat hidup dalam proyek yang sama: mode server memiliki tata letak `.nexy` dan mode klien memiliki tata letak kerangka kerja. Lihat [Mode server dan mode klien](../modes.md).

## Bagaimana browser mengambil alih dokumen

Dalam mode klien, Nexy merender tata letak root di Node, sehingga respons pertama adalah dokumen lengkap. Browser kemudian mengambil alihnya dengan salah satu dari dua cara berikut:

| Kerangka | Pengambilalihan | Apa artinya |
|---|---|---|
| React, Solid | **hidrasi** seluruh dokumen | HTML server digunakan kembali sebagaimana adanya |
| Preact, Vue, Svelte | **pengambilalihan tubuh** | kerangka kerja membangun badan halaman dan menukarnya dengan yang dikirim server |

Preact, Vue dan Svelte tidak dapat menghidrasi seluruh dokumen: `hydrate` Preact membuat elemen `<html>` kedua, kompiler Vue menjatuhkan `<script>` dari templat klien, dan Svelte tidak dapat membuat `<html>`, `<head>` atau `<body>` di browser. Jadi bagi mereka atribut `<html>`, `<head>` dan `<body>` adalah yang dikirim oleh server, dan hanya isi yang dibuat oleh browser. Dalam praktiknya:

- Letakkan judul, tag meta, font, dan skrip tema di tata letak root: semuanya dirender oleh server dan tetap apa adanya.
- Pengikatan pada `<html>`, `<head>` atau `<body>` (misalnya kelas reaktif) diterapkan oleh server tetapi tidak diperbarui di browser. Ubahlah dari skrip, seperti yang dilakukan skrip tema.
- Browser merender isi dari awal alih-alih menggunakan kembali markup server, sehingga isi diganti satu kali, dalam tugas yang sama seperti render pertama.

## Tata letak akar

Tata letak root adalah `src/routes/layout.<ext>`. Itu dibuat oleh `nx new` dan merupakan satu-satunya tempat yang menulis `<!DOCTYPE html>`, `<html>`, `<head>` dan `<body>` (setiap kerangka dan `.nexy`). Halaman dan tata letak bersarang tidak pernah mengulanginya.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` diterjemahkan sebagai `root layout > dashboard layout > page`.

## Grup rute

Direktori dalam tanda kurung dapat memiliki tata letaknya sendiri tanpa mengubah URL:

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## Kegigihan

Dalam mode klien, tata letak tetap terpasang saat pengguna bernavigasi di antara halaman-halaman yang membagikannya: DOM, status, dan posisi gulirnya dipertahankan. Dalam mode server, setiap navigasi adalah dokumen baru.

## Langkah selanjutnya

- [tata letak.nexy](../../../views/nexy/layouts.md)
- [tata letak.tsx](../../../views/react/differences.md)
- [Warisan](../inheritance.md)
