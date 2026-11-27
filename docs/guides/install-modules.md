# How do I install a module from the registry?

Run `nx add @scope/name` in a Nexy project to download one release from the module registry, check it, and apply its declared changes. Add `@1.2.0` to pin an exact version.

## Install a module

From the root of a Nexy project:

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` reads the release metadata and archive from `useModuleRegistry`, checks the SHA-256 checksum, and checks the module's `nexy` and `python` compatibility ranges. It then writes only the files the manifest declares, adds the declared Python packages with `uv add`, adds Node packages with the project's package manager, and applies the config hooks to `nexyconfig.py` and `package.json`. Existing settings and files stay as they are: a declared file that already exists is skipped with a `warning:` line.

Every successful install is recorded in `.nexy/modules.json`. Commit that file so a teammate gets the same module version.

## Upgrade a module

To upgrade, run `nx add @acme/auth` again after the registry has a newer release, or set a new pin such as `@acme/auth@1.3.0`. An unpinned name selects the newest version from the registry's `/versions` response. Running the same version again prints `is already installed` and changes nothing.

## Pin a version

A pin is exact: `nx add @acme/auth@1.2.0` installs `1.2.0` and no other release. Use a pin in CI and in a committed `.nexy/modules.json` so every checkout installs the same code. Without a pin, a new release changes the next install.

## Run migrations

Migrations are off by default. Add `--migrate` when you want a release's declared commands to run after its files and dependencies are in place:

```bash
nx add @acme/auth@1.2.0 --migrate
```

Each command is printed before it runs. The project needs its migration tool installed before a module can declare one.

## Set the registry and its trust rules

The defaults live in `nexyconfig.py`:

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` is the base URL the CLI reads. Only https URLs are accepted, except loopback http for a local registry during development. `useRequireSignedModules = True` refuses an unsigned release. A release that carries a signature is refused as well until a verifier is available; once one verifies it, `nx add` prints `Verified by` with the signer's identity. Keep the default `False` only for registries you trust.
