# Markdown und MDX

Zwei Formate für Inhaltsseiten: `.md`, wenn Sie nur Markdown benötigen, `.mdx`, wenn Sie Komponenten benötigen.

## `.md`: reiner Markdown

Eine `.md`-Datei ist reiner Inhalt. Nexy rendert es mit `cmarkgfm` (GFM), fügt Überschriften-IDs hinzu und leitet a ab
Inhaltsverzeichnis und verpackt es in das nächste `layout.*`.

```md filename="src/routes/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter in `.md` wird nicht als Python-Logik verwendet. Wenn Sie Serverlogik benötigen, verwenden Sie `.nexy`.
- Layout-Umbruch, Fehlerseiten und dynamische Segmente funktionieren auf die gleiche Weise wie andere Seiten.

## `.mdx`: Markdown mit Komponenten

`.mdx` Dateien werden von **Vite** über die Framework-Route-Pipeline (React oder Preact) kompiliert. Python
Schreibt nur den dünnen Wrapper, der die Route bedient; Es kompiliert oder rendert MDX selbst nie.
Komponenten werden vom Framework gerendert, wie andere Komponentenrouten vom Server gerendert und
vorgerendert in HTML von `nx build`.

- Erfordert `useFF`, um reagieren oder vorwirken zu können.
- Erfordert die optionalen Pakete `@mdx-js/rollup`, `remark-gfm` und `@mdx-js/react` (und
  `@mdx-js/esbuild` für den Build). Vite sagt Ihnen, welches fehlt.
- Das Framework wird bei Importen automatisch erkannt: Preact, wenn die Datei importiert wird `preact`, React
  sonst.

> [!NOTE]
> verwenden Sie `.nexy`, wenn Sie Python-Logik in Frontmatter benötigen.

## Nächste Schritte

- [.nexy-Dateien](README.md): das native Seitenformat
- [Ansichten](../README.md): Wählen Sie ein Format
- [i18n](../../guides/i18n.md): Internationalisierung