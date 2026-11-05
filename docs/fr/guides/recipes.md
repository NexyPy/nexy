# Recettes

Trois choses dont presque toutes les applications ont besoin, sous forme de fichiers complets que vous pouvez copier. Chaque bloc de code ci-dessous avec un `filename` est écrit dans un nouveau projet et utilisé par la suite de tests, donc ce que vous lisez est ce qui s'exécute.

Ils utilisent des gestionnaires d'API simples ; les mêmes fonctions fonctionnent derrière une page en [mode](../routing/fbr/modes.md).

## Connectez-vous avec une session

Un visiteur publie un nom et un mot de passe, le serveur les mémorise dans un cookie signé et tout ce qui se trouve sous `/api/account` est fermé à toute autre personne.

Activez les sessions. Ils ont besoin de `itsdangerous` (`uv add itsdangerous`) :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

Connectez-vous et déconnectez-vous :

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

Protégez un dossier entier avec un [`dependencies.py`](../routing/fbr/dependencies/README.md) :

```python filename="src/routes/api/account/dependencies.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!REMARQUE]
> gardez les vrais mots de passe hors de la source. Stockez un hachage (`argon2`, `bcrypt`) et lisez la clé secrète de l'environnement. Le cookie de session est signé et non crypté.

## Une API JSON avec création, lecture et suppression

Un magasin dans un module, un parcours de collecte et un parcours d'articles. Remplacez le dictionnaire par [une base de données](databases.md) lorsque les données doivent survivre à un redémarrage.

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

Un corps qui ne correspond pas à `NewNote` est refusé avec `422` avant l'exécution de votre code, et l'annotation de retour devient la réponse documentée. Voir [validation et erreurs](../routing/fbr/handlers/validation-and-errors.md).

## Recevoir un fichier

Les téléchargements nécessitent `python-multipart` (`uv add python-multipart`). Vérifiez vous-même la taille et n'utilisez jamais le nom de fichier du client comme chemin :

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` supprime tout dossier que le client a mis dans le nom, tel que `../../etc/passwd`. Enregistrez les octets sous un nom que vous générez, pas sous celui-ci.

## Prochaines étapes

- [Actions](actions.md) : fonctions serveur typées pour les formulaires et les boutons
- [Middleware et sécurité](middleware-and-security.md) : CORS, hôtes, sessions
- [Testing](testing.md) : testez vos propres gestionnaires de la même manière
