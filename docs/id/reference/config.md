# Konfigurasi

Konfigurasi adalah kelas di `nexyconfig.py` di root proyek. Nexy memuatnya dari direktori tempat ia dijalankan; sebuah proyek tanpa file menggunakan default.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## pelayan

| Bidang | Bawaan | Artinya |
|---|---|---|
| `usePort` | `3000` | port untuk `dev` dan `start` |
| `useHost` | `"0.0.0.0"` | mengikat alamat |
| `useSslKeyfile`, `useSslCertfile` | `None` | melayani HTTPS secara langsung |
| `useDevTools` | `True` | toolbar `nexy dev` ditambahkan ke setiap halaman (info halaman, rute, kesalahan, konfigurasi); `False` menghapusnya. Tidak pernah hadir dalam produksi |
| `useHealth` | `False` | melayani `GET /health/live` dan `GET /health/ready` untuk penyeimbang beban dan probe Kubernetes; lihat [Menerapkan](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | isi permintaan terbesar yang dibaca pekerja, dalam byte (1 MiB); yang lebih besar adalah `413`, dan `0` mematikan batasnya. Naikkan untuk rute yang mengambil unggahan file |
| `useSiteUrl` | `None` | asal mula situs tersebut, seperti `"https://example.com"`; setelah diatur, Nexy melakukan servis `/sitemap.xml` dan `/robots.txt`. Lihat [Peta Situs dan robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | proses `nx start` berjalan; `0` adalah satu per CPU di Linux dan macOS, satu di Windows |
| `useCSR` | `False` | mode perutean sisi klien; `.nexy` rute dinonaktifkan |
| `useBasePath` | `None` | awalan publik untuk keseluruhan aplikasi, seperti `"/app"`; permintaan di luarnya menjawab 404, dan tautan yang dihasilkan, rute klien, panggilan tindakan, dan aset membawa awalan. Lihat [Menerapkan](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | lebar piksel `nx build` yang dihasilkan untuk gambar lokal; konversi memerlukan `Pillow`, dan tanpa itu gambar tetap menggunakan URL aslinya. Lihat [Gambar](../routing/fbr/navigation/linking-and-navigating.md#image) |
| `useISRCache` | `None` | Penyimpanan ISR: `None` atau `"memory"` untuk satu proses, `"file"` untuk satu host, `"redis"` untuk beberapa pekerja, pemetaan dengan `type` dan opsi, atau objek dengan `get`, `set` dan `invalidate`. Lihat [ISR](../rendering/isr.md#choose-a-store) |

## Modul

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useModuleRegistry` | `"https://registry.nexypy.dev"` | URL dasar `nx add` terbaca saat memasang `@scope/name`; https saja, dengan loopback http untuk registri lokal |
| `useRequireSignedModules` | `False` | menolak pelepasan tanpa tanda tangan yang terverifikasi; lihat [Memasang modul](../guides/install-modules.md#set-the-registry-and-its-trust-rules) |

## Basis data

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useORM` | `None` | ORM proyek: `"SQLModel"`, `"SQLAlchemy"` atau `"Tortoise-ORM"`. `nx new` menulisnya, dan `nx migrate` mengambil Alembic atau Aerich darinya; tanpanya, `nx migrate` mengambil ORM pertama yang diinstal. Lihat [Database](../guides/databases.md#migrations) |

## Rute

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useRouter` | `None` | sebuah instance atau kelas `APIRouter` yang dipasang di sebelah rute berbasis file; `None` berarti hanya berbasis file |
| `excludeDirs` | `["templates", "extension", "docs"]` | direktori dilewati saat memindai rute |
| `useAliases` | `None` | alias impor, mis. `{"@": "src"}` (`@/components/Counter.tsx` berarti `src/components/Counter.tsx`); `nx new` tulis yang Anda pilih, dan Vite dan `tsconfig.json` ikuti |

## Bagian depan

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useFF` | `None` | pabrik kerangka klien: `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | membangun dan melayani bundel klien dengan Vite |
| `useMarkdownExtensions` | `[]` | ekstensi tambahan untuk rendering `.md`/`.mdx` |
| `useWatchExtensions` | `None` | ekstensi tambahan yang diawasi oleh server dev |
| `useWatchExcludePatterns` | `None` | pola glob yang diabaikan oleh server pengembang |

> **Perlu diketahui**: `NexyConfigModel` menyatakan `useVite = False`; waktu proses `Config` defaultnya adalah `True`.

## Nama file yang dicadangkan

Setiap bidang menambahkan ekstensi ke peran yang dicadangkan. `useLayoutExtensions = ["md"]` membuat `layout.md` dicadangkan, persis seperti `layout.nexy`.

| Bidang | Menambahkan ekstensi ke |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## dokumentasi API

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useDocs` | `"dev"` | di mana halaman referensi Skalar dan `/openapi.json` disajikan: `"dev"` hanya di `nx dev`, `True` dalam produksi juga (skema mencantumkan setiap rute dan tindakan server), `False` tidak ada di mana pun |
| `useDocsUrl` | `"/docs"` | jalur halaman referensi API |
| `useRedocsUrl` | `"/redocs"` | dideklarasikan tetapi tidak ada rute yang dipasang |
| `useTitle` | `"Nexy App"` | OpenAPI judul dan judul halaman (`"Nexy"` di `NexyConfigModel`) |

### Gratis `/docs` untuk satu halaman proyek

Referensi API menjawab `/docs` sebelum rute mana pun, jadi `src/routes/docs.nexy` atau `src/routes/docs/[[...slug]].nexy` tidak pernah disajikan di sana. `nx dev` dan `nx start` beri nama halaman tersebut saat startup. Pindahkan referensi dengan `useDocsUrl`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Atau matikan dengan `useDocs = False`, yang juga berhenti ditayangkan `/openapi.json`. Saat referensi aktif, jauhkan rute proyek dari jalur tersebut.

## Perangkat Tengah

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useMiddlewares` | `[]` | Kelas middleware ASGI |
| `useCORS` | `None` | kwarg untuk `CORSMiddleware` |
| `useGZip` | `None` | kwarg untuk `GZipMiddleware` |
| `useTrustedHost` | `None` | kwarg untuk `TrustedHostMiddleware` |
| `useSession` | `None` | kwarg untuk `SessionMiddleware` |
| `useAuth` | `None` | konfigurasi middleware otentikasi |
| `useHTTPSRedirect` | `False` | mengalihkan HTTP ke HTTPS |
| `useRateLimit` | `None` | permintaan yang mungkin dikirim oleh satu alamat klien per jendela, seperti `{"requests": 60, "per": 60}`; satu lagi adalah `429` dengan `Retry-After`, dan `"paths": ["/api/"]` hanya membatasi awalan tersebut. Setiap pekerja menghitung sendiri-sendiri. Lihat [Pembatasan tarif](../guides/middleware-and-security.md#rate-limiting) |

## Markdown

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useTocDepth` | `"2-6"` | tingkat judul yang disertakan dalam daftar isi |
| `useTocTitle` | `"Table of Contents"` | Judul TOC |
| `useTocAuto` | `True` | menghasilkan daftar isi untuk Markdown halaman |

## Rute di luar pohon file

Bangun FastAPI `APIRouter` dan pasang dengan `useRouter`. Ini disajikan di sebelah rute berbasis file:

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Default di atas dibaca dari `nexy/core/config.py`.

## Dideklarasikan, belum dibaca

Bidang ini ada di `NexyConfigModel` tetapi tidak ada kode yang menggunakannya. Menyetelnya tidak berpengaruh:

`useViteDevUrl`, `useRTL`.

## Langkah selanjutnya

- [i18n](../guides/i18n.md): internasionalisasi
- [Frontend](../guides/frontend.md): `useFF` dan build klien
- [Penerapan](../deployment/README.md): opsi produksi
