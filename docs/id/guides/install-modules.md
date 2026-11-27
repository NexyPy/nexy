# Bagaimana cara menginstal modul dari registri?

Jalankan `nx add @scope/name` dalam proyek Nexy untuk mengunduh satu rilis dari registri modul, memeriksanya, dan menerapkan perubahan yang dinyatakan. Tambahkan `@1.2.0` untuk menyematkan versi yang tepat.

## Pasang modul

Dari akar proyek Nexy:

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` membaca metadata rilis dan arsip dari `useModuleRegistry`, memeriksa checksum SHA-256, dan memeriksa rentang kompatibilitas `nexy` dan `python` modul. Ia kemudian hanya menulis file yang dideklarasikan oleh manifes, menambahkan paket Python yang dideklarasikan dengan `uv add`, menambahkan paket Node dengan manajer paket proyek, dan menerapkan kait konfigurasi ke `nexyconfig.py` dan `package.json`. Pengaturan dan file yang ada tetap apa adanya: file yang dideklarasikan dan sudah ada dilewati dengan baris `warning:`.

Setiap instalasi yang berhasil dicatat di `.nexy/modules.json`. Komit file itu sehingga rekan satu tim mendapatkan versi modul yang sama.

## Tingkatkan modul

Untuk mengupgrade, jalankan `nx add @acme/auth` lagi setelah registri memiliki rilis yang lebih baru, atau setel pin baru seperti `@acme/auth@1.3.0`. Nama yang tidak dipasangi pin akan memilih versi terbaru dari respons `/versions` registri. Menjalankan versi yang sama lagi akan mencetak `is already installed` dan tidak mengubah apa pun.

## Sematkan versi

Sebuah pin tepat: `nx add @acme/auth@1.2.0` menginstal `1.2.0` dan tidak ada rilis lainnya. Gunakan pin di CI dan di commit `.nexy/modules.json` sehingga setiap checkout memasang kode yang sama. Tanpa pin, rilis baru akan mengubah instalasi berikutnya.

## Jalankan migrasi

Migrasi dinonaktifkan secara default. Tambahkan `--migrate` ketika Anda ingin perintah rilis yang dideklarasikan dijalankan setelah file dan dependensinya ada:

```bash
nx add @acme/auth@1.2.0 --migrate
```

Setiap perintah dicetak sebelum dijalankan. Proyek ini perlu menginstal alat migrasinya sebelum modul dapat mendeklarasikannya.

## Tetapkan registri dan aturan kepercayaannya

Defaultnya ada di `nexyconfig.py`:

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` adalah URL dasar yang dibaca CLI. Hanya URL https yang diterima, kecuali loopback http untuk registri lokal selama pengembangan. `useRequireSignedModules = True` menolak rilis yang tidak ditandatangani. Pelepasan yang disertai tanda tangan juga ditolak sampai tersedia verifikator; setelah seseorang memverifikasinya, `nx add` mencetak `Verified by` dengan identitas penandatangan. Pertahankan `False` default hanya untuk registri yang Anda percayai.
