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

## HTTPS

Sajikan HTTPS secara langsung dengan `useSslKeyfile` dan `useSslCertfile`, atau hentikan TLS di proksi terbalik dan atur `useHTTPSRedirect`. Dalam pengembangan, server pengembang Vite tetap menggunakan HTTP loopback di belakang asal Nexy, sehingga TLS tidak pernah mencapainya.

## Daftar periksa produksi

- `useDocs = False` jika skema OpenAPI tidak boleh bersifat publik.
- `useTrustedHost` disetel ke domain Anda, untuk memblokir serangan header host.
- `useCORS` dengan asal usul yang jelas, tidak pernah `["*"]` bersama dengan kredensial.
- `secret_key` nyata untuk sesi, dibaca dari lingkungan.
- Props yang diteruskan ke komponen klien di-escape oleh HTML oleh Nexy. Jangan tandai masukan pengguna `| safe` di templat.

## Penjaga dan ketergantungan

Perlindungan per rute menggunakan dependensi FastAPI. `dependencies.py` dalam direktori rute berlaku untuk semua yang ada di bawahnya: lihat [Dependensi](../routing/fbr/dependencies/README.md). Dalam router modular gunakan [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Langkah selanjutnya

- [Konfigurasi](../reference/config.md): setiap bidang middleware
- [Menyebarkan](../deployment/README.md)
- [Kinerja](../deployment/performance.md)
