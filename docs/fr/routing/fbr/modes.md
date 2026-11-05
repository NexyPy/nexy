# Mode serveur et mode client

Un projet Nexy est soit **rendu par le serveur**, soit **routé par le client**, comme un projet Next.js est soit des pages rendues sur le serveur, soit une application client. `useCSR` dans `nexyconfig.py` choisit.

## Mode serveur (`useCSR = False`)

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

- Les pages sont des fichiers `.nexy`, `.md` ou `.mdx` sous `src/routes/`.
- La racine `layout.nexy` possède `<!DOCTYPE html>`, `<html>`, `<head>` et `<body>`.
- Les composants clients (React, Vue, Svelte, Solid ou Preact) sont autorisés en tant qu'**îles** : vous en importez un à partir d'une page `.nexy` et il s'hydrate dans le navigateur. Voir [Îles](../../rendering/islands.md).
- Un composant client n'est jamais une route. Gardez-les dans `src/components/`.
- Un framework client à la fois.

```text
src/
├─ routes/
│  ├─ layout.nexy         document
│  ├─ index.nexy          page
│  └─ api/users.py        API handler
└─ components/Counter.tsx island
```

## Mode client (`useCSR = True`)

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

- Les pages sont les fichiers de votre framework client : `.tsx` pour React, `.vue`, `.svelte`.
- Les fichiers `.md` et `.mdx` restent des itinéraires valides : Nexy les restitue sur le serveur à l'intérieur de la configuration client, et le routeur client prend en charge la navigation à partir de là.
- La disposition racine de n'importe quel framework (`layout.tsx`, `layout.vue`, `layout.svelte`) possède `<!DOCTYPE html>`, `<html>`, `<head>` et `<body>`, comme la disposition racine du routeur d'application Next.js. Nexy le restitue dans Node pour la première réponse et le framework hydrate l'ensemble du document. Voir [layout.tsx](../../views/react/differences.md).
- Les fichiers `.py` sont des gestionnaires d'API servis par FastAPI, à côté des routes client.
- Il n'y a aucun fichier `.nexy` du tout, ni aucun `layout.nexy`.
- La navigation entre les pages s'effectue dans le navigateur.

```text
src/routes/
├─ layout.tsx             document
├─ index.tsx              page
├─ users.tsx              page
└─ api/users.py           API handler
```

## Ce qui est rejeté

Nexy vérifie le projet avant `nx dev`, `nx start` et `nx build` et s'arrête avec la liste des fichiers :

| Mode | Rejeté | Message |
|---|---|---|
| serveur | `.tsx`, `.jsx`, `.vue` ou `.svelte` sous `src/routes/` | déplacer les composants vers `src/components/`, ou définir `useCSR = True` |
| client | n'importe quel fichier `.nexy` sous `src/routes/` | écrivez-les en tant que composants du framework, ou définissez `useCSR = False` |
| les deux | plus d'un framework frontend dans `useFF` | `useFF must configure exactly one frontend framework` |
| client | `useRouter` (routeur modulaire) | `useCSR requires file-based routing` |
| client | non `useFF` | `useCSR requires a client framework` |

Les fichiers et dossiers commençant par `_` ou `.` sont ignorés par cette vérification.

## Lequel

- **Contenu, marketing, documentation, sites SEO-first** : mode serveur avec îlots.
- **Tableaux de bord et applications avec navigation client riche** : mode client.
- **Une Python API avec une application client en haut** : mode client, avec des `.py` gestionnaires à côté des pages.

## Prochaines étapes

- [Mises en page](layouts/README.md)
- [Rendu](../../rendering/README.md)
- [Configuration](../../reference/config.md)
