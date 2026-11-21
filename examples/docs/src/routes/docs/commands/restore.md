# cairn restore

Brings back a whole snapshot, a folder of it, or one file.

```bash
cairn restore SNAPSHOT [--path PATH] [--to FOLDER]
```

## Options

| Option | What it does |
|---|---|
| `SNAPSHOT` | the snapshot id, or `latest` |
| `--path PATH` | only this file or folder of the snapshot |
| `--to FOLDER` | where to write; a new folder named after the snapshot when left out |

## Examples

Restore one file from the last snapshot:

```bash
cairn restore latest --path Documents/notes.md --to ~/Desktop
```

## Safety

`restore` never overwrites a file. When the target exists, it stops and names the file, so a restore
can never destroy the work it was meant to save.
