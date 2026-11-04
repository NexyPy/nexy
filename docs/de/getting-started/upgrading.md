# Upgrade auf 2.2

Was ändert sich für ein bestehendes Projekt, wenn Sie von 2.1 auf 2.2 wechseln, und was ist dagegen zu tun? Die
Die vollständige Liste finden Sie im [Changelog](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## Was Sie möglicherweise ändern müssen

| Ändern | Tun Sie dies |
|---|---|
| **`.mdx` wird nur von Vite kompiliert.** Der Python-Compiler rendert es nicht mehr. | Behalten Sie React oder Preact in `useFF` und installieren Sie `@mdx-js/rollup`, `remark-gfm` und `@mdx-js/react`. Eine Seite ohne Komponenten kann stattdessen eine `.md`-Datei sein |
| **`useBadge` ist weg.** Das Tag „Built with Nexy“ existiert nicht mehr | Löschen Sie die Zeile aus `nexyconfig.py`. Eine übrig gebliebene Zeile wird ignoriert |
| **`nx check` kompiliert nicht mehr `.mdx`** | Nichts: Vite meldet MDX-Fehler beim Build |

## Was gleich bleibt

- Ihre Routen, Layouts, Aktionen und Konfiguration.
- Bestehende Projekte behalten ihre eigenen Startseiten. Das neue Starterdesign gilt nur für Projekte
  nach dem Upgrade erstellt.
- Die Entwicklungssymbolleiste und `useDevTools`.

## Neu in 2.2

- **Agentendateien.** `nx new` schreibt `AGENTS.md`, `CLAUDE.md` und die Fähigkeiten für Codierungsagenten. Für einen
  Projekt, das Sie bereits haben, führen Sie `nx skills` aus. Es überschreibt niemals eine von Ihnen geschriebene Datei. Siehe
  [Kodierungsagenten](../guides/ai-agents.md).
- **Ein Entwicklungsserver, der weiterläuft.** Wenn Ihre Anwendung nicht gestartet werden kann, `nx dev` wird der Grund und die Ursache gemeldet
  wartet auf die nächste Änderung, anstatt zu beenden.
- **Ein neuer Starter** für jedes Framework in Tailwind oder UnoCSS, mit den gleichen Seiten und Komponenten.
- **UnoCSS liest `.nexy` Dateien** in einem Serverprojekt. Wenn Sie UnoCSS mit `.nexy` Seiten verwenden, fügen Sie Folgendes hinzu
  `content`-Block, der in [Fehlerbehebung](../guides/troubleshooting.md) angezeigt wird.

## Dokumentation korrigiert

Auf drei Seiten wurde etwas gesagt, was der Code nicht tut. Wenn Sie diese befolgt haben, überprüfen Sie Ihre Dateien:

- Eine `.nexy`-Komponente platziert ihre untergeordneten Elemente mit `<Slot />` (Großbuchstaben S), nicht mit `<slot />`.
- Eine `.nexy` Komponentendatei wird in PascalCase benannt: Sie wird als Python-Modul importiert, also ein Bindestrich
  kompiliert nicht.
- Für `.mdx` ist das Framework Preact, wenn die Datei importiert wird `preact`, andernfalls React.

## Wie geht es weiter?

- [Dokumentationsindex](../README.md): die Seite für das, was Sie erstellen
- [Fehlerbehebung](../guides/troubleshooting.md): Die Probleme, auf die die Leute zuerst stoßen
- [Config](../reference/config.md): jedes `use*` Feld und seine Standardeinstellung