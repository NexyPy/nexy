# SSR (Server-Rendering)

## Definition

SSR ist die Standardeinstellung: Der Server rendert die Seite für jede Anfrage in HTML. Nichts aktiviert es und kein Flag schaltet es aus – ein Projekt im Servermodus wird bei jeder Anfrage gerendert, es sei denn, eine Seite deklariert `revalidate`.

## Wie es funktioniert

| Routendatei | Was erzeugt den HTML | Wann |
|---|---|---|
| `.nexy` | das kompilierte Modul Python bis Jinja2 | jede Anfrage |
| `.md` | `cmarkgfm`, dann das nächstgelegene Layout | jede Anfrage |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | das Framework, gerendert in Node | beim Build, wenn die Route kein Layout hat, andernfalls im Browser |
| `.py` | nichts: Es gibt JSON oder ein `Response` zurück. | - |

Eine Komponentenroute ist der einzige Fall, der einen zweiten Satz benötigt. In der Produktion wird eine Komponentenroute **ohne** ein Layout mit dem beim Build erzeugten HTML bereitgestellt und die Komponente hydratisiert es. Bei einem Layout oder in der Entwicklung ist der Container leer und die Komponente wird im Browser gerendert – die Seite ist dann eine Hülle, die sich selbst füllt.

## Rendering-Lebenszyklus

1. Die Anfrage erreicht den dateibasierten Router. Der Pfad wird abgeglichen und dynamische Segmente werden in die von der Komponente deklarierten Typen umgewandelt.
2. Die Komponente läuft. Eines, das auf Node wartet – ein Clientdokument – ​​wird in einem Thread-Pool ausgeführt, sodass die Ereignisschleife nicht blockiert wird.
3. Der Körper wird als `text/html` gestreamt. Eine Komponente, die Chunks erzeugt, streamt diese, während sie sie erstellt.
4. Der Browser empfängt HTML. Inseln hydratisieren gemäß ihrer [Richtlinie](islands.md).

Ein beim Rendern ausgelöster Fehler wird von `errors.nexy` in eine Seite umgewandelt, wenn das Projekt einen hat: siehe [Fehlerseiten](../routing/fbr/errors/README.md).

## Wann zu verwenden

- Die Seite zeigt etwas, das der Leser besitzt: eine Sitzung, ein Konto, einen Warenkorb.
- Die Daten müssen bei jedem Ladevorgang aktuell sein.
- Der Inhalt muss im HTML für Crawler vorliegen, die nicht JavaScript ausführen.
- Die Seite ist kostengünstig zu rendern: eine Abfrage, eine Vorlage.

## Konfiguration

Keine. Zwei Auswege, und sie haben nicht die gleiche Körnung:

| SSR verlassen für | Tun Sie dies | Getreide |
|---|---|---|
| eine Seite, mit Cache | `revalidate = 60` im Vorwort → [ISR](isr.md) | Seite |
| das gesamte Projekt, vom Kunden weitergeleitet | `useCSR = True` in `nexyconfig.py` → [CSR](csr.md) | Projekt |

## Beispiel

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` führt diese Vorlage einmal aus, wobei `slug` auf `hello` gesetzt ist. Eine zweite Anfrage führt es erneut aus: Zwischen den beiden bleibt nichts bestehen. Die Abfragezeichenfolge ist keine Requisite – lesen Sie sie mit den Hooks in [Navigation](../routing/fbr/navigation/hooks.md).

## Einschränkungen

- **Ein Rendering pro Anfrage.** Zwei Besucher in derselben Sekunde zahlen jeweils für das Rendering und die dahinter stehenden Abfragen.
- **Kein Cache.** Es gibt keinen gemeinsamen Antwort-Cache zum Aufwärmen: [ISR](isr.md) fügt einen pro URL hinzu.
- **Streaming hilft nur einer Komponente, die nachgibt.** Eine langsame Abfrage oben auf der Seite verzögert immer noch das erste Byte.
- **Keine statische Ausgabe.** Im Servermodus wird beim Erstellen nichts eingefroren: Es gibt keinen SSG-Modus und keinen Exportbefehl. Siehe [Rendering](README.md).
- **Autoescaping ist in `.nexy` Vorlagen deaktiviert**. Entkommen Sie nicht vertrauenswürdigen Werten mit `| e`.

## Nächste Schritte

- [ISR](isr.md): Diese Seite pro URL zwischenspeichern
- [Inseln](islands.md): Behalten Sie SSR bei und machen Sie ein Widget interaktiv
- [CSR](csr.md): Handnavigation zum Browser
- [Leistung](../deployment/performance.md)
