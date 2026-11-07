# Solid

Nexy merender Solid 1.9 komponen di server, lalu Solid mengambilnya di browser. Halaman, tata letak, pulau, dan tindakan sama di setiap kerangka kerja: halaman ini mencakup penyiapan, lalu bagian-bagian yang berbeda dari [kontrak bersama](../frontend/pages.md).

<!-- router:fbr,custom -->
| Modus | `nexyconfig.py` | Halaman adalah | Solid adalah |
|---|---|---|---|
| Server (bawaan) | `useCSR = False` | `.nexy` file | [pulau](../../rendering/islands.md) di dalam halaman tersebut |
| Klien | `useCSR = True` | `.tsx` file | seluruh halaman, dengan [tata letak](../frontend/layouts.md) dan router klien |
<!-- /router -->

<!-- router:modular -->
Dengan router modular, komponen Solid adalah [pulau](../../rendering/islands.md) di dalam tampilan `.nexy` yang dikembalikan oleh pengontrol: tidak ada file halaman dan tidak ada router klien.
<!-- /router -->

## Mulai sebuah proyek

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-solid
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-solid
```
<!-- /router -->

Templatnya adalah proyek mode server dengan pulau Solid. Jalankan `nx new my-app` tanpa templat untuk menjawab petunjuknya: router, jenis proyek, apakah akan menggunakan perutean sisi klien, lalu kerangka kerja.

## Aktifkan Solid di proyek yang sudah ada

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

Dalam mode klien, tulis `solid({ ssr: true })`: Solid mengkompilasi komponen secara berbeda untuk server dan browser, dan mode klien memerlukan keduanya. `nx new` menulis file ini; Nexy menulis `__nexy__/vite.ts` sendiri, jadi jangan diedit.

| Paket | Versi `nx new` menulis |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (ketergantungan dev) |

## Berpikirlah dalam bentuk sinyal

Fungsi komponen Solid berjalan **sekali**. Perubahan apa yang terjadi kemudian dibaca melalui sinyal, dan hanya ekspresi yang membacanya yang diperbarui:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Panggil sinyal, `count()`, di dalam BEJ, bukan di variabel di atasnya.
- Baca alat peraga sebagai `props.start`. Destrukturisasi `{ start }` membaca nilai satu kali dan kehilangan pembaruan.
- Solid menulis atribut HTML: `class`, `for`, `charset`, bukan `className`.

## Aturan

- **Satu kerangka kerja per proyek.** `useFF` membutuhkan tepat satu kerangka kerja; `useFF = [solid(), react()]` menghentikan server saat startup. Dengan `useFF = solid()`, setiap file `.tsx` adalah Solid.
<!-- router:fbr,custom -->
- **Halaman adalah `.tsx`.** Hanya file `.tsx` di bawah `src/routes/` yang menjadi halaman; `.jsx` baik untuk sebuah komponen.
- **Komponen berada di luar `src/routes/`**, biasanya di `src/components/`, jadi bukan halaman.
- **Proyek mode server tidak memiliki halaman `.tsx`**, dan proyek mode klien tidak memiliki halaman `.nexy`: Nexy menolak untuk memulai dan memberi nama file. Lihat [mode](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Komponen berada di `src/components/`**, dan pandangan mengimpornya sebagai pulau.
<!-- /router -->
- **Tidak ada `.mdx` dengan Solid.** MDX yang dikompilasi menjadi React atau Preact; `.md` halaman berfungsi.

<!-- router:fbr,custom -->
## Halaman

Dalam mode klien (`useCSR = True`), halaman adalah file `.tsx`.

### Komponen halaman

Halaman adalah ekspor default file. Jika tidak ada ekspor default, Nexy memilih ekspor bernama pertama.

```tsx filename="src/rute/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Segmen dinamis

Parameter URL tersedia melalui hook `useParams`, yang mengembalikan pengakses:

```tsx filename="src/rute/blog/[siput].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Tata Letak

### Implementasi

Tata letak root mendefinisikan shell dokumen. Tata letak bersarang membungkus konten.

```tsx filename="src/route/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Jangan merusak struktur `props.children`, karena Solid membacanya dengan malas.
<!-- /router -->

## Pulau

Dalam mode server, komponen Solid yang diimpor ke file `.nexy` adalah sebuah pulau.

### Mengimpor

Impor komponen di frontmatter file `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### Arahan hidrasi

Gunakan prop `directive` untuk mengontrol kapan pulau terhidrasi:

- `client:load` (default): segera
- `client:idle`: saat browser dalam keadaan idle
- `client:visible`: saat bergulir hingga terlihat
- `client:media`: ketika kueri media cocok

## Tindakan dan navigasi

### Memanggil tindakan

Gunakan hook `useAction` untuk mengelola status panggilan tindakan. Di Solid, ini mengembalikan pengakses (sebut saja sebagai fungsi).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navigasi

Gunakan komponen `Link` untuk transisi sisi klien:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Untuk navigasi terprogram, gunakan kait `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Akses URL

Semua pengakses pengembalian kait lokasi:

- `usePathname()`: jalur saat ini
- `useParams()`: segmen dinamis
- `useSearchParams()`: string kueri
- `useLocation()`: objek lokasi penuh

## Langkah selanjutnya

- [Tampilan](../README.md): membandingkan format yang dapat digunakan suatu halaman
- [Frontend](../../guides/frontend.md): Vite dan build klien
