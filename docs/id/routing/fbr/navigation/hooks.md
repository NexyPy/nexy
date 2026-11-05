# Kait

Hooks membaca permintaan HTTP saat ini dari dalam halaman `.nexy`, pengendali API, atau pengontrol modular. Nama mereka cocok dengan kait router klien (`@nexy/client`) tempat mereka melakukan hal yang sama.

> [!NOTE]
> kait hanya berfungsi saat permintaan sedang ditangani. Memanggil seseorang ke tempat lain akan memunculkan `RuntimeError`.

## Kaitnya

| Kait | Mengembalikan |
|---|---|
| `usePathname()` | jalur permintaan, mis. `"/blog/post-1"` |
| `useSearchParams()` | string kueri sebagai `dict[str, str]`, nilai pertama per kunci |
| `useParams()` | parameter jalur dinamis, mis. `{"slug": "post-1"}` |
| `useQuery()` | nama asli `useParams()`, disimpan untuk halaman yang ada |
| `useRequest()` | permintaan Starlette, yang tidak tercakup dalam kait lainnya |
| `useHeaders()` | header permintaan sebagai `dict[str, str]`, nama dalam huruf kecil |
| `useUrl()` | URL lengkap: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | apakah `href` adalah halaman saat ini atau salah satu halaman induknya |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | semua cookie sebagai `dict[str, str]` |
| `useSession()` | dict sesi, `{}` ketika sesi tidak diaktifkan |
| `useToc(depth_range="2-6")` | daftar isi HTML untuk halaman saat ini, `""` bila tidak ada |
| `useViews(path, context=None)` | merender tampilan lain dan mengembalikan `HTMLResponse` |

## Baca permintaannya

```nexy filename="src/rute/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Tautan aktif di bilah navigasi

`useIsActive` mengikuti aturan yang sama seperti pada klien: string kueri, fragmen, dan garis miring di akhir diabaikan, tautan ke induk aktif pada turunannya kecuali `exact` disetel, dan `/` hanya aktif di `/`.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Catatan

- `useQuery()` mengembalikan parameter **path**, bukan string kueri, itulah sebabnya `useParams()` ada. String kuerinya adalah `useSearchParams()`.
- `useRouter()` ini kait permintaannya. Bukan kolom konfigurasi `useRouter` yang memasang `APIRouter`.
- `useSession()` membutuhkan `useSession = {...}` di `nexyconfig.py`; tanpanya dict tersebut kosong.
- `useViews("about.tsx", {"title": "About"})` mengembalikan HTML: tampilan `.nexy` dirender oleh modul yang dikompilasi, tampilan `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` menjadi wadah pemasangan klien.

## Langkah selanjutnya

- [Halaman](../pages/README.md): segmen dan tata letak dinamis
- [Resep](../../../guides/recipes.md): alur masuk teruji yang dibangun di `useSession()`
- [Config](../../../reference/config.md): mengaktifkan sesi dan lokal
- [.nexy files](../../../views/nexy/README.md): tempat kait biasanya dipanggil
