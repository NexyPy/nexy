# Inseln und Flüssigkeitszufuhr

## Definition

Eine Insel ist eine Client-Komponente – React, Vue, Svelte, Solid oder Preact – die in ein `.nexy` importiert wird.
Seite. Der Server rendert seinen HTML-Code. Der Browser macht diese eine Komponente interaktiv. Der Rest
Seite bleibt HTML.

Inseln existieren im Servermodus. Im Client-Modus *sind* die Komponenten die Seiten: siehe [CSR](csr.md).

## Wie es funktioniert

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

Nexy rendert die Komponente zum Zeitpunkt der Erstellung, speichert ihren HTML-Code und platziert ihn auf der Seite. Die Seite
Die Antwort enthält diesen HTML-Code und die Requisiten als JSON-Attribut. Im Browser die Insellaufzeit
lädt die Komponente und übernimmt den Container.

`directive` entscheidet, **wann** das passiert. Ohne eine spendet die Insel Feuchtigkeit, sobald ihre Laufzeit erreicht ist
ist fertig.

## Rendering-Lebenszyklus

1. Beim Build wird jede Client-Komponente in HTML gerendert und unter `__nexy__/client/static/` geschrieben.
2. Eine Anfrage rendert die Seite `.nexy`; Anstelle des Tags wird der HTML-Code der Insel eingefügt.
3. Die Antwort trägt den HTML-Code, die Requisiten und die Direktive als Attribute.
4. Im Browser plant die Laufzeit die Hydratation gemäß der Anweisung.
5. Hydration ersetzt das statische HTML durch die Live-Komponente; Der Rest der Seite ist unberührt.

In der Entwicklung gibt es keinen Build-Snapshot: Der Container ist leer und die Komponente wird im gerendert
Browser. Die Seite sieht gleich aus, aber die erste Lackierung weicht von der Produktion ab.

## Wann zu verwenden

- Eine Seite, die größtenteils aus Inhalten besteht und über ein oder zwei interaktive Bereiche verfügt.
- Ein Widget, das im HTML für Crawler vorhanden sein und trotzdem funktionieren muss.
- Eine Komponente, die den Browser benötigt, aber nicht die gesamte Seite in das Client-Rendering ziehen sollte.

## Konfiguration

| Richtlinie | Hydrate |
|---|---|
| keine, oder `client:load` | sofort |
| `client:idle` | wenn der Browser inaktiv ist (`requestIdleCallback`, 2 s Timeout) |
| `client:visible` | wenn die Insel das Ansichtsfenster betritt, 200 px früher |
| `client:media` | wenn eine Medienabfrage übereinstimmt; setze es mit der Requisite `media` |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` ist standardmäßig `(min-width: 768px)`, wenn `media` nicht vorhanden ist, und hydratisiert einmal. Auf einem
Browser ohne `IntersectionObserver`, `client:visible` fällt in den Ruhezustand zurück.

`directive` und `media` werden von Nexy verbraucht: Sie werden nicht an Ihre Komponente übergeben.

## Beispiel

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```

## Einschränkungen

- **`client:only` hydratisiert nie.** Es wird akzeptiert, aber die Laufzeit überspringt es, sodass das Server-HTML erhalten bleibt
  inert. Verwenden Sie eine Client-Route ([CSR](csr.md)), wenn eine Komponente nicht auf dem Server gerendert werden kann.
- **`client:manual` hat keinen öffentlichen Auslöser.** Es wird auch automatisch übersprungen, und das Handle dafür
  geht weiter, es ist intern.
- **Requisiten müssen JSON sein.** Sie werden mit `json.dumps` serialisiert; ein Wert, der nicht serialisiert werden kann, ist
  fallen gelassen, und die Insel empfängt `{}` – lautlos.
- **Eine Insel ist keine Client-Komponente mit einem gemeinsamen Status.** Zwei Inseln teilen keinen Status ohne einen
  Mechanismus, den Sie selbst hinzufügen.
- **Die Insel wird vom Server nicht neu gerendert.** Ihr HTML ist der Build-Snapshot, plus was auch immer
  Die Komponente wirkt, sobald sie mit Feuchtigkeit versorgt ist.
- **Eine Inselseite ist eine getarnte CSR-Seite.** Wenn jeder Block mit jedem anderen kommunizieren muss, wählen Sie
  Stattdessen wird der Client-Modus verwendet.

## Nächste Schritte

- [Rendering](README.md): die vier Modi
- [Komponenten](../views/nexy/components.md): wie eine `.nexy` Seite eine importiert
- [Reagieren](../views/react/differences.md), [Vue](../views/vue/differences.md),
  [Schlank](../views/svelte/differences.md), [Fest](../views/solid/differences.md),
  [Vorwirken](../views/preact/differences.md)