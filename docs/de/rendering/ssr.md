# SSR (Server-Rendering)

## Definition

SSR ist die Standardeinstellung: Der Server rendert die Seite für jede Anfrage in HTML. Nichts ermöglicht es, und
Kein Flag schaltet es aus – ein Servermodus-Projekt wird bei jeder Anfrage gerendert, es sei denn, eine Seite deklariert es
`revalidate`.

## Wie es funktioniert

| Routendatei | Was erzeugt den HTML-Code | Wann |
|---|---|---|
| `.nexy` | das kompilierte Python-Modul, über Jinja2 | jede Anfrage |
| `.md` | `cmarkgfm`, dann das nächstgelegene Layout | bei jeder Anfrage |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | das Framework, gerendert im Knoten | beim Build, wenn die Route kein Layout hat, andernfalls im Browser |
| `.py` | nichts: Es wird JSON oder ein `Response` | - | zurückgegeben.

Eine Komponentenroute ist der einzige Fall, der einen zweiten Satz benötigt. In der Produktion eine Komponentenroute
**Ohne** wird ein Layout mit dem beim Build erzeugten HTML bereitgestellt und von der Komponente hydratisiert. Mit
ein Layout oder in der Entwicklung, der Container ist leer und die Komponente wird im Browser gerendert – die
Die Seite ist dann eine Hülle, die sich selbst füllt.

## Rendering-Lebenszyklus

1. Die Anfrage erreicht den dateibasierten Router. Der Pfad wird abgeglichen und dynamische Segmente werden umgewandelt
   die Typen, die die Komponente deklariert.
2. Die Komponente wird ausgeführt. Einer, der auf einen Knoten wartet – ein Client-Dokument – wird in einem Thread-Pool ausgeführt
   stoppt die Ereignisschleife nicht.
3. Der Körper wird als `text/html` gestreamt. Eine Komponente, die Chunks erzeugt, streamt diese bei der Erstellung
   sie.
4. Der Browser empfängt HTML. Inseln hydratisieren gemäß ihrer [Richtlinie](islands.md).

Ein beim Rendern ausgelöster Fehler wird von `errors.nexy` in eine Seite umgewandelt, wenn das Projekt einen solchen hat: siehe
[Fehlerseiten](../routing/fbr/errors/README.md).

## Wann zu verwenden

- Die Seite zeigt etwas, das der Leser besitzt: eine Sitzung, ein Konto, einen Warenkorb.
- Die Daten müssen bei jedem Ladevorgang aktuell sein.
- Für Crawler, die kein JavaScript ausführen, muss der Inhalt im HTML-Format vorliegen.
- Die Seite ist kostengünstig zu rendern: eine Abfrage, eine Vorlage.

## Konfiguration

Keine. Zwei Auswege, und sie haben nicht die gleiche Körnung:

| SSR verlassen für | Tun Sie dies | Getreide |
|---|---|---|
| eine Seite, mit einem Cache | `revalidate = 60` in der Titelseite → [ISR](isr.md) | Seite |
| das gesamte Projekt, vom Kunden weitergeleitet | `useCSR = True` in `nexyconfig.py` → [CSR](csr.md) | Projekt |

## Beispiel

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` führt diese Vorlage einmal aus, wobei `slug` auf `hello` gesetzt ist. Eine zweite Anfrage führt es aus
Nochmals: Zwischen den beiden bleibt nichts. Die Abfragezeichenfolge ist keine Requisite – lesen Sie sie mit den Hooks ein
[Navigation](../routing/fbr/navigation/hooks.md).

## Einschränkungen

- **Ein Render pro Anfrage.** Zwei Besucher in derselben Sekunde zahlen jeweils für den Render und für die
  Fragen dahinter.
- **Kein Cache.** Es gibt keinen gemeinsamen Antwort-Cache zum Aufwärmen: [ISR](isr.md) fügt einen pro URL hinzu.
- **Streaming hilft nur einer Komponente, die Ergebnisse liefert.** Eine langsame Abfrage oben auf der Seite führt immer noch zu Verzögerungen
  das erste Byte.
- **Keine statische Ausgabe.** Im Servermodus wird beim Build nichts eingefroren: Es gibt keinen SSG-Modus und nein
  Exportbefehl. Siehe [Rendering](README.md).
- **Autoescaping ist in `.nexy` Vorlagen deaktiviert**. Entkommen Sie nicht vertrauenswürdigen Werten mit `| e`.

## Nächste Schritte

- [ISR](isr.md): Diese Seite pro URL zwischenspeichern
- [Inseln](islands.md): Behalten Sie SSR bei und machen Sie ein Widget interaktiv
- [CSR](csr.md): Handnavigation zum Browser
- [Leistung](../deployment/performance.md)