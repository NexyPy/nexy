# Markdown und MDX

Zwei Formate für Inhaltsseiten: `.md`, wenn Sie nur Markdown benötigen, `.mdx`, wenn Sie Komponenten benötigen.

## `.md`: rein Markdown

Eine `.md`-Datei ist reiner Inhalt. Nexy rendert es als Markdown im GitHub-Stil (Tabellen, Aufgabenlisten, durchgestrichen, Links), fügt Überschriften-IDs hinzu, leitet ein Inhaltsverzeichnis ab und verpackt es in das nächste `layout.*`.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter in `.md` wird nicht als Python-Logik verwendet. Wenn Sie Serverlogik benötigen, verwenden Sie `.nexy`.
- Roher HTML-Code in einer `.md`-Seite wird als Text angezeigt und nie ausgeführt. Wenn Sie HTML benötigen, verwenden Sie `.nexy`.
- Layoutumbruch, Fehlerseiten und dynamische Segmente funktionieren auf die gleiche Weise wie andere Seiten.

## `.mdx`: Markdown mit Komponenten

`.mdx`-Dateien werden von **Vite** über die Framework-Route-Pipeline (React oder Preact) kompiliert. Python schreibt nur den Thin Wrapper, der die Route bedient; es kompiliert oder rendert MDX nie selbst. Komponenten werden vom Framework gerendert, vom Server wie andere Komponentenrouten gerendert und von `nx build` in HTML vorgerendert.

- Erfordert, dass `useFF` React oder Preact ist.
- Erfordert die optionalen Pakete `@mdx-js/rollup`, `remark-gfm` und `@mdx-js/react` (und `@mdx-js/esbuild` für den Build). Vite sagt Ihnen, welches fehlt.
- Das Framework wird automatisch aus Importen erkannt: Preact, wenn die Datei importiert wird, `preact`, andernfalls React.

> [!NOTE]
> Verwenden Sie `.nexy`, wenn Sie Python-Logik in Frontmatter benötigen.

## Nächste Schritte

- [.nexy-Dateien](README.md): das native Seitenformat
- [Ansichten](../README.md): Wählen Sie ein Format
- [i18n](../../guides/i18n.md): Internationalisierung
