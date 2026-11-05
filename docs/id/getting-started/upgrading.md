# Meningkatkan ke 2.2

Perubahan apa yang terjadi pada proyek yang sudah ada saat Anda berpindah dari 2.1 ke 2.2, dan apa yang harus dilakukan untuk mengatasinya. Daftar selengkapnya ada di [catatan perubahan](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## Apa yang mungkin harus Anda ubah

| Ubah | Lakukan ini |
|---|---|
| **`.mdx` dikompilasi oleh Vite saja.** Kompiler Python tidak lagi merendernya | Simpan React atau Preact di `useFF` dan instal `@mdx-js/rollup`, `remark-gfm` dan `@mdx-js/react`. Halaman tanpa komponen dapat menjadi file `.md` sebagai gantinya |
| **`useBadge` hilang.** Tag "Dibangun dengan Nexy" sudah tidak ada lagi | Hapus baris dari `nexyconfig.py`. Baris sisa diabaikan |
| **`nx check` tidak lagi mengkompilasi `.mdx`** | Tidak ada: Vite melaporkan kesalahan MDX pada build |

## Apa yang tetap sama

- Rute, tata letak, tindakan, dan konfigurasi Anda.
- Proyek yang ada memiliki halaman awal sendiri. Desain awal yang baru hanya berlaku untuk proyek yang dibuat setelah peningkatan.
- Toolbar pengembangan dan `useDevTools`.

## Baru di 2.2

- **File agen.** `nx new` menulis `AGENTS.md`, `CLAUDE.md` dan keterampilan untuk agen pengkodean. Untuk proyek yang sudah Anda miliki, jalankan `nx skills`. Itu tidak pernah menimpa file yang Anda tulis. Lihat [Agen pengkodean](../guides/ai-agents.md).
- **Server pengembang yang terus berjalan.** Ketika aplikasi Anda tidak dapat dijalankan, `nx dev` melaporkan alasannya dan menunggu perubahan berikutnya alih-alih keluar.
- **Pemula baru** untuk setiap kerangka kerja di Tailwind atau UnoCSS, dengan halaman dan komponen yang sama.
- **UnoCSS membaca `.nexy` file** dalam proyek server. Jika Anda menggunakan UnoCSS dengan halaman `.nexy`, tambahkan blok `content` yang ditunjukkan di [Pemecahan Masalah](../guides/troubleshooting.md).

## Dokumentasi yang diperbaiki

Tiga halaman mengatakan sesuatu yang tidak dilakukan kode tersebut. Jika Anda mengikutinya, periksa file Anda:

- Komponen `.nexy` menempatkan turunannya dengan `<Slot />` (huruf kapital S), bukan `<slot />`.
- File komponen `.nexy` diberi nama dalam PascalCase: diimpor sebagai modul Python, sehingga tanda hubung tidak dapat dikompilasi.
- Untuk `.mdx`, kerangka kerjanya adalah Preact ketika file mengimpor `preact`, React sebaliknya.

## Dimana selanjutnya

- [Indeks dokumentasi](../README.md): halaman untuk apa yang sedang Anda buat
- [Pemecahan masalah](../guides/troubleshooting.md): masalah yang pertama kali dihadapi orang
- [Konfigurasi](../reference/config.md): setiap kolom `use*` dan defaultnya
