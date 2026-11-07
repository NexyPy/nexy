# Aktionen

Ein `@Action` verwandelt eine Python-Funktion in einen `POST`-Endpunkt. Im Gegensatz zu einem Standard-API-Handler ist es als typisierte Kommunikationsbrücke konzipiert: Nexy generiert automatisch den TypeScript-Client, validiert die Eingabe und verarbeitet die Antwort.

**Bevor Sie beginnen:** ein Projekt, das durch den [Schnellstart](../getting-started/quick-start.md) erstellt wurde. Aktionen werden neben den Seiten in `src/actions/` angezeigt.

```diagram filename="Der Aktionszyklus"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## Der Aktionszyklus

### 1. Definieren
Eine Aktion ist eine normale Python-Funktion, die mit `@Action` gekennzeichnet ist. Nexy verwendet seine Signatur, um den API-Vertrag zu definieren.

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

Die Parameter sind die Eingabe, validiert durch Pydantic. Ein Parameter mit dem Namen `request` oder `response` wird eingefügt und ist nicht Teil der Eingabe.

### 2. Validieren
Wenn die Aktion aufgerufen wird, validiert Nexy die Eingabe anhand der Typhinweise der Funktion. Wenn ein Feld fehlt oder den falschen Typ hat, wird die Aktion nicht ausgeführt und ein `422 Unprocessable Entity` zurückgegeben.

### 3. Ausführen
Die Logik läuft auf dem Server. Da es sich um eine Standardfunktion Python handelt, können Sie jede Bibliothek verwenden, auf die Datenbank zugreifen oder andere Dienste aufrufen. Sie können eine Seitenaktualisierung auch mit `revalidate()` auslösen.

### 4. Serialisieren
Der Rückgabewert wird automatisch in JSON serialisiert. Pydantic-Modelle werden nativ verarbeitet und Standard-Python-Typen werden ihren JSON-Äquivalenten zugeordnet.

### 5. Konsumieren
Das Frontend erhält das Ergebnis mit voller Typsicherheit. Nexy schreibt `__nexy__/src/actions.ts` aus Ihren Unterschriften, und `@nexy/actions` beschließt, es zu tun.

<!-- router:fbr,custom -->
```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```
<!-- /router -->

<!-- router:modular -->
Die Komponente ist eine Insel der Ansicht, die ein Controller zurückgibt:

```tsx filename="src/components/NewUser.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

```nexy filename="src/apps/users/user_view.nexy"
---
from "@/components/NewUser.tsx" import NewUser
---
<NewUser directive="client:load" />
```
<!-- /router -->

Ohne Hook ist eine Aktion nur eine `async`-Funktion: `const user = await create_user({ name: "Ada" })`.

| Rahmen | Was `useAction` zurückgibt |
|---|---|
| React, Preact | `{ pending, data, error, run, reset }` |
| Solid | das Gleiche, mit `pending()`, `data()` und `error()` als Accessoren |
| Vue | das Gleiche, mit `pending`, `data` und `error` als Referenzen |
| Svelte | ein Geschäft: `$save.pending`, `$save.data`, `$save.error`, plus `save.run(input)` und `save.reset()` |

`useAction(action, { onSuccess, onError })` nimmt auch zwei Rückrufe entgegen. `run` wirft nie: Ein Fehlschlag landet in `error` und `run` wird mit `undefined` aufgelöst.

Die Typen stammen von Python: `str` ist `string`, `int` und `float` sind `number`, `list[T]` ist `T[]`, ein Pydantic-Modell oder ein `Enum` ist ein benannter Typ, und ein Feld mit einem Standardwert ist in der Eingabe optional. Ein Typ, den Pydantic nicht beschreiben kann, wird zu `unknown`.

## Fehler und Ausfälle

Eine Aktion kann in verschiedenen Phasen fehlschlagen. Sie sollten in Ihrer Benutzeroberfläche zwischen ihnen unterscheiden:

