# Leistung

Was `nx start` standardmäßig tut, was eingeschaltet werden soll und was gemessen wurde.

## Standardeinstellungen

| Bedenken | Standard | Ändern |
|---|---|---|
| Verarbeitet | einen Uvicorn-Worker pro CPU unter Linux und macOS, einen unter Windows | `nx start` führt die App über Uvicorn aus |
| Komprimierung | aus | `useGZip = {"minimum_size": 1000}` in [Config](../reference/config.md), oder Komprimierung am Reverse-Proxy |
| Statische Dateien | werden mit `ETag` und `Last-Modified` bereitgestellt, kein `Cache-Control` | setzt langlebiges Caching am Reverse-Proxy oder CDN für Hash-Bundles |
| HTML-Seiten | werden pro Anfrage gerendert, kein Cache | [ISR](../rendering/isr.md) mit `revalidate = N` |
| API-Dokumente | zu | `useDocs = False` in der Produktion |
| Knoten zur Laufzeit | keiner | `nx build` rendert Client-Komponenten vor |

## Gemessen

Eine lokale Ausführung, ein Uvicorn-Worker, Windows, Python 3.13, Keep-Alive-Verbindungen von einem Python-Ladevorgang
Generator auf derselben Maschine. Behandeln Sie die Zahlen als Grundlage für den Vergleich von Änderungen, nicht als
Benchmarking mit anderen Frameworks.

| Route | Parallelität | Anfragen pro Sekunde | p50 | p99 |
|---|---|---|---|---|
| Bare FastAPI JSON-Route | 16 | ~4.500 | 3,4 ms | 5,1 ms |
| Nexy JSON-Route (`src/routes/api/ping.py`) | 16 | ~2.900 | 5,2 ms | 9,8 ms |
| Nexy SSR-Seite (16 KB, 16 Komponenten) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Nexy SSR-Seite (16 KB, 16 Komponenten) | 64 | ~670 | 94 ms | 126 ms |

Lesen der Tabelle:

- Nexys eigene Schichten (Pfadkontext, Middleware) kosten etwa ein Drittel des Durchsatzes eines Bare
  FastAPI-Route.
- Eine vom Server gerenderte Seite kostet etwa 2 ms CPU, verteilt auf etwa 16 Vorlagen-Renderings (eines pro
  Komponente). Seiten mit weniger Komponenten sind proportional günstiger.
- Durchsatz skaliert mit Arbeitern. Unter Linux startet `nx start` bereits einen pro CPU.

## Praktische Ratschläge

1. Setzen Sie Nginx, Caddy oder den Rand Ihrer Plattform in den Vordergrund: TLS, HTTP/2, Brotli und langlebiges Caching für
   `/__nexy__/client/` Vermögenswerte sind ihre Stärken. Siehe [Bereitstellen](README.md).
2. Verwenden Sie [ISR](../rendering/isr.md) für Seiten, die sich weniger als einmal pro Minute ändern.
3. Hydrieren Sie langsam mit [Inseln](../rendering/islands.md), damit beim ersten Laden weniger JavaScript versendet wird.
4. Halten Sie die Anzahl der `.nexy` Komponenten pro Seite angemessen: Jede einzelne ist eine separate Vorlage
   rendern.
5. Messen Sie Ihre eigenen Routen. Zum Vergleich reicht ein lokaler Lastgenerator, der die Verbindungen aufrechterhält
   zwei Versionen einer Seite.

## Nächste Schritte

- [Bereitstellen](README.md)
- [Rendering](../rendering/README.md)
- [Config](../reference/config.md)