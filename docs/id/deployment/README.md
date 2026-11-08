# Menyebarkan

Dua perintah: `nx build` menghasilkan artefak, `nx start` menyajikannya.

**Sebelum Anda memulai:** sebuah proyek yang dibangun secara lokal dengan `nx build`, dan - untuk halaman klien - rantai alat frontend yang `nx new` dipasang.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

Waktu proses hanya memerlukan Python saja. Uvicorn menyajikan aplikasi yang dikompilasi dan aset statis; tidak ada proses Node dan tidak ada proses Vite yang terlibat.

## Apa yang dihasilkan oleh bangunan tersebut

`__nexy__/` berisi modul rute yang dikompilasi, bundel klien di bawah `__nexy__/client/`, dan HTML yang telah dirender sebelumnya untuk rute kerangka kerja. Salin proyek - sumber plus `__nexy__/` - atau buat di dalam gambar.

## Docker

Tahap build membutuhkan Node (untuk Vite) dan Python (untuk compiler). Tahap runtime hanya memerlukan Python saja.

```dockerfile filename="file buruh pelabuhan"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` mengambil Python yang dikelola ketika gambar dasar tidak memilikinya, itulah sebabnya tahap pembangunan dapat dimulai dari gambar Node.

## Di belakang proxy terbalik

Jalankan `nx start` di localhost dan biarkan Nginx, Caddy atau proksi platform menghentikan TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

Pastikan proxy meneruskan WebSocket peningkatan jika Anda menggunakan penangan `SOCKET`, dan meneruskan host asli - FastAPI membuat URL absolut darinya.

## Pemeriksaan kesehatan

<!-- router:fbr,custom -->
Tambahkan file pengendali, `src/routes/api/health.py`, dan selidiki `/api/health` - daripada halaman yang mungkin dirender dengan lambat:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Tambahkan pengontrol, dan selidiki `/health/` - daripada tampilan yang mungkin dirender dengan lambat:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

Cantumkan di `controllers` modul root.
<!-- /router -->

### Titik akhir bawaan

Penyeimbang beban atau Kubernetes menanyakan dua pertanyaan: apakah prosesnya berjalan, dan bolehkah menerima lalu lintas? Setel `useHealth` dan Nexy menjawab keduanya, tanpa file pengendali dan tanpa pengontrol:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Titik akhir | Jawaban 200 | Jawaban 503 |
|---|---|---|
| `GET /health/live` | sementara proses menjawab | tidak pernah |
| `GET /health/ready` | setelah aplikasi dimulai | saat itu dimulai, dan setelah server memintanya untuk berhenti |

Nexy menjamin bahwa `/health/ready` mengikuti startup dan shutdown server.

Nexy menjamin bahwa kedua titik akhir tetap berada di luar log akses dan skema OpenAPI.

Nexy menjamin bahwa kedua endpoint menjawab sebelum `useTrustedHost` dan `useHTTPSRedirect`, sehingga penyelidikan yang dikirim melalui HTTP ke alamat sebuah pod tidak ditolak.

Berdasarkan konvensi, Anda menonaktifkan rute Anda sendiri `/health/live` dan `/health/ready` saat `useHealth` aktif: titik akhir jawaban Nexy terlebih dahulu. `useHealth` adalah `False` secara default, jadi proyek yang tidak menyetelnya akan mempertahankan kedua jalur.

Aplikasi Anda bertanggung jawab untuk memeriksa hal-hal yang bergantung padanya: `/health/ready` melaporkan siklus hidup server, bukan keadaan database.

Arahkan probe Kubernetes `Deployment` ke mereka:

```yaml filename="k8s/deployment.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.example.com/app:1.0
          ports:
            - containerPort: 8000
          livenessProbe:
            httpGet:
              path: /health/live
              port: 8000
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 8000
            periodSeconds: 5
```

## Hosting statis

Setiap halaman adalah HTML, tetapi Nexy mengasumsikan server untuk perutean dan penangan API.

> [!NOTE]
> tidak ada mode pembuatan `--static`. Ekspor statis murni harus dibuat di saluran Anda dari keluaran `nx build`.

## Daftar periksa

- [ ] `nx build` di CI, tidak ada peringatan untuk rute yang Anda harapkan akan dirender di server
- [ ] `nx start` keluar dengan kode 1, dan tidak memulai apa pun, ketika file rute tidak dapat dimuat
- [ ] `NEXY_ACTION_SECRET` disetel, atau `__nexy__/action.key` disimpan dengan build
- [ ] `useDocs = False` dalam produksi jika skema API tidak boleh bersifat publik
- [ ] `useTrustedHost` dan `useHTTPSRedirect` ditetapkan untuk penerapan publik
- [ ] `useHealth = True` ketika penyeimbang beban atau Kubernetes menyelidiki aplikasi
- [ ] `__nexy__/` tidak dilakukan

## Langkah selanjutnya

- [Konfigurasi](../reference/config.md): HTTPS, host tepercaya, sesi
- [Frontend](../guides/frontend.md): apa yang Vite buat
- [Pengujian](../guides/testing.md): perintah untuk dijalankan di CI
