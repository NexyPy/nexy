# Verlinken und navigieren

Beim Client-Routing (`useCSR = True`) tauscht ein Link zwischen zwei Seiten die Seite im Browser aus, anstatt das Dokument neu zu laden. The layouts keep their state.

## Einfache Links funktionieren bereits

Jeder `<a href>` zu einer Seite Ihres Projekts navigiert auf dem Client, ohne Komponente und ohne Markierung:

```html
<a href="/about">About</a>
```

Es wird ein Link zum Browser hinterlassen und die Seite wird normal geladen, wenn:

- eine Sondertaste gedrückt wird oder die Taste nicht die Haupttaste ist;
- es hat `target` (außer `_self`), `download`, `rel="external"` oder `data-nexy-reload`;
- das `href` ist ein anderer Ursprung, ein `mailto:`- oder `tel:`-Link oder nur ein `#fragment`;
- Da der Pfad mit keiner Client-Route übereinstimmt, antwortet der Server darauf.

## `Link`

`Link` ist derselbe Anker, den ein einfacher Anker nicht kann: Sein `href` wird mit Ihren Routen verglichen, er wärmt die Zielseite auf und weiß, wann er auf die aktuelle Seite zeigt. Nexy generiert die `Link` Ihres Frameworks in `__nexy__/src`, wenn Sie `nx dev` oder `nx build` ausführen.

| Rahmen | Importieren |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Prop | Bedeutung |
|---|---|
| `href` | Eine Route des Projekts (ein Tippfehler ist ein Tippfehler), optional mit `?query` oder `#fragment`, oder eine externe URL. |
| `replace` | Replace the history entry instead of adding one. |
| `scroll` | `false` behält die Scroll-Position nach dem Navigieren bei. Standard: `true`. |
| `prefetch` | `'intent'` (Standard) lädt die Seite beim Schweben, Fokussieren oder Berühren; `'viewport'` when the link scrolls into view; `false` niemals. |
| `activeClassName` | Der Klasse hinzugefügt, während der Link auf die aktuelle Seite oder eine Seite darunter verweist (`activeClass` in Vue und Svelte). |
| `exact` | Active only on the exact page. |

Der Link, der auf die aktuelle Seite verweist, erhält ebenfalls `aria-current="page"`.

## Haken

Der Speicherort ist in jedem Framework in der Sprache dieses Frameworks verfügbar. Beim ersten serverseitigen Rendern antworten die Hooks mit der URL der Anfrage, sodass die Seite ohne Abweichung angezeigt wird.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Pfad | `usePathname()` | `usePathname()` returns an accessor | `usePathname()` gibt eine Referenz zurück | `$pathname` speichern |
| Routenparameter | `useParams()` | `useParams()`-Accessor | `useParams()` Ref | `$params` speichern |
| Abfrage | `useSearchParams()` | `useSearchParams()`-Accessor | `useSearchParams()` Ref | `$searchParams` speichern |
| Alles | `useLocation()` | `useLocation()`-Accessor | `useLocation()` Ref | `$location` speichern |
| Navigieren | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Navigation im Flug | `useTransition()` | `useTransition()`-Accessor | `useTransition()` Ref | `useTransition()` speichern |
| Passen Sie einen Pfad an | `useMatch(path?)` | `useMatch(path?)`-Accessor | `useMatch(path?)` Ref | `useMatch(path?)` speichern |
| Fragen Sie vor der Abreise | `useBlocker(dirty)` | `useBlocker(dirty())` in `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` in `$effect` |

Die Abfrage ist ein `URLSearchParams`. `useRouter()` und `router` ergeben `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` und `prefetch(href)`; `push` and `replace` accept `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## Show a loading state with `useTransition`

`useTransition()` gibt an, ob sich eine Client-Navigation im Flug befindet. `pending` ist `true` vom Klick bis zur Anzeige der nächsten Seite und `next` ist der Ort, an den es geht. Es kehrt zu `{ pending: false, next: null }` zurück, sobald die Seite angezeigt wird, wenn die Navigation stoppt oder wenn eine neuere Seite sie ersetzt.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Passen Sie einen Pfad an `useMatch`

`useMatch(path)` gibt an, ob `path` mit einer Client-Route übereinstimmt. Es gibt `{ match, found }` zurück, wobei `match` die Route `file`, ihre `layouts` und ihre `params` enthält oder `null` ist. Ohne Pfad entspricht es der aktuellen Seite und folgt jeder Navigation. Während des Serverrenderings gibt es noch keinen Router, also ist `match` `null` und `found` ist `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Catch a page that fails with `ErrorBoundary`

