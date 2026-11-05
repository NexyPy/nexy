# Agen pengkodean

Sebuah proyek yang dibuat dengan `nx new` membawa aturan yang dibutuhkan agen pengkodean untuk menulis kode Nexy sesuai keinginan Anda: urutan pekerjaan, kode dan aturan penulisan, dan satu keterampilan per topik. Halaman ini menjelaskan apa yang Anda dapatkan, ke mana perginya, dan bagaimana menjaganya tetap terkini. Mengerjakan Nexy sendiri adalah pekerjaan yang berbeda: membaca root repositori `AGENTS.md`.

## Apa yang `nx new` tambahkan

| File | Dibaca oleh | Ditahan |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | tumpukan proyek, urutan pekerjaan, aturan, daftar keterampilan |
| `CLAUDE.md` | Claude Code | satu baris, `@AGENTS.md`, jadi keduanya membaca teks yang sama |
| `.agents/skills/` | Codex, OpenCode | keterampilan |
| `.claude/skills/` | Claude Code, OpenCode | keterampilan yang sama |

`AGENTS.md` pendek dan disesuaikan. Proyek Vue yang dirutekan klien berbunyi "dirutekan klien, Vue, ditata dengan Tailwind"; sebuah proyek API diberitahu bahwa tidak ada tampilan. Hanya keterampilan yang sesuai yang disalin: proyek React mendapat keterampilan `nexy-react` dan tidak ada Vue, proyek server mendapat keterampilan `.nexy` dan Markdown, proyek API tidak mendapat keterampilan tentang tampilan.

Untuk melewati semuanya, buat proyek dengan `nx new --no-agents`.

## Keterampilan

| Keterampilan | Meliputi |
|---|---|
| `nexy-principles` | urutan kerja, aturan kode, aturan penulisan |
| `nexy-ux-audit` | pengalaman dan audit arsitektur informasi yang dijalankan sebelum tampilan apa pun |
| `nexy-project` | mode, folder, konvensi file, konfigurasi, perintah |
| `nexy-file` | `.nexy` halaman, alat peraga, kait, pulau |
| `nexy-markdown` | `.md` dan `.mdx` konten |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | kode idiomatik untuk kerangka klien |
| `nexy-styling` | Tailwind, UnoCSS atau CSS biasa, dan token desain |
| `nexy-backend` | Penangan API, tindakan, WebSocket, ISR, middleware |
| `nexy-modular` | pengontrol, modul, injeksi, dan pelindung router modular |
| `nexy-security` | dependensi, masukan, sesi, otorisasi, rahasia |
| `nexy-testing` | loop pengujian pertama dan gerbangnya |
| `nexy-framework-dev` | mengubah Nexy itu sendiri, bukan proyek yang dibangun dengan Nexy |

Aturan yang mereka terapkan: mengaudit pengalaman sebelum membuat tampilan, menulis tes yang gagal terlebih dahulu, satu fungsi melakukan satu perawatan, satu kelas membawa satu niat, satu folder menampung satu set niat terkait, tanpa emoji, ikon SVG asli, teks biasa yang ditulis untuk orang, dan tidak ada skrip DOM tulisan tangan di React, Vue, Svelte, Solid atau Preact.

## Tambahkan mereka ke proyek yang sudah ada

```bash
nx skills
```

Jalankan di root proyek. Bunyinya `nexyconfig.py` dan `package.json` untuk menemukan tumpukan, menyalin keterampilan yang cocok, dan menulis `AGENTS.md` dan `CLAUDE.md` ketika hilang.

Itu tidak pernah menimpa file yang Anda tulis: `AGENTS.md` atau `CLAUDE.md` yang ada disimpan, dan perintah memberitahu Anda demikian. Tambahkan daftar keahlian ke file Anda sendiri dengan tangan jika Anda menginginkannya di sana. Keterampilan Anda sendiri di `.claude/skills/` atau `.agents/skills/` dibiarkan saja; hanya skill `nexy-*` yang disegarkan.

Jalankan `nx skills` lagi setelah Anda memutakhirkan Nexy untuk menyegarkan salinan, dan komit hasilnya sehingga seluruh tim membagikannya.

## Bagaimana agen menemukannya

