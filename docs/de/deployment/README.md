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

Fügen Sie eine Handler-Datei, `src/routes/api/health.py`, und prüfen Sie `/api/health` – anstelle einer Seite, die möglicherweise langsam gerendert wird:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## Statisches Hosting

Jede Seite ist HTML, aber Nexy geht von einem Server für das Routing und für API-Handler aus.

> [!NOTE]
> Es gibt keinen `--static` Build-Modus. Aus der `nx build`-Ausgabe muss in Ihrer Pipeline ein rein statischer Export generiert werden.

## Checkliste

- [ ] `nx build` in CI keine Warnungen für Routen, von denen Sie erwarten, dass sie auf dem Server gerendert werden
- [ ] `nx start` wird mit Code 1 beendet und startet nichts, wenn eine Routendatei nicht geladen werden kann
- [ ] `NEXY_ACTION_SECRET` gesetzt oder `__nexy__/action.key` mit dem Build beibehalten
- [ ] `useDocs = False` in der Produktion, wenn das API-Schema nicht öffentlich sein soll
- [ ] `useTrustedHost` und `useHTTPSRedirect` sind für öffentliche Bereitstellungen festgelegt
- [ ] `__nexy__/` nicht festgeschrieben

## Nächste Schritte

- [Konfiguration](../reference/config.md): HTTPS, vertrauenswürdige Hosts, Sitzungen
- [Frontend](../guides/frontend.md): was Vite erstellt
- [Testen](../guides/testing.md): die Befehle, die in CI ausgeführt werden sollen
