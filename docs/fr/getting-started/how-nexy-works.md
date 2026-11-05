# Comment fonctionne Nexy

Que se passe-t-il entre un fichier que vous écrivez et la page dans le navigateur : les couches traversées par une requête, qui construit quoi et ce que Nexy laisse à votre application. Vous n'avez pas besoin de cette page pour démarrer ; il répond plus tard aux questions « pourquoi ça marche comme ça ».

## Les couches

```diagram filename="Une demande, cinq niveaux"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Couche | Responsabilité | Ne |
|---|---|---|
| Uvicorn | accepter la connexion, parler ASGI | je sais ce qu'est une page |
| Intergiciel | décorez la requête : session, CORS, gzip, hôtes de confiance, redirection HTTPS, la vôtre | choisir un itinéraire |
| Routeur | faire correspondre l'URL à un fichier, avec ses mises en page, ses dépendances et ses pages d'erreur | produire du contenu |
| Moteur de rendu | exécuter la page et transformer son résultat en HTML ou JSON | récupérer vos données |
| Client | Vite et votre framework : bundles, hydratation, navigation client | répondre à une requête du serveur |

## Qui construit quoi

| Acteur | Possède | Ne possède pas |
|---|---|---|
| Nexy | routage, rendu serveur, actions, compilation `.nexy`, une origine | composants, réactivité, données |
| Vite | bundles clients, serveur de développement, rechargement à chaud | routage, rendu du serveur, Actions |
| Votre cadre | composants, réactivité, écosystème | routage, le document (Nexy demande sa mise en page) |
| Votre candidature | données, authentification, autorisation, règles métier | transport, rendu |

La règle derrière le tableau : **Nexy construit ce qu'il possède et ne compile jamais ce que Vite compile.**

## Le système de routage

Un chemin sous `src/routes/` devient une URL selon quatre règles :

| Fichier | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

L'extension n'apparaît jamais ; `index` est l'itinéraire de son dossier ; un dossier entre parenthèses regroupe les fichiers sans ajouter de segment.

Lorsque deux éléments peuvent répondre à la même URL, **le premier enregistré gagne**, et Nexy s'inscrit toujours dans cet ordre :

1. le point de terminaison Actions ;
2. fichiers statiques : `/public`, `/assets`, `/favicon.ico` ;
3. un `APIRouter` modulaire (`useRouter`) ;
4. les routes de fichiers, les plus spécifiques en premier : les chemins statiques, puis les chemins dynamiques avec les segments les plus fixes, puis les fourre-tout.

Deux itinéraires de fichiers de spécificité égale sont enregistrés par ordre alphabétique des chemins, donc `[id].nexy` répond avant `[slug].nexy`. Un itinéraire modulaire bat donc une page avec le même chemin. Il s’agit d’un ordre de priorité sur lequel vous pouvez compter, et non d’une règle de départage : donnez à une URL un fichier.

## Le système de visualisation

L'extension d'un fichier décide de ce dont il s'agit et la configuration du projet décide quelles extensions sont actives.

| Rallonge | Actif quand | Compilé par | Servi comme |
|---|---|---|---|
| `.nexy` | mode serveur | Nexy : le frontmatter devient Python, le balisage devient Jinja2 | une page |
| `.md` | toujours | Nexy : Markdown à saveur GitHub, identifiants de titre, table des matières | une page, à l'intérieur de la mise en page la plus proche |
| `.mdx` | toujours | Vite, avec React ou Preact | un itinéraire de composants |
| `.tsx` | `useFF` est React, Solid ou Preact | Vite et le cadre | un itinéraire de composants |
| `.vue` | `useFF` est Vue | Vite et Vue | un itinéraire de composants |
| `.svelte` | `useFF` est Svelte | Vite et Svelte | un itinéraire de composants |
| `.py` | toujours | Python | un gestionnaire d'API : `GET`, `POST`, ... sont les méthodes |

Un fichier dont l'extension n'est pas active est ignoré avec un avertissement, non servi. En mode client, `.nexy` est rejeté avant le démarrage du serveur. Voir [Conventions de fichiers](../reference/file-conventions.md).

## Le cycle de vie du rendu

Trois questions décident de tout ce qu'un lecteur remarque :

| Question | Réponse | Pages |
|---|---|---|
| Qui produit le HTML ? | le serveur, ou le navigateur pour une route client | [Rendu](../rendering/README.md) |
| Quand les données sont-elles lues ? | à chaque requête, à chaque régénération, ou dans le navigateur | [RSS](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Quand arrive JavaScript ? | uniquement pour une île, ou pour l'ensemble du document | [Îles](../rendering/islands.md), [CSR](../rendering/csr.md) |

En mode serveur, le serveur restitue chaque page, `revalidate` met en cache une page par URL et les îles ajoutent JavaScript à un composant. En mode client, le premier document est rendu dans Node et la navigation s'effectue ensuite dans le navigateur.

`__nexy__/` contient tout ce qui est généré : les pages compilées, l'entrée client, la sortie de build. Ne le modifiez jamais, ne le validez jamais ; supprimez-le pour forcer une version propre.

## L'intégration front-end

**Vite ne remplace pas Nexy.** Vite regroupe et sert le code client. Il n'achemine pas une requête, n'affiche pas de page `.nexy`, n'exécute pas d'action et ne possède pas l'origine. Le navigateur communique avec une seule origine - celle de Nexy - et en cours de développement avec les proxys Nexy Les points de terminaison de Vite le traversent, il n'y a donc pas de CORS à configurer.

**Nexy ne remplace pas React.** Nexy décide quel composant est rendu, quand et avec quels accessoires ; le framework possède le modèle de composants, la réactivité et l'écosystème. Une page `.nexy` importe un composant sous forme d'îlot ; en mode client, une route *est* un composant.

Pour une route de composant, Python écrit uniquement un module wrapper léger qui pointe vers le fichier. La compilation et le rendu côté serveur sont le travail de Vite.

## Développement et production

`nx dev` vérifie `nexyconfig.py`, compile les pages, démarre Vite lorsque le projet dispose d'un framework frontend et redémarre le serveur lorsque vous enregistrez. `nx build` fait le même travail une fois, à l'avance, et `nx start` sert le résultat.

| | `nx dev` | `nx build` puis `nx start` |
|---|---|---|
| Pages | compilé lorsque vous enregistrez | compilé une seule fois, à l'avance |
| Code client | Vite serveur de développement avec rechargement à chaud, derrière la propre origine de Nexy | bundle en `__nexy__/client/`, HTML pré-rendu |
| Node.js | court à côté de Python | pas besoin de servir |
| Erreurs | superposition dans le navigateur, barre d'outils sur chaque page | pages de statut sans détails |
| Origine | un port, `3000` | un port |

Ce qui ne change pas : les mêmes règles de routage, les mêmes fichiers de pages, les mêmes `nexyconfig.py`. Une page qui se comporte différemment entre les deux est un bug, pas un mode.

## Ce que Nexy vous laisse

Nexy s'arrête volontairement en bordure de votre application :

| Préoccupation | Ce que propose Nexy | Ce que tu écris |
|---|---|---|
| Authentification | middleware de session, `AuthenticationMiddleware` lorsqu'il est activé | la connexion, la recherche d'utilisateur, la politique en matière de cookies |
| Autorisation | `dependencies.py`, gardes, héritage par dossier | la règle elle-même |
| Base de données | pas d'ORM propre ; `nx new` peut échafauder SQLModel, SQLAlchemy ou Tortoise, `nx migrate` exécute Alembic ou Aerich | les modèles et les requêtes ([Bases de données](../guides/databases.md)) |
| Internationalisation | rien pour vos pages ; seule la CLI est traduite | la bibliothèque et les messages ([i18n](../guides/i18n.md)) |
| Travaux en arrière-plan | rien : pas de file d'attente, pas de planificateur | un processus de travail |
| E-mail, paiements, recherche | rien | le service que vous choisissez |

La raison est la même pour les six : un framework qui sélectionne votre ORM ou votre bibliothèque d'authentification décide des choses que seule votre application peut décider. Le coût est explicite : rien n'est câblé pour vous, et les guides liés dans le tableau indiquent où brancher chacun.

## Prochaines étapes

- [Structure du projet](project-structure.md) : où chaque partie vit dans un projet
- [Routage](../routing/README.md) : les routeurs basés sur fichiers, modulaires et personnalisés
- [Rendu](../rendering/README.md) : SSR, ISR, CSR et îles
- [Frontend](../guides/frontend.md) : Vite, style et build client
