# Verknüpfen und Navigieren

Beim Client-Routing (`useCSR = True`) tauscht ein Link zwischen zwei Seiten stattdessen die Seite im Browser aus
des erneuten Ladens des Dokuments. Die Layouts behalten ihren Zustand.

## Einfache Links funktionieren bereits

Jeder `<a href>` zu einer Seite Ihres Projekts navigiert auf dem Client, ohne Komponente und ohne Markierung:

```html
<a href="/about">About</a>
```

Es wird ein Link zum Browser hinterlassen und die Seite wird normal geladen, wenn:

- Eine Zusatztaste wird gedrückt oder die Taste ist nicht die Haupttaste;
- es hat `target` (außer `_self`), `download`, `rel="external"` oder `data-nexy-reload`;
- das `href` ist ein anderer Ursprung, ein `mailto:`- oder `tel:`-Link oder nur ein `#fragment`;
- Der Pfad stimmt mit keiner Client-Route überein, daher antwortet der Server darauf.

## `Link`

`Link` ist derselbe Anker mit dem, was ein einfacher Anker nicht kann: Sein `href` wird mit Ihren Routen verglichen,
Es erwärmt die Zielseite und weiß, wann es auf die aktuelle Seite zeigt. Nexy generiert die `Link`
Ihres Frameworks in `__nexy__/src`, wenn Sie `nx dev` oder `nx build` ausführen.

| Framework | Importieren |
|---|---|
| Reagieren, Vorwirken, Solid, Vue | `import { Link } from "@nexy/client"` |
| Schlank | `import Link from "@nexy/Link.svelte"` |

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
| `replace` | Ersetzen Sie den Verlaufseintrag, anstatt einen hinzuzufügen. |
| `scroll` | `false` behält die Scroll-Position nach dem Navigieren bei. Standard: `true`. |
| `prefetch` | `'intent'` (Standard) lädt die Seite beim Schweben, Fokussieren oder Berühren; `'viewport'` wenn der Link angezeigt wird; `false` niemals. |
| `activeClassName` | Der Klasse hinzugefügt, während der Link auf die aktuelle Seite oder eine Seite darunter zeigt (`activeClass` in Vue und Svelte). |
| `exact` | Nur auf der genauen Seite aktiv. |

Der Link, der auf die aktuelle Seite verweist, erhält ebenfalls `aria-current="page"`.

## Haken

Der Speicherort ist in jedem Framework in der Sprache dieses Frameworks verfügbar. Während des ersten,
Serverseitig rendern die Hooks die Antwort mit der URL der Anfrage, sodass die Seite ohne a hydratisiert wird
Nichtübereinstimmung.

| | Reagieren, Vorwirken | Solid | Vue | Svelte |
|---|---|---|---|---|
| Pfad | `usePathname()` | `usePathname()` gibt einen Accessor zurück | `usePathname()` gibt einen Ref zurück | `$pathname` Store |
| Route-Parameter | `useParams()` | `useParams()` Accessor | `useParams()` Ref | `$params` Store |
| Abfrage | `useSearchParams()` | `useSearchParams()` Accessor | `useSearchParams()` Ref | `$searchParams` Store |
| Alles | `useLocation()` | `useLocation()` Accessor | `useLocation()` Ref | `$location` Store |
| Navigieren | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

Die Abfrage ist ein `URLSearchParams`. `useRouter()` und `router` ergeben `push(href)`, `replace(href)`,
`back()`, `forward()`, `refresh()` und `prefetch(href)`; `push` und `replace` akzeptieren
`{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` rendert ein `<img>`, das standardmäßig verzögert ist und das Layout nicht verschiebt, wenn es groß ist
bekannt.

| Framework | Importieren |
|---|---|
| Reagieren, Vorwirken, Fest, Vue | `import { Image } from "@nexy/client"` |
| Schlank | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` ist erforderlich; Verwenden Sie `alt=""` für ein dekoratives Bild. Nexy warnt einmal, wenn es fehlt.
-  Sowohl bei `width` als auch bei `height` geben die Attribute dem Browser das Seitenverhältnis und das Bild an
  bleibt flüssig (`height: auto; max-width: 100%`).
- `priority` lädt das Bild jetzt mit hoher Priorität für das Bild, das bei der Ankunft sichtbar ist.
- `fill` bewirkt, dass das Bild sein positioniertes übergeordnetes Bild verdeckt, wobei `width` und `height` ignoriert werden.
- `sizes` und `srcSet` gehen durch. Nexy ändert die Größe von Bildern nicht und konvertiert sie nicht.

## Link von einer `.nexy` Seite

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` rendert
`<a href="/about" data-nexy-link="true">`. Jedes Attribut und das `href` sind HTML-escaped.

## Was der Router macht

Bei einer Navigation: Der Router:

1.  gleicht den Pfad mit den Client-Routen ab (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. importiert und rendert die Seite und ihre [Layouts](../layouts/README.md) **zuerst** und erst dann
   verschiebt die URL mit `history.pushState`, sodass in der Adressleiste nie eine Seite angezeigt wird, die fehlgeschlagen ist;
3. sendet ein `nexy:navigated`-Ereignis am `document`;
4. scrollt nach oben oder zum `#fragment`-Ziel.

Eine neuere Navigation bricht eine ältere ab, die noch gerendert wird. Wenn eine Seite nicht gerendert werden kann, wird der Browser
fragt stattdessen den Server danach. Die Schaltflächen „Zurück“ und „Vorwärts“ rendern die Seite dieses Eintrags und
stellt die Bildlaufposition wieder her.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

Der Router startet nur in einem Projekt mit Client-Routen, daher behält ein vom Server gerendertes Projekt dies bei
Browsereigene Zurück-Schaltfläche und Scroll-Wiederherstellung.

## Nächste Schritte

- [Layouts](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Komponenten](../../../views/nexy/components.md)