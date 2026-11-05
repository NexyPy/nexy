# Métadonnées de la page

Une page nomme son titre et ses balises head, et la mise en page racine les écrit une seule fois.

## Dites-le dans la page

Pour une page qui ne change jamais, écrivez un littéral en haut du texte :

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Lorsque le titre dépend des données, appelez plutôt `setMetadata` :

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Un contrôleur modulaire appelle `setMetadata(...)` avant de renvoyer `useViews(...)`.

## Écrivez-le dans la mise en page

La disposition racine possède le `<head>`. Une ligne écrit ce que dit la page, échappé :

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Une page s'exécute avant ses mises en page, de sorte que la mise en page trouve ce que la page a demandé. Une page qui ne dit rien obtient le `useTitle` de votre `nexyconfig.py`, et aucune autre balise.

## Les champs

| Champ | Écrit comme |
|---|---|
| `title` | `<title>` ; avec `title_template="%s \| My site"` le titre est mis dans le `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, par exemple `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | un `<meta property="og:...">` par touche : `{"image": "/cover.png"}` donne `og:image` |
| `twitter` | un `<meta name="twitter:...">` par clé |
| `extra` | une liste de dictionnaires d'attributs, un `<meta>` chacun : `[{"name": "theme-color", "content": "#fff"}]` |

Un appel ultérieur remplace une valeur ; `og`, `twitter` et `extra` s'ajoutent à ce qui est là. Un champ qui n'existe pas génère `TypeError`, donc une faute de frappe ne fait rien en silence.

## Coffre-fort par défaut

Chaque valeur est échappée en HTML, donc un titre construit à partir d'une URL ou de la base de données ne peut pas fermer la balise et injecter un script. Une valeur est échappée une fois, lorsque la mise en page appelle `html()` : ne l'échappez pas vous-même.

## Prochaines étapes

- [Pages](README.md)
- [Mises en page](../layouts/README.md)
- [Pages d'erreur](../errors/README.md)
