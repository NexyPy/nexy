# Upgrade auf 2.2

Was ändert sich für ein bestehendes Projekt, wenn Sie von 2.1 auf 2.2 wechseln, und was ist dagegen zu tun? Die vollständige Liste finden Sie im [Änderungsprotokoll](https://github.com/NexyPy/nexy/blob/main/CHANGELOG.md).

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
| **`nx check` kompiliert nicht mehr `.mdx`** | Nichts: Vite meldet MDX Fehler beim Build |

## Was gleich bleibt

- Ihre Routen, Layouts, Aktionen und Konfiguration.
- Bestehende Projekte behalten ihre eigenen Startseiten. Das neue Starterdesign gilt nur für Projekte, die nach dem Upgrade erstellt wurden.
- Die Entwicklungssymbolleiste und `useDevTools`.

## Neu in 2.2

- **Agentendateien.** `nx new` schreibt `AGENTS.md`, `CLAUDE.md` und die Fähigkeiten zum Codieren von Agenten. Führen Sie für ein Projekt, das Sie bereits haben, `nx skills` aus. Es überschreibt niemals eine von Ihnen geschriebene Datei. Siehe [Kodierungsagenten](../guides/ai-agents.md).
- **Ein Entwicklungsserver, der weiterläuft.** Wenn Ihre Anwendung nicht gestartet werden kann, `nx dev` wird der Grund gemeldet und auf die nächste Änderung gewartet, anstatt sie zu beenden.
- **Ein neuer Starter** für jedes Framework in Tailwind oder UnoCSS, mit den gleichen Seiten und Komponenten.
- **UnoCSS liest `.nexy` Dateien** in einem Serverprojekt. Wenn Sie UnoCSS mit `.nexy`-Seiten verwenden, fügen Sie den in [Fehlerbehebung](../guides/troubleshooting.md) gezeigten Block `content` hinzu.

## Korrigierte Dokumentation

Auf drei Seiten wurde etwas gesagt, was der Code nicht tut. Wenn Sie diese befolgt haben, überprüfen Sie Ihre Dateien:

- Eine `.nexy`-Komponente platziert ihre untergeordneten Elemente mit `<Slot />` (Großbuchstaben S) und nicht mit `<slot />`.
- Eine `.nexy`-Komponentendatei wird in PascalCase benannt: Sie wird als Python-Modul importiert, sodass ein Bindestrich nicht kompiliert wird.
- Für `.mdx` ist das Framework Preact, wenn die Datei `preact` importiert, andernfalls React.

## Wohin als nächstes

- [Dokumentationsindex](../README.md): die Seite für das, was Sie erstellen
- [Fehlerbehebung](../guides/troubleshooting.md): Die Probleme, auf die die Leute zuerst stoßen
- [Konfiguration](../reference/config.md): jedes `use*`-Feld und seine Standardeinstellung
