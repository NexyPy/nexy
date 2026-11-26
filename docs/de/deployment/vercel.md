# Wie stelle ich eine Nexy-App auf Vercel bereit?

Führen Sie `nx add vercel` aus, übergeben Sie die generierten Dateien zusammen mit Ihrer `nx build`-Ausgabe und verweisen Sie die Vercel-Laufzeitumgebung Python auf `src/server.py:app`.

## Fügen Sie die Plattformdateien hinzu

Aus dem Stammverzeichnis eines Nexy-Projekts:

```bash
nx add vercel
nx build
```

`nx add vercel` schreibt `src/server.py` und `vercel.json`. Außerdem werden Ignorierregeln für die Dateien angehängt, die sich während der Ausführung der App ändern: `__nexy__/build-cache.json`, `__nexy__/server.port`, `__nexy__/.temp/` und `__pycache__/`. Wenn Sie den Befehl erneut ausführen, bleiben bereits vorhandene Dateien erhalten und die Ignorierregeln werden nicht dupliziert.

## Richten Sie Vercel auf die App

Wählen Sie in den Vercel-Projekteinstellungen die Laufzeitumgebung Python aus und verwenden Sie `src/server.py:app` als Einstiegspunkt. Vercel entdeckt den Namen `app` in diesem Modul; `nx start` ist nicht beteiligt.

Das generierte `src/server.py` importiert das Lazy `nexy.app.app`, nachdem es den Arbeitsordner vorbereitet hat. Sie können denselben Einstiegspunkt mit `uvicorn src.server:app` lokal verwenden.

## Übernehmen Sie die Build-Ausgabe

Wenn Vercel keinen Build-Befehl hat, empfängt es nur das, was das Repository enthält. Commit `__nexy__/` nach jedem `nx build`, mit den kompilierten Routen, dem Client-Bundle unter `__nexy__/client/` und dem Manifest unter `__nexy__/client/.vite/manifest.json`.

Behalten Sie `vite.config.ts` im Projektstamm und übernehmen Sie es. In der Produktion liest Nexy das Vite-Manifest, um die Stylesheet- und Skript-Tags zu schreiben, gibt diese Tags jedoch nur aus, wenn `vite.config.ts` vorhanden ist. Ohne diese Datei antwortet die Seite immer noch mit 200 und kommt ohne CSS oder Client an JavaScript.

`__nexy__/build-cache.json` nicht festschreiben: Es enthält absolute Pfade von der Maschine, auf der der Build ausgeführt wurde. `__nexy__/server.port` gehört zu `nx start` und `__nexy__/.temp/` ist der Arbeitsspeicher.

## Akzeptieren Sie ein schreibgeschütztes Dateisystem

Vercel stellt das Projekt schreibgeschützt bereit, während eine Python-Anwendung gestartet wird. Nexy schreibt generierte Dateien während des Startvorgangs, sodass ein bloßes `from nexy.app import app` mit `OSError: [Errno 30] Read-only file system` fehlschlagen kann.

Der generierte Einstiegspunkt kopiert sechs Projektelemente in einen beschreibbaren temporären Ordner, bevor die App importiert wird: `src`, `__nexy__`, `public`, `nexyconfig.py`, `pyproject.toml` und `vite.config.ts`. Es ändert das Arbeitsverzeichnis und legt die Kopie zuerst auf `sys.path`, da Nexy Routen aus dem aktuellen Verzeichnis auflöst. Fügen Sie alle anderen Dateien, die Ihre App zur Laufzeit liest, manuell zu dieser Liste hinzu.

## Statische Assets zwischenspeichern

Das generierte `vercel.json` enthält die beiden Cache-Regeln, die eine bereitgestellte Nexy-Site verwendet: Dateien unter `/assets/` sind ein Jahr lang unveränderlich, und Bilder und Schriftarten unter `public/` bleiben einen Tag lang aktuell mit einem einwöchigen Verfallsfenster während der erneuten Validierung. Fügen Sie weitere Regeln in derselben Datei hinzu, wenn Ihr Projekt diese benötigt.

## Überprüfen Sie die Bereitstellung

Importieren Sie vor dem Pushen den Einstiegspunkt und fragen Sie ihn nach einer Seite:

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

Öffnen Sie dann `/`, eine generierte Route und eine Datei unter `/assets/`. Vergleichen Sie die Antwort lokal mit `nx start`: Status, Inhaltstyp und Größe sollten übereinstimmen. Eine Seite, die um genau die beiden Client-Tags kleiner als die lokale ist, bedeutet, dass `vite.config.ts` im kopierten Projekt fehlte.
