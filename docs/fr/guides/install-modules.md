# Comment installer un module depuis le registre ?

Exécutez `nx add @scope/name` dans un projet Nexy pour télécharger une version à partir du registre du module, vérifiez-la et appliquez ses modifications déclarées. Ajoutez `@1.2.0` pour épingler une version exacte.

## Installer un module

Depuis la racine d'un projet Nexy :

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` lit les métadonnées et les archives de la version à partir de `useModuleRegistry`, vérifie la somme de contrôle SHA-256 et vérifie les plages de compatibilité `nexy` et `python` du module. Il écrit ensuite uniquement les fichiers déclarés par le manifeste, ajoute les packages Python déclarés avec `uv add`, ajoute les packages Node avec le gestionnaire de packages du projet et applique les hooks de configuration à `nexyconfig.py` et `package.json`. Les paramètres et fichiers existants restent tels quels : un fichier déclaré qui existe déjà est ignoré avec une ligne `warning:`.

Chaque installation réussie est enregistrée dans `.nexy/modules.json`. Validez ce fichier afin qu'un coéquipier obtienne la même version du module.

## Mettre à niveau un module

Pour effectuer la mise à niveau, exécutez à nouveau `nx add @acme/auth` une fois que le registre dispose d'une version plus récente, ou définissez un nouveau code PIN tel que `@acme/auth@1.3.0`. Un nom non épinglé sélectionne la version la plus récente dans la réponse `/versions` du registre. Exécuter à nouveau la même version imprime `is already installed` et ne change rien.

## Épingler une version

Une épingle est exacte : `nx add @acme/auth@1.2.0` installe `1.2.0` et aucune autre version. Utilisez une épingle dans CI et dans un `.nexy/modules.json` validé pour que chaque paiement installe le même code. Sans code PIN, une nouvelle version modifie la prochaine installation.

## Exécuter des migrations

Les migrations sont désactivées par défaut. Ajoutez `--migrate` lorsque vous souhaitez que les commandes déclarées d'une version s'exécutent une fois ses fichiers et dépendances en place :

```bash
nx add @acme/auth@1.2.0 --migrate
```

Chaque commande est imprimée avant son exécution. Le projet a besoin que son outil de migration soit installé avant qu'un module puisse en déclarer un.

## Définir le registre et ses règles de confiance

Les valeurs par défaut se trouvent dans `nexyconfig.py` :

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` est l'URL de base lue par la CLI. Seules les URL https sont acceptées, sauf le bouclage http pour un registre local en cours de développement. `useRequireSignedModules = True` refuse une version non signée. Une autorisation portant une signature est également refusée jusqu'à ce qu'un vérificateur soit disponible ; une fois qu'on le vérifie, `nx add` imprime `Verified by` avec l'identité du signataire. Conservez la valeur par défaut `False` uniquement pour les registres de confiance.
