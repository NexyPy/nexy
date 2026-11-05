# Itinéraires dynamiques

Un segment de chemin écrit entre crochets correspond à n’importe quelle valeur et la transmet à la page ou au gestionnaire.

## Segments dynamiques

`blog/[slug].nexy` sert `/blog/{slug}`. Dans une page, déclarez le segment comme propriété ; dans un gestionnaire Python, prenez-le comme argument.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Segments typés

L'annotation décide du type.

| Où | Conversion |
|---|---|
| `.py` gestionnaire | toute annotation de type FastAPI (`int`, `UUID`, `Enum`...) |
| `.nexy` pages | `int` et `float` sont converties ; tout le reste reste une chaîne |

Une valeur qui ne correspond pas à l'annotation est **introuvable** : `/api/users/abc` répond à `404`, car une route dynamique capture n'importe quelle URL et une URL qui ne peut pas être convertie n'existe tout simplement pas. Voir [Validation et erreurs](../handlers/validation-and-errors.md).

## Segments fourre-tout

`docs/[...path].nexy` sert `/docs/{path:path}`. Les segments restants arrivent sous la forme d’une seule chaîne, barres obliques incluses.

```nexy filename="src/routes/docs/[...chemin].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` donne `path == "a/b/c"`.

## Groupes d'itinéraires

Un répertoire entre parenthèses organise les fichiers sans apparaître dans l'URL. Il participe toujours à l'[héritage](../inheritance.md) : ses `layout.*` et `dependencies.py` s'appliquent à ce qui est à l'intérieur.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Utilisez des groupes pour donner différentes mises en page à différentes sections sans modifier leurs URL.

## Priorité

Les itinéraires statiques l'emportent sur les itinéraires dynamiques et les itinéraires dynamiques sur les fourre-tout : `/blog/new` correspond à `blog/new.nexy` avant `blog/[slug].nexy`.

## Un fichier par URL

Deux fichiers qui renvoient à la même URL sont tous deux enregistrés. Ne mettez pas `blog.nexy` à côté de `blog/index.nexy`, et ne mélangez pas `index.nexy` et `index.py` pour le même chemin.

## Prochaines étapes

- [Pages](README.md)
- [Pages d'erreur](../errors/README.md)
- [Conventions de fichiers](../../../reference/file-conventions.md)
