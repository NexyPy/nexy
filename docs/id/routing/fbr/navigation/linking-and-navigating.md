# Menghubungkan dan menavigasi

Dengan perutean klien (`useCSR = True`), tautan antara dua halaman akan menukar halaman di browser alih-alih memuat ulang dokumen. Tata letaknya mempertahankan statusnya.

## Tautan biasa sudah berfungsi

Setiap `<a href>` ke halaman proyek Anda bernavigasi di klien, tanpa komponen dan tanpa penanda:

```html
<a href="/about">About</a>
```

Tautan diserahkan ke browser, dan memuat halaman secara normal, ketika:

- tombol pengubah ditahan, atau tombol tersebut bukan tombol utama;
- memiliki `target` (selain `_self`), `download`, `rel="external"` atau `data-nexy-reload`;
- `href` adalah asal lain, tautan `mailto:` atau `tel:`, atau hanya `#fragment`;
- jalurnya tidak cocok dengan rute klien, sehingga server menjawabnya.

## `Link`

`Link` adalah jangkar yang sama dengan apa yang tidak bisa dilakukan oleh jangkar biasa: `href`-nya dicentang berdasarkan rute Anda, menghangatkan halaman target, dan mengetahui kapan ia menunjuk ke halaman saat ini. Nexy menghasilkan `Link` kerangka kerja Anda di `__nexy__/src` ketika Anda menjalankan `nx dev` atau `nx build`.

| Kerangka | Impor |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Prop | Artinya |
|---|---|
| `href` | Rute proyek (salah ketik adalah kesalahan ketik), opsional dengan `?query` atau `#fragment`, atau URL eksternal. |
| `replace` | Ganti entri riwayat alih-alih menambahkannya. |
| `scroll` | `false` mempertahankan posisi gulir setelah bernavigasi. Bawaan: `true`. |
| `prefetch` | `'intent'` (default) memuat halaman saat mengarahkan kursor, fokus, atau menyentuh; `'viewport'` ketika tautan bergulir hingga terlihat; `false` tidak pernah. |
| `activeClassName` | Ditambahkan ke kelas saat tautan menunjuk ke halaman saat ini atau halaman di bawahnya (`activeClass` di Vue dan Svelte). |
| `exact` | Aktif hanya pada halaman yang tepat. |

Tautan yang mengarah ke halaman saat ini juga mendapat `aria-current="page"`.

## Kait

Lokasi tersedia di setiap framework, dalam idiom framework tersebut. Selama tahap pertama, sisi server merender jawaban kait dengan URL permintaan, sehingga halaman terhidrasi tanpa ketidakcocokan.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Jalan | `usePathname()` | `usePathname()` mengembalikan pengakses | `usePathname()` mengembalikan referensi | `$pathname` toko |
| Parameter rute | `useParams()` | `useParams()` pengakses | `useParams()` rujukan | `$params` toko |
| Pertanyaan | `useSearchParams()` | `useSearchParams()` pengakses | `useSearchParams()` rujukan | `$searchParams` toko |
| Semuanya | `useLocation()` | `useLocation()` pengakses | `useLocation()` rujukan | `$location` toko |
| Navigasi | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Navigasi dalam penerbangan | `useTransition()` | `useTransition()` pengakses | `useTransition()` referensi | `useTransition()` toko |
| Cocokkan jalan | `useMatch(path?)` | `useMatch(path?)` pengakses | `useMatch(path?)` rujukan | `useMatch(path?)` toko |
| Tanyakan sebelum pergi | `useBlocker(dirty)` | `useBlocker(dirty())` di `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` di `$effect` |

Kuerinya adalah `URLSearchParams`. `useRouter()` dan `router` menghasilkan `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` dan `prefetch(href)`; `push` dan `replace` menerima `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## Tampilkan status pemuatan dengan `useTransition`

`useTransition()` memberitahukan apakah navigasi klien sedang dalam penerbangan. `pending` adalah `true` dari klik hingga halaman berikutnya ditampilkan, dan `next` adalah lokasi yang dituju. Ini kembali ke `{ pending: false, next: null }` setelah halaman ditampilkan, saat navigasi berhenti, atau saat ada halaman baru yang menggantikannya.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Cocokkan jalur dengan `useMatch`

`useMatch(path)` memberitahukan apakah `path` cocok dengan rute klien. Ia mengembalikan `{ match, found }`, di mana `match` memegang rute `file`, `layouts` dan `params`, atau `null`. Tanpa jalur, itu cocok dengan halaman saat ini dan mengikuti setiap navigasi. Saat server render belum ada router, jadi `match` adalah `null` dan `found` adalah `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Tangkap halaman yang gagal dengan `ErrorBoundary`

