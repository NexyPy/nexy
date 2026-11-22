# 如何在 Nexy 中调试服务器代码？

在终端中使用 `breakpoint()` 或使用 VS Code 和 `debugpy` 调试 `nx dev` 的服务器代码：开发服务器在其自己的进程中运行 Python，因此附加到它的调试器会在您的页面、API 处理程序和操作中停止。

## `nx dev` 如何运行您的代码

`nx dev` 在自己的进程中启动 uvicorn，无需单独的工作人员。当 Python 文件或 `.nexy` 页面更改时，它会忘记项目的模块并在同一过程中再次导入它们。因此，附加到 `nx dev` 的调试器在重新加载时保持附加状态，并且文件中设置的断点保留其在新代码中的位置。

`.nexy` 文件被编译为 `__nexy__/` 下的 Python 模块，位于同一路径，运行如下：

<!-- router:fbr,custom -->
| 你写 | 内克西跑 |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`，函数 `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | 文件本身 |
<!-- /router -->

<!-- router:modular -->
| 你写 | 内克西跑 |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | 文件本身 |
<!-- /router -->

`.nexy` 文件的 frontmatter（两个 `---` 行之间的 Python）成为该模块的函数体。每次更改时都会再次写入 `__nexy__/`：切勿编辑它。

## 使用 `breakpoint()` 在终端停止

将 `breakpoint()` 放在您想要停止的位置，在 `.py` 文件中或在 `.nexy` 文件的 frontmatter 中：

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

打开页面。请求等待，`nx dev` 的终端显示pdb，在编译的模块中：

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

打开 `/users`。请求等待，`nx dev` 的终端在该行显示 pdb。在视图的 frontmatter 中，pdb 在 `__nexy__/src/apps/` 下显示已编译的模块。
<!-- /router -->

输入 `p page` 打印一个值，输入 `n` 打印下一行，输入 `c` 让请求继续。完成后删除该行：下一个请求将再次停止。

## 使用 VS Code 进行调试

在项目环境中安装 `debugpy`：

```bash
uv add --dev debugpy
```

然后添加启动配置。 `nexy.modules.cli` 是 `nx` 命令背后的模块，因此这在 Linux、macOS 和 Windows 上的工作方式相同：

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

按 F5。在 `.py` 文件中以及 `__nexy__/` 下的 `.nexy` 文件的已编译模块中设置断点：VS Code 无法在 `.nexy` 文件中停止，因为在编译之前它不是 Python。编译模块的行号跟在frontmatter后面，所以编辑页面后，那里的断点可能会移动； `breakpoint()` 的 frontmatter 则不然。

## 从另一个终端连接

要自己启动开发服务器并稍后附加调试器：

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` 保持开始直到调试器附加；把它放在一边立即开始。在 VS Code 中，附加 `"request": "attach"` 和 `"connect": { "host": "127.0.0.1", "port": 5678 }` 的配置。

debugpy 可能会警告“正在使用冻结的模块”。如果错过了标准库中的断点，则以 `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) 开始 Python；您自己代码中的断点不受影响。

## 后续步骤

- [故障排除](troubleshooting.md)：人们遇到的第一个问题
- [测试](testing.md)：发现错误后在测试中重现该错误
- [.nexy 文件](../views/nexy/README.md)：frontmatter、props 和模板
