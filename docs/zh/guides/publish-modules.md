# 如何将模块发布到 Nexy 注册表？

使用有效的 `nx.toml`、注册表令牌以及清单声明的每个文件从模块目录运行 `nx publish`；该命令检查版本，构建一个存档，并上传一个不可变的版本。

## 准备清单

源模块列出了它附带的每个文件。存档包含 `nx.toml` 以及这些文件。

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

`name` 字段必须为小写 `@scope/name`。 `version` 字段必须是由点分隔的三个数字。这些文件必须是模块内的相对路径。包模块声明 `source.package` 而不是 `source.files`。

## 上传前检查

使用 `--dry-run` 验证清单，归档声明的文件，并打印校验和而不上传：

```bash
nx publish --dry-run
```

试运行不需要令牌。它为每个指向清单未声明的文件的相对导入打印 `warning:` 行。例如，`src/auth.py` 中的 `from .helpers import token` 需要 `source.files` 中的 `src/helpers.py`，否则安装将导致导入损坏。

## 设置令牌

`nx publish` 读取 `NEXY_REGISTRY_TOKEN`，然后读取 `~/.config/nexy/registry-token`。令牌在 `Authorization` 标头中发送，并且从不打印。

```bash
export NEXY_REGISTRY_TOKEN="your-token"
nx publish
```

令牌文件让未来的 `nx login` 写入相同的凭证。如果没有任一源，该命令将打印 `error: No registry token` 并以状态 1 退出。

## 发布

```bash
nx publish
```

该命令打印其发布的版本的名称、版本和 SHA-256 校验和。名称和版本对是不可变的：再次发布它会打印冲突错误。改为发布新版本。

## 使用另一个注册表

默认情况下，该命令发布到 `https://registry.nexypy.dev`。将 `--registry` 用于另一个注册表，例如开发期间的本地注册表：

```bash
nx publish --registry http://localhost:8000
```

仅接受 https URL，以及 `localhost`、`127.0.0.1` 和 `::1` 上的纯 http。瞬态 `429` 和 `5xx` 答案重试两次；清单错误、令牌丢失或冲突不会重试。

## 验证发布

```bash
nx add @acme/auth@1.2.0
```

有关升级、引脚和信任设置，请参阅[安装模块](install-modules.md)。
