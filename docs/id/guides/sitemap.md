# Bagaimana cara menambahkan sitemap.xml dan robots.txt ke situs Nexy?

Tetapkan `useSiteUrl` di `nexyconfig.py`: Nexy kemudian menyajikan `/sitemap.xml`, yang mencantumkan setiap halaman statis proyek, dan `/robots.txt` yang mengarahkan mesin pencari ke sana.

## Aktifkan dengan `useSiteUrl`

`useSiteUrl` adalah situs asal publik, yang dilihat mesin pencari:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` dan `nx start` lalu jawab kedua file tersebut. Tanpa `useSiteUrl` tidak ada satu pun yang ada, jadi proyek tidak akan pernah memublikasikan URL server pengembangnya secara tidak sengaja.

## Apa yang tercantum dalam peta situs

Peta situs memberikan setiap halaman sebagai URL absolut pada `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Sebuah rute dicantumkan ketika menjawab HTML ke `GET` pada jalur tetap:

<!-- router:fbr,custom -->
- halaman (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) dicantumkan;
- halaman dinamis, seperti `src/routes/users/[id].nexy`, tidak disertakan: Nexy tidak dapat mengetahui nilainya;
- pengendali rute Python menjawab JSON, sehingga diabaikan.
<!-- /router -->

<!-- router:modular -->
- rute pengontrol yang menjawab HTML, dengan `@UseResponse(response_class=HTMLResponse)`, terdaftar;
- rute dengan parameter jalur, seperti `/users/{id}`, tidak disertakan: Nexy tidak dapat mengetahui nilainya;
- rute yang menjawab JSON tidak disertakan.
<!-- /router -->

Rute yang disembunyikan dari skema API (`include_in_schema=False`) juga tidak disertakan.

## `robots.txt` yang dilayaninya

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Tulis sendiri saja

File Anda sendiri selalu menang, dan Nexy tidak pernah menimpanya:

- `public/robots.txt` atau `public/sitemap.xml` disajikan apa adanya, sebagaimana setiap file `public/` disajikan;
- rute proyek di `/robots.txt` atau `/sitemap.xml` mempertahankan jalurnya.

Tulis peta situs Anda sendiri untuk mencantumkan halaman dinamis, seperti satu URL per postingan blog.

## Langkah selanjutnya

- [Metadata halaman](../routing/fbr/pages/metadata.md): judul dan deskripsi yang ditampilkan mesin pencari
- [Konfigurasi](../reference/config.md): setiap pengaturan `nexyconfig.py`
- [Penerapan](../deployment/README.md): melayani proyek dalam produksi
