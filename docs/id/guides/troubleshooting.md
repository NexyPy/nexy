# Pemecahan masalah

Masalah yang pertama kali dihadapi orang, dengan apa yang Anda lihat dan apa yang harus dilakukan. Masing-masing berasal dari perjalanan nyata.

## Sebuah halaman menjawab 404 tetapi filenya ada

Lihatlah terminal yang menjalankan `nx dev` atau `nx start`. Ketika halaman tidak dapat diimpor, Nexy melaporkan kesalahan tersebut dengan file dan barisnya, dan rutenya tidak terdaftar:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Perbaiki impor yang disebutkan di sana. Penyebab umum adalah komponen yang nama fungsinya tidak sesuai dengan yang Anda impor (lihat item berikutnya) dan salah ketik jalurnya.

## Halaman `.nexy` tidak dapat dikompilasi: "Logic Parse Error"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

Komponen `.nexy` diimpor sebagai modul Python, jadi nama filenya harus nama yang valid. Tanda hubung tidak. Beri nama dalam PascalCase, `LivePanel.nexy`, dan impor dengan nama yang sama:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## Sebuah komponen merender turunannya sebagai teks `<slot />`

Komponen `.nexy` menempatkan turunannya dengan `<Slot />`, dengan huruf kapital S. Huruf kecil `<slot />` dibiarkan apa adanya di halaman. Vue, yang memiliki `<slot />` sendiri, tidak terpengaruh.

## Prop menunjukkan nama variabel

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

Atribut tanpa kurung kurawal adalah teks. Masukkan ekspresi Jinja ke dalam atribut untuk meneruskan nilai yang dihitung.

## Nilai dalam `{{ ... }}` menjadi kosong

Jinja2 menyembunyikan variabel yang tidak ditentukan. Deklarasikan setiap properti yang Anda gunakan di frontmatter (`title: prop[str] = ""`), dan periksa ejaannya.

## Kelas utilitas tidak berpengaruh di halaman `.nexy` (UnoCSS)

UnoCSS membaca file hanya ketika ekstensinya ada di saluran kontennya. Proyek server yang dibuat oleh `nx new` dengan UnoCSS sudah mencantumkan `.nexy`; yang lebih tua membutuhkannya di `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind menemukan file `.nexy` sendiri.

## Halaman `.mdx` meminta paket

```text
[nexy] MDX support requires optional packages that are not installed.
```

Instal di proyek: `@mdx-js/rollup`, `remark-gfm` dan `@mdx-js/react` (ditambah `@mdx-js/esbuild` untuk `nx build`). MDX membutuhkan React atau Preact di `useFF`. Tanpa kerangka klien, tulis halaman sebagai `.md`. Lihat [Markdown dan MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (atau paket apa pun) saat perintah dimulai

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

Perintahnya salah Python. Paket-paket proyek Anda (ORM Anda, perpustakaan Anda) ada di `.venv`, dan `uvx nexy` atau `nexy` global berjalan di lingkungannya sendiri yang tidak memiliki satu pun paket tersebut.

Aktifkan lingkungan virtual proyek, dari folder proyek, lalu jalankan kembali perintah:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Prompt dimulai dengan `(.venv)` saat aktif. Atau lewati aktivasi dengan `uv run nexy dev`. Jika paket tersebut benar-benar hilang dari proyek, tambahkan dengan `uv add sqlmodel`.

## `nx dev` menunjukkan kesalahan dan menunggu

Ketika aplikasi Anda tidak dapat dijalankan, `nx dev` melaporkan alasannya dan menunggu perubahan file berikutnya; itu tidak keluar. Perbaiki file dan simpan. Hanya Ctrl+C yang menghentikannya.

## Pelabuhan sedang sibuk

`nx dev` mengambil port gratis berikutnya dan mencetaknya. Untuk memilih salah satu, gunakan `--port` atau atur `usePort` di `nexyconfig.py`.

## Tema berkedip putih pada halaman gelap

Tema yang disimpan harus diterapkan sebelum pengecatan pertama. Simpan skrip kecil starter di `<head>` tata letak root, dan letakkan `suppressHydrationWarning` di `<html>` di React.

## Masih macet

- Baca halaman fitur di [indeks dokumentasi](../README.md).
- Jika dokumen dan kode tidak sesuai, maka kodenya benar: silakan buka [masalah](https://github.com/NexyPy/nexy/issues) yang memberi nama pada halaman.
