# Configuration

Cairn reads `cairn.toml` in the folder it backs up, then `~/.config/cairn/cairn.toml`. A key in the
folder wins over the same key in your home.

## A complete file

```toml
repository = "s3://my-backups/laptop"
exclude = ["node_modules", ".cache", "*.tmp"]
compression = "zstd"

[keep]
daily = 30
weekly = 12
monthly = 24
```

## Keys

| Key | Default | What it does |
|---|---|---|
| `repository` | none | where snapshots go, as `s3://bucket/prefix` |
| `exclude` | `[]` | names and patterns that are never backed up |
| `compression` | `"zstd"` | `"zstd"`, `"gzip"` or `"none"` |
| `keep.daily` | `7` | how many daily snapshots `prune` keeps |
| `keep.weekly` | `4` | how many weekly snapshots `prune` keeps |
| `keep.monthly` | `12` | how many monthly snapshots `prune` keeps |

## Environment variables

`CAIRN_REPOSITORY` and `CAIRN_PASSPHRASE` replace the matching keys, which is what a scheduled job
needs. Never write the passphrase in `cairn.toml`.
