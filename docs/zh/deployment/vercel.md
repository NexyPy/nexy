# 如何在 Vercel 上部署 Nexy 应用程序？

运行 `nx add vercel`，将生成的文件与 `nx build` 输出一起提交，并将 Vercel Python 运行时指向 `src/server.py:app`。

## 添加平台文件

从 Nexy 项目的根目录来看：

```bash
nx add vercel
nx build
```

`nx add vercel` 写入 `src/server.py` 和 `vercel.json`。它还为应用程序运行时更改的文件附加忽略规则：`__nexy__/build-cache.json`、`__nexy__/server.port`、`__nexy__/.temp/` 和 `__pycache__/`。再次运行该命令会保留已存在的文件，并且不会重复忽略规则。

## 将 Vercel 指向应用程序

在 Vercel 项目设置中，选择 Python 运行时并使用 `src/server.py:app` 作为入口点。 Vercel 在该模块中发现名称 `app`； `nx start` 不涉及。

生成的 `src/server.py` 在准备好工作文件夹后导入惰性 `nexy.app.app`。您可以在本地使用与 `uvicorn src.server:app` 相同的入口点。

## 提交构建输出

当 Vercel 没有构建命令时，它仅接收存储库包含的内容。在每个 `nx build` 之后提交 `__nexy__/`，并使用已编译的路由、`__nexy__/client/` 下的客户端包和 `__nexy__/client/.vite/manifest.json` 下的清单。

将 `vite.config.ts` 保留在项目根目录并提交。在生产中，Nexy 读取 Vite 清单来编写样式表和脚本标签，但仅当 `vite.config.ts` 存在时才会发出这些标签。如果没有该文件，页面仍然会回答 200，并且在没有 CSS 或客户端的情况下到达 JavaScript。

不要提交 `__nexy__/build-cache.json`：它包含运行构建的计算机的绝对路径。 `__nexy__/server.port` 属于 `nx start`，`__nexy__/.temp/` 是暂存空间。

## 接受只读文件系统

当 Python 应用程序启动时，Vercel 以只读方式安装项目。 Nexy 在启动期间写入生成的文件，因此裸露的 `from nexy.app import app` 可能会失败并显示 `OSError: [Errno 30] Read-only file system`。

生成的入口点在导入应用程序之前将六个项目项复制到可写临时文件夹中：`src`、`__nexy__`、`public`、`nexyconfig.py`、`pyproject.toml` 和 `vite.config.ts`。它更改工作目录并将副本首先放在 `sys.path` 上，因为 Nexy 解析来自当前目录的路由。手动将应用程序在运行时读取的任何其他文件添加到该列表中。

## 缓存静态资源

生成的 `vercel.json` 包含部署的 Nexy 站点使用的两个缓存规则：`/assets/` 下的文件在一年内不可变，`public/` 下的图像和字体在一天内保持新鲜，并有一周的失效时间重新验证窗口。如果您的项目需要，请在同一文件中添加其他规则。

## 检查部署情况

在推送之前，导入入口点并请求一页：

```bash
uv run python -c "from src.server import app; print(type(app).__name__)"
uv run uvicorn src.server:app
```

然后打开 `/`，在 `/assets/`下有一条生成的路线和一个文件。将响应与本地的 `nx start` 进行比较：状态、内容类型和大小应该匹配。比本地页面小恰好两个客户端标签的页面意味着复制的项目中缺少 `vite.config.ts`。
