# Python API

Setiap nama Nexy diekspor ke kode Python Anda, berdasarkan modul. Pengujian memeriksa halaman ini terhadap kode di kedua arah: nama yang tercantum di sini harus ada, dan nama yang diekspor kode harus dicantumkan di sini.

## `nexy`

Komponen untuk templat `.nexy` dan kait permintaan.

| Nama | Apa itu |
|---|---|
| `Audio`, `Video` | pemain asli `<audio>` dan `<video>`, lihat [komponen](../views/nexy/components.md) |
| `Image` | dan `<img>` yang dimuat dengan lambat secara default |
| `Link` | sisi klien `<a>` dengan prefetch opsional |
| `Import` | mengimpor komponen klien ke halaman `.nexy` |
| `Template` | render Jinja2 dan Markdown template |
| `Vite` | tag klien Vite yang dibutuhkan setiap halaman |
| `Form` | placeholder tanpa perilaku: gunakan `<form>` biasa dengan [aksi](../guides/actions.md) |
| `usePathname` | jalur permintaan saat ini |
| `useSearchParams` | string kueri sebagai dict |
| `useParams` | parameter jalur dinamis sebagai dict, seperti `useParams()` pada klien |
| `useQuery` | nama asli `useParams`, disimpan untuk halaman yang ada (tidak membaca string kueri) |
| `useRequest` | permintaan saat ini, yang tidak tercakup dalam kait lainnya |
| `useHeaders` | header permintaan sebagai dict dengan nama huruf kecil |
| `useUrl` | URL lengkap: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | apakah tautan mengarah ke laman saat ini atau salah satu induknya, untuk bilah navigasi |
| `useRouter` | `path`, `base_url` dan `url_for` dari permintaan saat ini |
| `useSession` | dict sesi, kosong ketika sesi nonaktif |
| `useCookies` | permintaan cookie sebagai dict |
| `useToc` | daftar isi halaman saat ini, sebagai HTML |
| `useViews` | merender file tampilan seperti `about.tsx` dari handler |
| `setMetadata`, `useMetadata` | memberi nama judul dan tag kepala halaman, dan menuliskannya dalam tata letak |
| `redirect`, `permanentRedirect` | mengirim pengunjung ke tempat lain (307, 308) dan menghentikan permintaan |
| `notFound`, `forbidden`, `unauthorized` | jawaban 404, 403 atau 401 dari mana saja |

Kait hanya berfungsi di dalam permintaan: lihat [kait](../routing/fbr/navigation/hooks.md).

## `nexy.http`

Kosakata HTTP dari seorang penangan. Impor dari sini, bukan dari FastAPI, sehingga penangan Anda bergantung pada kontrak Nexy.

| Nama | Apa itu |
|---|---|
| `Request`, `Response` | permintaan masuk dan respons keluar |
| `HTTPException` | menghentikan pawang dengan status dan `detail` |
| `status` | memberi nama kode status, seperti `status.HTTP_404_NOT_FOUND` |
| `Depends` | menjalankan fungsi terlebih dahulu dan meneruskan hasilnya ke |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | dimana parameter berasal dari |
| `Form`, `File`, `UploadFile` | kolom formulir dan unggahan (membutuhkan `python-multipart`) |
| `BackgroundTasks` | pekerjaan yang dijalankan setelah jawaban dikirim |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | jawaban dengan tipe konten tetap |
| `RedirectResponse` | pengalihan HTTP |
| `redirect`, `permanentRedirect` | memunculkan pengalihan (307, 308) dari halaman, pengendali, pengontrol, atau penjaga |
| `notFound`, `forbidden`, `unauthorized` | menaikkan 404, 403 atau 401 dari tempat yang sama |
| `FileResponse`, `StreamingResponse` | jawaban dengan file atau aliran |

## `nexy.decorators`

| Nama | Apa itu |
|---|---|
| `Action` | mengubah fungsi menjadi titik akhir `POST`, lihat [tindakan](../guides/actions.md) |
| `revalidate` | memberi tahu browser halaman mana yang tindakannya dianggap basi |
| `Module`, `Controller` | mendeklarasikan modul dan pengontrol di [router modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injeksi ketergantungan](../routing/modular/dependency-injection.md) dan masa pakainya |
| `UseGuard`, `Middleware` | menjaga atau membungkus satu pawang, lihat [penjaga](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | beri nama rute dan jelaskan untuk OpenAPI |
| `UseResponse`, `ResponseMeta` | jelaskan jawaban suatu rute |
| `HTTP_METHODS` | metode HTTP yang dapat ditentukan oleh file pengendali |
| `ACTIONS_STORE` | pencatatan tindakan, untuk perkakas dan pengujian |

## `nexy.testing`

| Nama | Apa itu |
|---|---|
| `render` | HTML komponen `.nexy` untuk props tertentu, tanpa server, lihat [pengujian](../guides/testing.md) |

## Dimana selanjutnya

- [Konfigurasi](config.md): kolom `use*` di belakang nama-nama ini
- [Pengecualian dan kesalahan](exceptions.md): jawaban dari setiap kegagalan
- [Indeks dokumentasi](../README.md): halaman untuk apa yang sedang Anda buat
