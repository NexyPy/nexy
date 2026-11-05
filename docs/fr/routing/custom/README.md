# Intégration de routage personnalisé

Nexy vous permet d'inclure une application FastAPI existante en tant que routeur dans votre projet. Ceci est utile lorsque vous souhaitez réutiliser la logique backend d'un autre service, intégrer des API tierces ou créer une application composite avec plusieurs problèmes de routage.

Contrairement aux routeurs modulaires et basés sur des fichiers, intrinsèques à Nexy, un routeur personnalisé est simplement un `APIRouter` que vous montez dans votre application.

## Quand utiliser un routeur personnalisé

- **Services tiers** : vous disposez d'une application FastAPI existante que vous souhaitez exposer via le client de Nexy.
- **Réutilisation du code** : extrayez la logique backend d'un autre projet dans un routeur et incluez-la dans un nouveau.
- **Modèles multi-locataires ou micro-frontend** : chaque locataire ou module fournit son propre routeur.
- **Migration progressive** : Commencez avec un `APIRouter` et faites-le évoluer plus tard vers un module Nexy complet.

## Comment ça marche

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

Le routeur est monté automatiquement par le résolveur de routeur de Nexy. Ses itinéraires sont disponibles sous le même modèle d'URL que dans l'application d'origine. Aucune configuration supplémentaire n'est nécessaire.

## Construire un routeur personnalisé

1. **Créer le routeur**
   ```python
   à partir de l'importation fastapi APIRouter

   api = APIRouter()
   @api.get("/statut")
   statut de définition asynchrone() :
       return {"status": "ok"}
   ```

2. **Référencez-le dans `nexyconfig.py`**
   ```python
   à partir de l'API d'importation .my_backend

   utiliserRouter = API
   ```

3. **Voies d'accès**
   - Les pages basées sur des fichiers (`.nexy`, `.md`) et les gestionnaires modulaires peuvent référencer `/status` comme ils le feraient pour n'importe quelle autre route.
   - Le routeur s'exécute selon le même processus, donc les dépendances, les connexions à la base de données et l'authentification fonctionnent exactement comme dans l'application d'origine.

## Intégration avec d'autres routeurs

Un projet Nexy peut combiner :

- **Routage basé sur des fichiers** (`src/routes/`) pour les pages et les points de terminaison simples
- **Routage modulaire** (`useRouter = AppModule`) pour les backends structurés
- **Routage personnalisé** (`useRouter = APIRouter`) pour le code tiers

Tous les trois coexistent ; chaque itinéraire n'est enregistré qu'une seule fois. Le routeur basé sur des fichiers est toujours analysé lorsque `src/routes/` existe.

## Accès CLI à l'application incluse

Les commandes `nexy dev` et `nx` fonctionnent sur le routeur monté comme un routeur intégré. Vous obtenez :

- Rechargement à chaud pour les points de terminaison définis dans le routeur personnalisé (s'il utilise les fonctionnalités habituelles du serveur de développement `nexy` ou FastAPI)
- Validation dans `nexyconfig.py` (tous `APIRouter` travaux)
- Documents générés automatiquement pour les itinéraires inclus (si vous les activez)

## Sécurité et isolement

Étant donné que le routeur est inclus et non monté via `app.mount`, il n'y a pas de couche ASGI supplémentaire. Le routeur réside dans le même objet d'application que vos routes modulaires et basées sur des fichiers. Cela signifie :

- Le middleware ajouté par le routeur personnalisé s'applique à toutes les requêtes.
- Les gardes et l'injection de dépendances définis dans le routeur personnalisé peuvent accéder au même conteneur que votre propre code (si vous utilisez l'injection modulaire).
- Il n'y a pas de préfixe d'URL autre que celui défini par le routeur lui-même.

Si vous avez besoin d'isolation, enveloppez le routeur dans une sous-application avant de l'inclure, ou utilisez les techniques FastAPI standard.

## Exemple : Inclusion d'un projet FastAPI existant

Supposons que vous ayez `auth.py` dans un autre package :

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

Dans `nexyconfig.py` :

```python
from other_package.auth import api

useRouter = api
```

Le point de terminaison `/login` est désormais accessible depuis votre site Nexy sans déplacer une ligne de code.

## Comment commencer

1. Créez votre `APIRouter` (ou trouvez-en un dans un package existant).
2. Pointez `useRouter` dessus dans `nexyconfig.py`.
3. Accédez à ses itinéraires via vos pages, gestionnaires ou frameworks clients.
4. Si vous avez besoin de plus de contrôle, convertissez le routeur personnalisé en routeur modulaire à l'aide de `AppModule`.

## Prochaines étapes

- [Routage basé sur des fichiers](../fbr/README.md) – Créez des pages et des gestionnaires simples à partir de fichiers.
- [Routage modulaire](../modular/README.md) – Backends structurés avec injection et gardes.
- [Gestionnaires d'itinéraires](../fbr/handlers/README.md) – Définir les points de terminaison Python.

Le routeur personnalisé vous offre la flexibilité de réutiliser le code FastAPI existant tout en conservant la simplicité des pages basées sur des fichiers et de la structure modulaire.