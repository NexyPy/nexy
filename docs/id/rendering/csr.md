# CSR (render sisi klien)

## Definisi

CSR menyerahkan navigasi ke browser: setelah dokumen pertama, berpindah antar halaman tidak lagi meminta HTML dari server. Di Nexy, ini adalah keputusan **proyek**, bukan keputusan halaman pertama - `useCSR = True` mengubah seluruh aplikasi dialihkan ke klien.

## Bagaimana cara kerjanya

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Proyek kemudian berubah bentuk:

| | Mode server (`False`) | Mode klien (`True`) |
|---|---|---|
| Rute | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Dokumen | `layout.nexy` | root `layout.tsx` / `.vue` / `.svelte` memiliki `<html>`, `<head>`, `<body>` |
| Komponen klien | pulau-pulau di dalam halaman | halaman itu sendiri |
| `.nexy` di bawah `src/routes/` | format halaman | ditolak sebelum `nx dev`, `nx start` dan `nx build` |
| Navigasi | permintaan lengkap per link | router klien |

`.md` dan `.mdx` tetap valid: Nexy merendernya di server di dalam tata letak klien, dan router klien mengambil alih dari sana. `.py` penangan duduk di sebelah rute dan dilayani oleh FastAPI.

## Siklus hidup rendering

1. Permintaan tersebut mencapai router berbasis file, yang menemukan rute yang cocok dan tata letaknya.
2. Tata letak root merender **seluruh dokumen** di Node - respons pertama sudah membawa `<html>` asli, bukan shell kosong.
3. Nexy memasukkan aset klien dan deskripsi JSON dari halaman sebelum `</body>`.
4. Browser menghidrasi dokumen itu. Tata letak bersarang mempertahankan statusnya sejak saat itu.
5. Tautan ke rute lain ditangani oleh router klien: tidak ada permintaan dokumen, halaman ditampilkan di browser.

Dalam pengembangan, dokumen tersebut dirender sesuai permintaan oleh server pengembang Vite. Dalam produksi, ia dirender satu kali pada saat build: rute statis mendapatkan dokumennya, rute dinamis mendapatkan satu dokumen per parameter statis yang dideklarasikan, atau shell - tata letak di sekitar halaman kosong - ketika ia menyatakan tidak ada.

## Kapan harus digunakan

- Dasbor, editor, apa pun yang berperilaku seperti aplikasi.
- API Python dengan aplikasi klien di atasnya.
- Halaman di mana setiap interaksi bersifat lokal dan perjalanan pulang pergi akan terasa.

## Konfigurasi

| Pengaturan | Nilai |
|---|---|
| `useFF` | diperlukan: `useCSR` tanpa kerangka klien ditolak |
| `useCSR` | `True` |
| `useRouter` | harus tetap nonaktif: router modular ditolak dalam mode klien |

File dan folder yang dimulai dengan `_` atau `.` diabaikan oleh pemeriksaan ini.

## Contoh

```tsx filename="src/route/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/rute/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Keterbatasan

- **Keseluruhan proyek.** Anda tidak dapat menggabungkan satu halaman CSR ke dalam proyek mode server: pilih mode untuk aplikasi, lalu gunakan [pulau](islands.md) untuk bagian interaktif halaman mode server.
- **Tidak ada rute `.nexy`.** Apa pun yang Anda tulis di `.nexy` harus menjadi komponen kerangka kerja.
- **Data server melewati titik akhir.** Rute klien tidak dapat membaca database pada waktu render; ia memanggil pengendali `.py` atau [Action](../guides/actions.md).
- **Rute dinamis memerlukan param statis yang dideklarasikan, atau dimulai dari shell.** Ekspor `getStaticParams()` dari halaman - nama Next.js `getStaticPaths` dan `generateStaticParams` juga diterima - untuk memiliki satu dokumen per nilai. Tanpanya, shell membawa tata letak dan bukan halaman: halaman muncul setelah browser dijalankan.
- **CSR bukanlah halaman kosong, dan juga bukan SPA.** Dokumen pertama dirender oleh server; itu adalah navigasi yang terjadi di browser.

## Langkah selanjutnya

- [Mode server dan mode klien](../routing/fbr/modes.md): pemeriksaan dan file yang ditolak
- [Layouts](../routing/fbr/layouts/README.md): file mana yang memiliki dokumen
- [SSR](ssr.md): default, halaman demi halaman
- [Frontend](../guides/frontend.md): server pengembang dan build klien
