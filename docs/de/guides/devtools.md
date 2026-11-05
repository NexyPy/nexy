# Dev-Symbolleiste

`nexy dev` fügt jeder HTML-Seite eine Symbolleiste hinzu. Es befindet sich in der unteren linken Ecke, zeigt die Route an, auf der Sie sich befinden, und wie lange der Server benötigt hat, und öffnet sich in einem Fenster. Es ist niemals Teil einer Produktionsreaktion.

| Registerkarte | zeigt |
|---|---|
| Seite | URL, Route, Handler, die Datei, aus der sie stammt (mit einem Link, der sie in Ihrem Editor öffnet), Status, Serverzeit, erstes Byte, erster Paint, Hauptinhalt, Layoutverschiebung (abgestuft grün, gelb oder rot), DOM-bereit |
| Routen | jede Route der App mit ihren Methoden, einem Filter und der aktuell markierten; Jeder verlinkt auf seine Datei |
| Fehler | Serverfehler seit dem Start von `nexy dev` und die Fehler, die der Browser ausgelöst hat |
| Einstellungen | Thema (an die Seite anpassen, dunkel oder hell), Position, Größe, Ausblenden, Zurücksetzen |

## Bewegen Sie es

Ziehen Sie die Schaltfläche: Sie folgt dem Zeiger und springt an die nächstgelegene Ecke, wenn Sie sie loslassen. Das Bedienfeld öffnet sich von der Stelle aus, an der sich die Schaltfläche befindet, zur Mitte des Bildschirms hin. Die Position wird in diesem Browser gespeichert. Sie können auch in den **Einstellungen** eine Ecke auswählen.

`Shift` + `Alt` + `D` blendet die Symbolleiste ein und aus. `Esc` schließt das Panel.

## Fehler

Ein nicht erkannter Fehler im Browser öffnet einen Dialog über der Seite mit der Nachricht und dem Stapel; Bei mehreren Fehlern diese durchgehen (1 von 3). Ein Serverfehler antwortet mit einer Seite derselben Art: dem Fehler, dem Ort, an dem er ausgelöst wurde, und dem Code um ihn herum.

## Schalten Sie es aus

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

Die Symbolleiste ist ein Stilblock und ein vor `</body>` hinzugefügtes Skript: keine externe Anfrage, keine Abhängigkeit. JSON, Dateien und jede Antwort, die nicht HTML ist, bleiben in Ruhe.

## Nächste Schritte

- [Config](../reference/config.md): jede Option
- [Testen](testing.md): Testen Sie eine Seite oder eine Komponente
