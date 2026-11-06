# Tata Letak Bagian Depan

**Layout** adalah pembungkus yang mendefinisikan struktur bersama di sekitar satu halaman atau lebih. Tata letak memungkinkan pengalaman "seperti aplikasi" dengan mempertahankan status dan menghindari pemuatan ulang halaman penuh selama navigasi.

## Logika Bersarang

Tata letak mengikuti struktur hierarki berdasarkan pohon direktori di bawah `src/routes/`.

1.  **Tata Letak Akar**: Setiap proyek memiliki tata letak akar (misalnya, `src/routes/layout.nexy`). Ini adalah satu-satunya tata letak yang bertanggung jawab untuk mendefinisikan shell dokumen: `<html>`, `<head>`, dan `<body>`.
2.  **Tata Letak Bersarang**: Folder apa pun dapat berisi file `layout.*` miliknya sendiri. Tata letak ini membungkus semua halaman dan sub-tata letak dalam folder itu.
3.  **Warisan**: Sebuah halaman dibungkus oleh semua tata letak dari akar hingga ke foldernya sendiri.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Tata letak bersarang hanya menggambar bagiannya dari UI dan menempatkan halaman di mana `children` berada:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Keadaan & Komposisi Bersama

Tata letak dirancang agar stabil. Dalam mode klien, saat bernavigasi di antara dua halaman yang berbagi tata letak yang sama, tata letak tersebut **tidak** dirender ulang; hanya konten anak yang berubah. Dalam mode server, setiap navigasi adalah dokumen baru.

- **Slots**: Tata letak menyediakan slot tempat halaman bersarang dimasukkan: `children` di BEJ, dan prop `children` di tata letak `.nexy`.
- **Pelestarian Status**: Karena tata letak tetap terpasang, status apa pun yang ada di dalamnya (misalnya, kueri penelusuran di header) dipertahankan selama navigasi.

Slot yang sama dalam tata letak `.nexy`:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

Bidang pencarian di bawah menyimpan apa yang diketik pengguna saat mereka berpindah antar halaman dasbor, karena tata letak yang menampungnya tidak pernah dilepas:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Batasan Statis

Untuk rute yang telah dirender sebelumnya (SSG), tata letak root tidak dapat bergantung pada data waktu permintaan seperti cookie atau header. Itu harus dapat direpresentasikan sebagai cangkang statis yang kemudian dihidrasi oleh klien.

Baca tema dari browser, dalam skrip shell statis:

```tsx filename="src/route/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Implementasi Kerangka

Penerapan slot dan nesting sedikit berbeda berdasarkan kerangka kerja. Lihat panduan **Perbedaan** untuk teknologi pilihan Anda:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
