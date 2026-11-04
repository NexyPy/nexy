# 性能

`nx start` 默认执行什么操作、打开什么以及测量什么。

## 默认值

| 关注 | 默认 | 更改 |
|---|---|---|
| 在 Linux 和 macOS 上每个 CPU 进程 | 一个 Uvicorn 工作线程，在 Windows 上一个 | `nx start` 通过 Uvicorn 运行应用程序 |
| 压缩 | 关闭 [[Config](../reference/config.md)] 中的 | `useGZip = {"minimum_size": 1000}`，或在反向代理 | 处压缩
| 静态文件 | 与 `ETag` 和 `Last-Modified` 一起提供，没有 `Cache-Control` | 在反向代理或 CDN 上为散列包设置长期缓存 |
| HTML 页面 | 按请求呈现，无缓存 | [ISR](../rendering/isr.md) 和 `revalidate = N` |
| 生产 | 中 | `useDocs = False` 的 API 文档 |
| 运行时的节点 | 无 | `nx build` 预渲染客户端组件 |

## 测量

本地运行，一个 Uvicorn 工作线程，Windows，Python 3.13，来自 Python 负载的保持活动连接
发电机在同一台机器上。将数字视为比较变化的基线，而不是作为
与其他框架进行基准测试。

| 路由 | 并发 | 每秒请求数 | p50 | p99 |
|---|---|---|---|---|
| 裸 FastAPI JSON 路由 | 16 | ~4,500 | 3.4 毫秒 | 5.1 毫秒 |
| Nexy JSON 路由 (`src/routes/api/ping.py`) | 16 | ~2,900 | 5.2 毫秒 | 9.8 毫秒 |
| Nexy SSR 页面（16 KB，16 个组件） | 1 | ~500 | 1.9 毫秒 | 3.0 毫秒 |
| Nexy SSR 页面（16 KB，16 个组件） | 64 | ~670 | 94 毫秒 | 126 毫秒 |

读表：

- Nexy 自己的层（路径上下文、中间件）消耗的吞吐量约为裸层吞吐量的三分之一
  FastAPI 路线。
- 服务器渲染的页面大约需要 2 毫秒的 CPU 时间，分布在大约 16 个模板渲染上（每个模板渲染一个）
  组件）。组件较少的页面相应地更便宜。
- 吞吐量随工人而变化。在 Linux 上，`nx start` 已经为每个 CPU 启动一个。

## 实用建议

1. 将 Nginx、Caddy 或您平台的边缘放在前面：TLS、HTTP/2、Brotli 和长期缓存
   `/__nexy__/client/` 资产是他们的优势。请参阅[部署](README.md)。
2. 对于每分钟更改一次的页面使用 [ISR](../rendering/isr.md)。
3. 使用[islands](../rendering/islands.md)延迟水合，因此第一次加载会传送更少的JavaScript。
4. 保持每页`.nexy`组件的数量合理：每个组件都是一个单独的模板
   渲染。
5. 测量你自己的路线。保持连接活动的本地负载生成器足以进行比较
   一个页面的两个版本。

## 后续步骤

- [部署](README.md)
- [渲染](../rendering/README.md)
- [配置](../reference/config.md)