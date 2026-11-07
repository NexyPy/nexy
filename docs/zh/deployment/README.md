# 部署

两个命令：`nx build` 生成工件，`nx start` 为它们提供服务。

**开始之前：** 使用 `nx build` 在本地构建的项目，以及 - 对于客户端页面 - `nx new` 安装的前端工具链。

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

运行时仅需要 Python。 Uvicorn 提供编译后的应用程序和静态资源；不涉及 Node 进程和 Vite 进程。

## 构建产生什么

`__nexy__/` 包含已编译的路由模块、`__nexy__/client/` 下的客户端包以及框架路由的预渲染 HTML。复制项目 - 源加上 `__nexy__/` - 或在图像内构建。

## Docker

构建阶段需要 Node（对于 Vite）和 Python（对于编译器）。运行时阶段仅需要 Python。

```dockerfile filename="Dockerfile"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

当基础镜像没有时，`uv` 会获取托管的 Python，这就是构建阶段可以从 Node 镜像开始的原因。

## 在反向代理后面

在本地主机上运行 `nx start` 并让 Nginx、Caddy 或平台代理终止 TLS：

```bash
nx start --host 127.0.0.1 --port 8000
```

如果您使用 `SOCKET` 处理程序，请确保代理转发 WebSocket 升级，并且它转发原始主机 - FastAPI 从中构建绝对 URL。

## 健康检查

<!-- router:fbr,custom -->
添加处理程序文件 `src/routes/api/health.py` 和探针 `/api/health` - 而不是可能渲染缓慢的页面：

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
添加一个控制器，并探测 `/health/` - 而不是可能渲染缓慢的视图：

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

将其列在根模块的 `controllers` 中。
<!-- /router -->

## 静态托管

每个页面都是 HTML，但 Nexy 假定有一个用于路由和 API 处理程序的服务器。

> [!NOTE]
> 没有 `--static` 构建模式。必须在管道中从 `nx build` 输出生成纯静态导出。

## 清单

- [ ] `nx build` 在 CI 中，对于您希望在服务器上呈现的路由没有警告
- 当路径文件无法加载时，[ ] `nx start` 退出并显示代码 1，并且不启动任何内容
- [ ] `NEXY_ACTION_SECRET` 设置，或 `__nexy__/action.key` 与构建一起保留
- [ ] `useDocs = False` 在生产中如果 API 架构不应公开
- [ ] `useTrustedHost` 和 `useHTTPSRedirect` 设置为公共部署
- [ ] `__nexy__/` 未提交

## 后续步骤

- [配置](../reference/config.md)：HTTPS、可信主机、会话
- [前端](../guides/frontend.md)：Vite 构建什么
- [测试](../guides/testing.md)：在 CI 中运行的命令
