# SSR (rendering server)

## Definisi

SSR adalah defaultnya: server merender halaman ke HTML untuk setiap permintaan. Tidak ada yang mengaktifkannya, dan tidak ada tanda yang mematikannya - proyek mode server dirender pada setiap permintaan kecuali halaman mendeklarasikan `revalidate`.

## Bagaimana cara kerjanya

<!-- router:fbr,custom -->
| Berkas rute | Apa yang menghasilkan HTML | Kapan |
|---|---|---|
| `.nexy` | modul Python yang dikompilasi, melalui Jinja2 | setiap permintaan |
| `.md` | Markdown, lalu tata letak terdekat | setiap permintaan |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | kerangka kerja, dirender di Node | di build ketika rute tidak memiliki tata letak, sebaliknya di browser |
| `.py` | tidak ada: ia mengembalikan JSON atau `Response` | - |

Halaman Markdown dan pengendali, berdampingan dalam proyek yang sama:

```md filename="src/rute/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

Rute komponen adalah satu kasus yang memerlukan kalimat kedua. Dalam produksi, rute komponen **tanpa** tata letak disajikan dengan HTML yang diproduksi saat build, dan komponen menghidrasinya. Dengan tata letak, atau dalam pengembangan, wadahnya kosong dan komponen dirender di browser - halaman tersebut kemudian menjadi shell yang mengisi dirinya sendiri.

Rute komponen tabel, tanpa tata letak, sehingga produksi menyajikan HTML-nya dari build:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Pengontrol kembali | Apa yang menghasilkan HTML | Kapan |
|---|---|---|
| `useViews("....nexy")` | modul Python yang dikompilasi, melalui Jinja2 | setiap permintaan |
| a `dict`, daftar, model | tidak ada: FastAPI menjawab JSON | - |

Tampilan dan titik akhir JSON, berdampingan dalam modul yang sama:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Siklus hidup rendering

<!-- router:fbr,custom -->
1. Permintaan tersebut mencapai router berbasis file. Jalurnya cocok, dan segmen dinamis dilemparkan ke tipe yang dideklarasikan oleh komponen.

   ```nama filenexy="src/routes/orders/[id].nexy"
   ---
   id: penyangga[int]
   ---
   <h1>Pesanan #{{ id + 1000 }}</h1>
   ```

   `/orders/42` menerjemahkan `Order #1042`; `/orders/abc` jawaban `404`.
2. Komponen berjalan. Yang menunggu di Node - dokumen klien - berjalan di kumpulan thread, sehingga tidak menghentikan perulangan peristiwa.
3. Tubuh dialirkan sebagai `text/html`. Komponen yang menghasilkan potongan akan mengalirkannya saat membuatnya.
4. Browser menerima HTML. Pulau-pulau tersebut terhidrasi menurut [arahan](islands.md) mereka.

Kesalahan muncul saat rendering diubah menjadi halaman oleh `errors.nexy` ketika proyek memilikinya: lihat [halaman kesalahan](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. Permintaan tersebut mencapai pengontrol. Parameter jalurnya dimasukkan ke tipe yang dideklarasikan oleh metode, dan diteruskan ke tampilan:

   ```nama file python="src/apps/order_controller.py"
   dari pengontrol impor nexy.decorators
   dari nexy.hooks impor useViews


   @Controller("/pesanan/{id}")
   pengontrol pesanan kelas:
       async def get(diri, id: int):
           kembalikan useViews("src/apps/order_view.nexy", konteks={"id": id})
   ```

   ```nama filenexy="src/apps/order_view.nexy"
   ---
   id: penyangga[int]
   ---
   <h1>Pesanan #{{ id + 1000 }}</h1>
   ```

   `/orders/42/` menerjemahkan `Order #1042`; `/orders/abc/` jawaban `404`.
2. Tampilan berjalan, dan `useViews` mengembalikan HTML-nya sebagai respons.
3. Browser menerima HTML. Pulau-pulau tersebut terhidrasi menurut [arahan](islands.md) mereka.

Kesalahan yang muncul saat rendering dijawab dengan halaman kesalahan default.
<!-- /router -->

## Kapan harus digunakan

- Halaman tersebut menunjukkan sesuatu yang dimiliki pembaca: sesi, akun, keranjang.
- Data harus segar pada setiap pemuatan.
- Konten harus dalam HTML untuk crawler yang tidak berjalan JavaScript.
- Halaman ini murah untuk dirender: satu kueri, satu templat.

Kasus pertama, halaman yang menyapa pembaca dari sesi tersebut. `useSession` membaca sesi `useSession` di `nexyconfig.py`, yang tanpanya akan gagal:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/akun.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Konfigurasi

<!-- router:fbr,custom -->
Tidak ada. Ada dua jalan keluar, dan mereka tidak memiliki butir yang sama:

| Meninggalkan SSR untuk | Lakukan ini | Gandum |
|---|---|---|
| satu halaman, dengan cache | `revalidate = 60` di bagian depannya → [ISR](isr.md) | halaman |
| keseluruhan proyek, dialihkan ke klien | `useCSR = True` di `nexyconfig.py` → [CSR](csr.md) | proyek |

Peralihan seluruh proyek, di `nexyconfig.py`. Mode klien memerlukan kerangka klien:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Tidak ada. Setiap tampilan yang dikembalikan pengontrol dirender pada setiap permintaan: [ISR](isr.md) dan [CSR](csr.md) adalah mode router berbasis file.
<!-- /router -->

## Contoh

<!-- router:fbr,custom -->
```nexy filename="src/rute/blog/[siput].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` menjalankan templat ini satu kali, dengan `slug` disetel ke `hello`. Permintaan kedua menjalankannya lagi: tidak ada yang disimpan di antara keduanya. String kueri bukan penyangga - bacalah dengan kait di [navigasi](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` menjalankan tampilan ini satu kali, dengan `slug` diatur ke `hello`. Permintaan kedua menjalankannya lagi: tidak ada yang disimpan di antara keduanya. String kueri bukan prop - bacalah dengan `useSearchParams`.
<!-- /router -->

## Keterbatasan

- **Satu render per permintaan.** Dua pengunjung dalam detik yang sama masing-masing membayar untuk render dan pertanyaan di baliknya.
- **Tidak ada cache.** Tidak ada cache respons bersama untuk menghangatkan: dengan rute file, [ISR](isr.md) menambahkan satu, per URL.
- **Streaming hanya membantu komponen yang menghasilkan.** Permintaan yang lambat di bagian atas halaman masih menunda byte pertama.
- **Tidak ada keluaran statis.** Dalam mode server tidak ada yang dibekukan saat build: tidak ada mode SSG, dan tidak ada perintah ekspor. Lihat [Render](README.md).
- **Pelarian otomatis tidak aktif** di `.nexy` templat. Hindari nilai-nilai yang tidak dipercaya dengan `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/rute/pencarian.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Langkah selanjutnya

<!-- router:fbr,custom -->
- [ISR](isr.md): cache halaman ini per URL
<!-- /router -->
- [Pulau](islands.md): pertahankan SSR dan buat satu widget menjadi interaktif
<!-- router:fbr,custom -->
- [CSR](csr.md): navigasi tangan ke browser
<!-- /router -->
- [Pertunjukan](../deployment/performance.md)
