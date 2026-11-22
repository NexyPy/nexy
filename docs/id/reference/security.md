# Keamanan

Bagaimana Nexy menjaga permukaan serangannya tetap kecil, versi apa yang diperlukan, dan cara memeriksa proyek.

## Lantai versi

Nexy bergantung pada FastAPI, Starlette, Jinja2, Vite dan React. Lantai adalah versi terendah yang diizinkan Nexy; masing-masing menjawab nasihat yang diterbitkan.

| Paket | Lantai | Mengapa |
|---|---|---|
| `starlette` | 1.3.1 | CVE-2026-48710 (BadHost, diperbaiki di 1.0.1): header `Host` yang dibuat mengubah jalur laporan Starlette ke middleware, yang melewati otorisasi yang tertulis di `request.url.path`; terdaftar sebagai dieksploitasi oleh CISA. CVE-2026-48817 dan CVE-2026-48818 (pengiriman permintaan, `StaticFiles` pada Windows, diperbaiki di 1.1.0), CVE-2026-54282 (jalur permintaan tidak divalidasi, 1.3.0) dan CVE-2026-54283 (batas `request.form()`, 1.3.1). |
| `python-dotenv` | 1.2.2 | CVE-2026-28684, di pembaca file `.env` `nx migrate` memuat |
| `fastapi` | 0.133.0 | rilis pertama yang menerima Starlette tetap |
| `jinja2` | 3.1.6 | pelarian sandbox melalui filter `attr` (CVE-2025-27516) |
| `vite` (proyek perancah) | 6.4.5 | `server.fs.deny` bypass (CVE-2026-53571 pada jalur alternatif Windows; GHSA-rq7h-c2jc-7f22, diperbaiki di 6.4.4; GHSA-8g5g-mxqh-grgj, bypass kueri yang dibawa sendiri oleh 6.4.4, diperbaiki di 6.4.5), dan nasihat `launch-editor` diperbaiki di 6.4.4 |
| `svelte` (proyek perancah) | 5.55.7 | enam nasihat XSS rendering server melalui atribut penyebaran, nama tag dinamis dan `bind:innerText` |
| `esbuild` (proyek perancah) | 0.28.1 | file sewenang-wenang dibaca melalui server pengembangan (GHSA-g7r4-m6w7-qqqr) |
| `react`, `react-dom` | 19.2.5 | nasihat tahun 2026 React berkaitan dengan paket `react-server-dom-*`, yang tidak digunakan Nexy; lantai membuat garis tetap ditambal |

`python scripts/audit_dependencies.py` memeriksa setiap lantai terhadap OSV setelah kuncian, di CI juga: penasehat baru di lantai gagal dalam audit.

Periksa versi penyelesaian Anda:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Aturan yang diikuti Nexy

- **Jangan pernah mempercayai header Host untuk jalurnya.** Nexy membaca `scope["path"]`, bukan `request.url.path`, di middlewarenya sendiri (direktori middleware). Lakukan hal yang sama pada milik Anda.
- **Hindari apa yang mencapai HTML.** Props diteruskan ke komponen klien, atribut `Link`, atribut `Image`, `Audio` dan `Video`, jangkar daftar isi, dan detail `HTTPException` semuanya lolos dari HTML. Templat `.nexy` tidak lolos dengan sendirinya: tulis `{{ value | e }}` untuk nilai apa pun yang berasal dari pengunjung atau database, dan jangan pernah `| safe` pada input pengguna.
- **Titik akhir pengembang hanya bersifat loopback dan sempit.** Titik akhir render dev (`/__nexy__/render`) hanya menerima file di bawah `src/routes/` dengan ekstensi `.tsx` atau `.jsx`, dan hanya dapat dijangkau melalui server pengembang, yang menolak header `Host` asing.
- **Detail kesalahan tidak bocor.** Halaman kesalahan yang gagal hanya menampilkan kode status.
- **Jawaban produksi membawa header yang aman.** `X-Content-Type-Options: nosniff` dan `Referrer-Policy: strict-origin-when-cross-origin`, kecuali kode Anda menetapkannya sendiri. Header `Server` tidak terkirim. Tambahkan `Strict-Transport-Security` dan `Content-Security-Policy` di proxy atau middleware Anda: keduanya bergantung pada domain Anda.
- **Kecelakaan menunjukkan referensi, bukan kesalahannya.** Lihat [Halaman kesalahan](../routing/fbr/errors/README.md#unhandled-exceptions).
- **Tidak ada `eval` dan tidak ada `shell=True` dalam kode Python Nexy.** Program eksternal dijalankan dengan daftar argumen.

## Menjalankan audit

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Repositori Nexy sendiri menjalankan yang pertama dan ketiga dalam pemeriksaannya. Penasihat baru di lantai atas ditangani dengan menaikkan lantai di `pyproject.toml` atau di perancah `package.json`, lalu membuat ulang kuncinya.

## Menyebar dengan aman

- Setel `useTrustedHost` ke domain Anda: ia menolak header `Host` yang tidak diharapkan sebelum rute apa pun.
- Jangan mengekspos server pengembang Vite: `nx dev` simpan di loopback di belakang asal Nexy.
- Setel `useDocs = False` jika skema API tidak boleh bersifat publik.

Lihat [Middleware dan keamanan](../guides/middleware-and-security.md).

## Sumber

- [CVE-2026-48710 (BadHost) di Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite penasehat GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) dan [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React paket server CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Langkah selanjutnya

- [Middleware dan keamanan](../guides/middleware-and-security.md)
- [Menyebarkan](../deployment/README.md)
- [Konfigurasi](config.md)
