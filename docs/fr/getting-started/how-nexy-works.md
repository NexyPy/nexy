# Comment fonctionne Nexy

Le modèle mental en une page : ce que Nexy construit, ce que Vite construit et ce qui se passe entre un fichier
et une page dans votre navigateur. Lisez-le une fois ; le reste de la documentation est alors un ensemble de détails.

## L'architecture Nexy

Une requête traverse cinq couches : Uvicorn l'accepte, le middleware la décore, le routeur sélectionne un fichier,
le moteur de rendu transforme ce fichier en HTML ou JSON, et la couche client prend le relais si la page a
JavaScript. Nexy possède les trois du milieu ; Vite et votre framework possèdent le client ; votre candidature
est propriétaire des données, de l'authentification et de l'autorisation.

Chaque couche, et ce qu'elle refuse de faire, est dans [Architecture](../architecture.md). Pour les forfaits de
Nexy lui-même, voir `ARCHITECTURE.md` à la racine du référentiel - il est écrit pour les contributeurs.

## Le cycle de vie des applications

`nx dev` fait six choses avant la première requête :

1. valide `nexyconfig.py`, et s'arrête sur une configuration invalide ;
2. garantit que les packages Python du projet sont importables ;
3. résout les ports et supprime le marqueur `__nexy__/nexy.prod` obsolète ;
4. génère les fichiers clients et compile les routes, en parallèle ;
5. démarre Vite et attend qu'il réponde ;
6. installe l'observateur de fichiers, puis permet à uvicorn d'importer `nexy.modules.routers.app:_server`.

Cette importation assemble l'application - middleware, actions, routeurs, gestionnaires d'erreurs - et le
la première demande est signifiée par cette assemblée. Lorsque vous enregistrez, l'observateur redémarre uvicorn ; une page qui
apparu, disparu ou déplacé régénère également la liste des itinéraires clients.

## Le système de routage

Un chemin sous `src/routes/` devient une URL selon quatre règles :

| Fichier | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

L'extension n'apparaît jamais ; `index` est l'itinéraire de son dossier ; un dossier dans des groupes entre parenthèses
fichiers sans ajouter de segment.

Lorsque deux choses peuvent répondre à la même URL, **le premier enregistré gagne**, et Nexy toujours
s'inscrit dans cet ordre :

1. le point de terminaison Actions ;
2. fichiers statiques : `/public`, `/assets`, `/favicon.ico` ;
3. un `APIRouter` modulaire (`useRouter`) ;
4. routes de fichiers, les plus spécifiques d'abord : chemins statiques, puis chemins dynamiques avec les segments les plus fixes,
   puis des fourre-tout.

Deux itinéraires de fichiers d'égale spécificité sont enregistrés par ordre alphabétique des chemins, donc `[id].nexy`
réponses avant `[slug].nexy`. Un itinéraire modulaire bat donc une page avec le même chemin. C'est un
un ordre de priorité sur lequel vous pouvez compter, et non une règle de départage avec laquelle jouer : donnez à une URL un fichier.

## Le système de visualisation

L'extension d'un fichier décide de ce dont il s'agit et la configuration du projet décide quelles extensions sont
actif.

| Extension | Active lorsque | Compilée par | A servi de |
|---|---|---|---|
| `.nexy` | mode serveur | Nexy : le frontmatter devient Python, le balisage devient Jinja2 | une page |
| `.md` | toujours | Nexy : Markdown aromatisé à GitHub, identifiants de titre, table des matières | une page, dans la mise en page la plus proche |
| `.mdx` | toujours | Vite, avec React ou Preact | une route de composants |
| `.tsx` | `useFF` est React, Solid ou Preact | Vite et le framework | une route de composants |
| `.vue` | `useFF` est Vue | Vite et Vue | une route de composants |
| `.svelte` | `useFF` est Svelte | Vite et Svelte | une route composante |
| `.py` | toujours | Python | un gestionnaire d'API : `GET`, `POST`, ... sont les méthodes |

Un fichier dont l'extension n'est pas active est ignoré avec un avertissement, non servi. En mode client, `.nexy`
est rejeté avant le démarrage du serveur. Voir [Conventions de fichiers](../reference/file-conventions.md).

## Le cycle de vie du rendu

Trois questions décident de tout ce qu'un lecteur remarque :

| Question | Réponse | Page |
|---|---|---|
| Qui produit le HTML ? | le serveur, ou le navigateur pour une route client | [Rendu](../rendering/README.md) |
| Quand les données sont-elles lues ? | à chaque requête, à chaque régénération, ou dans le navigateur | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Quand JavaScript arrive-t-il ? | uniquement pour une île, ou pour l'ensemble du document | [Îles](../rendering/islands.md), [CSR](../rendering/csr.md) |

En mode serveur, le serveur restitue chaque page, `revalidate` met en cache une page par URL et les îles ajoutent
JavaScript vers un composant. En mode client le premier document est rendu dans Node et navigation
cela se produit ensuite dans le navigateur.

`__nexy__/` contient tout ce qui est généré : les pages compilées, l'entrée client, la sortie de build. Jamais
modifiez-le, ne le commettez jamais ; supprimez-le pour forcer une version propre.

## L'intégration frontend

**Vite ne remplace pas Nexy.** Vite regroupe et sert le code client. Il n'achemine pas une requête,
rendre une page `.nexy`, exécuter une action ou posséder l'origine. Le navigateur parle à une seule origine - celle de Nexy -
et en développement, Nexy transmet les points de terminaison de Vite via celui-ci, il n'y a donc pas de CORS à configurer.

**Nexy ne remplace pas React.** Nexy décide quel composant est rendu, quand et avec quels accessoires ;
le framework possède le modèle de composants, la réactivité et l'écosystème. Une page `.nexy` importe un
composant comme une île ; en mode client, une route *est* un composant.

Pour une route de composant, Python écrit uniquement un module wrapper léger qui pointe vers le fichier. Le
la compilation et le rendu côté serveur sont le travail de Vite.

## Développement et production

| | `nx dev` | `nx build` puis `nx start` |
|---|---|---|
| Pages | compilées lorsque vous enregistrez | compilées une fois, à l'avance |
| Code client | Serveur de développement Vite avec rechargement à chaud, derrière le bundle d'origine | de Nexy dans `__nexy__/client/`, HTML pré-rendu |
| Node.js | s'exécute à côté de Python | pas nécessaire pour servir |
| Erreurs | superposition dans le navigateur, barre d'outils sur chaque page | pages d'état sans détails |
| Origine | un port, `3000` | un port |

Ce qui ne change pas : les mêmes règles de routage, les mêmes fichiers de pages, les mêmes `nexyconfig.py`. Une page
qui se comporte différemment entre les deux est un bug, pas un mode.

## Aller plus loin

- [Structure du projet](project-structure.md) : chaque dossier d'un projet
- [Rendu](../rendering/README.md) : SSR, ISR, CSR et îles
- [Frontend](../guides/frontend.md) : Vite, style et build client
- [Routing](../routing/README.md) : les routeurs basés sur fichiers, modulaires et personnalisés