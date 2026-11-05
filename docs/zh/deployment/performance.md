# 性能

`nx start` 默认执行什么操作、打开什么以及测量什么。

## 默认值

| 关注 | 默认 | 改变它 |
|---|---|---|
| 流程 | Linux 和 macOS 上每个 CPU 一名 Uvicorn 工作人员，Windows 上一名工作人员 | `nx start` 通过 Uvicorn 运行应用程序 |
| 压缩 | 关闭 | [配置](../reference/config.md) 中的 `useGZip = {"minimum_size": 1000}`，或在反向代理处压缩 |
| 静态文件 | 与 `ETag` 和 `Last-Modified` 一起食用，没有 `Cache-Control` | 在反向代理或 CDN 上为散列包设置长期缓存 |
| HTML 页面 | 按请求渲染，无缓存 | [ISR](../rendering/isr.md) 与 `revalidate = N` |
| API文档 | 上 | `useDocs = False` 生产中 |
| 运行时的节点 | 无 | `nx build` 预渲染客户端组件 |

## 测量的

本地运行，一个 Uvicorn 工作线程，Windows，Python 3.13，来自同一计算机上的 Python 负载生成器的保持活动连接。将这些数字视为比较变化的基线，而不是作为其他框架的基准。

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
3. 用[岛屿](../rendering/islands.md) 懒惰地水合，因此第一批货物运输较少 JavaScript。
4. 保持每页的 `.nexy` 组件数量合理：每个组件都是一个单独的模板渲染。
5. 测量自己的路线。保持连接活动的本地负载生成器足以比较页面的两个版本。

## 后续步骤

- [部署](README.md)
- [渲染](../rendering/README.md)
- [配置](../reference/config.md)
