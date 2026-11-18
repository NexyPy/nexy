# CSR (rendu côté client)

## Définition

CSR confie la navigation au navigateur : après le premier document, le déplacement entre les pages ne demande plus de code HTML au serveur. Dans Nexy, il s'agit d'une décision de **projet**, pas d'une première page - `useCSR = True` fait en sorte que l'ensemble de l'application soit acheminé vers le client.

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
| Documenter | `layout.nexy` | la racine `layout.tsx` / `.vue` / `.svelte` possède `<html>`, `<head>`, `<body>` |
| Composants clients | îles à l'intérieur d'une page | les pages elles-mêmes |
| `.nexy` sous `src/routes/` | le format des pages | rejeté avant `nx dev`, `nx start` et `nx build` |
| Navigation | une demande complète par lien | le routeur client |

`.md` et `.mdx` restent valides : Nexy les restitue sur le serveur à l'intérieur de la configuration client, et le routeur client prend le relais à partir de là. Les gestionnaires de `.py` sont assis à côté des itinéraires et sont servis par FastAPI.

## Cycle de vie du rendu

1. La requête parvient au routeur basé sur des fichiers, qui trouve l'itinéraire correspondant et ses tracés.
2. La disposition racine restitue le **document entier** dans Node - la première réponse contient déjà le vrai `<html>`, pas une coquille vide.
3. Nexy injecte les actifs du client et une description JSON de la page avant `</body>`.
4. Le navigateur hydrate ce document. Les mises en page imbriquées conservent désormais leur état.
5. Un lien vers une autre route est géré par le routeur client : pas de demande de document, la page est rendue dans le navigateur.

En développement, le document est rendu à la demande par le serveur de développement Vite. En production, il est rendu une fois lors de la construction : une route statique obtient son document, une route dynamique en obtient un par paramètre statique déclaré, ou un shell - les mises en page autour d'une page vide - lorsqu'il n'en déclare aucun.

## Quand utiliser

- Tableaux de bord, éditeurs, tout ce qui se comporte comme une application.
- Une API Python avec une application client en haut.
- Une page où chaque interaction est locale et un aller-retour se ressentirait.

## Configuration

| Paramètre | Valeur |
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

## Pré-rendre un itinéraire dynamique

Un itinéraire dynamique tel que `src/routes/blog/[slug].tsx` correspond à n'importe quelle valeur, de sorte que la construction ne peut pas savoir quelles pages afficher. Exportez `generateStaticParams()` depuis la page pour les lister : `nexy build` restitue un document complet par entrée et `nexy start` le sert pour ce chemin. Les noms Next.js `getStaticPaths` et `getStaticParams` sont également acceptés, et la fonction peut être `async`.

```tsx filename="src/routes/blog/[slug].tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }]
}

export default function Post({ slug }: { slug: string }) {
  return <h1>{slug}</h1>
}
```

Chaque entrée est un objet de params, ou `{ params: {...} }` car `getStaticPaths` les renvoie. Le build écrit :

| Fichier dans `__nexy__/client/static/` | Servi pour |
|---|---|
| `src/routes/blog/[slug]/blog/hello.html` | `/blog/hello` |
| `src/routes/blog/[slug]/blog/world.html` | `/blog/world` |
| `src/routes/blog/[slug].shell.html` | tout autre `/blog/...` |

Un chemin que la liste ne nomme pas fonctionne toujours : il récupère le shell, les mises en page autour d'une page vide et la page apparaît une fois le navigateur exécuté. Dans `nexy dev`, chaque chemin est rendu à la demande, répertorié ou non.

## Limites

- **L'ensemble du projet.** Vous ne pouvez pas mélanger une page CSR dans un projet en mode serveur : choisissez le mode de l'application, puis utilisez [îlots](islands.md) pour les parties interactives d'une page en mode serveur.
- **Pas de routes `.nexy`.** Tout ce que vous avez écrit dans `.nexy` doit devenir un composant de framework.
- **Les données du serveur passent par les points de terminaison.** Une route client ne peut pas lire la base de données au moment du rendu ; il appelle un gestionnaire `.py` ou une [Action](../guides/actions.md).
- **Une route dynamique démarre à partir d'un shell à moins qu'il ne répertorie ses paramètres.** Voir [Pré-rendu d'une route dynamique](#pre-render-a-dynamic-route).
- **La CSR n'est pas une page blanche, ni une SPA non plus.** Le premier document est restitué par le serveur ; c'est la navigation qui se produit dans le navigateur.

## Prochaines étapes

- [Mode serveur et mode client](../routing/fbr/modes.md) : les contrôles et les fichiers rejetés
- [Mises en page](../routing/fbr/layouts/README.md) : quel fichier possède le document
- [SSR](ssr.md) : la valeur par défaut, page par page
- [Frontend](../guides/frontend.md) : le serveur de développement et le build client