`ErrorBoundary` menampilkan fallback alih-alih turunannya ketika salah satu dari mereka melempar saat dirender di browser. Fallback menerima kesalahan dan `reset`, yang merender turunan lagi.

| Kerangka | Impor | Penggantian |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | fungsi `fallback` prop; anak-anak masuk ke slot default |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | cuplikan `fallback` |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

Itu tidak menangkap:

- kesalahan yang muncul kemudian, dalam pengendali peristiwa, pengatur waktu, atau janji: tangkap di tempat terjadinya. Vue adalah pengecualian untuk pengendali kejadiannya sendiri, yang kesalahannya mencapai batas;
- halaman yang tidak dapat dimuat oleh router: browser malah memintanya ke server (lihat [Apa yang dilakukan router](#what-the-router-does)).

## Tanyakan sebelum meninggalkan halaman dengan perubahan yang belum disimpan

`useBlocker(dirty, message?)` bertanya kepada pengunjung sebelum mereka pergi sementara `dirty` benar: tautan, `router.push`, tombol mundur dan maju, muat ulang, dan tab tertutup. Navigasi klien menunjukkan `message` di `confirm()`: ya terus, tidak ada yang tetap di halaman. Tab yang dimuat ulang atau ditutup menunjukkan pertanyaan browser itu sendiri, yang tidak dapat diungkapkan oleh halaman mana pun. Tanpa pesan, pertanyaannya adalah "Anda memiliki perubahan yang belum disimpan. Tinggalkan halaman ini?".

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

Bendera dibaca di tempat yang berubah, dalam idiom setiap kerangka:

| Kerangka | Ikuti benderanya |
|---|---|
| React, Preact | `useBlocker(dirty)` pada setiap render |
| Vue | `useBlocker(dirty)` dengan `dirty` ref atau dihitung |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` juga mengambil fungsi, untuk keputusan yang bergantung pada kemana pengunjung pergi. Ia menerima lokasi berikutnya dan lokasi saat ini, dan mengembalikan alasan (string) untuk tetap tinggal, atau tidak melanjutkan apa pun:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Suatu fungsi tidak bertanya dengan sendirinya dan tidak memuat ulang; panggil `confirm()` di dalamnya untuk bertanya.

## `Image`

`Image` merender `<img>` yang malas secara default dan tidak mengubah tata letak saat ukurannya diketahui.

| Kerangka | Impor |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` diperlukan; gunakan `alt=""` untuk gambar dekoratif. Nexy memperingatkan sekali jika hilang.
- Dengan `width` dan `height`, atribut memberikan rasio aspek pada browser dan gambar tetap lancar (`height: auto; max-width: 100%`).
- `priority` sekarang memuat gambar dengan prioritas tinggi, untuk gambar yang terlihat saat tiba.
- `fill` membuat gambar menutupi posisi induknya, mengabaikan `width` dan `height`.
- `sizes` dan `srcSet` melewatinya. Nexy tidak mengubah ukuran atau mengonversi gambar.

## Tautan dari halaman `.nexy`.

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` menerjemahkan `<a href="/about" data-nexy-link="true">`. Setiap atribut dan `href` di-escape dengan HTML.

## Apa yang dilakukan router

Pada navigasi, router:

1. mencocokkan jalur dengan rute klien (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. mengimpor dan merender halaman dan [tata letak](../layouts/README.md) **pertama**, dan baru kemudian memindahkan URL dengan `history.pushState`, sehingga bilah alamat tidak pernah menampilkan halaman yang gagal;
3. mengirimkan acara `nexy:navigated` pada `document`;
4. bergulir ke atas, atau ke target `#fragment`.

Navigasi yang lebih baru membatalkan navigasi lama yang masih dirender. Jika halaman tidak dapat dirender, browser akan meminta halaman tersebut ke server. Tombol mundur dan maju merender halaman entri tersebut dan memulihkan posisi gulirnya.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

Router hanya dimulai dalam proyek dengan rute klien, sehingga proyek yang dirender oleh server tetap menggunakan tombol kembali dan pemulihan gulir browser.

## Langkah selanjutnya

- [Tata Letak](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Komponen](../../../views/nexy/components.md)
