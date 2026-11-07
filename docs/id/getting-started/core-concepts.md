# Konsep inti

Kata-kata yang digunakan dokumen lainnya - rute, halaman, tampilan, komponen, penangan, titik akhir - masing-masing dalam satu baris, dengan tautan ke halaman yang lebih dalam. Baru mengenal Nexy? Mulailah dengan [Apa itu Nexy?](what-is-nexy.md).

## Cara membaca dokumen ini

| Tingkat | Pertanyaan yang dijawabnya | Mulailah dengan |
|---|---|---|
| Arsitektur aplikasi | lapisan mana yang menjawab permintaan, dan apa yang ditolaknya | [Cara kerja Nexy](how-nexy-works.md) |
| Struktur aplikasi | di mana kode itu berada, dan menjadi apa sebuah file | [Struktur proyek](project-structure.md) |
| Presentasi dan rendering | apa yang dilihat pembaca, dan siapa yang menghasilkan HTML | [Penayangan](../views/README.md), [Perenderan](../rendering/README.md) |
| Interaksi aplikasi | apa yang dilakukan pembaca, dan apa tanggapannya | [Tindakan](../guides/actions.md) |

Level dibaca dalam urutan itu satu kali. Setelah itu, halaman yang Anda perlukan adalah pencarian, bukan kursus.

## Arsitektur aplikasi

Tiga cara untuk memutuskan kode mana yang menjawab URL. Itu adalah alternatif, bukan lapisan:

- **Perutean berbasis file (FBR)**: file di bawah `src/routes/` adalah rute. Standarnya.
- **Router modular**: pengontrol dan modul di bawah `src/apps/`, dideklarasikan dengan dekorator, untuk basis kode bergaya NestJS.
- **Router khusus**: FastAPI `APIRouter` yang sudah ada yang disertakan dalam aplikasi.

Pilihannya adalah satu baris kelas `NexyConfig` di `nexyconfig.py`.

<!-- router:fbr -->
Perutean berbasis file tidak memerlukan baris: tanpa `useRouter`, Nexy membaca `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
Router modular adalah modul root `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
Router khusus adalah `APIRouter` yang sudah Anda miliki:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Memilih salah satu dari ketiganya adalah satu keputusan. Memilih kerangka kerja frontend adalah hal lain yang terpisah: lihat [Memilih router](../routing/README.md) dan [Tampilan](../views/README.md).

## Struktur aplikasi

Lima gagasan yang berasal dari pembaca Next.js biasanya digabungkan menjadi satu. Keduanya bukanlah hal yang sama, dan perbedaannya menjelaskan sebagian besar pertanyaan "mengapa laman saya tidak dirender".

| Gagasan | Apa itu | Apa yang bukan |
|---|---|---|
| **Rute** | pola URL, dihasilkan oleh jalur file | satu file: satu file dapat menjawab beberapa URL (`[slug]`) |
| **Halaman** | file rute yang merender tampilan: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | titik akhir: ia menjawab dokumen, bukan data |
| **Lihat** | apa yang menghasilkan isi halaman: Jinja2 dan Python, Markdown, atau komponen klien | sebuah rute: tampilan yang sama dapat menyajikan beberapa halaman |
| **Komponen** | bagian yang dapat digunakan kembali yang diimpor halaman | sebuah rute: dalam mode server, sebuah komponen tidak pernah dilayani sendiri |
| **Pengendali rute** | fungsi file rute `.py`, dinamai menurut metode HTTP (`GET`, `POST`, …) | halaman: ia mengembalikan JSON, file atau `Response` |
| **Titik akhir** | pasangan (URL, metode) yang dijawab oleh penangan | seorang penangan: satu file dapat menjawab beberapa titik akhir |

Dalam satu kalimat: **halaman adalah file rute, tampilan adalah apa yang merendernya, komponen adalah apa yang digunakan kembali oleh halaman, penangan menjawab titik akhir.**

<!-- router:fbr -->
Kelimanya dalam satu proyek kecil:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/rute/blog/[siput].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

Frontmatter dan template di bawahnya adalah tampilan halaman; `Like` adalah komponen yang digunakan kembali.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
Pada router modular, rute adalah jalur pengontrol, dan penangan adalah salah satu metodenya, dinamai berdasarkan kata kerja HTTP:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

Halaman tetap berupa file `src/routes/`, atau tampilan yang dikembalikan pengontrol dengan `useViews`.
<!-- /router -->

<!-- router:custom -->
Dengan router khusus, rute adalah jalur `APIRouter` Anda, dan pengendali adalah fungsi yang didaftarkan oleh dekoratornya:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Halaman masih berupa file `src/routes/`: halaman `.nexy` menjawab di sebelah rute yang disertakan.
<!-- /router -->

Dua kata lagi yang muncul kembali di mana-mana:

