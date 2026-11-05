# Performances

Ce que fait `nx start` par défaut, ce qu'il faut activer et ce qui a été mesuré.

## Valeurs par défaut

| Préoccupation | Par défaut | Changez-le |
|---|---|---|
| Processus | un Uvicorn travailleur par CPU sous Linux et macOS, un sous Windows | `nx start` exécute l'application via Uvicorn |
| Compression | éteint | `useGZip = {"minimum_size": 1000}` dans [Configuration](../reference/config.md), ou compresser au niveau du proxy inverse |
| Fichiers statiques | servi avec `ETag` et `Last-Modified`, non `Cache-Control` | définir une mise en cache de longue durée au niveau du proxy inverse ou du CDN pour les bundles hachés |
| Pages HTML | rendu par requête, pas de cache | [ISR](../rendering/isr.md) avec `revalidate = N` |
| Documents sur l'API | sur | `useDocs = False` en production |
| Nœud au moment de l'exécution | aucun | `nx build` pré-rend les composants client |

Les deux switchs du tableau en `nexyconfig.py`, et ISR dans une page :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

## Mesuré

Une exécution locale, un travailleur Uvicorn, Windows, Python 3.13, des connexions persistantes à partir d'un générateur de charge Python sur la même machine. Considérez les chiffres comme une référence pour comparer les changements, et non comme une référence par rapport à d’autres cadres.

La route Nexy JSON de la table est ce fichier :

```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```

| Itinéraire | Concurrence | Requêtes par seconde | p50 | p99 |
|---|---|---|---|---|
| Route JSON nue FastAPI | 16 | ~4 500 | 3,4 ms | 5,1 ms |
| Itinéraire Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2 900 | 5,2 ms | 9,8 ms |
| Page Nexy SSR (16 Ko, 16 éléments) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Page Nexy SSR (16 Ko, 16 éléments) | 64 | ~670 | 94 ms | 126 ms |

Lecture du tableau :

- Les propres couches de Nexy (contexte de chemin, middleware) coûtent environ un tiers du débit d'une simple route FastAPI.
- Une page rendue par le serveur coûte environ 2 ms de CPU, réparties sur environ 16 rendus de modèles (un par composant). Les pages avec moins de composants sont proportionnellement moins chères.
- Le débit évolue avec les travailleurs. Sous Linux, `nx start` en démarre déjà un par CPU.

## Conseils pratiques

1. Mettez Nginx, Caddy ou la périphérie de votre plateforme : TLS, HTTP/2, Brotli et la mise en cache de longue durée pour les actifs `/__nexy__/client/` sont leurs points forts. Voir [Déployer](README.md).
2. Utilisez [ISR](../rendering/isr.md) pour les pages qui changent moins d'une fois par minute.
3. Hydratez-vous paresseusement avec les [îles](../rendering/islands.md) pour que le premier chargement soit expédié moins JavaScript.
4. Gardez le nombre de `.nexy` composants par page raisonnable : chacun est un rendu de modèle distinct.
5. Mesurez vos propres itinéraires. Un générateur de charge local qui maintient les connexions actives suffit pour comparer deux versions d’une page.

Conseil 1 avec Nginx : les bundles clients hachés sont mis en cache pendant un an, le reste va à Nexy.

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Prochaines étapes

- [Déployer](README.md)
- [Rendu](../rendering/README.md)
- [Configuration](../reference/config.md)
