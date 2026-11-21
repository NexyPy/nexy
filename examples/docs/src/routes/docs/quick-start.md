# Quick start

This page makes a first backup of a folder, lists it, and restores one file from it. It takes about
five minutes.

## 1. Choose where backups go

Cairn writes to any storage that speaks the S3 protocol. Give it the bucket and the keys:

```bash
cairn init s3://my-backups/laptop
```

`init` asks for the access keys, then for a passphrase. The passphrase protects the encryption key:
without it, nobody can read your backups, including you.

## 2. Back up a folder

```bash
cairn backup ~/Documents
```

The first backup sends everything. The next ones only send what changed, so they are fast.

## 3. List the snapshots

```bash
cairn snapshots
```

```text
ID        DATE              FILES   SIZE
a1f09c2   2026-11-20 09:14  12 408  3.1 GB
```

## 4. Restore a file

```bash
cairn restore a1f09c2 --path Documents/taxes/2025.pdf --to ~/Desktop
```

## Next

- Run backups on a schedule: [Schedule backups](/docs/guides/schedule).
- Keep the bucket small: [prune](/docs/commands/prune).
