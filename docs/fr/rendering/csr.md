# CSR (rendu côté client)

## Définition

La RSE confie la navigation au navigateur : après le premier document, le déplacement entre les pages ne demande plus
le serveur pour HTML. Dans Nexy, c'est une décision de **projet**, pas une première page - `useCSR = True` transforme le
l'ensemble de l'application est acheminé par le client.

## Comment ça marche

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Le projet change alors de forme :

| | Mode serveur (`False`) | Mode client (`True`) |
|---|---|---|
| Itinéraires | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Document | `layout.nexy` | la racine `layout.tsx` / `.vue` / `.svelte` possède `<html>`, `<head>`, `<body>` |
| Composants clients | îlots à l'intérieur d'une page | les pages elles-mêmes |
| `.nexy` sous `src/routes/` | le format de page | rejeté avant `nx dev`, `nx start` et `nx build` |
| Navigation | une requête complète par lien | le routeur client |

`.md` et `.mdx` restent valides : Nexy les restitue sur le serveur à l'intérieur du layout client, et le
Le routeur client prend le relais à partir de là. Les gestionnaires `.py` se trouvent à côté des routes et sont servis par FastAPI.

## Cycle de vie du rendu

1. La requête atteint le routeur basé sur des fichiers, qui trouve l'itinéraire correspondant et ses tracés.
2. La mise en page racine restitue le **document entier** dans Node - la première réponse porte déjà le
   un vrai `<html>`, pas une coquille vide.
3. Nexy injecte les actifs du client et une description JSON de la page avant `</body>`.
4. Le navigateur hydrate ce document. Les mises en page imbriquées conservent désormais leur état.
5. Un lien vers une autre route est géré par le routeur client : pas de demande de document, la page est
   rendu dans le navigateur.

En développement, le document est rendu à la demande par le serveur de développement Vite. En production, c'est
rendu une fois à la construction : une route statique récupère son document, une route dynamique en obtient un par déclaré
paramètre statique, ou un shell - les mises en page autour d'une page vide - lorsqu'il n'en déclare aucun.

## Quand utiliser

- Tableaux de bord, éditeurs, tout ce qui se comporte comme une application.
- Une API Python avec une application client en haut.
- Une page où chaque interaction est locale et un aller-retour se ressentirait.

## Configuration

| Réglage | Valeur |
|---|---|
| `useFF` | requis : `useCSR` sans framework client est rejeté |
| `useCSR` | `True` |
| `useRouter` | doit rester éteint : le routeur modulaire est rejeté en mode client |

Les fichiers et dossiers commençant par `_` ou `.` sont ignorés par ces vérifications.

## Exemple

```tsx filename="src/routes/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Contraintes

- **L'ensemble du projet.** Vous ne pouvez pas mélanger une page CSR dans un projet en mode serveur : choisissez le mode pour
  l'application, puis utilisez [islands](islands.md) pour les parties interactives d'une page en mode serveur.
- **Aucune route `.nexy`.** Tout ce que vous avez écrit dans `.nexy` doit devenir un composant de framework.
- **Les données du serveur passent par les points de terminaison.** Une route client ne peut pas lire la base de données au moment du rendu ; il
  appelle un gestionnaire `.py` ou une [Action](../guides/actions.md).
- **Une route dynamique a besoin d'un paramètre statique déclaré, ou elle démarre à partir d'un shell.** Exporter
  `getStaticParams()` de la page - les noms Next.js `getStaticPaths` et `generateStaticParams`
  sont également acceptés - avoir un document par valeur. Sans cela, le shell porte les mises en page et
  pas la page : la page apparaît une fois le navigateur exécuté.
- **La RSE n'est pas une page blanche, ni une SPA non plus.** Le premier document est restitué par le serveur ; il
  est la navigation qui se produit dans le navigateur.

## Prochaines étapes

- [Mode serveur et mode client](../routing/fbr/modes.md) : les contrôles et les fichiers rejetés
- [Layouts](../routing/fbr/layouts/README.md) : quel fichier possède le document
- [SSR](ssr.md) : la valeur par défaut, page par page
- [Frontend](../guides/frontend.md) : le serveur de développement et le build client