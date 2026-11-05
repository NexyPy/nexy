# Markdown dan MDX

Dua format untuk halaman konten: `.md` bila Anda hanya memerlukan Markdown, `.mdx` bila Anda memerlukan komponen.

## `.md`: murni Markdown

File `.md` adalah konten murni. Nexy merendernya dengan `cmarkgfm` (GFM), menambahkan ID judul, mendapatkan daftar isi, dan membungkusnya dalam `layout.*` terdekat.

```md filename="src/rute/tentang.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter di `.md` tidak digunakan sebagai logika Python. Jika Anda memerlukan logika server, gunakan `.nexy`.
- Pembungkusan tata letak, halaman kesalahan, dan segmen dinamis bekerja dengan cara yang sama seperti halaman lainnya.

## `.mdx`: Markdown dengan komponen

File `.mdx` dikompilasi oleh **Vite**, melalui pipeline rute kerangka kerja (React atau Preact). Python hanya menulis pembungkus tipis yang melayani rute; itu tidak pernah mengkompilasi atau merender MDX itu sendiri. Komponen dirender oleh kerangka kerja, dirender di server seperti rute komponen lainnya, dan dirender sebelumnya ke HTML oleh `nx build`.

- Membutuhkan `useFF` menjadi React atau Preact.
- Memerlukan paket opsional `@mdx-js/rollup`, `remark-gfm` dan `@mdx-js/react` (dan `@mdx-js/esbuild` untuk build). Vite memberi tahu Anda mana yang hilang.
- Kerangka kerja ini terdeteksi secara otomatis dari impor: Preact ketika file mengimpor `preact`, React sebaliknya.

> [!NOTE]
> gunakan `.nexy` jika Anda memerlukan logika Python di materi depan.

## Langkah selanjutnya

- [.nexy files](README.md): format halaman asli
- [Tampilan](../README.md): pilih format
- [i18n](../../guides/i18n.md): internasionalisasi
