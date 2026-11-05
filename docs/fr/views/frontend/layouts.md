# Dispositions frontales

Un **Layout** est un wrapper qui définit la structure partagée autour d'une ou plusieurs pages. Les mises en page permettent une expérience « semblable à celle d'une application » en préservant l'état et en évitant les rechargements d'une page entière pendant la navigation.

## Logique d'imbrication

Les mises en page suivent une structure hiérarchique basée sur l'arborescence des répertoires sous `src/routes/`.

1.  **Disposition racine** : chaque projet a une disposition racine (par exemple, `src/routes/layout.nexy`). Il s'agit de la seule mise en page responsable de la définition du shell du document : `<html>`, `<head>` et `<body>`.
2.  **Mises en page imbriquées** : n'importe quel dossier peut contenir son propre fichier `layout.*`. Cette mise en page enveloppe toutes les pages et sous-mises en page de ce dossier.
3.  **Héritage** : une page est enveloppée par toutes les mises en page depuis la racine jusqu'à son propre dossier.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Une mise en page imbriquée dessine uniquement sa partie de l'interface utilisateur et place la page là où va `children` :

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

## État partagé et composition

Les mises en page sont conçues pour être stables. En mode client, lors de la navigation entre deux pages partageant la même mise en page, la mise en page n'est **pas** restituée ; seul le contenu enfant change. En mode serveur, chaque navigation est un nouveau document.

- **Slots** : les mises en page fournissent un emplacement dans lequel la page imbriquée est injectée : `children` dans JSX et le prop `children` dans une mise en page `.nexy`.
- **Préservation de l'état** : étant donné que la mise en page reste montée, tout état qu'elle contient (par exemple, une requête de recherche dans un en-tête) est préservé pendant la navigation.

Le même emplacement dans une disposition `.nexy` :

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

Le champ de recherche ci-dessous conserve ce que l'utilisateur a saisi lorsqu'il se déplace entre les pages du tableau de bord, car la mise en page qui le contient ne se démonte jamais :

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

## Contraintes statiques

Pour les itinéraires pré-rendus (SSG), la disposition racine ne peut pas dépendre des données de temps de requête telles que les cookies ou les en-têtes. Il doit être représentable comme une coque statique que le client hydrate ensuite.

Lisez plutôt le thème depuis le navigateur, dans un script du shell statique :

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

## Mise en œuvre du cadre

La mise en œuvre des slots et de l’imbrication varie légèrement selon le framework. Consultez le guide des **Différences** pour la technologie que vous avez choisie :

- [React Différences](../react/differences.md)
- [Vue Différences](../vue/differences.md)
- [Svelte Différences](../svelte/differences.md)
- [Solid Différences](../solid/differences.md)
- [Preact Différences](../preact/differences.md)
