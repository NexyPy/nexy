# cairn prune

Deletes the snapshots your `keep` rules do not keep, and frees their space.

```bash
cairn prune [--dry-run]
```

## How it chooses

`prune` keeps the newest snapshot of each day, week and month, as many as `keep.daily`,
`keep.weekly` and `keep.monthly` say (see [Configuration](/docs/configuration)). Everything else
is deleted.

## Check first

```bash
cairn prune --dry-run
```

```text
keep    a1f09c2  2026-11-20  daily
keep    9e2b1d0  2026-11-16  weekly
delete  77c0e41  2026-11-15
```

## Tagged snapshots

A snapshot with a tag is never pruned. Remove the tag with `cairn tag SNAPSHOT --remove` when you
no longer need it.