1.  **Validierungsfehler (422)**: Die Eingabe stimmte nicht mit der Python-Signatur überein. `error.fields` ordnet jedes ungültige Feld seiner Nachricht zu.
2.  **Geschäftsfehler (`HTTPException`)**: Ihr Code hat den Anruf abgelehnt, zum Beispiel `403 Forbidden` oder `409 Conflict`.
3.  **Serverfehler (500)**: In Ihrem Python-Code ist eine nicht behandelte Ausnahme aufgetreten.
4.  **Netzwerkfehler**: Die Anfrage hat den Server nie erreicht, z. B. eine Zeitüberschreitung oder ein Verbindungsverlust.
5.  **Autorisierungsfehler (401, 403)**: Ihr eigener Scheck hat den Anrufer abgelehnt. Nexy entscheidet dies nicht für Sie.

Bei der unten beschriebenen Ursprungsprüfung handelt es sich um einen CSRF-Schutz, nicht um eine Autorisierung: Sie sagt aus, woher der Anruf kam, niemals, wer ihn tätigen darf.

## Aktualisieren Sie die Seite nach einer Aktion

Eine Aktion gibt an, welche Seiten durch ihre Änderung veraltet sind, wie es Next.js mit `revalidatePath` tut:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

Die Antwort trägt die Pfade in einem `x-nexy-revalidate`-Header. Der Client ruft dann die aktuelle Seite erneut über den Router ab oder lädt sie neu, wenn kein Client-Router vorhanden ist.

## Formulare ohne JavaScript

Eine Aktion nimmt auch ein Standard-HTML-Format an, sodass die Seite funktioniert, bevor ein Skript geladen wird:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

In einer `.nexy`-Vorlage ist `__actions_path["name"]` der Pfad, `__actions["name"]` die Funktion, und die Funktion befindet sich auch unter ihrem eigenen Namen im Gültigkeitsbereich.

Bei Erfolg wird der Besucher mit dem Status `303` auf die Seite zurückgeleitet, auf der sich das Formular befand. Um anders zu antworten, geben Sie ein `Response`-Objekt zurück (z. B. `RedirectResponse("/done", status_code=303)`).

## Sicherheit

### Pfadunklarheit ist keine Autorisierung
Der Aktionspfad ist `/_nx_`, gefolgt von einem Hash des Moduls der Funktion, seinem Namen und einem Geheimnis des Projekts. Es wird von `NEXY_ACTION_SECRET` festgelegt oder in `__nexy__/action.key` gespeichert, das `nx build` erstellt, sodass das Client-Bundle und `nx start` zustimmen: Behalten Sie diese Datei beim Build. Der Pfad verbirgt den Endpunkt vor zufälliger Entdeckung und **der generierte Pfad ist kein Autorisierungsmechanismus**.

Jeder, der den Weg kennt, kann die Aktion aufrufen. Sie **müssen** die Identität und Berechtigungen des Benutzers innerhalb der Aktion überprüfen:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### Herkunftsschutz
Um Cross-Site Request Forgery (CSRF) zu verhindern, lehnt Nexy Anfragen ab, deren `Origin` eine andere Site ist oder die der Browser `Sec-Fetch-Site: cross-site` mit einem `403` markiert. Listen Sie die Websites auf, die Ihre Aktionen in `NEXY_ALLOWED_ORIGINS` aufrufen können. Anrufe ohne `Origin` (wie `curl`) werden angenommen.

## Importfehler

Beim Start importiert Nexy jedes Modul von `src/`, um die Aktionen zu finden. Es wird ein Modul gemeldet, dessen Import fehlschlägt, während die anderen weiterhin geladen werden:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## Nächste Schritte

- [API](../routing/fbr/handlers/README.md): explizite Handler
- [Testen](testing.md#what-to-assert): So testen Sie eine Aktion
- [Konfiguration](../reference/config.md): Middleware- und Authentifizierungsoptionen
