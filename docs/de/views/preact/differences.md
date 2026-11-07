# Preact

Nexy rendert Preact 10 Komponenten auf dem Server, dann Preact übernimmt sie im Browser. Seiten, Layouts, Inseln und Aktionen sind in jedem Framework gleich: Auf dieser Seite geht es um die Einrichtung und dann um die Teile, die sich von den [gemeinsamen Verträgen](../frontend/pages.md) unterscheiden.

<!-- router:fbr,custom -->
| Modus | `nexyconfig.py` | Seiten sind | Preact ist |
|---|---|---|---|
| Server (Standard) | `useCSR = False` | `.nexy` Dateien | [Inseln](../../rendering/islands.md) innerhalb dieser Seiten |
| Kunde | `useCSR = True` | `.tsx` Dateien | die gesamte Seite, mit [Layouts](../frontend/layouts.md) und einem Client-Router |
<!-- /router -->

<!-- router:modular -->
Beim modularen Router sind Preact Komponenten [Inseln](../../rendering/islands.md) innerhalb der `.nexy` Ansichten, die ein Controller zurückgibt: Es gibt keine Auslagerungsdatei und keinen Client-Router.
<!-- /router -->

## Starten Sie ein Projekt

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-preact
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-preact
```
<!-- /router -->

Die Vorlage ist ein Servermodus-Projekt mit Preact Inseln. Führen Sie stattdessen `nx new my-app` ohne Vorlage aus, um die Eingabeaufforderungen zu beantworten: den Router, den Projekttyp, ob clientseitiges Routing verwendet werden soll, dann das Framework.

## Aktivieren Sie Preact in einem vorhandenen Projekt

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` schreibt diese Datei; Nexy schreibt `__nexy__/vite.ts` selbst, also bearbeiten Sie es nicht.

| Paket | Version `nx new` schreibt |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (Entwicklerabhängigkeit) |
| `preact-render-to-string` | `^6.7.0` (Entwicklerabhängigkeit, Renderings auf dem Server) |

## Schreiben Sie Preact

Eine Preact-Komponente ist eine Funktion im React-Stil. Die Unterschiede, auf die es hier ankommt:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- Haken stammen von `preact/hooks`, Typen wie `ComponentChildren` von `preact`.
- Schreiben Sie HTML-Attribute: `class`, `for`, `charset`. `Link` liest seine Klassen aus `class`.

## Regeln

- **Ein Framework pro Projekt.** `useFF` benötigt genau ein Framework; `useFF = [preact(), react()]` stoppt den Server beim Start. Mit `useFF = preact()` ist jede `.tsx`-Datei Preact.
<!-- router:fbr,custom -->
- **Seiten sind `.tsx`.** Nur eine `.tsx`-Datei unter `src/routes/` wird zu einer Seite; `.jsx` ist für eine Komponente in Ordnung.
- **Komponenten befinden sich außerhalb von `src/routes/`**, normalerweise in `src/components/`, daher sind sie keine Seiten.
- **Ein Servermodus-Projekt hat keine `.tsx` Seite**, und ein Clientmodus-Projekt hat keine `.nexy` Seite: Nexy weigert sich zu starten und benennt die Datei. Siehe [Modi](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Komponenten leben in `src/components/`** und eine Ansicht importiert sie als Inseln.
<!-- /router -->
- **Eine `.mdx`-Seite importiert aus `"preact"`.** Nexy kompiliert eine `.mdx`-Datei mit Preact nur, wenn es diesen Import sieht, zum Beispiel `import { h } from "preact"`, andernfalls mit React. Siehe [Markdown und MDX](../nexy/markdown.md).

<!-- router:fbr,custom -->
## Seiten

Im Client-Modus (`useCSR = True`) ist eine Seite eine `.tsx`-Datei.

### Seitenkomponente

Eine Seite ist der Standardexport der Datei. Wenn kein Standardexport vorhanden ist, wählt Nexy den zuerst benannten Export aus.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Dynamische Segmente

URL-Parameter sind über den Hook `useParams` verfügbar:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## Layouts

### Umsetzung

Das Root-Layout definiert die Dokumenthülle. Verschachtelte Layouts umschließen den Inhalt.

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```
<!-- /router -->

## Inseln

Im Servermodus ist eine in eine `.nexy`-Datei importierte Preact-Komponente eine Insel.

### Importieren

Importieren Sie Komponenten in die Frontmatter der Datei `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### Trinkrichtlinien

Verwenden Sie die Requisite `directive`, um zu steuern, wann die Insel hydratisiert:

- `client:load` (Standard): sofort
- `client:idle`: wenn der Browser inaktiv ist
- `client:visible`: wenn es in die Ansicht scrollt
- `client:media`: wenn die Medienabfrage übereinstimmt

## Aktionen und Navigation

### Aktionen aufrufen

Verwenden Sie den Hook `useAction`, um den Status eines Aktionsaufrufs zu verwalten:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### Navigation

Verwenden Sie die Komponente `Link` für clientseitige Übergänge. Beachten Sie, dass Preact `class` anstelle von `className` verwendet:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
```

Verwenden Sie für die programmatische Navigation den Hook `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL-Zugriff

- `usePathname()`: aktueller Pfad
- `useParams()`: dynamische Segmente
- `useSearchParams()`: Abfragezeichenfolge
- `useLocation()`: vollständiges Standortobjekt

## Nächste Schritte

- [Ansichten](../README.md): Vergleichen Sie die Formate, die eine Seite verwenden kann
- [Frontend](../../guides/frontend.md): Vite und der Client-Build
