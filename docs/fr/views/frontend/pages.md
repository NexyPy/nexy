# Pages d'interface

Une **Page** est l'unité de base d'une application Nexy. Il s'agit d'une ressource adressable par URL définie par un fichier sous `src/routes/`. 

Quel que soit le framework client utilisé, chaque page suit le même cycle de vie universel et les mêmes contraintes architecturales.

## Le cycle de vie des pages

Lorsqu'un utilisateur accède à une page, Nexy effectue les étapes suivantes :

1.  **Route Matching** : Le routeur identifie le fichier correspondant à l'URL.
2.  **Récupération de données** : le serveur exécute la logique de la page (frontmatter Python ou chargeur de framework) pour récupérer les données requises.
3.  **Composition** : la page est enveloppée dans sa `layout.nexy` (ou mise en page de cadre) la plus proche.
4.  **Rendu** : Le résultat est rendu au format HTML (via Jinja2, Markdown ou framework SSR).
5.  **Hydratation** : Si la page utilise un framework client, le navigateur attache la logique interactive au HTML statique.

## Routage et URL

Le routage est strictement basé sur des fichiers. L'URL est déterminée par le chemin du fichier sous `src/routes/`, moins l'extension.

### Segments dynamiques
Pour créer un itinéraire qui varie en fonction d'un paramètre (par exemple, un profil utilisateur), utilisez des crochets :
- `src/routes/user/[id].tsx` → `/user/123`

La valeur du segment (`123`) est disponible pour la page via le hook `useParams()` de `@nexy/client`.

### Groupes d'itinéraires
Les dossiers entre parenthèses sont ignorés par le routeur mais vous permettent de regrouper des fichiers à des fins d'organisation ou de présentations partagées :
- `src/routes/(auth)/login.tsx` → `/login`

## Métadonnées des pages
Chaque page peut définir des métadonnées (titre, description, balises OpenGraph) que Nexy injecte dans le shell du document. Dans les fichiers `.nexy`, cela se fait au début ; dans les fichiers framework, il est fourni via un export `metadata`.

## Mise en œuvre du cadre
Les concepts ci-dessus sont universels. Pour voir comment implémenter une page dans votre framework spécifique, consultez le guide **Différences** :

- [Réagir aux différences](../react/differences.md)
- [Différences de vue](../vue/differences.md)
- [Sveltes différences](../svelte/differences.md)
- [Des différences solides](../solid/differences.md)
- [Différences préact](../preact/differences.md)