# Dev-Symbolleiste

`nexy dev` fügt jeder HTML-Seite eine Symbolleiste hinzu. Es befindet sich in der unteren linken Ecke und zeigt Ihnen die Route
sind eingeschaltet und wie lange der Server gedauert hat, und öffnet sich in einem Panel. Es ist niemals Teil einer Produktion
Antwort.

| Registerkarte | Zeigt |
|---|---|
| Seite | URL, Route, Handler, die Datei, aus der sie stammt (mit einem Link, der sie in Ihrem Editor öffnet), Status, Serverzeit, erstes Byte, erste Farbe, Hauptinhalt, Layoutverschiebung (grün, gelb oder rot abgestuft), DOM-fähig |
| Routen | jede Route der App mit ihren Methoden, einem Filter und der aktuell markierten; Jeder verlinkt auf seine Datei |
| Fehler | Serverfehler seit dem Start von `nexy dev` und die Fehler, die der Browser ausgelöst hat |
| Einstellungen | Thema (an die Seite anpassen, dunkel oder hell), Position, Größe, Ausblenden, Zurücksetzen |

## Bewegen Sie es

Ziehen Sie die Schaltfläche: Sie folgt dem Zeiger und springt an die nächstgelegene Ecke, wenn Sie sie loslassen. Das Panel
öffnet sich von der Stelle aus, an der sich die Schaltfläche befindet, zur Mitte des Bildschirms. Die Position bleibt dabei erhalten
Browser. Sie können auch in den **Einstellungen** eine Ecke auswählen.

`Shift` + `Alt` + `D` blendet die Symbolleiste ein und aus. `Esc` schließt das Panel.

## Fehler

Ein nicht erkannter Fehler im Browser öffnet einen Dialog über der Seite mit der Nachricht und dem Stapel; mit
Mehrere Fehler, gehen Sie sie durch (1 von 3). Ein Serverfehler antwortet mit einer Seite der gleichen Art: der
Fehler, wo er ausgelöst wurde und der Code um ihn herum.

## Schalten Sie es aus

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

Die Symbolleiste ist ein Stilblock und ein Skript, das vor `</body>` hinzugefügt wurde: keine externe Anfrage, nein
Abhängigkeit. JSON, Dateien und jede Antwort, die nicht HTML ist, bleiben in Ruhe.

## Nächste Schritte

- [Config](../reference/config.md): jede Option
- [Testen](testing.md): Testen Sie eine Seite oder eine Komponente