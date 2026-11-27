# How do I publish a module to the Nexy registry?

Run `nx publish` from a module directory with a valid `nx.toml`, a registry token, and every file the manifest declares; the command checks the release, builds one archive, and uploads an immutable version.

## Prepare the manifest

A source module lists each file it ships. The archive holds `nx.toml` and exactly those files.

```toml filename="nx.toml"
name = "@acme/auth"
version = "1.2.0"
kind = "source"

[compatibility]
nexy = ">=2.0.0"
python = ">=3.12"

[dependencies]
python = []
node = []

[source]
files = ["src/auth.py", "src/helpers.py"]
```

The `name` field must be lowercase `@scope/name`. The `version` field must be three numbers separated by dots. The files must be relative paths inside the module. A package module declares `source.package` instead of `source.files`.

## Check before uploading

Use `--dry-run` to validate the manifest, archive the declared files, and print the checksum without uploading:

```bash
nx publish --dry-run
```

A dry run does not need a token. It prints a `warning:` line for each relative import that points to a file the manifest does not declare. For example, `from .helpers import token` in `src/auth.py` needs `src/helpers.py` in `source.files`, otherwise an install would get a broken import.

## Set the token

`nx publish` reads `NEXY_REGISTRY_TOKEN`, then `~/.config/nexy/registry-token`. The token is sent in the `Authorization` header and never printed.

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

The token file lets a future `nx login` write the same credential. Without either source, the command prints `error: No registry token` and exits with status 1.

## Publish

```bash
nx publish
```

The command prints the name, version and SHA-256 checksum of the release it published. A name and version pair is immutable: publishing it again prints a conflict error. Publish a new version instead.

## Use another registry

By default the command posts to `https://registry.nexypy.dev`. Use `--registry` for another registry, for example a local one during development:

```bash
nx publish --registry http://localhost:8000
```

Only https URLs are accepted, plus plain http on `localhost`, `127.0.0.1` and `::1`. Transient `429` and `5xx` answers are retried twice; a bad manifest, a missing token or a conflict is not retried.

## Verify the release

```bash
nx add @acme/auth@1.2.0
```

See [Install modules](install-modules.md) for upgrades, pins and trust settings.
