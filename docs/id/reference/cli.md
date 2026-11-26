# CLI

Binernya adalah `nx` (juga dipasang sebagai `nexy`). `uvx nexy new` membuat proyek (`uvx` hadir dengan uv). Jalankan setiap perintah lain di dalam lingkungan virtual proyek, atau melalui `uv run`, misalnya `uv run nexy dev`: di situlah paket Anda berada.

## Perintah

| Perintah | Alias | Apa fungsinya |
|---|---|---|
| `nx dev` | `nx d` | server pengembangan: kompilasi saat perubahan, Vite, HMR |
| `nx start` | `nx s` | server produksi pada output yang dikompilasi |
| `nx build` | `nx b` | membangun produksi |
| `nx new` | `nx n` | perancah sebuah proyek |
| `nx init` | `nx i` | tambahkan Nexy ke proyek yang sudah ada |
| `nx add` | - | tambahkan komponen UI dari registri atau URL, atau platform penerapan seperti `vercel` |
| `nx migrate` | `nx m` | membuat atau menerapkan migrasi database dengan Alembic atau Aerich |
| `nx check` | `nx c` | ketik-periksa: mypy di Python, `tsc` di TypeScript |
| `nx format` | `nx f` | format file Python (ruff), JS/TS (lebih cantik), `.nexy` |
| `nx test` | - | jalankan pytest; `--client` menambahkan vitest |
| `nx routes` | - | daftar rute aplikasi, metode HTTP, jalur dan file sumber |
| `nx skills` | - | menambah atau menyegarkan keterampilan, `AGENTS.md` dan `CLAUDE.md` untuk agen pengkodean |

## `nx routes`

Mencantumkan rute aplikasi, metode HTTP, jalur, dan file sumbernya dalam sebuah tabel. Rute diurutkan berdasarkan jalur. Rute favicon kerangka tidak termasuk.

Jalankan di dalam lingkungan proyek:

```bash
nx routes
```

Jika tidak ada rute aplikasi yang ditemukan, ia akan mencetak `No routes found.`.

## Bendera

| Perintah | Bendera | Bawaan |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `dev`, `start` | `--open`, `-o` | mati - buka browser di alamat lokal setelah server menjawab |
| `build` | `--check` | off - menjalankan ruff dan mypy setelah build |
| `format` | `--check` | mati - laporkan alih-alih menulis ulang |
| `test` | `--client` | off - jalankan juga vitest alih-alih pytest saja |
| `test` | `--no-server` | aktif - lewati pytest bila Anda hanya menginginkan pengujian klien |
| `new` | `--template`, `-t` | tidak ada - mengkloning templat terdaftar tanpa diminta |
| `new` | `--no-agents` | agen aktif - lewati `AGENTS.md` dan keterampilan agen |
| `add` | `--ui`, `--url` | off - memaksakan nama registri atau URL jika tidak jelas |
| `add` | `--all`, `-a` | off - tambahkan setiap komponen registri |
| `add` | `--sha256` | none - intisari yang diharapkan dari komponen jarak jauh; ketidakcocokan dibatalkan |
| `migrate` | `--init` | mati - tulis pengaturan Alembic atau Aerich |
| `migrate` | `--upgrade`, `-u` | mati - terapkan migrasi alih-alih menulis yang baru |
| `migrate` | `--message`, `-m` | kosong - nama revisi baru |

## Keluaran

Langkah-langkah panjang (menginstal paket, kompilasi, bundling) menunjukkan spinner dengan waktu yang telah berlalu dan baris terakhir perintah dicetak, kemudian meninggalkan satu baris, seperti yang dilakukan uv: `Synced .venv with uv in 1.4s`. Sekelompok langkah (penginstalan `nx new`) juga menunjukkan bilah kemajuan dan jumlah langkah yang diselesaikan, `2/5`. Langkah yang gagal adalah baris `error:` dengan penyebabnya, `cause: exit 1 after 2.1s`, diikuti dengan baris terakhir keluaran perintah alih-alih menyembunyikannya. Sesuatu untuk dilihat berbunyi `warning: ...`, dan apa yang harus dilakukan selanjutnya `hint: ...`. Log pengembang membaca `GET » /about 200 in 12ms` untuk permintaan dan `vite » ...` untuk Vite.

## Kesalahan saat `nx dev` berjalan

Menyimpan file yang rusak tidak pernah menghentikan server. File `.py` dengan kesalahan sintaksis dilaporkan bersama file dan barisnya, dan server terus menyajikan versi terakhir yang berfungsi hingga Anda memperbaikinya:

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

