# 安全

Nexy 如何保持自己的攻击面较小、它需要哪些版本以及如何检查项目。

## 版本楼层

Nexy 依赖于 FastAPI、Starlette、Jinja2、Vite 和 React。 A楼是Nexy最低版本
允许；每个人都回答已发布的建议。

| 套餐 | 楼层 | 为什么 |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost)：精心设计的 `Host` 标头更改了 Starlette 向中间件报告的路径，从而绕过了 `request.url.path` 上写入的授权。被 CISA 列为利用。 |
| `fastapi` | 0.133.0 | 第一个接受固定 Starlette 的版本 |
| `jinja2` | 3.1.6 | 通过 `attr` 过滤器逃逸沙箱 (CVE-2025-27516) |
| `vite`（脚手架项目）| 6.4.3 | `server.fs.deny` 在 Windows 备用路径上绕过 (CVE-2026-53571)；早期的查询字符串绕过 (CVE-2026-39364) 仅影响 Vite 7.1-7.3.1 和 8.0.0-8.0.4 |
| `react`、`react-dom` | 19.2.5 | 2026 React 建议涉及 `react-server-dom-*` 包，Nexy 不使用该包；地板使线路保持修补状态 |

检查您已解决的版本：

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Nexy 规则遵循

- **永远不要信任路径的主机标头。** Nexy 读取 `scope["path"]`，而不是 `request.url.path`，
  它自己的中间件（目录中间件）。在你的身上做同样的事情。
- **转义到达 HTML 的内容。** 传递给客户端组件的道具，`Link` 属性，`Image`，
  `Audio` 和 `Video` 属性、目录锚点和 `HTTPException` 详细信息都是
  HTML 转义。模板中的 `| safe` 会关闭此功能：切勿在用户输入上使用它。
- **开发者端点是仅环回且狭窄的。** 开发渲染端点
  (`/__nexy__/render`) 只接受 `src/routes/` 下带有 `.tsx` 或 `.jsx` 扩展名的文件，并且
  只能通过开发服务器访问，该服务器拒绝外部 `Host` 标头。
- **错误详细信息不会泄漏。**本身失败的错误页面仅显示状态代码。
- **生产答案带有安全标头。** `X-Content-Type-Options: nosniff` 和
  `Referrer-Policy: strict-origin-when-cross-origin`，除非你的代码设置了自己的。 `Server`
  标头未发送。添加 `Strict-Transport-Security` 和 `Content-Security-Policy` 在你的
  代理或中间件：它们取决于您的域。
- **崩溃显示参考，而不是错误。**请参阅[错误页面](../routing/fbr/errors/README.md#unhandled-exceptions)。
- **Nexy 的 Python 代码中没有 `eval` 和 `shell=True`。** 外部程序使用参数列表运行。

## 运行审核

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Nexy 自己的存储库在其检查中运行第一个和第三个。上一层的新建议是通过提高
地板在`pyproject.toml`或脚手架`package.json`中，然后重新生成锁。

## 安全部署

- 将 `useTrustedHost` 设置为您的域：它会拒绝任何路由之前的意外 `Host` 标头。
- 不要暴露 Vite 开发服务器：`nx dev`将其保持在 Nexy 源后面的环回上。
- 如果 API 模式不应公开，则设置 `useDocs = False`。

请参阅[中间件和安全性](../guides/middleware-and-security.md)。

## 来源

- [Starlette 中的 CVE-2026-48710 (BadHost) ](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite 咨询 GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) 和
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React 服务器包 CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## 后续步骤

- [中间件和安全性](../guides/middleware-and-security.md)
- [部署](../deployment/README.md)
- [配置](config.md)