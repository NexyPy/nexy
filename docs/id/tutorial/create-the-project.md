# Bangun aplikasi catatan dengan Nexy, bagian 1: buat proyek

Bagian 1 dari tutorial membuat proyek yang akan Anda kembangkan menjadi aplikasi catatan, dan menjalankannya di browser Anda dalam waktu sekitar lima menit.

**Sebelum Anda memulai:** [uv](https://docs.astral.sh/uv/) dan Node.js 20 atau lebih baru. Tutorialnya mengikuti router yang dipilih di bagian atas menu: alihkan ke sana dan setiap bagian menampilkan file router tersebut.

## Apa yang akan Anda bangun

Di akhir tutorial, aplikasi memiliki halaman dan API JSON untuk catatan, database, akun, catatan yang dibagikan melalui email, pembaruan langsung, pengujian, dan pembuatan produksi. Setiap bagian diakhiri dengan aplikasi yang berjalan, sehingga Anda dapat berhenti setelah salah satu bagian tersebut.

## Buat proyek

```bash
uvx nexy new notes
```

Jawab pertanyaannya dengan cara ini:

| Pertanyaan | Jawaban |
|---|---|
| Router berbasis file? | `Yes` untuk router berbasis file dan kustom, `No` untuk router modular |
| Jenis proyek | `Web` |
| Perutean sisi klien | `No`: server merender halaman |
| Kerangka klien | `React`: muncul kembali di unit 4, untuk pulau |
| Gaya | `Tailwind CSS` |
| Impor alias | `@` |
| ORM | `No database`: bagian 5 menambahkan satu |

<!-- router:custom -->
Router khusus adalah router berbasis file ditambah `APIRouter` yang sudah Anda miliki. Tutorial membangun aplikasi dengan file; [Sertakan router FastAPI yang ada](../routing/custom/README.md) yang menunjukkan cara memasang router Anda di sebelahnya.
<!-- /router -->

## Jalankan

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Buka <http://localhost:3000>. Anda akan melihat halaman selamat datang. Biarkan `nexy dev` berjalan: mulai sekarang, setiap file yang Anda simpan akan memuat ulang browser.

## Apa yang Anda pelajari

- `uvx nexy new` membuat proyek dan menginstal paket Python dan JavaScript-nya.
- `nexy dev` menyajikannya dan memuat ulang saat disimpan.
<!-- router:fbr,custom -->
- Halaman-halamannya ada di `src/routes/`: bagian selanjutnya menambahkan satu.
<!-- /router -->
<!-- router:modular -->
- Pengontrol dan pandangannya ada di `src/apps/`: bagian selanjutnya menambahkan satu.
<!-- /router -->

## Langkah selanjutnya

- [Bagian 2: halaman dan tata letak](pages-and-layouts.md)
- [Struktur proyek](../getting-started/project-structure.md): untuk apa setiap file proyek
