# Leistung

Was `nx start` standardmäßig tut, was eingeschaltet werden soll und was gemessen wurde.

## Standardeinstellungen

| Sorge | Standard | Ändere es |
|---|---|---|
| Prozesse | ein Uvicorn Worker pro CPU unter Linux und macOS, einer unter Windows | `nx start` führt die App durch Uvicorn |
| Komprimierung | aus | `useGZip = {"minimum_size": 1000}` in [Konfiguration](../reference/config.md) oder komprimieren Sie am Reverse-Proxy |
| Statische Dateien | serviert mit `ETag` und `Last-Modified`, nein `Cache-Control` | Legen Sie langlebiges Caching am Reverse-Proxy oder CDN für Hash-Bundles fest |
| HTML-Seiten | Wird pro Anfrage gerendert, kein Cache | [ISR](../rendering/isr.md) mit `revalidate = N` |
| API-Dokumente | auf | `useDocs = False` in der Produktion |
| Knoten zur Laufzeit | keine | `nx build` rendert Clientkomponenten vorab |

Die beiden Schalter der Tabelle in `nexyconfig.py` und ISR auf einer Seite:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```
<!-- /router -->

<!-- router:modular -->
ISR ist ein Modus für Dateiseiten: Eine Ansicht, die ein Controller zurückgibt, wird bei jeder Anfrage gerendert.
<!-- /router -->

## Gemessen

Eine lokale Ausführung, ein Uvicorn Worker, Windows, Python 3.13, Keep-Alive-Verbindungen von einem Python Lastgenerator auf demselben Computer. Behandeln Sie die Zahlen als Grundlage für den Vergleich von Änderungen und nicht als Maßstab für andere Frameworks.

Die Nexy-JSON-Route der Tabelle ist diese Datei:

<!-- router:fbr,custom -->
```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/ping_controller.py"
from nexy.decorators import Controller


@Controller("/api/ping")
class PingController:
    async def get(self):
        return {"ok": True}
```

Die folgenden Zahlen wurden mit der Dateiroute gemessen. Messen Sie einen Controller auf die gleiche Weise, bevor Sie sich darauf verlassen.
<!-- /router -->

| Route | Parallelität | Anfragen pro Sekunde | S. 50 | S. 99 |
|---|---|---|---|---|
| Nackte FastAPI JSON-Route | 16 | ~4.500 | 3,4 ms | 5,1 ms |
| Nexy-JSON-Route (`src/routes/api/ping.py`) | 16 | ~2.900 | 5,2 ms | 9,8 ms |
| Nexy SSR-Seite (16 KB, 16 Komponenten) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Nexy SSR-Seite (16 KB, 16 Komponenten) | 64 | ~670 | 94 ms | 126 ms |

Lesen der Tabelle:

- Nexys eigene Schichten (Pfadkontext, Middleware) kosten etwa ein Drittel des Durchsatzes einer bloßen FastAPI-Route.
- Eine vom Server gerenderte Seite kostet etwa 2 ms CPU, verteilt auf etwa 16 Vorlagen-Renderings (eines pro Komponente). Seiten mit weniger Komponenten sind proportional günstiger.
- Der Durchsatz skaliert mit den Arbeitern. Unter Linux startet `nx start` bereits einen pro CPU.

## Praktische Ratschläge

1. Stellen Sie Nginx, Caddy oder den Edge Ihrer Plattform in den Vordergrund: TLS, HTTP/2, Brotli und langlebiges Caching für `/__nexy__/client/` Assets sind ihre Stärken. Siehe [Bereitstellen](README.md).
2. Verwenden Sie [ISR](../rendering/isr.md) für Seiten, die sich weniger als einmal pro Minute ändern.
3. Hydratieren Sie langsam mit [Inseln](../rendering/islands.md), damit die erste Ladung weniger versendet JavaScript.
4. Halten Sie die Anzahl der `.nexy` Komponenten pro Seite angemessen: Jede davon ist ein separates Vorlagenrendering.
5. Messen Sie Ihre eigenen Routen. Ein lokaler Lastgenerator, der die Verbindungen aufrechterhält, reicht aus, um zwei Versionen einer Seite zu vergleichen.

Tipp 1 mit Nginx: Die gehashten Client-Bundles werden ein Jahr lang zwischengespeichert, der Rest geht an Nexy.

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Nächste Schritte

- [Bereitstellen](README.md)
- [Rendern](../rendering/README.md)
- [Konfiguration](../reference/config.md)
