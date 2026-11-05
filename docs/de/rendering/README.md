# Rendern

Das Rendern beantwortet eine Frage: **Wer produziert den HTML-Code und wann**. Nexy hat vier Antworten und eine Standardantwort.

**Nicht sicher? Behalten Sie SSR bei.** Ändern Sie eine Seite nur, wenn Sie den Grund nennen können: Inhalt, der sich selten ändert (ISR), ein Widget, das den Browser benötigt (Insel) oder App-ähnliche Navigation (CSR).

## Wie es funktioniert

```diagram filename="Wer erstellt den HTML-Code und wann?"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Die vier Modi

| | SSR | ISR | CSR | Inseln |
|---|---|---|---|---|
| Daten werden gelesen | bei jeder Anfrage | bei jeder Regeneration | im Browser | bei jeder Anfrage |
| Der HTML-Code kommt von | dem Server | dem Server, dann einem Cache | dem Server für das erste Dokument, dem Browser danach | dem Server |
| JavaScript | nur für Inseln | nur für Inseln | das Framework-Bundle | nur die Insel |
| Flüssigkeitszufuhr | keine | keine | das gesamte Dokument | die Insel |
| Cache | keine | pro URL, im Speicher | keine | keine |
| Entschieden durch | Standard | `revalidate = N` auf der Seite | `useCSR = True` im Projekt | `directive` auf der Komponente |
| Körnung | Seite | Seite | **Projekt** | Komponente |

## Rendering-Lebenszyklus

Zwei Fakten erklären die meisten Überraschungen.

1. **Ein Projekt befindet sich in einem Modus.** `useCSR` wählt zwischen Servermodus (SSR, ISR, Inseln, `.nexy`, `.md`, `.mdx` Routen) und Clientmodus (Framework-Routen und ein Client-Router). Die beiden können nicht gemischt werden: siehe [Servermodus und Clientmodus](../routing/fbr/modes.md).
2. **Im Servermodus erfolgt der Modus pro Seite.** Eine Seite kann mit `revalidate` zwischengespeichert werden, eine andere kann eine Insel enthalten, eine dritte kann keines von beidem.

Im Client-Modus wird immer noch ein echtes Dokument gesendet: Nexy rendert es in Node für die erste Antwort, dann übernimmt der Browser die Navigation. Eine CSR-Seite ist keine leere Seite, die auf ein Paket wartet.

## Wann zu verwenden

- **Inhalt, Marketing, Dokumentation**: SSR, plus ISR, wenn sich der Inhalt selten ändert.
- **Eine größtenteils statische Seite mit einem interaktiven Widget**: SSR mit einer Insel.
- **Dashboards, Editoren, App-ähnliche Navigation**: CSR.
- **Eine Seite, die ständig gelesen und selten geändert wird**: ISR.

## Konfiguration

| Modus | Wobei |
|---|---|
| SSR | nirgendwo: Es ist die Standardeinstellung |
| ISR | `revalidate = 60` im Titelblatt einer `.nexy` Seite |
| CSR | `useCSR = True` in `nexyconfig.py`, wobei `useFF` auf | gesetzt ist
| Inseln | `directive="client:visible"` auf dem Komponenten-Tag |

## Beispiel

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

Die gleiche Seite ohne die Frontmatter-Zeile ist SSR.

## Einschränkungen

- **Es gibt keinen SSG-Modus.** Nexy rendert HTML zur Erstellungszeit vor (Komponenten-HTML, Clientdokumente), liest es jedoch immer über den Server zurück: kein Exportbefehl, kein eigenständiger Ordner zum statischen Hosten. Für eingefrorene Inhalte verwenden Sie ISR mit einem langen Fenster.
- **ISR ist kein CDN.** Der Cache befindet sich in dem Prozess, der die Seite rendert; Mehrere Arbeiter halten mehrere Caches. Siehe [ISR](isr.md).
- **CSR ist eine Projektentscheidung.** Sie können nicht eine Seite CSR erstellen und die restliche Seite SSR behalten.
- **Inseln befeuchten die Insel, nicht die Seite.** Eine Seite, deren Inseln alle voneinander abhängen, ist eine getarnte CSR-Seite.

## Nächste Schritte

- [SSR](ssr.md): die Standardeinstellung
- [ISR](isr.md): Eine Seite pro URL zwischenspeichern
- [CSR](csr.md): Handnavigation zum Browser
- [Inseln](islands.md): Hydrate ein Widget
- [Leistung](../deployment/performance.md)
