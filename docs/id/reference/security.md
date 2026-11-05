# Keamanan

Bagaimana Nexy menjaga permukaan serangannya tetap kecil, versi apa yang diperlukan, dan cara memeriksa proyek.

## Lantai versi

Nexy bergantung pada FastAPI, Starlette, Jinja2, Vite dan React. Lantai adalah versi terendah yang diizinkan Nexy; masing-masing menjawab nasihat yang diterbitkan.

| Paket | Lantai | Mengapa |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): header `Host` yang dibuat mengubah jalur laporan Starlette ke middleware, yang melewati otorisasi yang tertulis pada `request.url.path`. Terdaftar sebagai dieksploitasi oleh CISA. |
| `fastapi` | 0.133.0 | rilis pertama yang menerima Starlette | tetap
| `jinja2` | 3.1.6 | escape sandbox melalui filter `attr` (CVE-2025-27516) |
| `vite` (proyek perancah) | 6.4.3 | `server.fs.deny` melewati jalur alternatif Windows (CVE-2026-53571); bypass string kueri sebelumnya (CVE-2026-39364) hanya memengaruhi Vite 7.1-7.3.1 dan 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | nasihat React tahun 2026 berkaitan dengan paket `react-server-dom-*`, yang tidak digunakan Nexy; lantai menjaga garis tetap ditambal |

Periksa versi penyelesaian Anda:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Aturan yang diikuti Nexy

- **Jangan pernah mempercayai header Host untuk jalurnya.** Nexy membaca `scope["path"]`, bukan `request.url.path`, di middlewarenya sendiri (direktori middleware). Lakukan hal yang sama pada milik Anda.
- **Hindari apa yang mencapai HTML.** Props diteruskan ke komponen klien, atribut `Link`, atribut `Image`, `Audio` dan `Video`, jangkar daftar isi, dan detail `HTTPException` semuanya lolos dari HTML. `| safe` dalam templat, nonaktifkan ini: jangan pernah menggunakannya pada input pengguna.
- **Titik akhir pengembang hanya bersifat loopback dan sempit.** Titik akhir render dev (`/__nexy__/render`) hanya menerima file pada `src/routes/` dengan ekstensi `.tsx` atau `.jsx`, dan hanya dapat dijangkau melalui server pengembang, yang menolak header `Host` asing.
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

- [Perangkat tengah dan keamanan](../guides/middleware-and-security.md)
- [Menyebarkan](../deployment/README.md)
- [Konfigurasi](config.md)
