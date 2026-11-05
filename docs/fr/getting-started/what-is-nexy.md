# Qu’est-ce que Nexy ?

Nexy est un framework Python pour les applications Web fullstack : vos pages et votre API vivent dans un seul projet et sont servies par un seul serveur.

## Ce que vous obtenez

- **Pages dans Python.** Un fichier `.nexy` est HTML avec quelques lignes de Python en haut ; un fichier `.md` est aussi une page. Aucun JavaScript n'est nécessaire pour afficher une page.
- **Une API dans le même projet.** Un fichier `.py` sous `src/routes/` répond aux requêtes HTTP : une fonction nommée `GET` répond à `GET`, une fonction nommée `POST` répond à `POST`.
- **Documentation API gratuite.** Chaque route API apparaît dans un schéma OpenAPI, et Scalar l'affiche comme référence interactive dans `/docs`.
- **Formulaires qui appellent Python.** Un formulaire, ou un appel tapé depuis le navigateur, atteint la même fonction Python.
- **Un framework frontend quand vous en voulez un.** React, Vue, Svelte, Solid ou Preact, pour un composant ou pour l'ensemble du site.
- **Une commande pour fonctionner, une pour expédier.** `nx dev` se recharge au fur et à mesure que vous enregistrez ; `nx build` prépare la production.

## Sur quoi il est construit

La version actuelle, 2.2, repose sur des outils que vous connaissez peut-être déjà :

| Partie | Construit sur | Ce que cela signifie pour vous |
|---|---|---|
| Serveur et API | [FastAPI](https://fastapi.tiangolo.com/) | une route API est une route FastAPI : la validation Pydantic et les dépendances fonctionnent comme d'habitude |
| Référence API | OpenAPI et [Scalaire](https://scalar.com/) | le schéma est à `/openapi.json`, la référence à `/docs` |
| Pages | Jinja2 | une page `.nexy` utilise des balises Jinja2 telles que `{{ title }}` |
| Frontend (facultatif) | [Vite](https://vite.dev/) | uniquement avec un framework frontend, qui nécessite également Node.js |

## Une première page et un premier point de terminaison

Une page, à `/hello` :

```nexy filename="src/routes/bonjour.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Un point de terminaison, à `GET /api/items`, répertorié à `/docs` sans aucun code supplémentaire :

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## Ce que Nexy vous laisse

La base de données, le login et les règles sur qui peut faire quoi appartiennent à votre application, vous choisissez donc les bibliothèques. [Bases de données](../guides/databases.md) et [Middleware et sécurité](../guides/middleware-and-security.md) montrent où chacun se connecte.

## Prochaines étapes

- [Installation](installation.md) : installez uv et créez un projet
- [Démarrage rapide](quick-start.md) : exécutez-le, modifiez une page, construisez-la
- [Concepts de base](core-concepts.md) : les quelques mots utilisés par le reste de la documentation
