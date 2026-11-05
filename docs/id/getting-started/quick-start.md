# Mulai cepat

Anda akan membuat proyek Nexy, menjalankannya, dan melihat perubahan halaman saat Anda mengeditnya. Dibutuhkan tiga menit. [Tutorial](tutorial.md) kemudian menambahkan titik akhir dan build produksi.

## Sebelum Anda mulai

| Anda memerlukan | Mengapa |
|---|---|
| Python 3.12+ | `requires-python` di `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | menyediakan `uvx`, membuat proyek dan menginstal paket-paketnya |
| Node.js 18+ | hanya jika Anda menggunakan kerangka klien (React, Vue, Svelte, Solid, Preact) |

Belum ada uv? Lihat [Instalasi](installation.md).

## 1. Buat proyek

```bash
uvx nexy new my-app
```

`uvx` disertakan dengan uv, jadi instal uv terlebih dahulu. Ini menjalankan Nexy dalam lingkungan sementara, cukup untuk **membuat** proyek. `nexy new` kemudian membuat `.venv` proyek itu sendiri dan menginstal paket-paketnya di sana. Empat petunjuk memutuskan pengkabelan:

| Perintah | Efek |
|---|---|
| Router berbasis file? | `Yes` memindai `src/routes/`; `No` merancah router modular di `src/apps/` |
| Jenis proyek | `Web` menambahkan tata letak dan aset klien, `API` dimulai tanpa tampilan |
| Komponen klien? | menambahkan kerangka kerja dan Vite pengaturannya |
| ORM / database | menambahkan lapisan model, atau tidak sama sekali |

Tidak yakin? Jawab `Yes`, `Web`, dan tidak ada komponen klien. Anda dapat menambahkannya nanti.

## 2. Jalankan

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Buka <http://localhost:3000>. Anda akan melihat halaman awal. Port berasal dari `usePort` (default `3000`); `--port` dan `--host` menimpanya per proses.

> [!NOTE]
> Jalankan setiap perintah kecuali `new` dan `init` di dalam lingkungan virtual proyek, atau awali dengan `uv run`, seperti pada `uv run nexy dev`. Di luar itu, proyek yang membutuhkan `sqlmodel` gagal dengan `No module named 'sqlmodel'`.

## 3. Ubah halaman

<!-- router:fbr,custom -->
File di bawah `src/routes/` adalah rute. Buat `src/routes/hello.nexy`:

```nexy filename="src/rute/halo.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Pengontrol mengembalikan tampilan. Buat `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Kemudian deklarasikan halaman tersebut di `src/apps/app_controller.py` dan tambahkan ke modul:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Buka <http://localhost:3000/hello>. Ubah `"Hello"` menjadi `"Bonjour"` dan simpan: halaman diperbarui tanpa memuat ulang secara manual. Jika kodenya salah, browser menampilkan kesalahan tersebut, bukan halaman kosong.

`prop[str]` mendeklarasikan properti yang diketik. Markup di bawah frontmatter adalah Jinja2 - lihat [.nexy files](../views/nexy/README.md).

## Dimana selanjutnya

| Anda ingin | Membaca |
|---|---|
| Tambahkan titik akhir Python dan kirimkan build | [Tutorial](tutorial.md) |
| Ketahui di mana setiap file berada | [Struktur proyek](project-structure.md) |
| Pahami siapa yang membangun apa | [Cara kerja Nexy](how-nexy-works.md) |
| Gunakan React, Vue, Svelte, Solid atau Preact | [Tampilan](../views/README.md) |
