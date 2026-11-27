# 如何从注册表安装模块？

在 Nexy 项目中运行 `nx add @scope/name` 以从模块注册表下载一个版本，检查它并应用其声明的更改。添加 `@1.2.0` 以固定确切版本。

## 安装模块

从 Nexy 项目的根目录来看：

```bash
nx add @acme/auth
nx add @acme/auth@1.2.0
```

`nx add` 从 `useModuleRegistry` 读取发布元数据和存档，检查 SHA-256 校验和，并检查模块的 `nexy` 和 `python` 兼容性范围。然后，它仅写入清单声明的文件，使用 `uv add` 添加声明的 Python 包，使用项目的包管理器添加 Node 包，并将配置挂钩应用到 `nexyconfig.py` 和 `package.json`。现有设置和文件保持原样：已存在的已声明文件将被 `warning:` 行跳过。

每个成功的安装都会记录在 `.nexy/modules.json` 中。提交该文件，以便队友获得相同的模块版本。

## 升级一个模块

要升级，请在注册表有更新版本后再次运行 `nx add @acme/auth`，或设置新的 pin，例如 `@acme/auth@1.3.0`。取消固定的名称会从注册表的 `/versions` 响应中选择最新版本。再次运行相同的版本会打印 `is already installed` 并且没有任何改变。

## 固定版本

引脚是准确的：`nx add @acme/auth@1.2.0` 安装 `1.2.0`，没有其他版本。在 CI 和提交的 `.nexy/modules.json` 中使用 pin，以便每次结账都会安装相同的代码。如果没有 PIN，新版本会更改下一次安装。

## 运行迁移

默认情况下迁移处于关闭状态。当您希望在文件和依赖项就位后运行版本声明的命令时，请添加 `--migrate`：

```bash
nx add @acme/auth@1.2.0 --migrate
```

每个命令在运行之前都会被打印。该项目需要先安装其迁移工具，然后才能声明模块。

## 设置注册表及其信任规则

默认值位于 `nexyconfig.py` 中：

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useModuleRegistry = "https://registry.nexypy.dev"
    useRequireSignedModules = False
```

`useModuleRegistry` 是 CLI 读取的基本 URL。仅接受 https URL，开发期间本地注册表的环回 http 除外。 `useRequireSignedModules = True` 拒绝未签名的发布。在验证者可用之前，带有签名的发布也会被拒绝；一旦验证，`nx add` 就会打印 `Verified by` 以及签名者的身份。仅对您信任的注册表保留默认的 `False`。
