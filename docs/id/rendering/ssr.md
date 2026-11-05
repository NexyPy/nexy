# SSR (rendering server)

## Definisi

SSR adalah defaultnya: server merender halaman ke HTML untuk setiap permintaan. Tidak ada yang mengaktifkannya, dan tidak ada tanda yang mematikannya - proyek mode server dirender pada setiap permintaan kecuali halaman mendeklarasikan `revalidate`.

## Bagaimana cara kerjanya

| Berkas rute | Apa yang menghasilkan HTML | Kapan |
|---|---|---|
| `.nexy` | modul Python yang dikompilasi, melalui Jinja2 | setiap permintaan |
| `.md` | Markdown, lalu tata letak terdekat | setiap permintaan |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | kerangka kerja, dirender di Node | di build ketika rute tidak memiliki tata letak, sebaliknya di browser |
| `.py` | tidak ada: ia mengembalikan JSON atau `Response` | - |

Halaman Markdown dan handler, berdampingan dalam proyek yang sama:

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

## Siklus hidup rendering

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

## Kapan harus digunakan

- Halaman tersebut menunjukkan sesuatu yang dimiliki pembaca: sesi, akun, keranjang.
- Data harus segar pada setiap pemuatan.
- Konten harus dalam HTML untuk crawler yang tidak berjalan JavaScript.
- Halaman ini murah untuk dirender: satu kueri, satu templat.

Kasus pertama, halaman yang menyambut pembaca dari sesi:

```nexy filename="src/routes/akun.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```

## Konfigurasi

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

## Contoh

```nexy filename="src/rute/blog/[siput].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` menjalankan templat ini satu kali, dengan `slug` disetel ke `hello`. Permintaan kedua menjalankannya lagi: tidak ada yang disimpan di antara keduanya. String kueri bukan penyangga - bacalah dengan kait di [navigasi](../routing/fbr/navigation/hooks.md).

## Keterbatasan

- **Satu render per permintaan.** Dua pengunjung dalam detik yang sama masing-masing membayar untuk render dan kueri di baliknya.
- **Tidak ada cache.** Tidak ada cache respons bersama untuk pemanasan: [ISR](isr.md) menambahkan satu, per URL.
- **Streaming hanya membantu komponen yang menghasilkan.** Permintaan yang lambat di bagian atas halaman masih menunda byte pertama.
- **Tidak ada keluaran statis.** Dalam mode server tidak ada yang dibekukan saat build: tidak ada mode SSG, dan tidak ada perintah ekspor. Lihat [Render](README.md).
- **Pelarian otomatis tidak aktif** di templat `.nexy`. Hindari nilai yang tidak dipercaya dengan `| e`.

```nexy filename="src/rute/pencarian.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```

## Langkah selanjutnya

- [ISR](isr.md): cache halaman ini per URL
- [Pulau](islands.md): pertahankan SSR dan buat satu widget menjadi interaktif
- [CSR](csr.md): navigasi tangan ke browser
- [Kinerja](../deployment/performance.md)
