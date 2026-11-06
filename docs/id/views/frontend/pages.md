# Halaman Depan

**Page** adalah unit dasar aplikasi Nexy. Ini adalah sumber daya beralamat URL yang ditentukan oleh file di bawah `src/routes/`. 

Terlepas dari kerangka klien yang digunakan, setiap halaman mengikuti siklus hidup universal dan batasan arsitektur yang sama.

## Siklus Hidup Halaman

Saat pengguna menavigasi ke suatu halaman, Nexy melakukan langkah-langkah berikut:

1.  **Pencocokan Rute**: Router mengidentifikasi file yang sesuai dengan URL.
2.  **Pengambilan Data**: Server menjalankan materi depan Python halaman untuk mengambil data yang diperlukan.
3.  **Komposisi**: Halaman dibungkus dalam `layout.nexy` terdekat (atau tata letak kerangka kerja).
4.  **Rendering**: Hasilnya dirender ke HTML (melalui Jinja2, Markdown, atau framework SSR).
5.  **Hidrasi**: Jika halaman menggunakan kerangka klien, browser melampirkan logika interaktif ke HTML statis.

Langkah 2 hingga 4 dalam satu halaman mode server: pengambilan materi depan, rendering template, dan tata letak root membungkus hasilnya.

```nexy filename="src/rute/pengguna.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Perutean & URL

Perutean sepenuhnya berbasis file. URL ditentukan oleh jalur file di bawah `src/routes/`, dikurangi ekstensi.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Segmen Dinamis
Untuk membuat rute yang bervariasi berdasarkan parameter (misalnya profil pengguna), gunakan tanda kurung siku:
- `src/routes/user/[id].tsx` → `/user/123`

Nilai segmen (`123`) tersedia ke halaman melalui kait `useParams()` dari `@nexy/client`.

```tsx filename="src/rute/pengguna/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Grup Rute
Folder yang dibungkus dalam tanda kurung diabaikan oleh router tetapi memungkinkan Anda mengelompokkan file untuk tujuan organisasi atau tata letak bersama:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Metadata Halaman
Setiap halaman dapat menentukan metadata (judul, deskripsi, tag OpenGraph) yang dimasukkan Nexy ke dalam shell dokumen. Halaman `.nexy` mengaturnya dalam materi depannya, dengan literal atau dengan `setMetadata`:

```nexy filename="src/rute/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` adalah Python: halaman `.tsx`, `.vue` atau `.svelte` tidak memiliki ekspor `metadata`, jadi dalam mode klien tulis judul dan tag meta di tata letak root. Lihat [Metadata halaman](../../routing/fbr/pages/metadata.md) untuk setiap bidang.

## Implementasi Kerangka
Konsep-konsep di atas bersifat universal. Untuk melihat cara mengimplementasikan Halaman dalam kerangka spesifik Anda, lihat panduan **Perbedaan**:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
