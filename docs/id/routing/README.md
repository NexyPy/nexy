# Perutean

Nexy memiliki dua router asli. Anda dapat memilih satu per fitur; mereka dapat hidup berdampingan dalam aplikasi yang sama.

**Tidak yakin? Gunakan perutean berbasis file.** Ini mencakup halaman dan titik akhir API tanpa pengaturan. Tambahkan router modular ketika backend memerlukan pengontrol, layanan yang disuntikkan, atau penjaga.

| Anda sedang membangun | Gunakan |
|---|---|
| Halaman, konten, situs dengan beberapa titik akhir | Berbasis file |
| API besar dengan layanan yang dibagikan ke seluruh rute | Modular |
| Keduanya: halaman untuk manusia, API terstruktur untuk mesin | Berbasis file dan modular bersama-sama |

```diagram filename="Sekilas tentang router berbasis file"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| Router | Sumber | Diaktifkan oleh |
|---|---|---|
| [Berbasis file (FBR)](fbr/README.md) | setiap file di bawah `src/routes/` | direktori ada |
| [Modular](modular/README.md) | pengontrol dan modul | `useRouter = AppModule` di `nexyconfig.py` |

FBR dipindai setiap kali `src/routes/` ada, bahkan dengan router modular terpasang.

## Hidup berdampingan dan prioritas

Anda dapat menggabungkan integrasi FBR, Modular, dan kustom. Nexy mendaftarkan rute-rute ini sesuai urutan penemuannya. Jika dua router menentukan jalur URL yang sama, router pertama yang terdaftar akan menang. 

*Catatan: Nexy saat ini tidak menyediakan diagnostik untuk tabrakan URL; rute pertama yang mengklaim suatu jalur hanya membayangi rute lainnya.*

## Perutean berbasis file

Rute adalah file. URL adalah jalurnya di bawah `src/routes/`, tanpa ekstensi. Seperti Next.js, sebuah proyek berada dalam salah satu dari dua mode, dipilih dengan `useCSR`:

| | `useCSR = False` (bawaan) | `useCSR = True` |
|---|---|---|
| Halaman | `.nexy`, `.md`, `.mdx` | file kerangka klien Anda |
| Tata letak akar | `layout.nexy` | `layout.tsx` (React) |
| Komponen klien | diperbolehkan, sebagai pulau di dalam halaman | halaman itu sendiri |
| Rute API | `.py` | `.py` |

Lihat [Mode server dan mode klien](fbr/modes.md).

| Bagian | Cakupannya |
|---|---|
| [fbr/pages](fbr/pages/README.md) | halaman, [rute dinamis](fbr/pages/dynamic-routes.md) dan grup rute |
| [fbr/tata letak](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` penangan rute, [validasi dan kesalahan](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` dan penjaga, diwarisi berdasarkan direktori |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, diwarisi oleh direktori |
| [fbr/kesalahan](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, kesalahan JSON |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | penautan, navigasi klien, [hook](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket penangan |
| [fbr/inheritance](fbr/inheritance.md) | bagaimana tata letak, dependensi, dan halaman kesalahan diwarisi |

## Perutean modular

Pengontrol, modul dan injeksi ketergantungan, dalam gaya NestJS. Lihat [Perutean modular](modular/README.md) dan [Nexy dan NestJS](modular/vs-nestjs.md).

## Integrasi Kustom

Anda juga dapat mengintegrasikan router FastAPI yang ada ke dalam proyek Nexy Anda. Lihat [Integrasi perutean khusus](custom/README.md).

## Langkah selanjutnya

- [Perutean berbasis file](fbr/README.md)
- [Render](../rendering/README.md)
- [Views](../views/README.md): apa yang ada di dalam file
