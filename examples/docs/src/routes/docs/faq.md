# Questions

## How much space do backups take?

The first snapshot is about the size of the folder after compression. Each next one adds only the
blocks that changed, so a hundred snapshots of a folder that changes a little take little more than
one.

## Can two machines use the same bucket?

Yes, with a different prefix each: `s3://my-backups/laptop` and `s3://my-backups/desktop`. They never
read or write each other's snapshots.

## Does Cairn follow symbolic links?

No. It stores the link itself, so a restore brings back the link, not a copy of its target.

## What happens if a backup is interrupted?

Nothing is lost. The next backup finds the blocks that were already sent and only sends the rest.