- **Layout**: file `layout.*` yang membungkus halaman di bawah foldernya; yang root memiliki dokumen HTML. Lihat [Tata Letak](../routing/fbr/layouts/README.md).
- **Ketergantungan**: fungsi yang dijalankan sebelum penangan, diterapkan per rute atau per folder. Lihat [Ketergantungan](../routing/fbr/dependencies/README.md).

## Presentasi dan rendering

Dua keputusan independen, yang sering membingungkan:

- **Format** memutuskan file mana yang merender halaman: [Tampilan](../views/README.md).
- **Mode** memutuskan siapa yang memproduksi HTML dan kapan: [Perenderan](../rendering/README.md).

| Gagasan | Satu baris |
|---|---|
| Modus pelayan | server merender halaman `.nexy` dan `.md`; komponennya adalah pulau ([mode](../routing/fbr/modes.md)) |
| Modus klien | `useCSR = True`: file kerangka adalah rutenya, dan navigasi terjadi di browser |
| SSR, ISR, CSR, kepulauan | empat mode rendering, ditentukan per halaman kecuali CSR, yaitu per proyek ([perenderan](../rendering/README.md)) |
| Hidrasi | browser yang melampirkan kerangka kerja ke HTML yang sudah dikirim server ([pulau](../rendering/islands.md)) |
| Alat peraga | nilai yang diberikan induk ke komponen, dideklarasikan `name: prop[type]` dalam file `.nexy` ([berkas .nexy](../views/nexy/README.md)) |

Halaman mode server dengan satu pulau: server merender halaman, browser menghidrasi grafik hanya ketika grafik digulir hingga terlihat.

<!-- router:fbr,custom -->
```nexy filename="src/rute/penjualan.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
Pulau masuk dalam tampilan, dan pengontrol mengembalikan tampilan:

```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

```python filename="src/apps/sales_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/sales")
class SalesController:
    async def get(self):
        return useViews("src/apps/sales_view.nexy")
```
<!-- /router -->

## Interaksi aplikasi

| Gagasan | Satu baris |
|---|---|
| Tindakan | fungsi Python yang ditandai `@Action`, berfungsi sebagai `POST`, dapat dipanggil dari formulir atau sebagai fungsi yang diketik ([tindakan](../guides/actions.md)) |
| Formulir | formulir HTML yang diposkan ke suatu Tindakan, dengan kesalahan validasi kembali ke halaman ([tindakan](../guides/actions.md)) |
| Navigasi | tautan yang mengambil terlebih dahulu, dan kait yang membaca jalur, kueri, cookie, dan sesi ([kait](../routing/fbr/navigation/hooks.md)) |
| Pengambilan data | dilakukan oleh halaman atau penangan yang memerlukannya; Nexy tidak mengirimkan lapisan data klien ([handler](../routing/fbr/handlers/README.md)) |

Tindakan dan formulir yang diposkan ke dalamnya, yang berfungsi sebelum skrip apa pun dimuat:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

<!-- router:fbr,custom -->
```html filename="src/rute/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

<!-- router:modular -->
```html filename="src/apps/home_view.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```
<!-- /router -->

## Apa yang Nexy tidak lakukan

Otentikasi, otorisasi, database, internasionalisasi, pekerjaan latar belakang, email, pembayaran dan pencarian adalah **tanggung jawab aplikasi Anda**, bukan kerangka kerja. Nexy memberikan poin ekstensi dan mengatakan di mana harus memasang masing-masing poin: lihat [Apa yang diserahkan Nexy kepada Anda](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
Otentikasi, misalnya, dihubungkan ke ketergantungan folder yang dilindunginya. Nexy menjalankannya sebelum setiap rute di bawah; siapa penggunanya tetap menjadi keputusan Anda:

```python filename="src/routes/akun/dependensi.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
Otentikasi, misalnya, dihubungkan ke pelindung pada pengontrol yang dilindunginya. Nexy menjalankannya sebelum setiap penangan kelas; siapa penggunanya tetap menjadi keputusan Anda:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
Otentikasi, misalnya, dihubungkan ke ketergantungan router yang dilindunginya, seperti pada FastAPI; siapa penggunanya tetap menjadi keputusan Anda:

```python filename="src/akun.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

Alasannya bukan karena minimalisme itu sendiri: kerangka kerja yang memilih ORM atau perpustakaan autentikasi Anda telah memutuskan sesuatu yang hanya dapat diputuskan oleh aplikasi Anda.

## Langkah selanjutnya

- [Struktur proyek](project-structure.md): setiap folder dan file proyek
- [Glosarium](../reference/glossary.md): kata-kata yang sama, dalam satu indeks abjad
- [Cara kerja Nexy](how-nexy-works.md): lapisannya, siapa yang membuat apa, dan apa yang Nexy serahkan kepada Anda
