# Sécurité

Comment Nexy maintient sa propre surface d'attaque petite, quelles versions il nécessite et comment vérifier un projet.

## Étages de versions

Nexy dépend de FastAPI, Starlette, Jinja2, Vite et React. Un étage est la version la plus basse Nexy
permet ; chacun répond à un avis publié.

| Forfait | Sol | Pourquoi |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost) : un en-tête `Host` contrefait modifie le chemin que Starlette rapporte au middleware, qui contourne l'autorisation écrite sur `request.url.path`. Répertorié comme exploité par CISA. |
| `fastapi` | 0.133.0 | la première version qui accepte une Starlette fixe |
| `jinja2` | 3.1.6 | évasion du bac à sable via le filtre `attr` (CVE-2025-27516) |
| `vite` (projets échafaudés) | 6.4.3 | `server.fs.deny` contournement des chemins alternatifs Windows (CVE-2026-53571) ; le contournement de chaîne de requête antérieur (CVE-2026-39364) affecte uniquement Vite 7.1-7.3.1 et 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | les avis React 2026 concernent les packages `react-server-dom-*`, que Nexy n'utilise pas ; le sol maintient la ligne raccordée |

Vérifiez vos versions résolues :

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Règles que Nexy suit

- **Ne faites jamais confiance à l'en-tête Host pour les chemins.** Nexy lit `scope["path"]`, et non `request.url.path`, dans
  son propre middleware (middleware d'annuaire). Faites de même dans le vôtre.
- **Échappez ce qui atteint HTML.** Props transmis aux composants clients, `Link` attributs, `Image`,
  Les attributs `Audio` et `Video`, les ancres de table des matières et les détails `HTTPException` sont tous
  HTML échappé. `| safe` dans un modèle désactive cela : ne l'utilisez jamais lors d'une saisie utilisateur.
- **Les points de terminaison du développeur sont uniquement en boucle et sont étroits.** Le point de terminaison de rendu de développement
  (`/__nexy__/render`) n'accepte que les fichiers sous `src/routes/` avec une extension `.tsx` ou `.jsx`, et
  est accessible uniquement via le serveur de développement, qui refuse les en-têtes `Host` étrangers.
- **Les détails de l'erreur ne fuient pas.** Une page d'erreur qui elle-même échoue affiche uniquement le code d'état.
- **Les réponses de production comportent des en-têtes sécurisés.** `X-Content-Type-Options: nosniff` et
  `Referrer-Policy: strict-origin-when-cross-origin`, à moins que votre code ne définisse le sien. Le `Server`
  l’en-tête n’est pas envoyé. Ajoutez `Strict-Transport-Security` et un `Content-Security-Policy` dans votre
  proxy ou middleware : ils dépendent de votre domaine.
- **Un crash affiche une référence, pas l'erreur.** Voir [Pages d'erreur](../routing/fbr/errors/README.md#unhandled-exceptions).
- **Pas de `eval` et non de `shell=True` dans le code Python de Nexy.** Les programmes externes s'exécutent avec une liste d'arguments.

## Réaliser les audits

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Le propre référentiel de Nexy exécute le premier et le troisième lors de ses vérifications. Un nouvel avis à un étage supérieur est traité en augmentant le
sol en `pyproject.toml` ou dans l'échafaudage `package.json`, puis régénérer la serrure.

## Déployer en toute sécurité

- Définissez `useTrustedHost` sur vos domaines : il rejette les en-têtes `Host` inattendus avant toute route.
- Ne pas exposer le serveur de développement Vite : `nx dev` le maintient en bouclage derrière l'origine Nexy.
- Définissez `useDocs = False` si le schéma API ne doit pas être public.

Voir [Middleware et sécurité](../guides/middleware-and-security.md).

## Sources

- [CVE-2026-48710 (BadHost) dans Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Avis Vite GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) et
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [Packages serveur React CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Étapes suivantes

- [Middleware et sécurité](../guides/middleware-and-security.md)
- [Déployer](../deployment/README.md)
- [Configuration](config.md)