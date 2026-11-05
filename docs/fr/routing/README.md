# Routage

Nexy dispose de deux routeurs natifs. Vous pouvez en choisir un par fonctionnalité ; ils peuvent coexister dans la même application.

**Pas sûr? Utilisez le routage basé sur des fichiers.** Il couvre les pages et les points de terminaison de l'API sans configuration. Ajoutez le routeur modulaire lorsqu'un backend a besoin de contrôleurs, de services injectés ou de gardes.

| Vous construisez | Utilisez |
|---|---|
| Des pages, du contenu, un site avec quelques points de terminaison | Basé sur des fichiers |
| Une grande API avec des services partagés sur les itinéraires | Modulaire |
| Les deux : des pages pour les personnes, une API structurée pour les machines | Basés sur des fichiers et modulaires ensemble |

```diagram filename="Le routeur basé sur fichiers, en un coup d'œil"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| Routeur | Source | Activé par |
|---|---|---|
| [Basé sur un fichier (FBR)](fbr/README.md) | chaque fichier sous `src/routes/` | le répertoire existe |
| [Modulaire](modular/README.md) | contrôleurs et modules | `useRouter = AppModule` dans `nexyconfig.py` |

FBR est analysé chaque fois que `src/routes/` existe, même avec un routeur modulaire monté.

## Coexistence et priorités

Vous pouvez combiner une intégration FBR, modulaire et personnalisée. Nexy enregistre ces routes dans l'ordre de leur découverte. Si deux routeurs définissent le même chemin URL, le premier enregistré gagne. 

*Remarque : Nexy ne fournit actuellement pas de diagnostic pour les collisions d'URL ; le premier itinéraire pour revendiquer un chemin fait simplement de l'ombre aux autres.*

## Routage basé sur des fichiers

Un itinéraire est un fichier. L'URL est son chemin sous `src/routes/`, moins l'extension. Comme Next.js, un projet est dans l'un des deux modes, choisis avec `useCSR` :

| | `useCSR = False` (par défaut) | `useCSR = True` |
|---|---|---|
| Pages | `.nexy`, `.md`, `.mdx` | fichiers de votre framework client |
| Disposition des racines | `layout.nexy` | `layout.tsx` (React) |
| Composants clients | autorisés, sous forme d'îlots à l'intérieur des pages | les pages elles-mêmes |
| Routes API | `.py` | `.py` |

Voir [Mode serveur et mode client](fbr/modes.md).

| Article | Ce qu'il couvre |
|---|---|
| [fbr/pages](fbr/pages/README.md) | pages, [routes dynamiques](fbr/pages/dynamic-routes.md) et groupes de routes |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` gestionnaires de routes, [validation et erreurs](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` et gardes, hérités du répertoire |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, hérité du répertoire |
| [fbr/erreurs](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, erreurs JSON |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | liaison, navigation client, [hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket gestionnaires |
| [fbr/inheritance](fbr/inheritance.md) | comment les mises en page, les dépendances et les pages d'erreur héritent |

## Routage modulaire

Contrôleurs, modules et injection de dépendances, à la manière de NestJS. Voir [Routage modulaire](modular/README.md) et [Nexy et NestJS](modular/vs-nestjs.md).

## Intégration personnalisée

Vous pouvez également intégrer un routeur FastAPI existant dans votre projet Nexy. Voir [Intégration du routage personnalisé](custom/README.md).

## Prochaines étapes

- [Routage basé sur des fichiers](fbr/README.md)
- [Rendu](../rendering/README.md)
- [Views](../views/README.md) : ce qui se passe à l'intérieur des fichiers
