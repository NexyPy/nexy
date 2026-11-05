# Frontend-Layouts

Ein **Layout** ist ein Wrapper, der die gemeinsame Struktur um eine oder mehrere Seiten definiert. Layouts ermöglichen ein „App-ähnliches“ Erlebnis, indem sie den Status beibehalten und das Neuladen ganzer Seiten während der Navigation vermeiden.

## Verschachtelungslogik

Layouts folgen einer hierarchischen Struktur, die auf dem Verzeichnisbaum unter `src/routes/` basiert.

1.  **Root-Layout**: Jedes Projekt hat ein Root-Layout (z. B. `src/routes/layout.nexy`). Dies ist das einzige Layout, das für die Definition der Dokumenthülle verantwortlich ist: `<html>`, `<head>` und `<body>`.
2.  **Verschachtelte Layouts**: Jeder Ordner kann seine eigene `layout.*`-Datei enthalten. Dieses Layout umschließt alle Seiten und Unterlayouts in diesem Ordner.
3.  **Vererbung**: Eine Seite wird von allen Layouts vom Stammverzeichnis bis hinunter zu ihrem eigenen Ordner umschlossen.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Ein verschachteltes Layout zeichnet nur seinen Teil der Benutzeroberfläche und platziert die Seite dort, wo `children` hingehört:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Gemeinsamer Zustand und Zusammensetzung

Layouts sind auf Stabilität ausgelegt. Wenn Sie im Client-Modus zwischen zwei Seiten navigieren, die dasselbe Layout haben, wird das Layout **nicht** neu gerendert; Nur der untergeordnete Inhalt ändert sich. Im Servermodus ist jede Navigation ein neues Dokument.

- **Slots**: Layouts bieten einen Slot, in den die verschachtelte Seite eingefügt wird: `children` in JSX und die `children`-Requisite in einem `.nexy`-Layout.
- **Statuserhaltung**: Da das Layout gemountet bleibt, bleibt jeder darin enthaltene Status (z. B. eine Suchabfrage in einem Header) während der Navigation erhalten.

Derselbe Slot in einem `.nexy`-Layout:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

Das Suchfeld unten speichert, was der Benutzer eingegeben hat, während er zwischen den Dashboard-Seiten wechselt, da das Layout, in dem es gespeichert ist, nie ausgehängt wird:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Statische Einschränkungen

Bei Routen, die vorab gerendert werden (SSG), kann das Root-Layout nicht von Daten zur Anforderungszeit wie Cookies oder Headern abhängen. Es muss als statische Hülle darstellbar sein, die der Kunde dann hydratisiert.

Lesen Sie das Theme stattdessen aus dem Browser, in einem Skript der statischen Shell:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Framework-Implementierung

Die Implementierung von Slots und Verschachtelungen variiert geringfügig je nach Framework. Sehen Sie sich den Leitfaden **Unterschiede** für die von Ihnen gewählte Technologie an:

- [React Unterschiede](../react/differences.md)
- [Vue Unterschiede](../vue/differences.md)
- [Svelte Unterschiede](../svelte/differences.md)
- [Solid Unterschiede](../solid/differences.md)
- [Preact Unterschiede](../preact/differences.md)