`ErrorBoundary` zeigt einen Fallback anstelle seiner untergeordneten Elemente an, wenn eines von ihnen beim Rendern im Browser auslöst. Der Fallback erhält den Fehler und `reset`, wodurch die untergeordneten Elemente erneut gerendert werden.

| Rahmen | Importieren | Rückfall |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | eine `fallback`-Funktion prop; the children go in the default slot |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | ein `fallback`-Ausschnitt |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

Es fängt nicht:

- ein später ausgelöster Fehler, in einem Event-Handler, einem Timer oder einem Versprechen: Fangen Sie ihn dort ab, wo er passiert. Vue ist die Ausnahme für seine eigenen Event-Handler, deren Fehler die Grenze erreichen;
- eine Seite, die der Router nicht laden kann: Der Browser fragt stattdessen den Server danach (siehe [Was der Router macht](#what-the-router-does)).

## Fragen Sie nach, bevor Sie eine Seite mit nicht gespeicherten Änderungen verlassen

`useBlocker(dirty, message?)` fragt den Besucher, bevor er geht, während `dirty` wahr ist: ein Link, ein `router.push`, die Zurück- und Vorwärts-Buttons, ein Neuladen und ein geschlossener Tab. Eine Client-Navigation zeigt `message` in `confirm()`: „Ja“ geht weiter, „Nein“ bleibt auf der Seite. Ein Neuladen oder ein geschlossener Tab zeigt die eigene Frage des Browsers an, die keine Seite formulieren kann. Ohne Meldung lautet die Frage: „Sie haben nicht gespeicherte Änderungen. Diese Seite verlassen?“.

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

Das Flag wird dort gelesen, wo es sich ändert, in der Sprache jedes Frameworks:

| Rahmen | Folgen Sie der Flagge |
|---|---|
| React, Preact | `useBlocker(dirty)` bei jedem Rendern |
| Vue | `useBlocker(dirty)` mit `dirty` einer Referenz oder einer berechneten |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` übernimmt auch eine Funktion für eine Entscheidung, die davon abhängt, wohin der Besucher geht. Es empfängt den nächsten und den aktuellen Standort und gibt einen Grund (eine Zeichenfolge) zurück, zu bleiben oder nichts weiterzumachen:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Eine Funktion fragt nicht selbst nach und hält kein Neuladen bereit; Rufen Sie `confirm()` darin an, um zu fragen.

## `Image`

`Image` rendert ein `<img>`, das standardmäßig verzögert ist und das Layout nicht verschiebt, wenn seine Größe bekannt ist.

| Rahmen | Importieren |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` ist erforderlich; Verwenden Sie `alt=""` für ein dekoratives Bild. Nexy warnt einmal, wenn es fehlt.
- Sowohl bei `width` als auch bei `height` geben die Attribute dem Browser das Seitenverhältnis vor und das Bild bleibt flüssig (`height: auto; max-width: 100%`).
- `priority` lädt das Bild jetzt mit hoher Priorität für das Bild, das bei der Ankunft sichtbar ist.
- `fill` sorgt dafür, dass das Bild sein positioniertes übergeordnetes Element verdeckt und ignoriert dabei `width` und `height`.
- `sizes` und `srcSet` gehen durch. Nexy ändert die Größe von Bildern nicht und konvertiert sie nicht.

## Link von einer `.nexy`-Seite

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` rendert `<a href="/about" data-nexy-link="true">`. Jedes Attribut und das `href` sind HTML-escaped.

## Was der Router macht

Bei einer Navigation: Der Router:

1. gleicht den Pfad mit den Client-Routen ab (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. importiert und rendert die Seite und ihre [Layouts](../layouts/README.md) **zuerst** und verschiebt erst dann die URL mit `history.pushState`, sodass in der Adressleiste nie eine Seite angezeigt wird, die fehlgeschlagen ist;
3. löst ein `nexy:navigated`-Ereignis am `document` aus;
4. scrollt nach oben oder zum Ziel `#fragment`.

Der Seitenwechsel wird innerhalb eines Browseransichtsübergangs ausgeführt, sofern einer verfügbar ist: siehe [Funktionsweise von Seitenübergängen](page-transitions.md).

Eine neuere Navigation bricht eine ältere ab, die noch gerendert wird. Wenn eine Seite nicht gerendert werden kann, fragt der Browser stattdessen den Server danach. Die Schaltflächen „Zurück“ und „Vorwärts“ rendern die Seite dieses Eintrags und stellen die Scrollposition wieder her.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

Der Router startet nur in einem Projekt mit Client-Routen, daher behält ein vom Server gerendertes Projekt die browsereigene Zurück-Schaltfläche und die Scroll-Wiederherstellung bei.

## Nächste Schritte

- [Layouts](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Komponenten](../../../views/nexy/components.md)
