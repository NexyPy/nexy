# Wie veröffentliche ich ein Modul in der Nexy-Registrierung?

Führen Sie `nx publish` aus einem Modulverzeichnis mit einem gültigen `nx.toml`, einem Registrierungstoken und jeder Datei aus, die das Manifest deklariert. Der Befehl überprüft die Version, erstellt ein Archiv und lädt eine unveränderliche Version hoch.

## Bereiten Sie das Manifest vor

Ein Quellmodul listet jede Datei auf, die es versendet. Das Archiv enthält `nx.toml` und genau diese Dateien.

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

Das Feld `name` muss ein Kleinbuchstabe `@scope/name` sein. Das Feld `version` muss aus drei durch Punkte getrennten Zahlen bestehen. Die Dateien müssen relative Pfade innerhalb des Moduls sein. Ein Paketmodul deklariert `source.package` anstelle von `source.files`.

## Vor dem Hochladen prüfen

Verwenden Sie `--dry-run`, um das Manifest zu validieren, die deklarierten Dateien zu archivieren und die Prüfsumme auszudrucken, ohne Folgendes hochzuladen:

```bash
nx publish --dry-run
```

Für einen Probelauf ist kein Token erforderlich. Es gibt eine `warning:`-Zeile für jeden relativen Import aus, der auf eine Datei verweist, die das Manifest nicht deklariert. Beispielsweise benötigt `from .helpers import token` in `src/auth.py` `src/helpers.py` in `source.files`, andernfalls würde eine Installation einen fehlerhaften Import verursachen.

## Legen Sie den Token fest

`nx publish` lautet `NEXY_REGISTRY_TOKEN`, dann `~/.config/nexy/registry-token`. Das Token wird im Header `Authorization` gesendet und nie gedruckt.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

Die Token-Datei ermöglicht es einem zukünftigen `nx login`, dieselben Anmeldeinformationen zu schreiben. Ohne eine der Quellen gibt der Befehl `error: No registry token` aus und wird mit Status 1 beendet.

## Veröffentlichen

```bash
nx publish
```

Der Befehl gibt den Namen, die Version und die SHA-256-Prüfsumme der veröffentlichten Version aus. Ein Namens- und Versionspaar ist unveränderlich: Wenn es erneut veröffentlicht wird, wird ein Konfliktfehler ausgegeben. Veröffentlichen Sie stattdessen eine neue Version.

## Verwenden Sie eine andere Registrierung

Standardmäßig ist das Kommando auf `https://registry.nexypy.dev` eingestellt. Verwenden Sie `--registry` für eine andere Registrierung, beispielsweise eine lokale während der Entwicklung:

```bash
nx publish --registry http://localhost:8000
```

Es werden nur https-URLs sowie einfaches http auf `localhost`, `127.0.0.1` und `::1` akzeptiert. Vorübergehende `429`- und `5xx`-Antworten werden zweimal wiederholt; Ein fehlerhaftes Manifest, ein fehlendes Token oder ein Konflikt werden nicht erneut versucht.

## Überprüfen Sie die Freigabe

```bash
nx add @acme/auth@1.2.0
```

Siehe [Module installieren](install-modules.md) für Upgrades, Pins und Vertrauenseinstellungen.
