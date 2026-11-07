# Basis Data

`nx new` dapat merancah lapisan model dengan SQLModel, SQLAlchemy atau Tortoise-ORM. Nexy tidak membungkus ORM: Anda menggunakannya secara langsung, dari penangan dan halaman.

## Apa yang ditambahkan perancah

| Mengajukan | Tujuan |
|---|---|
| `src/configs/db.py` | mesin (SQLModel, SQLAlchemy) atau pengaturan `TORTOISE_ORM` |
| `src/models/` | kelas teladan |
| `src/services/` | fungsi yang menanyakan model |
| `.env` | `DATABASE_URL`, ditulis ketika Anda memberikan URL database pada saat `nx new` |

String koneksi berasal dari variabel lingkungan `DATABASE_URL`. Jika tidak disetel, mesin scaffold akan kembali ke file SQLite lokal, `dev.db`.

## Gunakan layanan di halaman

<!-- router:fbr,custom -->
```nexy filename="src/rute/pengguna/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Gunakan layanan di pengendali API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```
<!-- /router -->

<!-- router:modular -->
Pengontrol memanggil layanan, dan meneruskan baris ke tampilannya atau mengembalikannya sebagai JSON:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = UserService.get_all()
        return useViews("src/apps/users/user_view.nexy", context={"users": users})


@Controller("/api/users")
class UserApiController:
    async def get(self):
        return UserService.get_all()
```

```nexy filename="src/apps/users/user_view.nexy"
---
users: prop[list] = []
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```
<!-- /router -->

## Tortoise-ORM tidak sinkron

Sebuah halaman berjalan di loop peristiwa server dan tidak dapat menunggu, jadi `asyncio.run(...)` gagal di sana dengan "tidak dapat dipanggil dari loop peristiwa yang sedang berjalan". Perancah `src/configs/db.py` memberikan Tortoise sebuah loopnya sendiri, dalam satu thread, dan dua pembantu yang mengirimkan coroutine ke sana:

| Dimana kamu berada | Telepon | Apakah |
|---|---|---|
| kode sinkronisasi, seperti halaman | `run(UserService.get_all())` | menjalankannya dan mengembalikan hasilnya |
| kode async, seperti handler atau pengontrol | `await arun(UserService.get_all())` | sama, tanpa memblokir server |

<!-- router:fbr,custom -->
```nexy filename="src/rute/pengguna/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```
<!-- /router -->

<!-- router:modular -->
Pengontrol bersifat asinkron: ia menunggu layanan melalui `arun`, dan tampilan hanya menampilkan baris:

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

from src.configs.db import arun
from src.services.user_service import UserService


@Controller("/users")
class UserController:
    async def get(self):
        users = await arun(UserService.get_all())
        return useViews("src/apps/users/user_view.nexy", context={"users": users})
```
<!-- /router -->

Tortoise menghubungkan saat pertama kali salah satunya dipanggil. Panggil model dari `async def` (`await UserModel.all()` di dalam layanan), bukan di tingkat modul: panggilan di luar coroutine dijalankan sebelum Tortoise terhubung.

Cantumkan setiap modul yang menampung model di `TORTOISE_ORM` (entri `models` dari `src/configs/db.py`). Perancah mencantumkan model pengguna dan `aerich.models`; model dalam modul yang tidak terdaftar tidak ditemukan.

## Migrasi

`nx migrate` memilih alat untuk ORM Anda: Alembic untuk SQLModel dan SQLAlchemy, Aerich untuk Tortoise-ORM.

| Perintah | Apakah |
|---|---|
| `nx migrate --init` | inisialisasi alat migrasi untuk proyek tersebut |
| `nx migrate -m "add users"` | buat migrasi dari perubahan model Anda |
| `nx migrate --upgrade` | terapkan migrasi yang tertunda |

Dengan Aerich, `nx migrate` pertama dijalankan `aerich init-db`, yang membuat migrasi pertama dan tabel-tabelnya bersamaan; yang berikutnya menjalankan `aerich migrate --name "..."`, dan `--upgrade` menjalankan `aerich upgrade`.

`nx migrate` berhenti dengan pesan yang jelas ketika `DATABASE_URL` hilang atau database tidak dapat dijangkau (hanya Alembic: Aerich melaporkan kesalahannya sendiri).

### Migrasi pertama dibuat untuk Anda

Saat Anda memilih ORM dan memberikan URL database, `nx new` menyiapkan alat migrasi, membuat migrasi pertama dan menerapkannya, sehingga halaman pengguna menjawab pada `nexy dev` pertama. Alat migrasi (`alembic` atau `aerich`) dipasang di proyek dengan ORM.

Jika database tidak menjawab (server PostgreSQL tidak berjalan, driver hilang), `nx new` menjelaskan alasannya, lewati migrasi dan daftarkan dua perintah untuk dijalankan ketika sudah siap:

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Sampai tabel tersebut ada, halaman yang membaca database gagal dengan "tidak ada tabel seperti itu".

### Tambahkan model

Alembic membandingkan database dengan model yang `alembic/env.py` diimpor. Model dalam modul baru tidak akan terlihat sampai modul tersebut diimpor ke sana, di samping model pengguna:

```python filename="alembic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Untuk Tortoise-ORM, daftarkan modulnya di `TORTOISE_ORM` (lihat di atas).

## Langkah selanjutnya

- [Pengujian](testing.md): menguji penangan terhadap database sementara
- [Konfigurasi](../reference/config.md)
- [Penerapan](../deployment/README.md): mengatur `DATABASE_URL` dalam produksi
