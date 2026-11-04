# Héritage

Plusieurs fichiers dans `src/routes/` s'appliquent à tout ce qui se trouve sous leur répertoire. Ils résolvent tous de la même manière
chemin : Nexy part du répertoire de l'itinéraire et se dirige vers `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Fichier | Règle |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | chaque mise en page, de la racine à la page, l'enveloppe, **le plus à l'extérieur en premier** |
| `middleware.py` | chaque fichier de la racine à la route encapsule la requête, **le plus à l'extérieur en premier**, avant les dépendances |
| `dependencies.py` | chaque fichier de la racine à la route s'exécute, **le plus à l'extérieur en premier**, puis les propres gardes du gestionnaire |
| `notfound.nexy`, `errors.nexy` | le **le plus proche** gagne, par code de statut |

Pour la page ci-dessus, les mises en page s'imbriquent comme
`root layout > (shop) layout > cart layout > page`, et les dépendances s'exécutent comme
`root > (shop) > cart > handler guards`.

## Pourquoi les plus extérieurs en premier

Une disposition externe dessine le cadre et une dépendance externe décide qui peut entrer. Les mettre
signifie d'abord que les internes peuvent compter sur eux : un répertoire qui nécessite une authentification s'exécute avant un
gestionnaire qui lit l'utilisateur.

## Mise en page

Tous les fichiers de mise en page d'une pile de familles de dossiers : voir [Layouts](layouts/README.md). Différentes familles le font
ne pas mélanger : un `layout.vue` ne termine jamais une page `.tsx`, et un projet a soit `layout.nexy`, soit un client
mises en page, jamais les deux ([modes](modes.md)).

## Fichiers middleware

Voir [Fichiers Middleware](middleware/README.md) : ils s'exécutent avant les dépendances et peuvent répondre
sans atteindre la route.

## Dépendances

Voir [Dépendances](dependencies/README.md) pour l'ordre dans un fichier de gestionnaire, y compris `@UseGuard`
et `@Middleware`.

## Pages d'erreur

`notfound.nexy` et `errors.nexy` sont installés une fois à la racine des routes ; une copie dans un sous-répertoire
affine la page pour ce préfixe. Voir [Pages d'erreur](errors/README.md).

## Prochaines étapes

- [Mise en page](layouts/README.md)
- [Dépendances](dependencies/README.md)
- [Pages d'erreur](errors/README.md)