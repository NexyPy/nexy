# React

Nexy merender React 19 komponen di server, lalu React menghidrasinya di browser. Halaman, tata letak, pulau, dan tindakan sama di setiap kerangka kerja: halaman ini mencakup penyiapan, lalu bagian-bagian yang berbeda dari [kontrak bersama](../frontend/pages.md).

| Mode | `nexyconfig.py` | Halaman adalah | React adalah |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` file | [pulau](../../rendering/islands.md) di dalam halaman tersebut |
| Klien | `useCSR = True` | `.tsx` mengarsipkan | seluruh halaman, dengan [layouts](../frontend/layouts.md) dan router klien |

## Mulai sebuah proyek

```bash
nx new my-app --template web-fbr-react
```

Templatnya adalah proyek mode server dengan pulau React. Jalankan `nx new my-app` tanpa templat untuk menjawab petunjuknya: router, jenis proyek, apakah akan menggunakan perutean sisi klien, lalu kerangka kerja.

## Aktifkan React di proyek yang sudah ada

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` menulis file ini; Nexy menulis `__nexy__/vite.ts` sendiri, jadi jangan diedit.

| Paket | Versi `nx new` menulis |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | dependensi pengembang |

## Aturan

- **Satu kerangka kerja per proyek.** `useFF` membutuhkan tepat satu kerangka kerja; `useFF = [react(), vue()]` menghentikan server saat startup.
- **Halaman adalah `.tsx`.** React memiliki `.tsx` dan `.jsx` untuk komponen, tetapi hanya file `.tsx` di bawah `src/routes/` yang menjadi halaman.
- **Komponen berada di luar `src/routes/`**, biasanya di `src/components/`, jadi bukan halaman.
- **Proyek mode server tidak memiliki halaman `.tsx`**, dan proyek mode klien tidak memiliki halaman `.nexy`: Nexy menolak untuk memulai dan memberi nama file. Lihat [mode](../../routing/fbr/modes.md).

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

Tata letak root mendefinisikan shell dokumen. Tata letak bersarang membungkus konten di bawahnya.

```tsx filename="src/route/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## Pulau

Dalam mode server, komponen React yang diimpor ke file `.nexy` adalah sebuah pulau.

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

- `usePathname()`: jalur saat ini
- `useParams()`: segmen dinamis
- `useSearchParams()`: string kueri
- `useLocation()`: objek lokasi penuh

## Langkah selanjutnya

- [Views](../README.md): membandingkan format yang dapat digunakan suatu halaman
- [Frontend](../../guides/frontend.md): Vite dan build klien
