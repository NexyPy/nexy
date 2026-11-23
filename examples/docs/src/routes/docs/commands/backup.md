# cairn backup

Takes a snapshot of a folder and sends what changed since the last one.

```bash
cairn backup [FOLDER] [--tag TAG] [--dry-run]
```

## Options

| Option | What it does |
|---|---|
| `FOLDER` | the folder to back up; the current one when left out |
| `--tag TAG` | a word stored with the snapshot, to find it later |
| `--dry-run` | lists what would be sent, sends nothing |

## Examples

Back up the current folder and tag the snapshot:

```bash
cairn backup --tag before-upgrade
```

See what a backup would send:

```bash
cairn backup ~/Photos --dry-run
```

## What counts as changed

A file is sent again when its size or its modification time changed. Cairn then sends only the
blocks of the file that are new, so renaming a large file costs almost nothing.
