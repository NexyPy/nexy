# Mode server dan mode klien

Proyek Nexy dapat berupa **dirender server** atau **dirutekan klien**, seperti proyek Next.js yang merupakan halaman yang dirender di server atau aplikasi klien. `useCSR` di `nexyconfig.py` memilih.

## Modus server (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Halaman adalah file `.nexy`, `.md` atau `.mdx` di bawah `src/routes/`.
- Akar `layout.nexy` memiliki `<!DOCTYPE html>`, `<html>`, `<head>` dan `<body>`.
- Komponen klien (React, Vue, Svelte, Solid atau Preact) diizinkan sebagai **pulau**: Anda mengimpor satu dari halaman `.nexy` dan komponen tersebut terhidrasi di browser. Lihat [Pulau](../../rendering/islands.md).
- Komponen klien tidak pernah menjadi rute. Simpan di `src/components/`.
- Satu kerangka klien pada satu waktu.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Mode klien (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Halaman adalah file kerangka klien Anda: `.tsx` untuk React, `.vue`, `.svelte`.
- File `.md` dan `.mdx` tetap memiliki rute yang valid: Nexy merendernya di server di dalam tata letak klien, dan router klien mengambil alih navigasi dari sana.
- Tata letak akar kerangka apa pun (`layout.tsx`, `layout.vue`, `layout.svelte`) memiliki `<!DOCTYPE html>`, `<html>`, `<head>` dan `<body>`, seperti tata letak akar dari Next.js Router Aplikasi. Nexy merendernya di Node untuk respons pertama dan kerangka kerja tersebut menghidrasi seluruh dokumen. Lihat [tata letak.tsx](../../views/react/differences.md).
- File `.py` adalah penangan API yang dilayani oleh FastAPI, di sebelah rute klien.
- Tidak ada file `.nexy` sama sekali, dan tidak ada `layout.nexy`.
- Navigasi antar halaman terjadi di browser.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## Apa yang ditolak

Nexy memeriksa proyek sebelum `nx dev`, `nx start` dan `nx build` dan berhenti dengan daftar file:

| Mode | Ditolak | Pesan |
|---|---|---|
| server | `.tsx`, `.jsx`, `.vue` atau `.svelte` di bawah `src/routes/` | memindahkan komponen ke `src/components/`, atau mengatur `useCSR = True` |
| klien | file `.nexy` apa pun di bawah `src/routes/` | tuliskan sebagai komponen kerangka kerja, atau setel `useCSR = False` |
| keduanya | lebih dari satu kerangka frontend di `useFF` | `useFF must configure exactly one frontend framework` |
| klien | `useRouter` (router modular) | `useCSR requires file-based routing` |
| klien | tidak ada `useFF` | `useCSR requires a client framework` |

File dan folder yang dimulai dengan `_` atau `.` diabaikan oleh pemeriksaan ini.

## Yang mana

- **Konten, pemasaran, dokumen, situs yang mengutamakan SEO**: mode server dengan pulau.
- **Dasbor dan aplikasi dengan navigasi klien yang kaya**: mode klien.
- **API Python dengan aplikasi klien di atas**: mode klien, dengan penangan `.py` di sebelah halaman.

## Langkah selanjutnya

- [Tata Letak](layouts/README.md)
- [Render](../../rendering/README.md)
- [Konfigurasi](../../reference/config.md)
