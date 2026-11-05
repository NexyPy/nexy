# Aktionen und Navigation

Die Interaktion in Nexy wird über ein einheitliches System von **Aktionen** und **Navigation** abgewickelt, wodurch sichergestellt wird, dass Frontend und Backend ohne manuellen API-Glue-Code synchron bleiben.

## Der Aktionsvertrag

Eine **Aktion** ist eine serverseitige Funktion, die eine Mutation verarbeitet (z. B. das Aktualisieren einer Datenbank). 

1.  **Typisierte Eingabe**: Aktionen werden in Python mit Typhinweisen definiert. Nexy generiert einen passenden TypeScript-Client, sodass Sie in Ihrer IDE eine automatische Vervollständigung und Validierung erhalten.
2.  **Atomare Ausführung**: Eine Aktion ist eine einzelne `POST` Anfrage.
3.  **Ergebnisverarbeitung**: Aktionen geben ein typisiertes Ergebnis zurück, das der Client zum Aktualisieren der Benutzeroberfläche verwenden kann.

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

Die Seite ruft es mit der deklarierten Eingabe Python auf und erhält ein eingegebenes `Todo` zurück:

```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

## Clientseitige Navigation

Die Navigation in Nexy ist „intelligent“. Anstelle eines vollständigen Neuladens des Browsers tauscht Nexy den Inhalt der aktuellen Seite aus, während die aktiven Layouts weiterhin bereitgestellt bleiben.

- **Die `Link`-Komponente**: Verwenden Sie die Framework-spezifische `Link`-Komponente, um clientseitige Übergänge durchzuführen.
- **Programmatische Navigation**: Verwenden Sie `useRouter()` von `@nexy/client` und rufen Sie `push()` auf, um die Seiten als Reaktion auf die Logik zu wechseln (z. B. nach einer erfolgreichen Anmeldung).

```tsx filename="src/components/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## Koordination: Aktion → Navigation

Das häufigste Muster besteht darin, eine Aktion auszuführen und den Benutzer dann zu einer neuen Seite zu navigieren.

**Der Revalidierungsablauf:**
1.  Der Client ruft eine Aktion auf.
2.  Die Aktion wird auf dem Server ausgeführt und ruft `revalidate("/path")` auf.
3.  Der Server gibt das Ergebnis mit einem `x-nexy-revalidate`-Header zurück, der die veralteten Pfade benennt.
4.  Der Client aktualisiert den Seiteninhalt, um den neuen Status widerzuspiegeln.

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```

`check_password` steht für Ihren eigenen Scheck. Siehe [Aktionen](../../guides/actions.md) für Fehler, Formulare ohne JavaScript und Sicherheit.

## Framework-Implementierung

Die API zum Aufrufen von Aktionen und Navigieren variiert je nach Framework. Sehen Sie sich den Leitfaden **Unterschiede** für die von Ihnen gewählte Technologie an:

- [React Unterschiede](../react/differences.md)
- [Vue Unterschiede](../vue/differences.md)
- [Svelte Unterschiede](../svelte/differences.md)
- [Solid Unterschiede](../solid/differences.md)
- [Preact Unterschiede](../preact/differences.md)
