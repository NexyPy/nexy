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
| `useWorkers` | `0` | proses `nx start` berjalan; `0` adalah satu per CPU di Linux dan macOS, satu di Windows |
| `useCSR` | `False` | mode perutean sisi klien; `.nexy` rute dinonaktifkan |

## Rute

| Bidang | Bawaan | Artinya |
|---|---|---|
| `useRouter` | `None` | sebuah instance atau kelas `APIRouter` yang dipasang di sebelah rute berbasis file; `None` berarti hanya berbasis file |
| `excludeDirs` | `["templates", "extension", "docs"]` | direktori dilewati saat memindai rute |
| `useAliases` | `None` | alias impor, mis. `{"@": "src"}` (`@/components/Counter.tsx` berarti `src/components/Counter.tsx`); `nx new` tulis yang Anda pilih, dan Vite dan `tsconfig.json` mengikutinya |

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
| `useDocs` | `True` | melayani halaman referensi Skalar; `/openapi.json` disajikan dengan cara apa pun |
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

Atau matikan dengan `useDocs = False`. `/openapi.json` tetap dilayani dalam kedua kasus: menjaga rute proyek keluar dari jalur tersebut.

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
