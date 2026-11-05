# Vues

Avant de choisir un format de fichier, il est important de faire la distinction entre la manière dont Nexy gère les ressources et la manière dont il les restitue.

| Durée | Définition |
|---|---|
| **Page** | Une ressource adressable par URL de l'application. Il est défini par un fichier sous `src/routes/`. |
| **Voir** | Processus de production du corps de réponse pour une page. Une vue transforme la logique et les données en HTML ou JSON. |
| **Composant** | Un bloc de construction d'interface utilisateur réutilisable utilisé pour composer une vue. Les composants peuvent être des assistants Nexy natifs ou spécifiques au framework (React, Vue, etc.). |
| **Gestionnaire de route** | Une fonction Python qui gère une requête HTTP pour une méthode spécifique (par exemple, `GET`, `POST`). |
| **Point de terminaison** | Combinaison unique d'une URL et d'une méthode HTTP à laquelle répond un gestionnaire de route. |

**Pas sûr? Écrivez un fichier `.nexy`.** Il ne nécessite aucun framework client et vous pouvez y ajouter un composant React, Vue, Svelte, Solid ou Preact plus tard, en tant qu'îlot.

```diagram filename="Quel fichier pour quelle page"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## Formats

| Formater | Fichier | Rendu du serveur | Cadre client | Remarques |
|---|---|---|---|---|
| `.nexy` | [Fichiers .nexy](nexy/README.md) | Jinja2 + Python logique, diffusée en continu | facultatif | Format de page Natif Nexy |
| `.md` | [Markdown et MDX](nexy/markdown.md) | Markdown au moment de la demande | en option via la mise en page | Pure Markdown, GFM, encapsulé dans la mise en page |
| `.mdx` | [Markdown et MDX](nexy/markdown.md) | cadre RSS | React ou Preact | Markdown avec des composants |
| `.tsx` | [React](react/differences.md), [Solid](solid/differences.md) ou [Preact](preact/differences.md) | mode client : le framework, rendu en Node | React, Solid ou Preact | Itinéraires de composants |
| `.vue` | [Vue](vue/differences.md) | mode client : le framework, rendu en Node | Vue | Itinéraires SFC |
| `.svelte` | [Svelte](svelte/differences.md) | mode client : le framework, rendu en Node | Svelte | Itinéraires SFC |

Assistants `Image`, `Link`, `Audio`, `Video` et `Import` intégrés : [Composants](nexy/components.md).

## Formats de mixage

Vous pouvez mélanger différentes technologies au sein d’un même projet :
- **Îles** : Vous pouvez importer un composant React ou Vue dans une page `.nexy`. Le serveur restitue le shell et le framework hydrate le composant sur le client.
- **Logique partagée** : les gestionnaires de routes dans les fichiers `.py` peuvent fournir des données aux pages dans n'importe quel format via l'état d'application partagé ou les appels d'API.

## Activer un cadre

Définissez `useFF` dans `nexyconfig.py` et exécutez `nexy new` pour ajouter des dépendances :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

Avec un framework activé, Vite gère ses bundles clients. En mode client, ses extensions deviennent des routes ; en mode serveur, les mêmes fichiers sont des composants que vous importez en tant qu'îlots - un fichier framework sous `src/routes/` y est rejeté. Voir [mode serveur et mode client](../routing/fbr/modes.md).

> [!NOTE]
> en mode [CSR](../rendering/csr.md), seuls les fichiers de routes du framework sont navigables côté client.

## Mises en page

Un `layout.*` dans un répertoire enveloppe les pages en dessous. Voir [mises en page](../routing/fbr/layouts/README.md).

## Prochaines étapes

- [Fichiers .nexy](nexy/README.md) : Python + Jinja2 + accessoires
- [Markdown et MDX](nexy/markdown.md) : pages de contenu
- [Composants](nexy/components.md) : assistants HTML intégrés
