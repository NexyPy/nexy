# Instalasi

## Persyaratan

| Persyaratan | Mengapa |
|---|---|
| Python 3.12+ | `requires-python` di `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | membuat proyek, menginstal paket-paketnya dan menjalankan Nexy |
| Node.js 18+ | hanya untuk kerangka klien (React, Vue, Svelte, Solid, Preact) |

Sebuah proyek tanpa kerangka klien tidak memerlukan Node.js sama sekali.

## Instal uv terlebih dahulu

`uvx` bukan alat terpisah: ia disertakan dengan uv, jadi instal uv sebelum melakukan hal lain.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Periksa dengan `uv --version` dan `uvx --version`.

## Buat proyek

```bash
uvx nexy new my-app
```

`uvx` menjalankan Nexy di lingkungan sementara dan tidak meninggalkan apa pun. Itu cukup untuk **membuat** sebuah proyek (`new`, `init`) dan tidak lebih: lingkungan sementara menampung Nexy dan tidak ada paket lainnya. `nexy new` membuat lingkungan virtual proyek itu sendiri, `.venv`, dan menginstal paket-paketnya di sana.

`nexy new my-app` menanyakan empat pertanyaan: router (berbasis file atau modular), jenis proyek (web atau API), kerangka klien, ORM. Instalasi dependensi Python dan Node kemudian dijalankan dengan satu baris per langkah dan durasinya. Lihat [CLI](../reference/cli.md).

Lewati petunjuk dengan templat terdaftar:

```bash
uvx nexy new my-app --template <name>
```

## Bekerja di dalam lingkungan virtual proyek

Setiap perintah lainnya (`nexy dev`, `nexy build`, `nexy migrate`...) harus dijalankan **di dalam lingkungan virtual proyek**. Di situlah paket Anda berada: ORM Anda, perpustakaan Anda, dan Nexy yang digunakan untuk membuat proyek. Di luar itu, proyek yang membutuhkan `sqlmodel` gagal dengan `ModuleNotFoundError: No module named 'sqlmodel'`.

Aktifkan sekali per terminal, dari folder proyek:

| Kerang | Perintah |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

Prompt kemudian dimulai dengan `(.venv)`. Dari sana:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Buka <http://localhost:3000>.

Untuk melewati aktivasi, biarkan uv melakukannya untuk satu perintah: `uv run nexy dev`.

> [!CATATAN]
> `nexy` dan `nx` adalah biner yang sama. Salinan yang diinstal dengan `uv tool install nexy` berada di lingkungannya sendiri, seperti `uvx`, jadi gunakan itu untuk membuat proyek dan menjalankan segala sesuatu yang lain dari lingkungan proyek.

## Tambahkan Nexy ke proyek yang sudah ada

Jalankan dari lingkungan virtual proyek, dengan Nexy di antara paketnya (`uv add nexy`):

```bash
nexy init
```

## Langkah selanjutnya

- [Mulai cepat](quick-start.md)
- [Tutorial](tutorial.md)
- [Struktur proyek](project-structure.md)
- [Pemecahan Masalah](../guides/troubleshooting.md)
