# 性能

`nx start` 默认执行什么操作、要打开什么以及项目启动和响应的速度。

## 默认值

| 关注 | 默认 | 改变它 |
|---|---|---|
| 流程 | Linux 和 macOS 上每个 CPU 一名 Uvicorn 工作人员，Windows 上一名工作人员 | `nx start` 通过 Uvicorn 运行应用程序 |
| 压缩 | 关闭 | [配置](../reference/config.md) 中的 `useGZip = {"minimum_size": 1000}`，或在反向代理处压缩 |
| 静态文件 | 与 `ETag` 和 `Last-Modified` 一起食用，没有 `Cache-Control` | 在反向代理或 CDN 上为散列包设置长期缓存 |
| HTML 页面 | 按请求渲染，无缓存 | [ISR](../rendering/isr.md) 和 `revalidate = N` |
| API文档 | 上 | `useDocs = False` 生产中 |
| 运行时的节点 | 无 | `nx build` 预渲染客户端组件 |

`nexyconfig.py`中的表和页中的ISR的两个开关：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```
<!-- /router -->

<!-- router:modular -->
ISR 是一种文件页面模式：控制器返回的视图在每个请求上呈现。
<!-- /router -->

## 启动、首页并重新编译

具有一个 `.nexy` 页面的项目需要多长时间，中位数为 5 次运行，每次运行在一个新的 Python 进程中：

| 测量 | 中位数 | 它涵盖什么 |
|---|---|---|
| 启动 | 460毫秒 | 从新流程到准备好回答的应用程序：导入、路由扫描、编译 |
| 第一页 | 554 毫秒 | 相同，加上对 `/` 的第一个请求及其 HTML |
| 重新编译页面 | 1.8毫秒 | 编辑后在已运行的进程中再次编译页面 |

在 AMD Ryzen 5 4500U、Linux、6 个 CPU、Python 3.13.15 上测量。重新编译是 `nx dev` 对更改的 Python 方面所做的事情；浏览器重新加载还需要支付 Vite 的模块图和浏览器自己的渲染费用，因此这不是重新加载时间。

用写表的脚本测量一下你自己的机器：

```bash
python scripts/measure_speed.py --runs 5
```

`Speed` 工作流程在每次推送到 `main` 时运行它，并在 GitHub 托管的 Ubuntu 运行器上的运行摘要中写入相同的表。

## 每秒请求数

本地运行，一个 Uvicorn 工作线程，Windows，Python 3.13，来自同一计算机上的 Python 负载生成器的保持活动连接。将这些数字视为比较变化的基线，而不是作为其他框架的基准。

表的 Nexy JSON 路由是这个文件：

<!-- router:fbr,custom -->
```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/ping_controller.py"
from nexy.decorators import Controller


@Controller("/api/ping")
class PingController:
    async def get(self):
        return {"ok": True}
```

下面的数字是用文件路径测量的。在使用控制器之前，请以相同的方式对其进行测量。
<!-- /router -->

| 路线 | 并发性 | 每秒请求数 | p50 | p99 |
|---|---|---|---|---|
| 裸 FastAPI JSON 路由 | 16 | 〜4,500 | 3.4毫秒 | 5.1毫秒 |
| Nexy JSON 路由 (`src/routes/api/ping.py`) | 16 | 〜2,900 | 5.2毫秒 | 9.8 毫秒 |
| Nexy SSR 页面（16 KB，16 个组件） | 1 | 〜500 | 1.9 毫秒 | 3.0毫秒 |
| Nexy SSR 页面（16 KB，16 个组件） | 64 | 〜670 | 94毫秒 | 126 毫秒 |

读表：

- Nexy 自己的层（路径上下文、中间件）消耗的吞吐量约为裸 FastAPI 路由的三分之一。
- 服务器渲染的页面大约需要 2 毫秒的 CPU 时间，分布在大约 16 个模板渲染上（每个组件一个）。组件较少的页面相应地更便宜。
- 吞吐量随工人而变化。在 Linux 上，`nx start` 已经为每个 CPU 启动一个。

## 实用建议

1. 将 Nginx、Caddy 或您平台的优势放在前面：TLS、HTTP/2、Brotli 和 `/__nexy__/client/` 资产的长期缓存是它们的优势。请参阅[部署](README.md)。
2. 对于每分钟更改次数少于一次的页面，请使用 [ISR](../rendering/isr.md)。
3. 使用[岛屿](../rendering/islands.md) 懒惰地水合，因此第一批货物运输较少 JavaScript。
4. 保持每页的 `.nexy` 组件数量合理：每个组件都是一个单独的模板渲染。
5. 测量自己的路线。保持连接活动的本地负载生成器足以比较页面的两个版本。

Nginx 的建议 1：散列的客户端包缓存一年，其余的交给 Nexy。

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 后续步骤

- [部署](README.md)
- [渲染](../rendering/README.md)
- [配置](../reference/config.md)
