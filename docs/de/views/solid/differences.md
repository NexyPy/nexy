# Solide

Nexy rendert Solid 1.9-Komponenten auf dem Server, dann übernimmt Solid sie im Browser. Seiten,
Layouts, Inseln und Aktionen sind in jedem Framework gleich: Auf dieser Seite geht es um die Einrichtung und dann um die Teile
die von den [gemeinsamen Verträgen](../frontend/pages.md) abweichen.

| Modus | `nexyconfig.py` | Seiten sind | Vollton ist |
|---|---|---|---|
| Server (Standard) | `useCSR = False` | `.nexy` Dateien | [Inseln](../../rendering/islands.md) innerhalb dieser Seiten |
| Client | `useCSR = True` | `.tsx` Dateien | die gesamte Seite, mit [Layouts](../frontend/layouts.md) und einem Client-Router |

## Starten Sie ein Projekt

```bash
nx new my-app --template web-fbr-solid
```

Die Vorlage ist ein Servermodus-Projekt mit Solid Islands. Führen Sie `nx new my-app` ohne Vorlage aus
Beantworten Sie stattdessen die Eingabeaufforderungen: den Router, den Projekttyp, ob clientseitiges Routing verwendet werden soll
der Rahmen.

## Aktivieren Sie Solid in einem vorhandenen Projekt

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

Im Client-Modus schreiben Sie `solid({ ssr: true })`: Solid kompiliert eine Komponente anders für den Server
und für den Browser, und der Client-Modus benötigt beides. `nx new` schreibt diese Datei; Nexy schreibt
`__nexy__/vite.ts` selbst, also bearbeiten Sie es nicht.

| Paket | Version `nx new` schreibt |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (Entwicklerabhängigkeit) |

## Denken Sie in Signalen

Eine Solid-Komponentenfunktion wird **einmal** ausgeführt. Was sich später ändert, wird durch ein Signal gelesen, und nur das
Ausdrücke, die es lesen, aktualisieren:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- Rufen Sie das Signal `count()` innerhalb des JSX auf, nicht in einer Variablen darüber.
- Lesen Sie Requisiten als `props.start`. Durch die Destrukturierung `{ start }` wird der Wert einmal gelesen und die Aktualisierungen gehen verloren.
- Solid schreibt HTML-Attribute: `class`, `for`, `charset`, nicht `className`.

## Regeln

- **Ein Framework pro Projekt.** `useFF` benötigt genau ein Framework; `useFF = [solid(), react()]`
  Stoppt den Server beim Start. Mit `useFF = solid()` ist jede `.tsx`-Datei Solid.
- **Seiten sind `.tsx`.** Nur eine `.tsx`-Datei unter `src/routes/` wird zu einer Seite; `.jsx` ist in Ordnung für a
  Komponente.
- **Komponenten befinden sich außerhalb von `src/routes/`**, normalerweise in `src/components/`, also sind sie keine Seiten.
- **Ein Projekt im Servermodus hat keine `.tsx` Seite**, und ein Projekt im Clientmodus hat keine `.nexy` Seite: Nexy
  weigert sich zu starten und benennt die Datei. Siehe [Modi](../../routing/fbr/modes.md).
- **Nein `.mdx` mit Solid.** MDX wird zu React oder Preact kompiliert; `.md` Seiten funktionieren.

## Seiten

Im Client-Modus (`useCSR = True`) ist eine Seite eine `.tsx`-Datei.

### Seitenkomponente

Eine Seite ist der Standardexport der Datei. Wenn kein Standardexport vorhanden ist, wählt Nexy den zuerst genannten aus
exportieren.

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### Dynamische Segmente

URL-Parameter sind über den Hook `useParams` verfügbar, der einen Accessor zurückgibt:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## Layouts

### Implementierung

Das Root-Layout definiert die Dokumenthülle. Verschachtelte Layouts umschließen den Inhalt.

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

Zerstören Sie nicht `props.children`, da Solid es träge liest.

## Inseln

Im Servermodus ist eine in eine `.nexy`-Datei importierte Solid-Komponente eine Insel.

### Importieren

Importieren Sie Komponenten in die Frontmatter der Datei `.nexy`:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### Hydrationsanweisungen

Verwenden Sie die Requisite `directive`, um zu steuern, wann die Insel hydratisiert:

- `client:load` (Standard): sofort
- `client:idle`: wenn der Browser inaktiv ist
- `client:visible`: wenn es in die Ansicht scrollt
- `client:media`: wenn die Medienabfrage übereinstimmt

## Aktionen und Navigation

### Aktionen aufrufen

Verwenden Sie den Hook `useAction`, um den Status eines Aktionsaufrufs zu verwalten. In Solid gibt dies Zugriffsmethoden zurück (Aufruf
sie als Funktionen).

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
```

### Navigation

Verwenden Sie die Komponente `Link` für clientseitige Übergänge:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

Verwenden Sie für die programmatische Navigation den Hook `useRouter`:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### URL-Zugriff

Alle Standort-Hooks geben Accessoren zurück:

- `usePathname()`: aktueller Pfad
- `useParams()`: dynamische Segmente
- `useSearchParams()`: Abfragezeichenfolge
- `useLocation()`: vollständiges Standortobjekt

## Nächste Schritte

- [Ansichten](../README.md): Vergleichen Sie die Formate, die eine Seite verwenden kann
- [Frontend](../../guides/frontend.md): Vite und der Client-Build