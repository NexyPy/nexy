# Introduction

Cairn backs up a folder to object storage, keeps every version you ask it to keep, and brings any of
them back with one command. It runs on your machine, encrypts before anything leaves it, and needs no
server of its own.

> Cairn is made up: these are the docs of the documentation example of Nexy. The commands do not
> exist, but every page works the way a real docs site would.

## What Cairn does

- **Backs up a folder**, sending only what changed since the last backup.
- **Keeps versions**: every backup is a snapshot you can list, compare and restore.
- **Encrypts on your machine** with a key that never leaves it.
- **Prunes old snapshots** by a rule you write once, such as "one per day for a month".

## What Cairn does not do

Cairn is not a sync tool: it never changes the folder it backs up, and two machines never write to
each other's snapshots. It is not a disk image either: it backs up files, not partitions.

## Where to go next

Start with [Installation](/docs/installation), then follow the [Quick start](/docs/quick-start)
to make a first backup in five minutes.
