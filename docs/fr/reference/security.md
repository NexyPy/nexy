# Sécurité

Comment Nexy maintient sa propre surface d'attaque petite, quelles versions il nécessite et comment vérifier un projet.

## Planchers de version

Nexy dépend de FastAPI, Starlette, Jinja2, Vite et React. Un plancher est la version la plus basse autorisée par Nexy ; chacun répond à un avis publié.

| Forfait | Sol | Pourquoi |
|---|---|---|
| `starlette` | 1.3.1 | CVE-2026-48710 (BadHost, corrigé dans la version 1.0.1) : un en-tête `Host` contrefait modifie le chemin d'accès Starlette vers le middleware, qui contourne l'autorisation écrite sur `request.url.path` ; répertorié comme exploité par CISA. CVE-2026-48817 et CVE-2026-48818 (envoi de requêtes, `StaticFiles` sous Windows, corrigé dans 1.1.0), CVE-2026-54282 (chemin de requête non validé, 1.3.0) et CVE-2026-54283 (limites de `request.form()`, 1.3.1). |
| `python-dotenv` | 1.2.2 | CVE-2026-28684, dans le lecteur du fichier `.env` `nx migrate` se charge |
| `fastapi` | 0.133.0 | la première version qui accepte un Starlette fixe |
| `jinja2` | 3.1.6 | le bac à sable s'échappe à travers le filtre `attr` (CVE-2025-27516) |
| `vite` (projets échafaudés) | 6.4.5 | `server.fs.deny` contournements (CVE-2026-53571 sur les chemins alternatifs Windows ; GHSA-rq7h-c2jc-7f22, corrigé dans la version 6.4.4 ; GHSA-8g5g-mxqh-grgj, un contournement de requête 6.4.4 lui-même apporté, corrigé dans la version 6.4.5), et les `launch-editor` avis corrigés dans la version 6.4.4. |
| `svelte` (projets échafaudés) | 5.55.7 | six avis XSS rendus par le serveur via des attributs de diffusion, des noms de balises dynamiques et `bind:innerText` |
| `esbuild` (projets échafaudés) | 0.28.1 | fichier arbitraire lu via le serveur de développement (GHSA-g7r4-m6w7-qqqr) |
| `react`, `react-dom` | 19.2.5 | les avis de 2026 React concernent les packages `react-server-dom-*`, que Nexy n'utilise pas ; le sol maintient la ligne réparée |

`python scripts/audit_dependencies.py` vérifie chaque étage par rapport à l'OSV après le verrouillage, également en CI : un nouvel avis sur un étage échoue à l'audit.

Vérifiez vos versions résolues :

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Règles que Nexy suit

- **Ne faites jamais confiance à l'en-tête Host pour les chemins.** Nexy lit `scope["path"]`, et non `request.url.path`, dans son propre middleware (middleware d'annuaire). Faites de même dans le vôtre.
- **Échappez ce qui atteint HTML.** Props transmis aux composants clients, les attributs `Link`, `Image`, `Audio` et `Video`, les ancres de table des matières et les détails `HTTPException` sont tous échappés en HTML. Un modèle `.nexy` ne s'échappe pas tout seul : écrivez `{{ value | e }}` pour toute valeur provenant d'un visiteur ou de la base de données, et jamais `| safe` lors d'une saisie utilisateur.
- **Les points de terminaison du développeur sont uniquement en boucle et étroits.** Le point de terminaison de rendu de développement (`/__nexy__/render`) n'accepte que les fichiers sous `src/routes/` avec une extension `.tsx` ou `.jsx`, et n'est accessible que via le serveur de développement, qui refuse les en-têtes `Host` étrangers.
- **Les détails de l'erreur ne sont pas divulgués.** Une page d'erreur qui échoue elle-même affiche uniquement le code d'état.
- **Les réponses de production comportent des en-têtes sécurisés.** `X-Content-Type-Options: nosniff` et `Referrer-Policy: strict-origin-when-cross-origin`, à moins que votre code ne définisse les siens. L'en-tête `Server` n'est pas envoyé. Ajoutez un `Strict-Transport-Security` et un `Content-Security-Policy` dans votre proxy ou middleware : ils dépendent de votre domaine.
- **Un crash affiche une référence, pas l'erreur.** Voir [Pages d'erreur](../routing/fbr/errors/README.md#unhandled-exceptions).
- **Pas de `eval` et pas de `shell=True` dans le code Python de Nexy.** Les programmes externes s'exécutent avec une liste d'arguments.

## Réaliser les audits

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Le propre référentiel de Nexy exécute le premier et le troisième lors de ses vérifications. Un nouvel avis sur un étage supérieur est traité en surélevant l'étage dans `pyproject.toml` ou dans l'échafaudage `package.json`, puis en régénérant la serrure.

## Déployer en toute sécurité

- Définissez `useTrustedHost` sur vos domaines : il rejette les en-têtes `Host` inattendus avant toute route.
- N'exposez pas le serveur de développement Vite : `nx dev` le maintient en boucle derrière l'origine Nexy.
- Définissez `useDocs = False` si le schéma API ne doit pas être public.

Voir [Middleware et sécurité](../guides/middleware-and-security.md).

## Sources

- [CVE-2026-48710 (BadHost) dans Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite avis GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) et [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React packages serveur CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Prochaines étapes

- [Middleware et sécurité](../guides/middleware-and-security.md)
- [Déployer](../deployment/README.md)
- [Configuration](config.md)
