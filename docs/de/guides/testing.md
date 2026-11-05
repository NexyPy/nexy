# Testen

`nx test` führt die Servertests mit pytest aus und die Clienttests mit vitest, wenn Sie danach fragen.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## Was läuft

| Teil | Befehl | Bedingung |
|---|---|---|
| Server | `pytest` | läuft auf `tests/`, wenn er existiert, andernfalls auf dem Projektstamm; wird mit einer Warnung übersprungen, wenn pytest nicht installiert ist |
| Client | `npx vitest run` | nur mit `--client` und nur wenn `vitest.config.ts` existiert oder `vitest` in `package.json` | erscheint

Es gibt keinen integrierten End-to-End-Läufer. Steuern Sie den Server mit `TestClient` und fügen Sie Playwright oder Cypress selbst für das Browserverhalten hinzu.

## Testen Sie den Server

Der Testclient kommuniziert während des Prozesses mit der ASGI-App: kein Server zum Starten, kein Port zum Auswählen.

```python filename="tests/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` ist die zusammengestellte Anwendung, die beim ersten Lesen erstellt wird. Es liest `nexyconfig.py` aus dem Arbeitsverzeichnis, also führen Sie pytest aus dem Projektstammverzeichnis aus.

Wenn ein Test die Konfiguration oder Routen ändert, erstellen Sie eine neue Anwendung, anstatt die Anwendung auf Modulebene wiederzuverwenden:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` setzt Routen, Middleware, Sitzungen und Übersetzungen neu zusammen, sodass jeder Aufruf mit dem aktuellen Status des Projektverzeichnisses beginnt.

## Was soll ich behaupten?

Eine Seite gibt HTML zurück. Bestätigen Sie den Status und dann den Inhalt, der Ihnen wichtig ist:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Ein API-Handler gibt JSON zurück. Ein Validierungsfehler ist ein `422`, und eine fehlende Route ist ein `404`, der mit `notfound.nexy` beantwortet wird, wenn diese Datei vorhanden ist:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Testen Sie für eine Aktion die Funktion direkt – es handelt sich um eine normale Funktion – und testen Sie den HTTP-Endpunkt, indem Sie seinen generierten Pfad von der Seite lesen, die ihn verfügbar macht:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

Ein Anruf mit JSON antwortet mit dem Ergebnis und `422` mit den ungültigen Feldern.

> [!NOTE]
> Aktionspfade sind projektspezifisch und generiert. Kodieren Sie niemals `/_nx_<hash>` in einem Test fest.

## Testen Sie eine `.nexy`-Komponente

`nexy.testing.render` kompiliert eine Komponente mit den importierten Komponenten und gibt deren HTML zurück. Requisiten sind Schlüsselwortargumente und `children=` füllt den Platz:

```python filename="tests/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Führen Sie pytest aus dem Projektstammverzeichnis aus: Die kompilierten Dateien werden wie bei `nx dev` nach `__nexy__/` verschoben. Eine Komponente, die die Anfrage (`usePathname`, `useSession`) liest, benötigt stattdessen einen Seitentest mit `TestClient`.

## Testen Sie den Client

`nx test --client` erwartet Ihr eigenes vitest-Setup. Ein minimaler Komponententest:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` und die Testbibliothek sind Projektabhängigkeiten: `nexy new` installiert keinen Test-Stack. Fügen Sie `vitest.config.ts` mit der Umgebung hinzu, die Sie benötigen (jsdom oder happy-dom für Komponenten).

## Kontinuierliche Integration

Für eine Projektpipeline genügen zwei Befehle:

```bash
nx build
nx test
```

`nx build` schlägt aufgrund eines Kompilierungsfehlers fehl; `nx test` schlägt bei einer fehlerhaften Behauptung fehl und wird mit einem Wert ungleich Null beendet. `nx check` fügt mypy und `tsc` zum Lauf hinzu.

Die Arbeit an Nexy selbst verwendet verschiedene Befehle: siehe [CONTRIBUTING](../../CONTRIBUTING.md).

## Nächste Schritte

- [CLI](../reference/cli.md): jedes Flag von `nx test`
- [API](../routing/fbr/handlers/README.md): Was ein Endpunkt zurückgibt
- [Bereitstellen](../deployment/README.md): Erstellen Sie, bevor Sie in CI testen
