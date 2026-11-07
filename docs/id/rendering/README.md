# Render

Rendering menjawab satu pertanyaan: **siapa yang memproduksi HTML, dan kapan**. Nexy memiliki empat jawaban dan satu default.

**Tidak yakin? Pertahankan SSR.** Ubah halaman hanya jika Anda dapat menyebutkan alasannya: konten yang jarang berubah (ISR), satu widget yang memerlukan browser (pulau), atau navigasi seperti aplikasi (CSR).

<!-- router:modular -->
> [!NOTE]
> Router modular merender setiap tampilan di server, dengan pulau-pulau tempat tampilan menampungnya. ISR dan CSR adalah mode halaman file: mereka memerlukan router berbasis file.
<!-- /router -->

## Bagaimana cara kerjanya

```diagram filename="Siapa yang memproduksi HTML, dan kapan"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Empat mode

| | RSK | ISR | CSR | Pulau |
|---|---|---|---|---|
| Data dibaca | pada setiap permintaan | pada setiap regenerasi | di peramban | pada setiap permintaan |
| HTML berasal dari | server | server, lalu cache | server untuk dokumen pertama, browser setelahnya | server |
| JavaScript | hanya untuk pulau-pulau | hanya untuk pulau-pulau | bundel kerangka | hanya pulau itu |
| Hidrasi | tidak ada | tidak ada | seluruh dokumen | pulau |
| Tembolok | tidak ada | per URL, di memori | tidak ada | tidak ada |
| Diputuskan oleh | bawaan | `revalidate = N` di halaman | `useCSR = True` dalam proyek | `directive` pada komponen |
| Gandum | halaman | halaman | **proyek** | komponen |

## Siklus hidup rendering

Dua fakta menjelaskan sebagian besar kejutan.

1. **Sebuah proyek berada dalam satu mode.** `useCSR` memilih antara mode server (SSR, ISR, pulau, `.nexy`, `.md`, `.mdx` rute) dan mode klien (rute kerangka kerja dan router klien). Keduanya tidak dapat dicampur: lihat [mode server dan mode klien](../routing/fbr/modes.md).
2. **Di dalam mode server, modenya adalah per halaman.** Satu halaman dapat di-cache dengan `revalidate`, halaman lain dapat menampung sebuah pulau, halaman ketiga tidak dapat melakukan keduanya.

Mode klien masih mengirimkan dokumen nyata: Nexy merendernya di Node untuk respons pertama, lalu browser mengambil alih navigasi. Halaman CSR bukanlah halaman kosong yang menunggu bundel.

## Kapan harus digunakan

- **Konten, pemasaran, dokumentasi**: RSK, ditambah ISR ketika konten jarang berubah.
- **Halaman yang sebagian besar statis dengan satu widget interaktif**: SSR dengan sebuah pulau.
- **Dasbor, editor, navigasi seperti aplikasi**: CSR.
- **Halaman dibaca terus-menerus dan jarang diubah**: ISR.

## Konfigurasi

| Modus | Dimana |
|---|---|
| RSK | tidak ada tempat: ini adalah default |
| ISR | `revalidate = 60` di bagian depan halaman `.nexy`. |
| CSR | `useCSR = True` di `nexyconfig.py`, dengan `useFF` disetel |
| Pulau | `directive="client:visible"` pada tag komponen |

## Contoh

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

Halaman yang sama tanpa garis frontmatter adalah SSR.
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Rendered on every request</h1>
<Chart directive="client:visible" />
```

Tampilannya adalah SSR, dan grafiknya adalah pulau yang terhidrasi saat ditampilkan.
<!-- /router -->

## Keterbatasan

- **Tidak ada mode SSG.** Nexy melakukan pra-render HTML pada waktu pembuatan (HTML komponen, dokumen klien), tetapi selalu membacanya kembali melalui server: tidak ada perintah ekspor, tidak ada folder mandiri untuk dihosting secara statis. Untuk konten yang dibekukan, gunakan ISR dengan jendela yang panjang.
- **ISR bukan CDN.** Cache berada dalam proses rendering halaman; beberapa pekerja menyimpan beberapa cache. Lihat [ISR](isr.md).
- **CSR adalah keputusan proyek.** Anda tidak dapat membuat satu halaman CSR dan menyimpan SSR sisanya.
- **Pulau menghidrasi pulau, bukan halamannya.** Halaman yang pulau-pulaunya bergantung satu sama lain adalah halaman CSR yang terselubung.

## Langkah selanjutnya

- [SSR](ssr.md): bawaannya
- [ISR](isr.md): menyimpan halaman per URL dalam cache
- [CSR](csr.md): navigasi tangan ke browser
- [Pulau](islands.md): menghidrasi satu widget
- [Pertunjukan](../deployment/performance.md)
