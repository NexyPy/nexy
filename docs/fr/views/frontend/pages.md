# Pages frontales

Une **Page** est l'unité de base d'une application Nexy. Il s'agit d'une ressource adressable par URL définie par un fichier sous `src/routes/`. 

Quel que soit le framework client utilisé, chaque page suit le même cycle de vie universel et les mêmes contraintes architecturales.

## Le cycle de vie des pages

Lorsqu'un utilisateur accède à une page, Nexy effectue les étapes suivantes :

1.  **Route Matching** : Le routeur identifie le fichier correspondant à l'URL.
2.  **Récupération de données** : le serveur exécute le frontmatter Python de la page pour récupérer les données dont il a besoin.
3.  **Composition** : la page est enveloppée dans son `layout.nexy` (ou mise en page de cadre) le plus proche.
4.  **Rendu** : le résultat est rendu au format HTML (via Jinja2, Markdown ou le framework SSR).
5.  **Hydratation** : Si la page utilise un framework client, le navigateur attache la logique interactive au HTML statique.

Étapes 2 à 4 dans une page en mode serveur : le contenu est récupéré, le modèle est restitué et la mise en page racine encapsule le résultat.

```nexy filename="src/routes/users.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Routage et URL

Le routage est strictement basé sur des fichiers. L'URL est déterminée par le chemin du fichier sous `src/routes/`, moins l'extension.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Segments dynamiques
Pour créer un itinéraire qui varie en fonction d'un paramètre (par exemple, un profil utilisateur), utilisez des crochets :
- `src/routes/user/[id].tsx` → `/user/123`

La valeur du segment (`123`) est disponible pour la page via le hook `useParams()` de `@nexy/client`.

```tsx filename="src/routes/user/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Groupes de routes
Les dossiers entre parenthèses sont ignorés par le routeur mais vous permettent de regrouper des fichiers à des fins d'organisation ou de présentations partagées :
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Métadonnées de la page
Chaque page peut définir des métadonnées (titre, description, balises OpenGraph) que Nexy injecte dans le shell du document. Une page `.nexy` le place dans son frontmatter, avec un littéral ou avec `setMetadata` :

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` est Python : une page `.tsx`, `.vue` ou `.svelte` n'a pas d'exportation `metadata`, donc en mode client, écrivez le titre et les balises méta dans la mise en page racine. Voir [Métadonnées de la page](../../routing/fbr/pages/metadata.md) pour chaque champ.

## Mise en œuvre du cadre
Les concepts ci-dessus sont universels. Pour voir comment implémenter une page dans votre framework spécifique, consultez le guide **Différences** :

- [React Différences](../react/differences.md)
- [Vue Différences](../vue/differences.md)
- [Svelte Différences](../svelte/differences.md)
- [Solid Différences](../solid/differences.md)
- [Preact Différences](../preact/differences.md)
