# React

Nexy rendert React 19 Komponenten auf dem Server und React hydratisiert sie dann im Browser. Seiten, Layouts, Inseln und Aktionen sind in jedem Framework gleich: Auf dieser Seite geht es um die Einrichtung und dann um die Teile, die sich von den [gemeinsamen Verträgen](../frontend/pages.md) unterscheiden.

<!-- router:fbr,custom -->
| Modus | `nexyconfig.py` | Seiten sind | React ist |
|---|---|---|---|
| Server (Standard) | `useCSR = False` | `.nexy` Dateien | [Inseln](../../rendering/islands.md) innerhalb dieser Seiten |
| Kunde | `useCSR = True` | `.tsx` Dateien | die gesamte Seite, mit [Layouts](../frontend/layouts.md) und einem Client-Router |
<!-- /router -->

<!-- router:modular -->
Beim modularen Router sind React Komponenten [Inseln](../../rendering/islands.md) innerhalb der `.nexy` Ansichten, die ein Controller zurückgibt: Es gibt keine Auslagerungsdatei und keinen Client-Router.
<!-- /router -->

## Starten Sie ein Projekt

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-react
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-react
```
<!-- /router -->

Die Vorlage ist ein Servermodus-Projekt mit React Inseln. Führen Sie stattdessen `nx new my-app` ohne Vorlage aus, um die Eingabeaufforderungen zu beantworten: den Router, den Projekttyp, ob clientseitiges Routing verwendet werden soll, dann das Framework.

## Aktivieren Sie React in einem vorhandenen Projekt

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` schreibt diese Datei; Nexy schreibt `__nexy__/vite.ts` selbst, also bearbeiten Sie es nicht.

| Paket | Version `nx new` schreibt |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | Entwicklerabhängigkeiten |

## Regeln

- **Ein Framework pro Projekt.** `useFF` benötigt genau ein Framework; `useFF = [react(), vue()]` stoppt den Server beim Start.
<!-- router:fbr,custom -->
- **Seiten sind `.tsx`.** React besitzt `.tsx` und `.jsx` für Komponenten, aber nur eine `.tsx`-Datei unter `src/routes/` wird zu einer Seite.
- **Komponenten befinden sich außerhalb von `src/routes/`**, normalerweise in `src/components/`, daher sind sie keine Seiten.
- **Ein Servermodus-Projekt hat keine `.tsx` Seite**, und ein Clientmodus-Projekt hat keine `.nexy` Seite: Nexy weigert sich zu starten und benennt die Datei. Siehe [Modi](../../routing/fbr/modes.md).
<!-- /router -->
<!-- router:modular -->
- **Komponenten leben in `src/components/`** und eine Ansicht importiert sie als Inseln.
<!-- /router -->

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

Das Root-Layout definiert die Dokumenthülle. Verschachtelte Layouts umschließen den Inhalt darunter.

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```
<!-- /router -->

## Inseln

Im Servermodus ist eine in eine `.nexy`-Datei importierte React-Komponente eine Insel.

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

- `usePathname()`: aktueller Pfad
- `useParams()`: dynamische Segmente
- `useSearchParams()`: Abfragezeichenfolge
- `useLocation()`: vollständiges Standortobjekt

## Nächste Schritte

- [Ansichten](../README.md): Vergleichen Sie die Formate, die eine Seite verwenden kann
- [Frontend](../../guides/frontend.md): Vite und der Client-Build
