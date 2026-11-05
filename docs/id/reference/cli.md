# CLI

Binernya adalah `nx` (juga dipasang sebagai `nexy`). `uvx nexy new` membuat proyek (`uvx` hadir dengan uv). Jalankan setiap perintah lain di dalam lingkungan virtual proyek, atau melalui `uv run`, misalnya `uv run nexy dev`: di situlah paket Anda berada.

## Perintah

| Perintah | Alias | Apa fungsinya |
|---|---|---|
| `nx dev` | `nx d` | server pengembangan: kompilasi saat perubahan, Vite, HMR |
| `nx start` | `nx s` | server produksi pada output yang dikompilasi |
| `nx build` | `nx b` | pembangunan produksi |
| `nx new` | `nx n` | merancang proyek |
| `nx init` | `nx i` | menambahkan Nexy ke proyek yang sudah ada |
| `nx add` | - | menambahkan komponen UI dari registri atau URL ke `src/components/ui` |
| `nx migrate` | `nx m` | membuat atau menerapkan migrasi database dengan Alembic atau Aerich |
| `nx check` | `nx c` | pemeriksaan ketik: mypy di Python, `tsc` di TypeScript |
| `nx format` | `nx f` | format Python (ruff), JS/TS (lebih cantik), `.nexy` file |
| `nx test` | - | lari pytest; `--client` menambahkan vitest |
| `nx skills` | - | menambah atau menyegarkan keterampilan, `AGENTS.md` dan `CLAUDE.md` untuk agen pengkodean |

## Bendera

| Perintah | Bendera | Default |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off - menjalankan ruff dan mypy setelah build |
| `format` | `--check` | mati - laporkan alih-alih menulis ulang |
| `test` | `--client` | mati - juga menjalankan vitest alih-alih pytest saja |
| `test` | `--no-server` | aktif - lewati pytest bila Anda hanya ingin pengujian klien |
| `new` | `--template`, `-t` | tidak ada - mengkloning templat terdaftar tanpa perintah |
| `new` | `--no-agents` | agen aktif - lewati `AGENTS.md` dan keterampilan agen |
| `add` | `--ui`, `--url` | menonaktifkan - memaksa nama registri atau URL jika ambigu |
| `add` | `--all`, `-a` | nonaktif - tambahkan setiap komponen registri |
| `add` | `--sha256` | tidak ada - intisari yang diharapkan dari komponen jarak jauh; ketidakcocokan dibatalkan |
| `migrate` | `--init` | mati - tulis pengaturan Alembic atau Aerich |
| `migrate` | `--upgrade`, `-u` | mati - terapkan migrasi alih-alih menulis yang baru |
| `migrate` | `--message`, `-m` | kosong - nama revisi baru |

## Keluaran

Langkah-langkah panjang (menginstal paket, kompilasi, bundling) menunjukkan spinner dengan waktu yang telah berlalu, kemudian meninggalkan satu baris di belakang: `✔ uv sync .venv  1.4s`. Sekelompok langkah (penginstalan `nx new`) menunjukkan bilah kemajuan dengan jumlah langkah yang diselesaikan, `━━━━────  2/5`; satu langkah (`nx add`) menunjukkan bilah yang berdenyut saat dijalankan. Log pengembang membaca `GET » /about 200 in 12ms` untuk permintaan dan `vite » ...` untuk Vite. Langkah yang gagal akan mencetak baris terakhir keluaran perintah alih-alih menyembunyikannya. Terminal yang tidak dapat merender Unicode mendapatkan `+` dan `x`.

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

File yang diurai tetapi gagal ketika aplikasi dimuat (impor hilang, kesalahan pada tingkat modul) dilaporkan dengan cara yang sama dan `nx dev` menunggu penyimpanan Anda berikutnya; tidak ada yang dilayani sampai aplikasi dimuat lagi. Penyimpanan yang valid berbunyi `nexy » update <file>` saat server memuat ulang. File Markdown di luar `src/routes`, seperti `README.md`, bukan halaman dan tidak memicu apa pun. `nx start` lebih ketat: keluar dengan kode 1, dan tidak memulai apa pun, jika file rute tidak dapat dimuat.

## Pertanyaan dari `nx new`

