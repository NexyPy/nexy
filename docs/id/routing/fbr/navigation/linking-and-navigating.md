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

| Prop | Arti |
|---|---|
| `href` | Rute proyek (salah ketik adalah kesalahan ketik), opsional dengan `?query` atau `#fragment`, atau URL eksternal. |
| `replace` | Ganti entri riwayat alih-alih menambahkannya. |
| `scroll` | `false` mempertahankan posisi gulir setelah bernavigasi. Bawaan: `true`. |
| `prefetch` | `'intent'` (default) memuat halaman saat mengarahkan kursor, fokus, atau menyentuh; `'viewport'` ketika tautan bergulir hingga terlihat; `false` tidak pernah. |
| `activeClassName` | Ditambahkan ke kelas sementara tautan menunjuk ke halaman saat ini atau halaman di bawahnya (`activeClass` di Vue dan Svelte). |
| `exact` | Aktif hanya pada halaman yang tepat. |

Tautan yang mengarah ke halaman saat ini juga mendapat `aria-current="page"`.

## Kait

Lokasi tersedia di setiap framework, dalam idiom framework tersebut. Selama tahap pertama, sisi server merender jawaban kait dengan URL permintaan, sehingga halaman terhidrasi tanpa ketidakcocokan.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Jalur | `usePathname()` | `usePathname()` mengembalikan pengakses | `usePathname()` mengembalikan ref | `$pathname` penyimpanan |
| Param rute | `useParams()` | `useParams()` pengakses | `useParams()` ref | `$params` penyimpanan |
| Kueri | `useSearchParams()` | `useSearchParams()` pengakses | `useSearchParams()` ref | `$searchParams` penyimpanan |
| Semuanya | `useLocation()` | `useLocation()` pengakses | `useLocation()` ref | `$location` menyimpan |
| Navigasi | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

Kuerinya adalah `URLSearchParams`. `useRouter()` dan `router` memberikan `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` dan `prefetch(href)`; `push` dan `replace` menerima `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

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
- `priority` memuat gambar sekarang dengan prioritas tinggi, untuk gambar yang terlihat pada saat kedatangan.
- `fill` membuat gambar menutupi induk posisinya, mengabaikan `width` dan `height`.
- `sizes` dan `srcSet` melewatinya. Nexy tidak mengubah ukuran atau mengonversi gambar.

## Tautan dari halaman `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` merender `<a href="/about" data-nexy-link="true">`. Setiap atribut dan `href` lolos dari HTML.

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
