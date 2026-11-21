# Installation

Cairn is one binary with no dependencies. Install it with the package manager of your system, or
download it.

## macOS

```bash
brew install cairn
```

## Linux

```bash
curl -fsSL https://cairn.example/install.sh | sh
```

The script puts `cairn` in `~/.local/bin`. Read it first if you prefer: it only downloads the binary
for your architecture and checks its signature.

## Windows

```powershell
winget install Cairn.Cairn
```

## Check the installation

```bash
cairn --version
```

It prints the version and the build date:

```text
cairn 1.4.2 (2026-10-02)
```

## Update

Run the same command as the installation. Cairn reads snapshots written by any older version, so an
update never needs a migration.
