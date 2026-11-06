# Tindakan dan Navigasi

Interaksi di Nexy ditangani melalui sistem terpadu **Tindakan** dan **Navigasi**, memastikan bahwa frontend dan backend tetap sinkron tanpa kode lem API manual.

## Kontrak Aksi

Sebuah **Action** adalah fungsi sisi server yang menangani mutasi (misalnya, memperbarui database). 

1.  **Input yang Diketik**: Tindakan ditentukan di Python dengan petunjuk tipe. Nexy menghasilkan klien TypeScript yang cocok, sehingga Anda mendapatkan pelengkapan otomatis dan validasi di IDE Anda.
2.  **Eksekusi Atom**: Suatu tindakan adalah permintaan `POST` tunggal.
3.  **Penanganan Hasil**: Tindakan mengembalikan hasil yang diketik yang dapat digunakan klien untuk memperbarui UI.

```python filename="src/aksi/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

Halaman ini memanggilnya dengan input Python yang dideklarasikan, dan mendapatkan kembali `Todo` yang diketik:

```tsx filename="src/rute/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

## Navigasi Sisi Klien

Navigasi di Nexy "cerdas". Alih-alih memuat ulang browser secara penuh, Nexy menukar konten halaman saat ini sambil tetap menjaga tata letak aktif tetap terpasang.

- **Komponen `Link`**: Gunakan komponen `Link` khusus kerangka kerja untuk melakukan transisi sisi klien.
- **Navigasi Terprogram**: Gunakan `useRouter()` dari `@nexy/client` dan panggil `push()` untuk mengubah halaman sebagai respons terhadap logika (misalnya, setelah login berhasil).

```tsx filename="src/komponen/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Selesai.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Koordinasi: Tindakan → Navigasi

Pola yang paling umum adalah melakukan suatu tindakan dan kemudian mengarahkan pengguna ke halaman baru.

**Alur Validasi Ulang:**
1.  Klien memanggil Tindakan.
2.  Aksi dijalankan di server dan memanggil `revalidate("/path")`.
3.  Server mengembalikan hasilnya dengan header `x-nexy-revalidate` yang memberi nama jalur basi.
4.  Klien memperbarui konten halaman untuk mencerminkan keadaan baru.

```python filename="src/aksi/sesi.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/rute/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```

`check_password` berarti cek Anda sendiri. Lihat [Tindakan](../../guides/actions.md) untuk kesalahan, formulir tanpa JavaScript dan keamanan.

## Implementasi Kerangka

API untuk memanggil tindakan dan bernavigasi bervariasi berdasarkan kerangka kerja. Lihat panduan **Perbedaan** untuk teknologi pilihan Anda:

- [React Perbedaan](../react/differences.md)
- [Vue Perbedaan](../vue/differences.md)
- [Svelte Perbedaan](../svelte/differences.md)
- [Solid Perbedaan](../solid/differences.md)
- [Preact Perbedaan](../preact/differences.md)
