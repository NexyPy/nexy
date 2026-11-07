# Vue

Nexy merender Vue 3 komponen file tunggal di server, lalu Vue mengambil alihnya di browser. Halaman, tata letak, pulau, dan tindakan sama di setiap kerangka kerja: halaman ini mencakup penyiapan, lalu bagian-bagian yang berbeda dari [kontrak bersama](../frontend/pages.md).

<!-- router:fbr,custom -->
| Modus | `nexyconfig.py` | Halaman adalah | Vue adalah |
|---|---|---|---|
| Server (bawaan) | `useCSR = False` | `.nexy` file | [pulau](../../rendering/islands.md) di dalam halaman tersebut |
| Klien | `useCSR = True` | `.vue` file | seluruh halaman, dengan [tata letak](../frontend/layouts.md) dan router klien |
<!-- /router -->

<!-- router:modular -->
Dengan router modular, komponen Vue adalah [pulau](../../rendering/islands.md) di dalam tampilan `.nexy` yang dikembalikan oleh pengontrol: tidak ada file halaman dan tidak ada router klien.
<!-- /router -->

## Mulai sebuah proyek

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-vue
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-vue
```
<!-- /router -->

Templatnya adalah proyek mode server dengan pulau Vue. Jalankan `nx new my-app` tanpa templat untuk menjawab petunjuknya: router, jenis proyek, apakah akan menggunakan perutean sisi klien, lalu kerangka kerja.

## Aktifkan Vue di proyek yang sudah ada

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` menulis file ini; Nexy menulis `__nexy__/vite.ts` sendiri, jadi jangan diedit.

| Paket | Versi `nx new` menulis |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## Aturan

- **Satu kerangka kerja per proyek.** `useFF` membutuhkan tepat satu kerangka kerja; `useFF = [vue(), react()]` menghentikan server saat startup.
- **Satu komponen per file.** File `.vue` mengekspor komponennya sebagai default; nama yang Anda impor hanyalah tag yang Anda tulis.
<!-- router:fbr,custom -->
- **Komponen berada di luar `src/routes/`**, biasanya di `src/components/`, jadi bukan halaman.
- **Proyek mode server tidak memiliki halaman `.vue`**, dan proyek mode klien tidak memiliki halaman `.nexy`: Nexy menolak untuk memulai dan memberi nama file. Lihat [mode](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Komponen berada di `src/components/`**, dan pandangan mengimpornya sebagai pulau.
<!-- /router -->

<!-- router:fbr,custom -->
## Halaman

Dalam mode klien (`useCSR = True`), halaman adalah file `.vue`.

### Komponen halaman

Halaman adalah komponen yang ditentukan oleh blok `<script setup>`.

```vue filename="src/rute/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### Segmen dinamis

Parameter URL mencapai halaman sebagai alat peraga. Anda dapat mendeklarasikannya menggunakan `defineProps`:

```vue filename="src/rute/blog/[siput].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

Alternatifnya, gunakan kait `useParams` dari `@nexy/client` di komponen mana pun.

## Tata Letak

### Implementasi

Tata letak root mendefinisikan shell dokumen. Tata letak bersarang membungkus konten dalam slot defaultnya.

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```
<!-- /router -->

## Pulau

Dalam mode server, komponen Vue yang diimpor ke file `.nexy` adalah sebuah pulau.

### Mengimpor

Impor komponen di frontmatter file `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.vue" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.vue" import Counter
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

Gunakan hook `useAction` untuk mengelola status panggilan tindakan. Di Vue, status yang dikembalikan (`pending`, `data`, `error`) adalah referensi yang dihitung.

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### Navigasi

Gunakan komponen `Link` untuk transisi sisi klien:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

Untuk navigasi terprogram, gunakan kait `useRouter`:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### Akses URL

Semua kait lokasi mengembalikan referensi yang dihitung:

- `usePathname()`: jalur saat ini
- `useParams()`: segmen dinamis
- `useSearchParams()`: string kueri
- `useLocation()`: objek lokasi penuh

## Langkah selanjutnya

- [Tampilan](../README.md): membandingkan format yang dapat digunakan suatu halaman
- [Frontend](../../guides/frontend.md): Vite dan build klien
