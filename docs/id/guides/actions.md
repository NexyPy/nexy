# Tindakan

Sebuah `@Action` mengubah fungsi Python menjadi titik akhir `POST`. Berbeda dengan pengendali API standar, ia dirancang sebagai jembatan komunikasi yang diketik: Nexy secara otomatis menghasilkan klien TypeScript, memvalidasi masukan, dan menangani respons.

**Sebelum Anda memulai:** proyek yang dibuat oleh [Mulai cepat](../getting-started/quick-start.md). Tindakan ada di sebelah halaman, di `src/actions/`.

```diagram filename="Siklus Aksi"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## Siklus Aksi

### 1. Definisikan
Suatu tindakan adalah fungsi normal Python yang ditandai dengan `@Action`. Nexy menggunakan tanda tangannya untuk menentukan kontrak API.

```python filename="src/aksi/pengguna.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

Parameternya adalah masukan, divalidasi oleh Pydantic. Parameter bernama `request` atau `response` dimasukkan dan bukan merupakan bagian dari input.

### 2. Validasi
Saat tindakan dipanggil, Nexy memvalidasi input berdasarkan petunjuk tipe fungsi. Jika suatu bidang hilang atau memiliki tipe yang salah, tindakan tidak dijalankan, dan `422 Unprocessable Entity` dikembalikan.

### 3. Jalankan
Logikanya berjalan di server. Karena ini adalah fungsi standar Python, Anda dapat menggunakan perpustakaan apa pun, mengakses database, atau memanggil layanan lain. Anda juga dapat memicu penyegaran halaman menggunakan `revalidate()`.

### 4. Buat serial
Nilai yang dikembalikan secara otomatis diserialkan ke JSON. Model Pydantic ditangani secara asli, dan tipe Python standar dipetakan ke padanan JSON-nya.

### 5. Konsumsi
Frontend menerima hasilnya dengan keamanan tipe penuh. Nexy menulis `__nexy__/src/actions.ts` dari tanda tangan Anda, dan `@nexy/actions` memutuskan untuk itu.

<!-- router:fbr,custom -->
```tsx filename="src/rute/pengguna.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
Komponennya adalah pulau tampilan yang dikembalikan oleh pengontrol:

```tsx filename="src/components/Pengguna Baru.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

Tanpa hook, suatu tindakan hanyalah sebuah fungsi `async`: `const user = await create_user({ name: "Ada" })`.

| Kerangka | Apa yang `useAction` kembalikan |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | sama, dengan `pending()`, `data()` dan `error()` sebagai pengakses |
| Vue | sama, dengan `pending`, `data` dan `error` sebagai referensi |
| Svelte | toko: `$save.pending`, `$save.data`, `$save.error`, ditambah `save.run(input)` dan `save.reset()` |

`useAction(action, { onSuccess, onError })` juga menerima dua panggilan balik. `run` tidak pernah melempar: kegagalan terjadi di `error` dan `run` diselesaikan dengan `undefined`.

Tipe berasal dari Python: `str` adalah `string`, `int` dan `float` adalah `number`, `list[T]` adalah `T[]`, model Pydantic atau `Enum` adalah tipe bernama, dan bidang dengan default adalah opsional dalam input. Tipe Pydantic yang tidak dapat dideskripsikan menjadi `unknown`.

## Kesalahan dan Kegagalan

Suatu tindakan bisa gagal pada tahapan yang berbeda. Anda harus membedakannya di UI Anda:

1.  **Kesalahan validasi (422)**: input tidak cocok dengan tanda tangan Python. `error.fields` memetakan setiap bidang yang tidak valid ke pesannya.
2.  **Kesalahan bisnis (`HTTPException`)**: kode Anda menolak panggilan, misalnya `403 Forbidden` atau `409 Conflict`.
3.  **Kesalahan server (500)**: pengecualian yang tidak tertangani terjadi pada kode Python Anda.
4.  **Kesalahan jaringan**: permintaan tidak pernah sampai ke server, misalnya waktu habis atau koneksi terputus.
5.  **Kesalahan otorisasi (401, 403)**: cek Anda sendiri menolak penelepon. Nexy tidak memutuskan ini untuk Anda.

Pemeriksaan asal yang dijelaskan di bawah ini adalah perlindungan CSRF, bukan otorisasi: pemeriksaan ini menyatakan dari mana panggilan itu berasal, tidak pernah siapa yang diizinkan melakukannya.

## Segarkan halaman setelah melakukan tindakan

Suatu tindakan menyatakan halaman mana yang perubahannya menjadi basi, seperti yang dilakukan Next.js pada `revalidatePath`:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

Jawabannya membawa jalur dalam header `x-nexy-revalidate`. Klien kemudian mengambil kembali halaman saat ini melalui router, atau memuat ulang ketika tidak ada router klien.

## Formulir tanpa JavaScript

Suatu tindakan juga mengambil bentuk HTML standar, sehingga halaman berfungsi sebelum skrip apa pun dimuat:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

Dalam templat `.nexy`, `__actions_path["name"]` adalah jalurnya, `__actions["name"]` adalah fungsinya, dan fungsi tersebut juga berada dalam cakupan dengan namanya sendiri.

Jika berhasil, pengunjung akan dikirim kembali ke halaman tempat formulir berada, dengan status `303`. Untuk menjawab berbeda, kembalikan objek `Response` (misalnya, `RedirectResponse("/done", status_code=303)`).

Formulir yang dikirim sebagai `application/x-www-form-urlencoded`, yang dilakukan browser secara default, tidak memerlukan paket tambahan. Tambahkan `enctype="multipart/form-data"` dan panggilan memerlukan `python-multipart`: tanpanya tindakan akan menjawab `500` dengan pesan yang menyebutkan perintah, `uv add python-multipart`.

Suatu tindakan membaca bidang, bukan file: masukan file mencapainya sebagai string. Untuk menerima upload, tulis rute di `src/routes/api/` dengan parameter `File` atau `UploadFile`.

## Keamanan

### Ketidakjelasan jalur bukanlah otorisasi
Jalur tindakannya adalah `/_nx_` diikuti dengan hash modul fungsi, namanya, dan rahasia proyek. Itu diatur oleh `NEXY_ACTION_SECRET`, atau disimpan di `__nexy__/action.key`, yang `nx build` dibuat sehingga bundel klien dan `nx start` setuju: simpan file itu dengan build. Jalur tersebut menyembunyikan titik akhir dari penemuan biasa, dan **jalur yang dihasilkan bukan merupakan mekanisme otorisasi**.

Siapa pun yang mengetahui jalannya dapat melakukan tindakan. Anda **harus** memverifikasi identitas dan izin pengguna di dalam tindakan:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Perlindungan asal
Untuk mencegah Pemalsuan Permintaan Lintas Situs (CSRF), Nexy menolak permintaan yang `Origin` merupakan situs lain atau yang ditandai oleh browser `Sec-Fetch-Site: cross-site` dengan `403`. Cantumkan situs yang mungkin menyerukan tindakan Anda di `NEXY_ALLOWED_ORIGINS`. Panggilan tanpa `Origin` (seperti `curl`) diterima.

## Kesalahan impor

Saat startup Nexy mengimpor setiap modul `src/` untuk menemukan tindakan. Modul yang gagal diimpor dilaporkan, dan modul lainnya masih dimuat:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Langkah selanjutnya

- [API](../routing/fbr/handlers/README.md): penangan eksplisit
- [Pengujian](testing.md#what-to-assert): cara menguji suatu tindakan
- [Konfigurasi](../reference/config.md): opsi middleware dan autentikasi
