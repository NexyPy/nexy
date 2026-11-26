# Middleware dan keamanan

Nexy berjalan pada FastAPI dan Starlette, sehingga middleware mereka berlaku. Yang umum adalah satu baris di `nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Setiap kamus `use*` diteruskan sebagai argumen kata kunci ke middleware Starlette yang cocok: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Middleware Anda sendiri

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` mengambil kelas middleware ASGI.

## Pembatasan tarif

`useRateLimit` menjawab `429 Too Many Requests` ke alamat klien yang mengirimkan lebih dari `requests` permintaan dalam satu jendela `per` detik.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy menjamin bahwa permintaan yang melebihi batas akan mendapatkan `429` dengan header `Retry-After`, beberapa detik tersisa di jendela, dan tidak pernah mencapai rute, tindakan, atau middleware Anda.

Nexy menjamin bahwa tanpa `useRateLimit` tidak ada middleware batas kecepatan yang ditambahkan.

Nexy menjamin bahwa probe `useHealth` tidak pernah dibatasi.

`paths` bersifat opsional: tanpanya setiap jalur akan terbatas. Tindakan server disajikan di bawah `/_nx_`, sehingga awalan membatasi semuanya.

Jendela diperbaiki dan dibagikan oleh semua klien: penghitungan dimulai lagi pada setiap kelipatan `per` detik. Oleh karena itu, klien dapat mengirim hingga dua kali `requests` melintasi tepi jendela.

Hitungannya hidup dalam ingatan setiap pekerja. Dengan `useWorkers` di atas satu, klien dapat mengirim `requests` ke setiap pekerja, dan penghitungan dimulai lagi saat server dimulai ulang.

Alamat klien adalah alamat yang diberikan uvicorn untuk meminta. Di balik proxy terbalik pada mesin yang sama, uvicorn membacanya dari `X-Forwarded-For`; untuk proxy di komputer lain, cantumkan alamatnya di variabel lingkungan `FORWARDED_ALLOW_IPS`, atau setiap klien akan berbagi alamat proxy tersebut.

Aplikasi Anda bertanggung jawab atas batas yang dibagikan oleh beberapa pekerja atau server: proxy terbalik atau toko seperti Redis.

## HTTPS

Sajikan HTTPS secara langsung dengan `useSslKeyfile` dan `useSslCertfile`, atau hentikan TLS di proksi terbalik dan atur `useHTTPSRedirect`. Dalam pengembangan, server pengembang Vite tetap menggunakan HTTP loopback di belakang asal Nexy, sehingga TLS tidak pernah mencapainya.

## Daftar periksa produksi

- `useDocs = False` jika skema OpenAPI tidak boleh dipublikasikan.
- `useTrustedHost` disetel ke domain Anda, untuk memblokir serangan header host.
- `useCORS` dengan asal usul yang jelas, tidak pernah `["*"]` bersama dengan kredensial.
- `secret_key` nyata untuk sesi, dibaca dari lingkungan.
- Props yang diteruskan ke komponen klien di-escape oleh Nexy. Jangan tandai masukan pengguna `| safe` di templat.

## Penjaga dan ketergantungan

Perlindungan per rute menggunakan dependensi FastAPI. `dependencies.py` dalam direktori rute berlaku untuk semua yang ada di bawahnya: lihat [Dependensi](../routing/fbr/dependencies/README.md). Dalam router modular gunakan [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Langkah selanjutnya

- [Konfigurasi](../reference/config.md): setiap bidang middleware
- [Menyebarkan](../deployment/README.md)
- [Pertunjukan](../deployment/performance.md)
