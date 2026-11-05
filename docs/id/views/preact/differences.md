# Preact

Nexy merender Preact 10 komponen di server, lalu Preact mengambilnya di browser. Halaman, tata letak, pulau, dan tindakan sama di setiap kerangka kerja: halaman ini mencakup penyiapan, lalu bagian-bagian yang berbeda dari [kontrak bersama](../frontend/pages.md).

| Mode | `nexyconfig.py` | Halaman adalah | Preact adalah |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` file | [pulau](../../rendering/islands.md) di dalam halaman tersebut |
| Klien | `useCSR = True` | `.tsx` mengarsipkan | seluruh halaman, dengan [tata letak](../frontend/layouts.md) dan router klien |

## Mulai sebuah proyek

```bash
nx new my-app --template web-fbr-preact
```

Templatnya adalah proyek mode server dengan pulau Preact. Jalankan `nx new my-app` tanpa templat untuk menjawab petunjuknya: router, jenis proyek, apakah akan menggunakan perutean sisi klien, lalu kerangka kerja.

## Aktifkan Preact di proyek yang sudah ada

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` menulis file ini; Nexy menulis `__nexy__/vite.ts` sendiri, jadi jangan diedit.

| Paket | Versi `nx new` menulis |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (ketergantungan dev) |
| `preact-render-to-string` | `^6.7.0` (ketergantungan dev, dirender di server) |

## Tulis Preact

Komponen Preact adalah fungsi bergaya React. Perbedaan yang penting di sini:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Kait berasal dari `preact/hooks`, tipe seperti `ComponentChildren` dari `preact`.
- Tulis atribut HTML: `class`, `for`, `charset`. `Link` membaca kelasnya dari `class`.

## Aturan

- **Satu kerangka kerja per proyek.** `useFF` membutuhkan tepat satu kerangka kerja; `useFF = [preact(), react()]` menghentikan server saat startup. Dengan `useFF = preact()`, setiap file `.tsx` adalah Preact.
- **Halaman adalah `.tsx`.** Hanya file `.tsx` di bawah `src/routes/` yang menjadi halaman; `.jsx` baik untuk sebuah komponen.
- **Komponen berada di luar `src/routes/`**, biasanya di `src/components/`, jadi bukan halaman.
- **Proyek mode server tidak memiliki halaman `.tsx`**, dan proyek mode klien tidak memiliki halaman `.nexy`: Nexy menolak untuk memulai dan memberi nama file. Lihat [mode](../../routing/fbr/modes.md).
- **Halaman `.mdx` diimpor dari `"preact"`.** Nexy mengkompilasi file `.mdx` dengan Preact hanya ketika ia melihat impor tersebut, misalnya `import { h } from "preact"`, dan dengan React sebaliknya. Lihat [Markdown dan MDX](../nexy/markdown.md).

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

Parameter URL tersedia melalui kait `useParams`:

```tsx filename="src/rute/blog/[siput].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Tata Letak

### Implementasi

Tata letak root mendefinisikan shell dokumen. Tata letak bersarang membungkus konten.

```tsx filename="src/route/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## Pulau

Dalam mode server, komponen Preact yang diimpor ke file `.nexy` adalah sebuah pulau.

### Mengimpor

Impor komponen di frontmatter file `.nexy`:

```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Arahan hidrasi

Gunakan prop `directive` untuk mengontrol kapan pulau terhidrasi:

- `client:load` (default): segera
- `client:idle`: saat browser dalam keadaan idle
- `client:visible`: saat bergulir hingga terlihat
- `client:media`: ketika kueri media cocok

## Tindakan dan navigasi

### Memanggil tindakan

Gunakan hook `useAction` untuk mengelola status panggilan tindakan:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navigasi

Gunakan komponen `Link` untuk transisi sisi klien. Perhatikan bahwa Preact menggunakan `class` alih-alih `className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

Untuk navigasi terprogram, gunakan kait `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Akses URL

- `usePathname()`: jalur saat ini
- `useParams()`: segmen dinamis
- `useSearchParams()`: string kueri
- `useLocation()`: objek lokasi penuh

## Langkah selanjutnya

- [Tampilan](../README.md): membandingkan format yang dapat digunakan suatu halaman
- [Frontend](../../guides/frontend.md): Vite dan build klien
