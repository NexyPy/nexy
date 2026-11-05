# 安全性

Nexy 如何保持自己的攻击面较小、它需要哪些版本以及如何检查项目。

## 版本楼层

Nexy 取决于 FastAPI、Starlette、Jinja2、Vite 和 React。楼层是 Nexy 允许的最低版本；每个人都回答已发布的建议。

| 套餐 | 楼层 | 为什么 |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost)：精心设计的 `Host` 标头更改了 Starlette 向中间件报告的路径，从而绕过了 `request.url.path` 上写入的授权。被 CISA 列为利用。 |
| `fastapi` | 0.133.0 | 接受固定 Starlette | 的第一个版本
| `jinja2` | 3.1.6 | 通过 `attr` 过滤器逃逸沙箱 (CVE-2025-27516) |
| `vite`（脚手架项目）| 6.4.3 | `server.fs.deny` 在 Windows 备用路径上绕过 (CVE-2026-53571)；早期的查询字符串绕过 (CVE-2026-39364) 仅影响 Vite 7.1-7.3.1 和 8.0.0-8.0.4 |
| `react`、`react-dom` | 19.2.5 | 2026 React 公告涉及 `react-server-dom-*` 软件包，Nexy 不使用该软件包；地板使线路保持修补状态 |

检查您已解决的版本：

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## 规则 Nexy 遵循

- **切勿信任路径的 Host 标头。** Nexy 在其自己的中间件（目录中间件）中读取 `scope["path"]`，而不是 `request.url.path`。在你的身上做同样的事情。
- **对到达 HTML 的内容进行转义。** 传递给客户端组件的属性、`Link` 属性、`Image`、`Audio` 和 `Video` 属性、目录锚点和 `HTTPException` 详细信息都是 HTML 转义的。模板中的 `| safe` 会关闭此功能：切勿在用户输入上使用它。
- **开发者端点是仅环回且狭窄的。** 开发渲染端点（`/__nexy__/render`）仅接受 `src/routes/` 下具有 `.tsx` 或 `.jsx` 扩展名的文件，并且只能通过开发服务器访问，该服务器拒绝外部 `Host` 标头。
- **错误详细信息不会泄漏。** 本身失败的错误页面仅显示状态代码。
- **生产答案带有安全标头。** `X-Content-Type-Options: nosniff` 和 `Referrer-Policy: strict-origin-when-cross-origin`，除非您的代码设置了自己的标头。不发送 `Server` 标头。在您的代理或中间件中添加 `Strict-Transport-Security` 和 `Content-Security-Policy`：它们取决于您的域。
- **崩溃显示引用，而不是错误。** 请参阅[错误页面](../routing/fbr/errors/README.md#unhandled-exceptions)。
- **Nexy 的 Python 代码中没有 `eval` 和 `shell=True`。** 外部程序使用参数列表运行。

## 运行审核

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Nexy 自己的存储库在其检查中运行第一个和第三个。通过升高 `pyproject.toml` 或脚手架 `package.json`中的地板，然后重新生成锁来处理上方楼层的新建议。

## 安全部署

- 将 `useTrustedHost` 设置为您的域：它会拒绝任何路由之前的意外 `Host` 标头。
- 不要公开 Vite 开发服务器：`nx dev` 使其保持在 Nexy 源后面的环回状态。
- 如果 API 架构不应公开，则设置 `useDocs = False`。

请参阅[中间件和安全性](../guides/middleware-and-security.md)。

## 来源

- Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/) 中的 [CVE-2026-48710 (BadHost)
- [Vite 咨询 GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) 和 [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React 服务器包CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## 后续步骤

- [中间件和安全性](../guides/middleware-and-security.md)
- [部署](../deployment/README.md)
- [配置](config.md)
