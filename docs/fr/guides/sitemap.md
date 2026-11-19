# Comment ajouter un sitemap.xml et un robots.txt à un site Nexy ?

Définissez `useSiteUrl` dans `nexyconfig.py` : Nexy sert ensuite `/sitemap.xml`, qui répertorie chaque page statique du projet, et un `/robots.txt` qui y pointe les moteurs de recherche.

## Allumez-le avec `useSiteUrl`

`useSiteUrl` est l'origine publique du site, celle que les moteurs de recherche voient :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` et `nx start` répondent ensuite aux deux fichiers. Sans `useSiteUrl`, aucun des deux n'existe, donc un projet ne publie jamais l'URL de son serveur de développement par erreur.

## Ce que répertorie le plan du site

Le plan du site donne chaque page sous forme d'URL absolue sur `useSiteUrl` :

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Une route est répertoriée lorsqu'elle répond HTML à un `GET` sur un chemin fixe :

<!-- router:fbr,custom -->
- une page (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) est répertoriée ;
- une page dynamique, telle que `src/routes/users/[id].nexy`, est laissée de côté : Nexy ne peut pas connaître ses valeurs ;
- un gestionnaire de route Python répond à JSON, il est donc laissé de côté.
<!-- /router -->

<!-- router:modular -->
- une route de contrôleur qui répond au HTML, avec `@UseResponse(response_class=HTMLResponse)`, est répertoriée ;
- une route avec un paramètre de chemin, tel que `/users/{id}`, est laissée de côté : Nexy ne peut pas connaître ses valeurs ;
- une route qui répond à JSON est laissée de côté.
<!-- /router -->

Une route masquée du schéma API (`include_in_schema=False`) est également laissée de côté.

## Le `robots.txt` qu'il sert

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Écrivez le vôtre à la place

Votre propre fichier gagne toujours et Nexy ne l'écrase jamais :

- `public/robots.txt` ou `public/sitemap.xml` est servi tel quel, comme chaque fichier de `public/` ;
- un itinéraire du projet en `/robots.txt` ou `/sitemap.xml` garde son chemin.

Rédigez votre propre plan de site pour répertorier les pages dynamiques, par exemple une URL par article de blog.

## Prochaines étapes

- [Métadonnées de la page](../routing/fbr/pages/metadata.md) : les moteurs de recherche de titre et de description affichent
- [Configuration](../reference/config.md) : chaque paramètre de `nexyconfig.py`
- [Déployer](../deployment/README.md) : servir le projet en production