File yang diurai tetapi gagal ketika aplikasi dimuat (impor hilang, kesalahan pada tingkat modul) dilaporkan dengan cara yang sama dan `nx dev` menunggu penyimpanan Anda berikutnya; tidak ada yang dilayani sampai aplikasi dimuat lagi. Penyimpanan yang valid berbunyi `nexy » update <file>` saat server memuat ulang. File Markdown di luar `src/routes`, seperti `README.md`, bukan halaman dan tidak memicu apa pun. `nx start` lebih ketat: keluar dengan kode 1, dan tidak memulai apa pun, jika file rute tidak dapat dimuat atau jika `nx build` belum membangun proyek.

## Pertanyaan dari `nx new`

`nx new` menanyakan, dalam urutan ini: router berbasis file, jenis proyek (web atau API), perutean sisi klien, kerangka klien, cara menata gaya aplikasi, alias impor, ORM, basis data, dan URL basis data. Setiap opsi memiliki deskripsi singkat dan opsi terkini disorot. Pertanyaan yang tidak berlaku akan dilewati (proyek API tidak memiliki kerangka kerja atau gaya; memilih **Tidak ada database** karena ORM melewatkan database dan URL). Bergerak dengan tombol panah (atau `j`/`k`, atau angka), konfirmasi dengan `enter`, kembali ke pertanyaan sebelumnya dengan `←` atau `esc`, keluar dengan `ctrl+c`.

| Pertanyaan | Pilihan |
|---|---|
| Impor alias | `@` (`@/components/...` menunjuk ke `src/`), atau awalan lain seperti `~` atau `#app` |
| Gaya | Tailwind CSS, UnoCSS, Vanilla CSS, Lainnya (tanpa alat CSS, stylesheet biasa sama seperti Vanilla) |
| ORM | SQLModel, SQLAlchemy, Kura-kura-ORM, Tidak ada database |
| Basis Data (dengan ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Lainnya (Anda mengetikkan URL) |

Driver database untuk ORM yang dipilih diinstal dengannya (`psycopg`, `pymysql`, `asyncpg` atau `aiomysql`), dan URL ditulis ke `.env`.

Sebelum menginstal paket, `nx new` memeriksa koneksi. Tanpa satu pun, ia akan melewatkan instalasi dan meminta Anda untuk menjalankan `uv sync` dan instalasi manajer paket Anda nanti. Dengan satu, ia mencetak latensi dan kecepatan pengunduhan, dan memperingatkan ketika koneksi lambat (lebih dari 400 ms, atau di bawah 100 KB/s). Setiap baris instalasi memberi nama alat dan folder yang diisinya, misalnya `pnpm install node_modules` atau `uv sync .venv`.

## Apa yang `dev`, `build` dan `start` ciptakan

Sebelum dijalankan, ketiga perintah tersebut membuat `__init__.py` kosong di `src/` dan di setiap folder di bawahnya yang menyimpan file `.py` atau `.nexy`, sehingga rute seperti `src/routes/users.py` mengimpor dengan cara yang sama ke semuanya. File yang sudah ada tidak pernah disentuh, dan `nx dev` melakukan hal yang sama lagi saat Anda menambahkan folder. Python bytecode masuk ke `__nexy__/__pycache__`, jadi tidak ada folder `__pycache__` yang muncul di sebelah sumber Anda.

## Bahasa

Baris perintah berbicara bahasa Inggris, Cina, Hindi, Spanyol, Portugis, Prancis, Jerman, Jepang, Rusia, Korea, Indonesia, dan Arab. Ia menggunakan yang pertama yang didukungnya:

1. variabel lingkungan `NEXY_LANG` (`NEXY_LANG=ja nx dev`);
2. variabel lokal shell Anda (`LC_ALL`, `LC_MESSAGES`, `LANG`, lalu `LANGUAGE`);
3. bahasa sistem operasi Anda.

Yang lainnya adalah bahasa Inggris, begitu pula pesan apa pun yang belum dimiliki bahasa tersebut. Hanya apa yang `nx` cetak yang diterjemahkan: kesalahan kompiler, penelusuran balik, dan keluaran alat yang dijalankannya tetap sebagaimana adanya. Terjemahannya belum ditinjau oleh penutur asli: koreksi dipersilakan sebagai permintaan penarikan ke `nexy/modules/i18n/<language>.json`.

## Membangun perilaku

`nx build` mengkompilasi rute, lalu menggabungkan klien ketika `useVite` aktif.

> [!NOTE]
> tidak ada bendera `--static`. Hosting statis adalah pilihan penerapan, bukan mode build - lihat [Penerapan](../deployment/README.md).

## Mengerjakan Nexy itu sendiri

Di dalam repositori ini gerbangnya adalah:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Langkah selanjutnya

- [Memulai](../getting-started/quick-start.md): proyek pertama
- [Pengujian](../guides/testing.md): apa yang `nx test` dijalankan
- [Penerapan](../deployment/README.md): `build` dan `start` dalam produksi
