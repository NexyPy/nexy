# Bereitstellen

Zwei Befehle: `nx build` produziert die Artefakte, `nx start` stellt sie bereit.

**Bevor Sie beginnen:** ein Projekt, das lokal mit `nx build` erstellt wird, und – für Clientseiten – die Frontend-Toolchain, die `nx new` installiert hat.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

Die Laufzeit benötigt nur Python. Uvicorn stellt die kompilierte App und die statischen Assets bereit; Es sind kein Node-Prozess und kein Vite-Prozess beteiligt.

## Was der Build erzeugt

`__nexy__/` enthält die kompilierten Routenmodule, das Client-Bundle unter `__nexy__/client/` und den vorgerenderten HTML-Code für Framework-Routen. Kopieren Sie das Projekt – Quelle plus `__nexy__/` – oder erstellen Sie es im Image.

## Docker

Die Build-Phase benötigt Node (für Vite) und Python (für den Compiler). Die Laufzeitstufe benötigt nur Python.

```dockerfile filename="Docker-Datei"
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

`uv` ruft ein verwaltetes Python ab, wenn das Basis-Image keines hat, weshalb die Build-Phase von einem Knoten-Image aus beginnen kann.

## Hinter einem Reverse-Proxy

Führen Sie `nx start` auf localhost aus und lassen Sie Nginx, Caddy oder den Plattform-Proxy TLS beenden:

```bash
nx start --host 127.0.0.1 --port 8000
```

Stellen Sie sicher, dass der Proxy WebSocket Upgrades weiterleitet, wenn Sie `SOCKET`-Handler verwenden, und dass er den ursprünglichen Host weiterleitet – FastAPI erstellt daraus absolute URLs.

## Gesundheitscheck

<!-- router:fbr,custom -->
Fügen Sie eine Handler-Datei, `src/routes/api/health.py`, und prüfen Sie `/api/health` – anstelle einer Seite, die möglicherweise langsam gerendert wird:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
Fügen Sie einen Controller hinzu und prüfen Sie `/health/` – anstelle einer Ansicht, die möglicherweise langsam rendert:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

Listen Sie es im `controllers` des Root-Moduls auf.
<!-- /router -->

### Integrierte Endpunkte

Ein Load Balancer oder Kubernetes stellt zwei Fragen: Ist der Prozess aktiv und darf er Datenverkehr empfangen? Setze `useHealth` und Nexy antwortet beides, ohne Handler-Datei und ohne Controller:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useHealth = True
```

| Endpunkt | Antworten 200 | Antworten 503 |
|---|---|---|
| `GET /health/live` | während der Prozess antwortet | niemals |
| `GET /health/ready` | sobald die Anwendung gestartet ist | während es startet und sobald der Server es zum Stoppen auffordert |

Nexy garantiert, dass `/health/ready` das Starten und Herunterfahren des Servers verfolgt.

Nexy garantiert, dass beide Endpunkte aus dem Zugriffsprotokoll und dem OpenAPI-Schema fernbleiben.

Nexy garantiert, dass beide Endpunkte vor `useTrustedHost` und `useHTTPSRedirect` antworten, sodass eine über HTTP an die Adresse eines Pods gesendete Probe nicht abgelehnt wird.

Konventionell lassen Sie Ihre eigenen Routen von `/health/live` und `/health/ready` fern, während `useHealth` eingeschaltet ist: Die Endpunkte von Nexy antworten zuerst. `useHealth` ist standardmäßig `False`, sodass ein Projekt, das es nicht festlegt, beide Pfade behält.

Ihre Anwendung ist dafür verantwortlich, zu prüfen, wovon sie abhängt: `/health/ready` meldet den Lebenszyklus des Servers, nicht den Status einer Datenbank.

Richten Sie die Sonden eines Kubernetes `Deployment` auf sie:

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

## Statisches Hosting

Jede Seite ist HTML, aber Nexy geht von einem Server für das Routing und für API-Handler aus.

> [!NOTE]
> Es gibt keinen `--static` Build-Modus. Aus der `nx build`-Ausgabe muss in Ihrer Pipeline ein rein statischer Export generiert werden.

## Checkliste

- [ ] `nx build` in CI keine Warnungen für Routen, die voraussichtlich auf dem Server gerendert werden
- [ ] `nx start` wird mit Code 1 beendet und startet nichts, wenn eine Routendatei nicht geladen werden kann
- [ ] `NEXY_ACTION_SECRET` gesetzt oder `__nexy__/action.key` mit dem Build beibehalten
- [ ] `useDocs = False` in der Produktion, wenn das API-Schema nicht öffentlich sein soll
- [ ] `useTrustedHost` und `useHTTPSRedirect` sind für öffentliche Bereitstellungen festgelegt
- [ ] `useHealth = True` wenn ein Load Balancer oder Kubernetes die App prüft
- [ ] `__nexy__/` nicht festgeschrieben

## Nächste Schritte

- [Konfiguration](../reference/config.md): HTTPS, vertrauenswürdige Hosts, Sitzungen
- [Frontend](../guides/frontend.md): was Vite erstellt
- [Testen](../guides/testing.md): die Befehle, die in CI ausgeführt werden sollen
