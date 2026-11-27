# Comment publier un module dans le registre Nexy ?

Exécutez `nx publish` à partir d'un répertoire de module avec un `nx.toml` valide, un jeton de registre et chaque fichier déclaré par le manifeste ; la commande vérifie la version, crée une archive et télécharge une version immuable.

## Préparer le manifeste

Un module source répertorie chaque fichier qu'il livre. L'archive contient `nx.toml` et exactement ces fichiers.

```toml filename="nx.toml"
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py", "src/helpers.py"]
```

Le champ `name` doit être en minuscule `@scope/name`. Le champ `version` doit contenir trois chiffres séparés par des points. Les fichiers doivent être des chemins relatifs à l'intérieur du module. Un module de package déclare `source.package` au lieu de `source.files`.

## Vérifiez avant de télécharger

Utilisez `--dry-run` pour valider le manifeste, archiver les fichiers déclarés et imprimer la somme de contrôle sans télécharger :

```bash
nx publish --dry-run
```

Un essai à sec ne nécessite pas de jeton. Il imprime une ligne `warning:` pour chaque importation relative qui pointe vers un fichier que le manifeste ne déclare pas. Par exemple, `from .helpers import token` dans `src/auth.py` a besoin de `src/helpers.py` dans `source.files`, sinon une installation obtiendrait une importation interrompue.

## Définir le jeton

`nx publish` lit `NEXY_REGISTRY_TOKEN`, puis `~/.config/nexy/registry-token`. Le jeton est envoyé dans l'en-tête `Authorization` et n'est jamais imprimé.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

Le fichier de jetons permet à un futur `nx login` d'écrire le même identifiant. Sans aucune des sources, la commande imprime `error: No registry token` et quitte avec l'état 1.

## Publier

```bash
nx publish
```

La commande imprime le nom, la version et la somme de contrôle SHA-256 de la version publiée. Une paire nom et version est immuable : la publier à nouveau imprime une erreur de conflit. Publiez plutôt une nouvelle version.

## Utiliser un autre registre

Par défaut, la commande poste sur `https://registry.nexypy.dev`. Utilisez `--registry` pour un autre registre, par exemple local lors du développement :

```bash
nx publish --registry http://localhost:8000
```

Seules les URL https sont acceptées, plus le http simple sur `localhost`, `127.0.0.1` et `::1`. Les réponses transitoires `429` et `5xx` sont réessayées deux fois ; un mauvais manifeste, un jeton manquant ou un conflit ne sont pas retentés.

## Vérifier la version

```bash
nx add @acme/auth@1.2.0
```

Voir [Installer les modules](install-modules.md) pour les mises à niveau, les broches et les paramètres de confiance.