- `AGENTS.md` (atau `CLAUDE.md`, yang mengimpornya) dibaca pada awal setiap sesi. Itu menyebutkan keterampilannya.
- Setiap keterampilan dimulai dengan nama dan deskripsi yang menjelaskan cakupannya dan kapan memuatnya. Agen membacanya terlebih dahulu dan membuka keterampilan hanya ketika tugasnya cocok.

Skillnya mengikuti [format Skill Agen](https://agentskills.io/specification) yang terbuka, sehingga agen lain yang membaca folder `SKILL.md` juga dapat menggunakannya.

## Apa yang tidak mereka lakukan

Keterampilan memberi tahu agen cara bekerja; mereka tidak membuat keluarannya benar. Simpan cek Anda sendiri:

- Baca apa yang diubah agen.
- Jalankan `nx check`, `nx test` dan `nx build`. Keterampilan meminta hal ini dan keluarannya dilaporkan, bukan diringkas.
- Audit dependensi yang ditambahkan agen (`nexy-security` menjelaskan caranya).

Contoh-contoh dalam keterampilan diperiksa dengan pengujian Nexy sendiri: impor ada, bidang konfigurasi ada, perintah ada, Python diurai. Itu menangkap penyimpangan, bukan salah penilaian.

## Peta

Agen menjawab lebih cepat ketika mengetahui halaman mana yang menyimpan jawabannya.

| Anda perlu | Baca |
|---|---|
| produknya, dalam satu halaman | [README](../README.md) |
| untuk menjalankan proyek | [memulai](../getting-started/quick-start.md) |
| URL file | [perutean](../routing/README.md) |
| segmen dinamis, tata letak, halaman kesalahan | [halaman](../routing/fbr/pages/README.md) |
| jalur saat ini, kueri, cookie, sesi | [kait](../routing/fbr/navigation/hooks.md) |
| untuk mengedit halaman | [.nexy files](../views/nexy/README.md) atau [views](../views/README.md) |
| Markdown atau MDX | [penurunan harga](../views/nexy/markdown.md) |
| pembantu HTML bawaan | [komponen](../views/nexy/components.md) |
| mode rendering | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| a WebSocket | [soket web](../routing/fbr/realtime/websocket.md) |
| pengontrol dan modul | [modular](../routing/modular/README.md) |
| untuk menambahkan titik akhir | [API](../routing/fbr/handlers/README.md) |
| formulir yang diposting dari halaman | [tindakan](actions.md) |
| mengapa permintaan gagal, dan halaman mana yang menjawabnya | [pengecualian](../reference/exceptions.md) |
| terjemahan | [i18n](i18n.md) |
| bidang konfigurasi | [config](../reference/config.md) |
| untuk menguji aplikasi | [pengujian](testing.md) |
| build klien | [frontend](frontend.md) |

## Invarian proyek

1. `__nexy__/` dihasilkan. Jangan pernah mengeditnya, jangan pernah melakukan itu. Hapus untuk memaksa pembangunan yang bersih.
2. Satu file per URL. `index.nexy` dan `index.py` untuk jalur yang sama merupakan bug, bukan aturan prioritas.
3. Nama yang dicadangkan di dalam `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `__init__.py`. Jangan gunakan mereka untuk konten.
4. `.nexy` frontmatter adalah Python yang dijalankan per permintaan. Tidak ada efek samping tingkat modul: tidak ada pegangan file, tidak ada koneksi database, tidak ada panggilan jaringan saat impor.
5. `.py` di `src/routes/` adalah pengendali API. Metode adalah nama fungsi (`GET`, `POST`, ...).
6. Konfigurasi berada di `nexyconfig.py`, bukan di variabel lingkungan dan bukan di konstanta yang tersebar.
7. Pelarian otomatis tidak aktif di templat `.nexy`: keluar dari nilai yang tidak dipercaya dengan `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Ketika dokumen dan kode tidak sesuai, percayai kode tersebut dan katakan demikian: `nexy/core/config.py` memegang setiap opsi, `nexy/modules/routers/fbrouter/` aturan perutean, `nexy/modules/compiler/` bagaimana `.nexy` file menjadi modul.

## Langkah selanjutnya

- [CLI](../reference/cli.md): `nx new` dan `nx skills`
- [Konvensi file](../reference/file-conventions.md): nama khusus dan aturan perutean
- [Glosarium](../reference/glossary.md): kata-kata yang menjadi dasar aturan ini
- [Keamanan](../reference/security.md): versi yang menunjukkan keterampilan keamanan
