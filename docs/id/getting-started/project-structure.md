# Struktur proyek

Setiap file dalam proyek Nexy memiliki satu pekerjaan. Halaman ini mengatakan yang mana.

## Tingkat atas

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Untuk memilih folder, tanyakan file apa itu:

- **Sesuatu yang dapat dibuka oleh browser** - rute: `src/routes/`.
- **Sepotong yang digunakan oleh beberapa rute** - komponen atau modul: `src/components/`, `src/`.
- **File disajikan apa adanya** - `public/`.
- **Pengontrol router modular** - `src/apps/`.
- **Dihasilkan** - `__nexy__/`; jangan pernah mengeditnya.

> [!WARNING]
> `src/routes/` dipindai: pembantu yang ditempatkan di sana menjadi rute. Letakkan helper yang bukan merupakan rute di luar `src/routes/`, atau awali namanya dengan `_`.

## `src/routes/`

Setiap file menjadi rute, kecuali nama yang dicadangkan di bawah. Jalur file tanpa ekstensi adalah URL - lihat [routing](../routing/README.md).

| File | Peran |
|---|---|
| `layout.nexy` | membungkus halaman saudara dan anak |
| `errors.nexy` | 500 halaman untuk direktori |
| `notfound.nexy` | 404 halaman untuk direktori |
| `dependencies.py` | berbagi FastAPI dependensi untuk direktori |
| `__init__.py` | Python penanda paket |
| `loading.nexy` | dicadangkan - dikecualikan dari rute, namun belum memiliki efek runtime |

Setiap nama halaman juga ada per kerangka. Dengan `react()` dikonfigurasi, `layout.jsx` dan `layout.tsx` dicadangkan persis seperti `layout.nexy`. Daftar dibuat di `nexy/core/config.py` (`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` dan `errors.nexy` hanya diinstal ketika salinan ada di root rute. Salinan dalam subdirektori kemudian menyaring halaman untuk awalan tersebut.

## `src/apps/`

Direktori `nexy new` digunakan untuk router modular: pengontrol, modul, dan penyedia mendaftarkan rute mereka melalui dekorator dari `nexy.decorators`, kemudian agregat `APIRouter` dipasang dengan `useRouter` di `nexyconfig.py`.

Sebuah proyek dapat memiliki kedua router: `useRouter` memasang router modular, dan `src/routes/` dipindai setiap kali direktori tersebut ada. Lihat [perutean modular](../routing/modular/README.md).

## `public/`

File di sini disajikan dari root situs: `/favicon.ico`, `/robots.txt`, gambar, font.

## `__nexy__/`

Dihasilkan oleh `nx build` (dan oleh `nx dev` untuk bagian-bagian yang dibutuhkannya). Ini berisi:

- modul rute yang dikompilasi, sebagai paket Python (`__nexy__/src/routes/...`);
- titik masuk klien yang dihasilkan (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` setelah Vite build - aset, manifes, HTML yang telah dirender sebelumnya;
- `build-cache.json`.

Perlakukan seluruh direktori sebagai sekali pakai: hapus, bangun kembali. Mengeditnya dengan tangan akan menghilangkan perubahan pada build berikutnya. Tambahkan ke `.gitignore`.

## Langkah selanjutnya

- [Routing](../routing/README.md): bagaimana jalur menjadi URL
- [Config](../reference/config.md): setiap opsi proyek
- [Frontend](../guides/frontend.md): Vite, gaya dan pembuatan klien
