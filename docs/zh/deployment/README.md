# 部署

两个命令：`nx build` 生成工件，`nx start` 为它们提供服务。

**开始之前：** 使用 `nx build` 在本地构建的项目，以及 - 对于客户端页面 -
`nx new` 安装的前端工具链。

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

运行时只需要Python。 Uvicorn 提供编译后的应用程序和静态资源；无节点
流程，不涉及Vite流程。

## 构建产生什么

`__nexy__/` 包含已编译的路由模块、`__nexy__/client/` 下的客户端包以及
框架路由的预渲染 HTML。复制项目 - 源加 `__nexy__/` - 或在内部构建
图像。

## 码头工人

构建阶段需要 Node（用于 Vite）和 Python（用于编译器）。运行时阶段需要Python
仅。

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

`uv` 当基础镜像没有托管 Python 时获取托管 Python，这就是构建阶段可以开始的原因
来自节点图像。

## 反向代理背后

在 localhost 上运行 `nx start` 并让 Nginx、Caddy 或平台代理终止 TLS：

```bash
nx start --host 127.0.0.1 --port 8000
```

如果您使用 `SOCKET` 处理程序，请确保代理转发 WebSocket 升级，并且它转发
原始主机 - FastAPI 从中构建绝对 URL。

## 健康检查

添加处理程序文件 `src/routes/api/health.py` 和探测 `/api/health` - 而不是可能的页面
缓慢渲染：

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## 静态托管

每个页面都是 HTML，但 Nexy 假定有一个用于路由和 API 处理程序的服务器。

> [！注意]
> 没有`--static`构建模式。必须在以下位置生成纯静态导出
> 来自`nx build`输出的管道。

## 清单

- [ ] `nx build` 在 CI 中，对于您希望在服务器上渲染的路由没有警告
当路由文件无法加载时，- [ ] `nx start` 退出并显示代码 1，并且不启动任何内容
- [ ] `NEXY_ACTION_SECRET` 设置，或 `__nexy__/action.key` 与构建一起保留
如果 API 模式不应公开，则 - [ ] `useDocs = False` 在生产中
- [ ] `useTrustedHost` 和 `useHTTPSRedirect` 设置为公共部署
- [ ] `__nexy__/` 未提交

## 后续步骤

- [配置](../reference/config.md)：HTTPS、受信任的主机、会话
- [前端](../guides/frontend.md)：Vite 构建的内容
- [测试](../guides/testing.md)：在 CI 中运行的命令