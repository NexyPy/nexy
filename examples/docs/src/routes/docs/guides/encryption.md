# Encryption

Everything Cairn sends is encrypted on your machine first. The storage only ever sees encrypted
blocks and their sizes.

## The key and the passphrase

`cairn init` makes a random key, then encrypts that key with your passphrase and stores it next to the
snapshots. To read a snapshot, Cairn needs both: the stored key, and the passphrase to open it.

## Change the passphrase

```bash
cairn passphrase change
```

Only the stored key is encrypted again: no snapshot has to be sent twice.

## If you lose the passphrase

Nobody can open the snapshots, and there is no reset. Keep the passphrase in a password manager, and
a copy of it on paper somewhere safe.
