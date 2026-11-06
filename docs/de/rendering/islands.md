# Inseln und Flüssigkeitszufuhr

## Definition

Eine Insel ist eine Client-Komponente – React, Vue, Svelte, Solid oder Preact – die in eine `.nexy`-Seite importiert wird. Der Server rendert seinen HTML-Code. Der Browser macht diese eine Komponente interaktiv. Der Rest der Seite bleibt HTML.

Inseln existieren im Servermodus. Im Client-Modus *sind* die Komponenten die Seiten: siehe [CSR](csr.md).

## Wie es funktioniert

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

Nexy rendert die Komponente zum Zeitpunkt der Erstellung, speichert ihren HTML-Code und platziert ihn auf der Seite. Die Seitenantwort enthält diesen HTML-Code und die Requisiten als JSON-Attribut. Im Browser lädt die Insellaufzeit die Komponente und übernimmt den Container.

`directive` entscheidet, **wann** das geschieht. Ohne eine spendet die Insel Feuchtigkeit, sobald ihre Laufzeit bereit ist.

## Rendering-Lebenszyklus

1. Beim Build wird jede Client-Komponente in HTML gerendert und unter `__nexy__/client/static/` geschrieben.
2. Eine Anfrage rendert die Seite `.nexy`; Anstelle des Tags wird der HTML-Code der Insel eingefügt.
3. Die Antwort enthält den HTML-Code, die Requisiten und die Direktive als Attribute.
4. Im Browser plant die Laufzeit die Flüssigkeitszufuhr gemäß der Anweisung.
5. Hydration ersetzt das statische HTML durch die Live-Komponente; Der Rest der Seite ist unberührt.

In der Entwicklung gibt es keinen Build-Snapshot: Der Container ist leer und die Komponente wird im Browser gerendert. Die Seite sieht gleich aus, aber die erste Lackierung weicht von der Produktion ab.

## Wann zu verwenden

- Eine Seite, die größtenteils aus Inhalten besteht und über ein oder zwei interaktive Bereiche verfügt.
- Ein Widget, das für Crawler im HTML vorhanden sein und trotzdem funktionieren muss.
- Eine Komponente, die den Browser benötigt, aber nicht die gesamte Seite in das Client-Rendering ziehen sollte.

## Konfiguration

| Richtlinie | Spendet Feuchtigkeit |
|---|---|
| keine, oder `client:load` | sofort |
| `client:idle` | wenn der Browser inaktiv ist (`requestIdleCallback`, 2 s Timeout) |
| `client:visible` | wenn die Insel das Ansichtsfenster betritt, 200 Pixel früher |
| `client:media` | wenn eine Medienanfrage übereinstimmt; Stellen Sie es mit der Requisite `media` ein |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` wird standardmäßig auf `(min-width: 768px)` gesetzt, wenn `media` nicht vorhanden ist, und hydratisiert einmal. Bei einem Browser ohne `IntersectionObserver` fällt `client:visible` auf den Leerlauf zurück.

`directive` und `media` werden von Nexy verbraucht: Sie werden nicht an Ihre Komponente übergeben.

## Beispiel

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

## Einschränkungen

- **`client:only` spendet nie Feuchtigkeit.** Es wird akzeptiert, aber die Laufzeit überspringt es, sodass das Server-HTML inaktiv bleibt. Verwenden Sie eine Client-Route ([CSR](csr.md)), wenn eine Komponente nicht auf dem Server gerendert werden kann.
- **`client:manual` hat keinen öffentlichen Auslöser.** Es wird auch automatisch übersprungen und das Handle, das es fortsetzt, ist intern.
- **Requisiten müssen JSON sein.** Sie werden mit `json.dumps` serialisiert; Ein Wert, der nicht serialisiert werden kann, wird gelöscht und die Insel empfängt `{}` – stillschweigend.
- **Eine Insel ist keine Client-Komponente mit gemeinsamem Status.** Ohne einen Mechanismus, den Sie selbst hinzufügen, teilen sich zwei Inseln keinen Status.
- **Die Insel wird vom Server nicht neu gerendert.** Ihr HTML ist der Build-Snapshot sowie alles, was die Komponente nach der Hydratisierung tut.
- **Eine Inselseite ist eine getarnte CSR-Seite.** Wenn jeder Block mit jedem anderen kommunizieren muss, wählen Sie stattdessen den Client-Modus.

## Nächste Schritte

- [Rendering](README.md): die vier Modi
- [Komponenten](../views/nexy/components.md): wie eine `.nexy`-Seite eine importiert
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md)