`nx new` menanyakan, dalam urutan ini: router berbasis file, jenis proyek (web atau API), perutean sisi klien, kerangka klien, cara menata gaya aplikasi, alias impor, ORM, basis data, dan URL basis data. Setiap opsi memiliki deskripsi singkat dan opsi terkini disorot. Pertanyaan yang tidak berlaku akan dilewati (proyek API tidak memiliki kerangka kerja atau gaya; memilih **Tidak ada database** karena ORM melewatkan database dan URL). Bergerak dengan tombol panah (atau `j`/`k`, atau angka), konfirmasi dengan `enter`, kembali ke pertanyaan sebelumnya dengan `←` atau `esc`, keluar dengan `ctrl+c`.

| Pertanyaan | Pilihan |
|---|---|
| Impor alias | `@` (`@/components/...` menunjuk ke `src/`), atau awalan lain seperti `~` atau `#app` |
| Style | Tailwind CSS, UnoCSS, Vanilla CSS, Lainnya (tanpa alat CSS, stylesheet biasa sama seperti Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, Tanpa basis data |
| Database (dengan ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Lainnya (Anda mengetikkan URL) |

Driver database untuk ORM yang dipilih diinstal dengannya (`psycopg`, `pymysql`, `asyncpg` atau `aiomysql`), dan URL ditulis ke `.env`.

Sebelum menginstal paket, `nx new` memeriksa koneksi. Tanpa satu pun, ia akan melewatkan instalasi dan meminta Anda untuk menjalankan `uv sync` dan instalasi manajer paket Anda nanti. Dengan satu, ia mencetak latensi dan kecepatan pengunduhan, dan memperingatkan ketika koneksi lambat (lebih dari 400 ms, atau di bawah 100 KB/s). Setiap baris instalasi memberi nama alat dan folder yang diisinya, misalnya `pnpm install node_modules` atau `uv sync .venv`.

## Apa yang `dev`, `build` dan `start` buat

Sebelum dijalankan, ketiga perintah tersebut membuat `__init__.py` kosong di `src/` dan di setiap folder di bawahnya yang menyimpan file `.py` atau `.nexy`, sehingga rute seperti `src/routes/users.py` mengimpor dengan cara yang sama ke semuanya. File yang ada tidak pernah disentuh, dan `nx dev` melakukan hal yang sama lagi saat Anda menambahkan folder. Python bytecode masuk ke `__nexy__/__pycache__`, jadi tidak ada folder `__pycache__` yang muncul di sebelah sumber Anda.

## Bahasa

Baris perintah berbicara bahasa Inggris, Cina, Hindi, Spanyol, Portugis, Prancis, Jerman, Jepang, Rusia, Korea, Indonesia, dan Arab. Ia menggunakan yang pertama yang didukungnya:

1. variabel lingkungan `NEXY_LANG` (`NEXY_LANG=ja nx dev`);
2. variabel lokal shell Anda (`LC_ALL`, `LC_MESSAGES`, `LANG`, lalu `LANGUAGE`);
3. bahasa sistem operasi Anda.

Yang lainnya adalah bahasa Inggris, begitu pula pesan apa pun yang belum dimiliki bahasa tersebut. Hanya apa yang `nx` cetak yang diterjemahkan: kesalahan kompiler, penelusuran balik, dan keluaran alat yang dijalankannya tetap sebagaimana adanya. Terjemahannya belum ditinjau oleh penutur asli: koreksi dipersilakan sebagai permintaan penarikan ke `nexy/modules/i18n/<language>.json`.

## Membangun perilaku

`nx build` mengkompilasi rute, lalu menggabungkan klien ketika `useVite` aktif.

> [!CATATAN]
> tidak ada bendera `--static`. Hosting statis adalah pilihan penerapan, bukan mode build - lihat [Deploy](../deployment/README.md).

## Mengerjakan Nexy itu sendiri

Di dalam repositori ini gerbangnya adalah:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Langkah selanjutnya

- [Memulai](../getting-started/quick-start.md): proyek pertama
- [Testing](../guides/testing.md): apa yang `nx test` jalankan
- [Deploy](../deployment/README.md): `build` dan `start` dalam produksi
