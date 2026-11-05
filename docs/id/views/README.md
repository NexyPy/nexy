# Tampilan

Sebelum memilih format file, penting untuk membedakan antara cara Nexy menangani sumber daya dan cara merendernya.

| Istilah | Definisi |
|---|---|
| **Halaman** | Sumber daya aplikasi yang dapat dialamatkan URL. Ini ditentukan oleh file di bawah `src/routes/`. |
| **View** | Proses menghasilkan isi respons untuk sebuah halaman. Tampilan mengubah logika dan data menjadi HTML atau JSON. |
| **Component** | Blok penyusun UI yang dapat digunakan kembali untuk menyusun tampilan. Komponen dapat berupa pembantu asli Nexy atau khusus kerangka kerja (React, Vue, dll.). |
| **Pengendali rute** | Fungsi Python yang menangani permintaan HTTP untuk metode tertentu (misalnya, `GET`, `POST`). |
| **Endpoint** | Kombinasi unik dari URL dan metode HTTP yang dijawab oleh pengendali rute. |

**Tidak yakin? Tulis file `.nexy`.** Tidak memerlukan kerangka klien, dan Anda dapat menambahkan komponen React, Vue, Svelte, Solid atau Preact di dalamnya nanti, sebagai sebuah pulau.

```diagram filename="File mana untuk halaman mana"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Format

| Format | File | Render server | Kerangka klien | Catatan |
|---|---|---|---|---|
| `.nexy` | [.nexy files](nexy/README.md) | Jinja2 + Python logika, dialirkan | opsional | Format halaman Nexy asli |
| `.md` | [Markdown dan MDX](nexy/markdown.md) | cmarkgfm pada waktu permintaan | opsional melalui tata letak | Murni Markdown, GFM, dibungkus tata letak |
| `.mdx` | [Markdown dan MDX](nexy/markdown.md) | framework SSR | React atau Preact | Markdown dengan komponen |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) atau [Preact](preact/differences.md) | mode klien: kerangka kerja, dirender dalam Node | React, Solid atau Preact | Rute komponen |
| `.vue` | [Vue](vue/differences.md) | mode klien: kerangka kerja, dirender dalam Node | Vue | rute SFC |
| `.svelte` | [Svelte](svelte/differences.md) | mode klien: kerangka kerja, dirender dalam Node | Svelte | Rute SFC |

Pembantu bawaan `Image`, `Link`, `Audio`, `Video` dan `Import`: [Komponen](nexy/components.md).

## Mencampur format

Anda dapat menggabungkan berbagai teknologi dalam proyek yang sama:
- **Pulau**: Anda dapat mengimpor komponen React atau Vue di dalam halaman `.nexy`. Server merender shell, dan framework menghidrasi komponen pada klien.
- **Logika Bersama**: Penangan rute di file `.py` dapat menyediakan data ke halaman dalam format apa pun melalui status aplikasi bersama atau panggilan API.

## Aktifkan kerangka kerja

Atur `useFF` di `nexyconfig.py` dan jalankan `nexy new` untuk menambahkan dependensi:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

Dengan kerangka kerja yang diaktifkan, Vite menangani bundel kliennya. Dalam mode klien, ekstensinya menjadi rute; dalam mode server, file yang sama adalah komponen yang Anda impor sebagai pulau - file kerangka kerja di bawah `src/routes/` ditolak di sana. Lihat [mode server dan mode klien](../routing/fbr/modes.md).

> [!CATATAN]
> dalam mode [CSR](../rendering/csr.md), hanya file rute kerangka kerja yang dapat dinavigasi di sisi klien.

## Tata Letak

A `layout.*` dalam direktori membungkus halaman di bawahnya. Lihat [tata letak](../routing/fbr/layouts/README.md).

## Langkah selanjutnya

- [file .nexy](nexy/README.md): Python + Jinja2 + alat peraga
- [Markdown dan MDX](nexy/markdown.md): halaman konten
- [Komponen](nexy/components.md): pembantu HTML bawaan
