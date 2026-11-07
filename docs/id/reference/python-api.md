# Python API

Setiap nama Nexy diekspor ke kode Python Anda, berdasarkan modul. Pengujian memeriksa halaman ini terhadap kode di kedua arah: nama yang tercantum di sini harus ada, dan nama yang diekspor kode harus dicantumkan di sini.

## `nexy`

Komponen untuk templat `.nexy` dan kait permintaan.

| Nama | Apa itu |
|---|---|
| `Audio`, `Video` | pemain asli `<audio>` dan `<video>`, lihat [komponen](../views/nexy/components.md) |
| `Image` | sebuah `<img>` yang memuat dengan lambat secara default |
| `Link` | sisi klien `<a>` dengan prefetch opsional |
| `Import` | impor komponen klien ke halaman `.nexy` |
| `Template` | render templat Jinja2 dan Markdown |
| `Vite` | tag klien Vite yang dibutuhkan setiap halaman |
| `Form` | placeholder tanpa perilaku: gunakan `<form>` biasa dengan [aksi](../guides/actions.md) |
| `usePathname` | jalur permintaan saat ini |
| `useSearchParams` | string kueri sebagai dict |
| `useParams` | parameter jalur dinamis sebagai dict, seperti `useParams()` pada klien |
| `useQuery` | nama asli `useParams`, disimpan untuk halaman yang ada (tidak membaca string kueri) |
| `useRequest` | permintaan saat ini, yang tidak tercakup dalam kait lainnya |
| `useHeaders` | header permintaan sebagai dict dengan nama huruf kecil |
| `useUrl` | URL lengkapnya: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | apakah tautan mengarah ke halaman saat ini atau salah satu halaman induknya, untuk bilah navigasi |
| `useRouter` | `path`, `base_url` dan `url_for` dari permintaan saat ini |
| `useSession` | dict sesi, kosong ketika sesi tidak aktif |
| `useCookies` | permintaan cookie sebagai dict |
| `useToc` | daftar isi halaman saat ini, sebagai HTML |
| `useViews` | merender file tampilan seperti `about.tsx` dari handler |
| `setMetadata`, `useMetadata` | beri nama judul dan tag kepala halaman, dan tuliskan di tata letak |
| `redirect`, `permanentRedirect` | kirim pengunjung ke tempat lain (307, 308) dan hentikan permintaan |
| `notFound`, `forbidden`, `unauthorized` | jawab 404, 403 atau 401 dari mana saja |

Kait hanya berfungsi di dalam permintaan: lihat [kait](../routing/fbr/navigation/hooks.md).

<!-- router:fbr,custom -->
```nexy filename="src/rute/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

## `nexy.http`

Kosakata HTTP dari seorang penangan. Impor dari sini, bukan dari FastAPI, sehingga penangan Anda bergantung pada kontrak Nexy.

| Nama | Apa itu |
|---|---|
| `Request`, `Response` | permintaan masuk dan respons keluar |
| `HTTPException` | hentikan pawang dengan status dan `detail` |
| `status` | diberi nama kode status, seperti `status.HTTP_404_NOT_FOUND` |
| `Depends` | jalankan fungsi terlebih dahulu dan masukkan hasilnya |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | dari mana suatu parameter berasal |
| `Form`, `File`, `UploadFile` | kolom formulir dan unggahan (perlu `python-multipart`) |
| `BackgroundTasks` | pekerjaan yang berjalan setelah jawaban dikirim |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | jawaban dengan tipe konten tetap |
| `RedirectResponse` | pengalihan HTTP |
| `redirect`, `permanentRedirect` | memunculkan pengalihan (307, 308) dari halaman, pengendali, pengontrol, atau penjaga |
| `notFound`, `forbidden`, `unauthorized` | naikkan 404, 403 atau 401 dari tempat yang sama |
| `FileResponse`, `StreamingResponse` | jawab dengan file atau aliran |

<!-- router:fbr,custom -->
```python filename="src/routes/api/item/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/items/items_by_id_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


@Controller("/api/items/{id}")
class ItemsByIdApiController:
    async def get(self, id: int, key: str = Depends(api_key)):
        return {"id": id}
```

Cantumkan pengontrol di `controllers` modul root.
<!-- /router -->

## `nexy.decorators`

| Nama | Apa itu |
|---|---|
| `Action` | mengubah suatu fungsi menjadi titik akhir `POST`, lihat [tindakan](../guides/actions.md) |
| `revalidate` | beri tahu browser halaman mana yang tindakannya menjadi basi |
| `Module`, `Controller` | mendeklarasikan modul dan pengontrol di [router modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injeksi ketergantungan](../routing/modular/dependency-injection.md) dan masa pakainya |
| `UseGuard`, `Middleware` | menjaga atau membungkus satu pawang, lihat [penjaga](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | beri nama rute dan jelaskan untuk OpenAPI |
| `UseResponse`, `ResponseMeta` | jelaskan jawaban suatu rute |
| `HTTP_METHODS` | metode HTTP yang mungkin ditentukan oleh file penangan |
| `ACTIONS_STORE` | pencatatan tindakan, untuk perkakas dan pengujian |

```python filename="src/aksi/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Nama | Apa itu |
|---|---|
| `render` | HTML komponen `.nexy` untuk props tertentu, tanpa server, lihat [pengujian](../guides/testing.md) |

```python filename="tes/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## Dimana selanjutnya

- [Konfigurasi](config.md): kolom `use*` di belakang nama-nama ini
- [Pengecualian dan kesalahan](exceptions.md): jawaban dari setiap kegagalan
- [Indeks dokumentasi](../README.md): halaman untuk apa yang sedang Anda buat
