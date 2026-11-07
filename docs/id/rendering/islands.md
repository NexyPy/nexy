# Pulau dan hidrasi

## Definisi

Pulau adalah komponen klien - React, Vue, Svelte, Solid atau Preact - yang diimpor ke halaman `.nexy`. Server merender HTML-nya; browser menjadikan satu komponen itu interaktif. Sisa halamannya tetap HTML.

Pulau ada dalam mode server. Dalam mode klien, komponen *adalah* halaman: lihat [CSR](csr.md).

## Bagaimana cara kerjanya

<!-- router:fbr,custom -->
```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

Nexy merender komponen pada waktu pembuatan, menyimpan HTML-nya, dan menempatkannya di dalam halaman. Respon halaman membawa HTML itu ditambah alat peraga sebagai atribut JSON. Di browser, runtime pulau memuat komponen dan mengambil alih container.

`directive` memutuskan **kapan** itu terjadi. Tanpanya, pulau akan terhidrasi segera setelah waktunya siap.

## Siklus hidup rendering

1. Saat dibangun, setiap komponen klien dirender ke HTML dan ditulis di bawah `__nexy__/client/static/`.
2. Permintaan merender halaman `.nexy`; HTML pulau disisipkan sebagai pengganti tag.
3. Responsnya membawa HTML, props, dan direktif sebagai atribut.
4. Di browser, runtime menjadwalkan hidrasi sesuai dengan arahan.
5. Hidrasi menggantikan HTML statis dengan komponen aktif; sisa halamannya tidak tersentuh.

Dalam pengembangan, tidak ada snapshot build: container kosong dan komponen dirender di browser. Halamannya terlihat sama, tetapi cat pertama berbeda dengan produksi.

## Kapan harus digunakan

- Halaman yang sebagian besar berisi konten dan memiliki satu atau dua tempat interaktif.
- Widget yang harus ada di HTML untuk crawler dan tetap berfungsi.
- Komponen yang memerlukan browser tetapi tidak boleh menyeret seluruh halaman ke dalam rendering klien.

## Konfigurasi

| Petunjuk | Hidrat |
|---|---|
| tidak ada, atau `client:load` | segera |
| `client:idle` | saat browser dalam keadaan idle (`requestIdleCallback`, batas waktu 2 detik) |
| `client:visible` | ketika pulau memasuki viewport, 200 px lebih awal |
| `client:media` | ketika kueri media cocok; atur dengan prop `media` |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` defaultnya adalah `(min-width: 768px)` ketika `media` tidak ada, dan terhidrasi satu kali. Pada browser tanpa `IntersectionObserver`, `client:visible` kembali ke siaga.

`directive` dan `media` digunakan oleh Nexy: keduanya tidak diteruskan ke komponen Anda.

## Contoh

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

<!-- router:fbr,custom -->
```nexy filename="src/rute/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

## Keterbatasan

- **`client:only` tidak pernah terhidrasi.** Diterima, tetapi runtime melewatkannya, sehingga HTML server tetap inert. Gunakan rute klien ([CSR](csr.md)) ketika komponen tidak dapat dirender di server.
- **`client:manual` tidak memiliki pemicu publik.** Ini juga dilewati secara otomatis, dan pegangan yang melanjutkannya bersifat internal.
- **Props harus berupa JSON.** Props tersebut diserialkan dengan `json.dumps`; nilai yang tidak dapat diserialkan akan dihilangkan, dan pulau menerima `{}` - secara diam-diam.
- **Sebuah pulau bukanlah komponen klien dengan negara bersama.** Dua pulau tidak berbagi negara tanpa mekanisme yang Anda tambahkan sendiri.
- **Pulau ini tidak dirender ulang oleh server.** HTML-nya adalah snapshot build, ditambah apa pun yang dilakukan komponen setelah terhidrasi.
- **Halaman pulau adalah halaman CSR yang menyamar.** Jika setiap blok perlu berkomunikasi satu sama lain, pilih mode klien saja.

## Langkah selanjutnya

- [Perenderan](README.md): empat mode
- [Komponen](../views/nexy/components.md): bagaimana halaman `.nexy` mengimpornya
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md)
