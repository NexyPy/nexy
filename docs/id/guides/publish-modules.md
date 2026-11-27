# Bagaimana cara menerbitkan modul ke registri Nexy?

Jalankan `nx publish` dari direktori modul dengan `nx.toml` yang valid, token registri, dan setiap file yang dideklarasikan manifes; perintah memeriksa rilis, membuat satu arsip, dan mengunggah versi yang tidak dapat diubah.

## Siapkan manifesnya

Modul sumber mencantumkan setiap file yang dikirimkannya. Arsip tersebut menampung `nx.toml` dan file-file tersebut.

```toml filename="nx.toml"
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py", "src/helpers.py"]
```

Bidang `name` harus huruf kecil `@scope/name`. Bidang `version` harus terdiri dari tiga angka yang dipisahkan oleh titik. File harus berupa jalur relatif di dalam modul. Modul paket mendeklarasikan `source.package` alih-alih `source.files`.

## Periksa sebelum mengunggah

Gunakan `--dry-run` untuk memvalidasi manifes, mengarsipkan file yang dideklarasikan, dan mencetak checksum tanpa mengunggah:

```bash
nx publish --dry-run
```

Uji coba tidak memerlukan token. Ia mencetak baris `warning:` untuk setiap impor relatif yang menunjuk ke file yang tidak dideklarasikan oleh manifes. Misalnya, `from .helpers import token` di `src/auth.py` memerlukan `src/helpers.py` di `source.files`, jika tidak maka instalasi akan mendapatkan impor yang rusak.

## Tetapkan tokennya

`nx publish` dibaca `NEXY_REGISTRY_TOKEN`, lalu `~/.config/nexy/registry-token`. Token dikirim dalam header `Authorization` dan tidak pernah dicetak.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

File token memungkinkan masa depan `nx login` menulis kredensial yang sama. Tanpa salah satu sumber, perintah akan mencetak `error: No registry token` dan keluar dengan status 1.

## Publikasikan

```bash
nx publish
```

Perintah ini mencetak nama, versi, dan checksum SHA-256 dari rilis yang diterbitkannya. Pasangan nama dan versi tidak dapat diubah: memublikasikannya lagi akan mencetak kesalahan konflik. Publikasikan versi baru sebagai gantinya.

## Gunakan registri lain

Secara default, perintah diposting ke `https://registry.nexypy.dev`. Gunakan `--registry` untuk registri lain, misalnya registri lokal selama pengembangan:

```bash
nx publish --registry http://localhost:8000
```

Hanya URL https yang diterima, ditambah http biasa di `localhost`, `127.0.0.1` dan `::1`. Jawaban sementara `429` dan `5xx` dicoba ulang dua kali; manifes yang buruk, token yang hilang, atau konflik tidak dicoba ulang.

## Verifikasi rilisnya

```bash
nx add @acme/auth@1.2.0
```

Lihat [Instal modul](install-modules.md) untuk peningkatan, pin, dan pengaturan kepercayaan.
