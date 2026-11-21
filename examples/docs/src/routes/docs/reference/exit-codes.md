# Exit codes

Every command ends with a code a script can test.

| Code | Meaning |
|---|---|
| `0` | done |
| `1` | done, but some files could not be read; they are listed |
| `2` | the command line is wrong |
| `3` | the repository cannot be reached |
| `4` | the passphrase is wrong |
| `5` | another Cairn holds the lock of this repository |

## In a script

```bash
cairn backup ~/Documents
if [ $? -eq 1 ]; then
  echo "Backup done with unreadable files" >&2
fi
```
