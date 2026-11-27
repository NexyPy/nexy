# Wie installiere ich ein Modul aus der Registry?

Führen Sie `nx add @scope/name` in einem Nexy-Projekt aus, um eine Version aus der Modulregistrierung herunterzuladen, sie zu überprüfen und die deklarierten Änderungen anzuwenden. Fügen Sie `@1.2.0` hinzu, um eine genaue Version anzupinnen.

## Installieren Sie ein Modul

Aus dem Stammverzeichnis eines Nexy-Projekts:

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` liest die Release-Metadaten und das Archiv von `useModuleRegistry`, überprüft die SHA-256-Prüfsumme und überprüft die Kompatibilitätsbereiche `nexy` und `python` des Moduls. Anschließend schreibt es nur die Dateien, die im Manifest deklariert sind, fügt die deklarierten Python-Pakete mit `uv add` hinzu, fügt Node-Pakete mit dem Paketmanager des Projekts hinzu und wendet die Konfigurations-Hooks auf `nexyconfig.py` und `package.json` an. Vorhandene Einstellungen und Dateien bleiben unverändert: Eine deklarierte Datei, die bereits existiert, wird mit einer `warning:`-Zeile übersprungen.

Jede erfolgreiche Installation wird in `.nexy/modules.json` aufgezeichnet. Übertragen Sie diese Datei, damit ein Teamkollege dieselbe Modulversion erhält.

## Aktualisieren Sie ein Modul

Um ein Upgrade durchzuführen, führen Sie `nx add @acme/auth` erneut aus, nachdem die Registrierung eine neuere Version hat, oder legen Sie eine neue PIN fest, z. B. `@acme/auth@1.3.0`. Ein nicht angehefteter Name wählt die neueste Version aus der `/versions`-Antwort der Registrierung aus. Wenn Sie dieselbe Version erneut ausführen, wird `is already installed` gedruckt und es ändert sich nichts.

## Pinne eine Version

Ein Pin ist genau: `nx add @acme/auth@1.2.0` installiert `1.2.0` und keine andere Version. Verwenden Sie eine PIN in CI und in einem Commit `.nexy/modules.json`, damit bei jedem Checkout derselbe Code installiert wird. Ohne PIN ändert eine neue Version die nächste Installation.

## Führen Sie Migrationen durch

Migrationen sind standardmäßig deaktiviert. Fügen Sie `--migrate` hinzu, wenn Sie möchten, dass die deklarierten Befehle einer Version ausgeführt werden, nachdem ihre Dateien und Abhängigkeiten vorhanden sind:

```bash
nx add @acme/auth@1.2.0 --migrate
```

Jeder Befehl wird vor seiner Ausführung gedruckt. Das Projekt muss sein Migrationstool installiert haben, bevor ein Modul eines deklarieren kann.

## Legen Sie die Registrierung und ihre Vertrauensregeln fest

Die Standardeinstellungen leben in `nexyconfig.py`:

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` ist die Basis-URL, die die CLI liest. Es werden nur https-URLs akzeptiert, mit Ausnahme von Loopback-http für eine lokale Registrierung während der Entwicklung. `useRequireSignedModules = True` lehnt eine nicht unterzeichnete Veröffentlichung ab. Eine mit einer Signatur versehene Freigabe wird ebenfalls abgelehnt, bis ein Prüfer verfügbar ist; Sobald man es verifiziert hat, druckt `nx add` `Verified by` mit der Identität des Unterzeichners. Behalten Sie die Standardeinstellung `False` nur für vertrauenswürdige Registrierungen bei.
