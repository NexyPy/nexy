# Bagaimana cara menyebarkan aplikasi Nexy di Vercel?

Jalankan `nx add vercel`, komit file yang dihasilkan bersama dengan keluaran `nx build` Anda, dan arahkan waktu proses Vercel Python ke `src/server.py:app`.

## Tambahkan file platform

Dari akar proyek Nexy:

```bash
nx add vercel
nx build
```

`nx add vercel` menulis `src/server.py` dan `vercel.json`. Itu juga menambahkan aturan pengabaian untuk file yang berubah saat aplikasi berjalan: `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` dan `__pycache__/`. Menjalankan kembali perintah akan menyimpan file yang sudah ada dan tidak menduplikasi aturan abaikan.

## Arahkan Vercel ke aplikasi

Dalam pengaturan proyek Vercel, pilih runtime Python dan gunakan `src/server.py:app` sebagai titik masuk. Vercel menemukan nama `app` di modul itu; `nx start` tidak terlibat.

`src/server.py` yang dihasilkan mengimpor `nexy.app.app` yang malas setelah menyiapkan folder kerja. Anda dapat menggunakan titik masuk yang sama dengan `uvicorn src.server:app` secara lokal.

## Komit keluaran build

Ketika Vercel tidak memiliki perintah build, ia hanya menerima isi repositori. Komit `__nexy__/` setelah setiap `nx build`, dengan rute yang dikompilasi, bundel klien di bawah `__nexy__/client/` dan manifes di `__nexy__/client/.vite/manifest.json`.

Pertahankan `vite.config.ts` di root proyek dan komit. Dalam produksi, Nexy membaca manifes Vite untuk menulis tag stylesheet dan skrip, namun ia memancarkan tag tersebut hanya ketika `vite.config.ts` ada. Tanpa file itu halaman masih menjawab 200 dan tiba tanpa CSS atau klien JavaScript.

Jangan melakukan `__nexy__/build-cache.json`: ini berisi jalur absolut dari mesin yang menjalankan build. `__nexy__/server.port` milik `nx start`, dan `__nexy__/.temp/` adalah ruang awal.

## Terima sistem file read-only

Vercel memasang proyek hanya-baca saat aplikasi Python dimulai. Nexy menulis file yang dihasilkan saat startup, sehingga `from nexy.app import app` yang kosong bisa gagal dengan `OSError: [Errno 30] Read-only file system`.

Titik masuk yang dihasilkan menyalin enam item proyek ke dalam folder sementara yang dapat ditulis sebelum mengimpor aplikasi: `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` dan `vite.config.ts`. Ini mengubah direktori kerja dan menempatkan salinannya terlebih dahulu di `sys.path`, karena Nexy menyelesaikan rute dari direktori saat ini. Tambahkan file lain yang dibaca aplikasi Anda saat runtime ke daftar itu secara manual.

## Cache aset statis

`vercel.json` yang dihasilkan berisi dua aturan cache yang digunakan oleh situs Nexy yang diterapkan: file di bawah `/assets/` tidak dapat diubah selama satu tahun, dan gambar serta font di bawah `public/` tetap segar selama satu hari dengan jendela basi selama satu minggu sambil memvalidasi ulang. Tambahkan aturan lain di file yang sama jika proyek Anda membutuhkannya.

## Periksa penerapannya

Sebelum mendorong, impor titik masuk dan minta satu halaman:

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Kemudian buka `/`, satu rute yang dihasilkan dan satu file di bawah `/assets/`. Bandingkan respons dengan `nx start` secara lokal: status, jenis konten, dan ukuran harus cocok. Halaman yang lebih kecil dari halaman lokal dengan tepat dua tag klien berarti `vite.config.ts` hilang dari proyek yang disalin.
