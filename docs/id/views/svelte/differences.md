# Svelte

Nexy merender Svelte 5 komponen di server, lalu Svelte mengambilnya di browser. Halaman, tata letak, pulau, dan tindakan sama di setiap kerangka kerja: halaman ini mencakup penyiapan, lalu bagian-bagian yang berbeda dari [kontrak bersama](../frontend/pages.md).

| Mode | `nexyconfig.py` | Halaman adalah | Svelte adalah |
|---|---|---|---|
| Server (default) | `useCSR = False` | `.nexy` file | [pulau](../../rendering/islands.md) di dalam halaman tersebut |
| Klien | `useCSR = True` | `.svelte` mengarsipkan | seluruh halaman, dengan [layouts](../frontend/layouts.md) dan router klien |

## Mulai sebuah proyek

```bash
nx new my-app --template web-fbr-svelte
```

Templatnya adalah proyek mode server dengan pulau Svelte. Jalankan `nx new my-app` tanpa templat untuk menjawab petunjuknya: router, jenis proyek, apakah akan menggunakan perutean sisi klien, lalu kerangka kerja.

## Aktifkan Svelte di proyek yang sudah ada

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` menulis file ini; Nexy menulis `__nexy__/vite.ts` sendiri, jadi jangan diedit.

| Paket | Versi `nx new` menulis |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## Aturan

- **Svelte 5.** Komponen menggunakan rune: `$props()`, `$state()`, dan cuplikan untuk anak-anak.
- **Satu kerangka kerja per proyek.** `useFF` membutuhkan tepat satu kerangka kerja; `useFF = [svelte(), vue()]` menghentikan server saat startup.
- **Satu komponen per file.** Nama file `.svelte` yang Anda impor hanyalah tag yang Anda tulis.
- **Komponen berada di luar `src/routes/`**, biasanya di `src/components/`, jadi bukan halaman.
- **Proyek mode server tidak memiliki halaman `.svelte`**, dan proyek mode klien tidak memiliki halaman `.nexy`: Nexy menolak untuk memulai dan memberi nama file. Lihat [mode](../../routing/fbr/modes.md).

## Halaman

Dalam mode klien (`useCSR = True`), halaman adalah file `.svelte`.

### Komponen halaman

Halaman adalah komponen yang ditentukan oleh blok skrip file `.svelte`.

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### Segmen dinamis

Parameter URL mencapai halaman sebagai props melalui rune `$props()`:

```svelte filename="src/rute/blog/[siput].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

Alternatifnya, gunakan penyimpanan `$params` dari `@nexy/client` di komponen mana pun.

## Tata Letak

### Implementasi

Tata letak root mendefinisikan shell dokumen. Tata letak bertingkat membungkus konten menggunakan cuplikan `children`.

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## Pulau

Dalam mode server, komponen Svelte yang diimpor ke file `.nexy` adalah sebuah pulau.

### Mengimpor

Impor komponen di frontmatter file `.nexy`:

```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.svelte" import Counter
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

Gunakan hook `useAction` untuk mengelola status panggilan tindakan. Di Svelte, ini mengembalikan toko (dibaca dengan `$`).

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### Navigasi

Gunakan komponen `Link` untuk transisi sisi klien:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

Untuk navigasi terprogram, gunakan objek `router` dari `@nexy/client`:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### Akses URL

Semua data lokasi disediakan sebagai penyimpanan:

- `$pathname`: jalur saat ini
- `$params`: segmen dinamis
- `$searchParams`: string kueri
- `$location`: objek lokasi penuh

## Langkah selanjutnya

- [Views](../README.md): membandingkan format yang dapat digunakan suatu halaman
- [Frontend](../../guides/frontend.md): Vite dan build klien
