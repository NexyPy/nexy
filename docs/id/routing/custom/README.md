# Integrasi perutean khusus

Nexy memungkinkan Anda memasukkan aplikasi FastAPI yang ada sebagai router ke dalam proyek Anda. Ini berguna ketika Anda ingin menggunakan kembali logika backend dari layanan lain, berintegrasi dengan API pihak ketiga, atau membangun aplikasi komposit dengan beberapa masalah perutean.

Tidak seperti router berbasis file dan modular, yang merupakan bagian intrinsik Nexy, router khusus hanyalah sebuah `APIRouter` yang Anda pasang ke dalam aplikasi Anda.

## Kapan menggunakan router khusus

- **Layanan pihak ketiga**: Anda sudah memiliki aplikasi FastAPI yang ingin Anda ekspos melalui klien Nexy.
- **Penggunaan kembali kode**: Ekstrak logika backend dari proyek lain ke dalam router dan sertakan dalam yang baru.
- **Pola multi-penyewa atau mikro-frontend**: Setiap penyewa atau modul menyediakan routernya sendiri.
- **Migrasi bertahap**: Mulailah dengan `APIRouter` dan kembangkan menjadi modul Nexy lengkap nanti.

## Bagaimana cara kerjanya

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

Router dipasang secara otomatis oleh pemecah router Nexy. Rutenya tersedia dengan pola URL yang sama seperti di aplikasi aslinya. Tidak diperlukan konfigurasi tambahan.

## Membangun router khusus

1. **Buat routernya**
   ``` ular piton
   dari fastapi impor APIRouter

   api = APIRouter()
   @api.get("/status")
   status def async():
       kembalikan {"status": "oke"}
   ```

2. **Referensikan di `nexyconfig.py`**
   ``` ular piton
   dari .my_backend impor api

   gunakanRouter = api
   ```

3. **Akses rute**
   - Halaman berbasis file (`.nexy`, `.md`) dan pengendali modular dapat mereferensikan `/status` seperti pada rute lainnya.
   - Router berjalan dalam proses yang sama, sehingga dependensi, koneksi database, dan autentikasi berfungsi persis seperti di aplikasi aslinya.

## Integrasi dengan router lain

Proyek Nexy dapat menggabungkan:

- **Perutean berbasis file** (`src/routes/`) untuk halaman dan titik akhir sederhana
- **Perutean modular** (`useRouter = AppModule`) untuk backend terstruktur
- **Perutean khusus** (`useRouter = APIRouter`) untuk kode pihak ketiga

Ketiganya hidup berdampingan; setiap rute didaftarkan hanya satu kali. Router berbasis file selalu dipindai ketika `src/routes/` ada.

## Akses CLI ke aplikasi yang disertakan

Perintah `nexy dev` dan `nx` beroperasi pada router yang terpasang seperti router bawaan. Anda mendapatkan:

- Hot reload untuk titik akhir yang ditentukan di router khusus (jika menggunakan fitur server pengembang biasa `nexy` atau FastAPI)
- Validasi di `nexyconfig.py` (semua `APIRouter` berfungsi)
- Dokumen yang dibuat secara otomatis untuk rute yang disertakan (jika Anda mengaktifkannya)

## Keamanan dan isolasi

Karena router disertakan, tidak dipasang melalui `app.mount`, tidak ada lapisan ASGI tambahan. Router berada di objek aplikasi yang sama dengan rute berbasis file dan modular Anda. Artinya:

- Middleware yang ditambahkan oleh router khusus berlaku untuk semua permintaan.
- Penjaga dan injeksi ketergantungan yang ditentukan di router khusus dapat mengakses wadah yang sama dengan kode Anda sendiri (jika Anda menggunakan injeksi modular).
- Tidak ada awalan URL selain yang ditentukan oleh router itu sendiri.

Jika Anda memerlukan isolasi, gabungkan router dalam sub-aplikasi sebelum memasukkannya, atau gunakan teknik standar FastAPI.

## Contoh: Menyertakan proyek FastAPI yang sudah ada

Misalkan Anda memiliki `auth.py` di paket lain:

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

Dalam `nexyconfig.py`:

```python
from other_package.auth import api

useRouter = api
```

Titik akhir `/login` sekarang dapat dijangkau dari situs Nexy Anda tanpa memindahkan sebaris kode pun.

## Bagaimana memulainya

1. Buat `APIRouter` Anda (atau temukan di paket yang sudah ada).
2. Arahkan `useRouter` ke dalamnya di `nexyconfig.py`.
3. Akses rutenya melalui halaman, penangan, atau kerangka klien Anda.
4. Jika Anda memerlukan kontrol lebih besar, ubah router khusus menjadi router modular menggunakan `AppModule`.

## Langkah selanjutnya

- [Perutean berbasis file](../fbr/README.md) – Membangun halaman dan penangan sederhana dari file.
- [Perutean modular](../modular/README.md) – Backend terstruktur dengan injeksi dan pelindung.
- [Penanganan rute](../fbr/handlers/README.md) – Tentukan Python titik akhir.

Router khusus memberi Anda fleksibilitas untuk menggunakan kembali kode FastAPI yang ada sambil menjaga kesederhanaan halaman berbasis file dan struktur modular.