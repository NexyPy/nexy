# Déployer

Deux commandes : `nx build` produit les artefacts, `nx start` les sert.

**Avant de commencer :** un projet qui se construit localement avec `nx build` et - pour les pages client - la chaîne d'outils frontend installée par `nx new`.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

Le runtime n’a besoin que de Python. Uvicorn sert l'application compilée et les actifs statiques ; aucun processus Node et aucun processus Vite ne sont impliqués.

## Ce que produit la construction

`__nexy__/` contient les modules de route compilés, le bundle client sous `__nexy__/client/` et le code HTML pré-rendu pour les routes du framework. Copiez le projet - source plus `__nexy__/` - ou construisez à l'intérieur de l'image.

## Docker

L'étape de construction a besoin de Node (pour Vite) et de Python (pour le compilateur). L'étape d'exécution n'a besoin que de Python.

```dockerfile filename="Fichier Docker"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` récupère un Python géré lorsque l'image de base n'en a pas, c'est pourquoi l'étape de construction peut démarrer à partir d'une image Node.

## Derrière un proxy inverse

Exécutez `nx start` sur localhost et laissez Nginx, Caddy ou le proxy de la plateforme mettre fin à TLS :

```bash
nx start --host 127.0.0.1 --port 8000
```

Assurez-vous que le proxy transfère les mises à niveau de WebSocket si vous utilisez les gestionnaires `SOCKET` et qu'il transfère l'hôte d'origine - FastAPI crée des URL absolues à partir de celui-ci.

## Bilan de santé

Ajoutez un fichier de gestionnaire, `src/routes/api/health.py`, et sondez `/api/health` - plutôt qu'une page dont le rendu peut être lent :

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## Hébergement statique

Chaque page est HTML, mais Nexy suppose un serveur pour le routage et pour les gestionnaires d'API.

> [!REMARQUE]
> il n'y a pas de mode de construction `--static`. Une exportation purement statique doit être générée dans votre pipeline à partir de la sortie `nx build`.

## Liste de contrôle

- [ ] `nx build` dans CI, aucun avertissement pour les routes que vous prévoyez d'afficher sur le serveur
- [ ] `nx start` se termine avec le code 1 et ne démarre rien lorsqu'un fichier de route ne peut pas se charger
- [ ] `NEXY_ACTION_SECRET` défini, ou `__nexy__/action.key` conservé avec la build
- [ ] `useDocs = False` en production si le schéma API ne doit pas être public
- [ ] `useTrustedHost` et `useHTTPSRedirect` définis pour les déploiements publics
- [ ] `__nexy__/` non engagé

## Prochaines étapes

- [Config](../reference/config.md) : HTTPS, hôtes de confiance, sessions
- [Frontend](../guides/frontend.md) : ce que Vite construit
- [Testing](../guides/testing.md) : les commandes à exécuter en CI
