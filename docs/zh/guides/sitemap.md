# 如何将 sitemap.xml 和 robots.txt 添加到 Nexy 站点？

在 `nexyconfig.py` 中设置 `useSiteUrl`：Nexy 然后提供 `/sitemap.xml`，其中列出了项目的每个静态页面，以及将搜索引擎指向它的 `/robots.txt`。

## 使用 `useSiteUrl` 将其打开

`useSiteUrl` 是该网站的公共来源，搜索引擎会看到：

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` 和 `nx start` 然后回答两个文件。如果没有 `useSiteUrl`，两者都不存在，因此项目永远不会错误地发布其开发服务器的 URL。

## 站点地图列出了哪些内容

站点地图将每个页面指定为 `useSiteUrl` 上的绝对 URL：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

当它向固定路径上的 `GET` 响应 HTML 时，就会列出路由：

<!-- router:fbr,custom -->
- 列出页面（`.nexy`、`.md`、`.mdx`、`.tsx`、`.jsx`、`.vue`、`.svelte`）；
- 动态页面，例如 `src/routes/users/[id].nexy`，被忽略：Nexy 无法知道其值；
- Python 路由处理程序回答 JSON，因此它被省略。
<!-- /router -->

<!-- router:modular -->
- 列出了一个响应 HTML 的控制器路由，带有 `@UseResponse(response_class=HTMLResponse)`；
- 带有路径参数的路由，例如 `/users/{id}`，被忽略：Nexy 无法知道其值；
- 回答 JSON 的路由被省略。
<!-- /router -->

API 模式中隐藏的路由 (`include_in_schema=False`) 也被忽略。

## 它所服务的 `robots.txt`

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## 而是自己写一个

您自己的文件总是获胜，并且 Nexy 永远不会覆盖它：

- `public/robots.txt` 或 `public/sitemap.xml` 按原样提供，就像 `public/` 的每个文件一样；
- `/robots.txt` 或 `/sitemap.xml` 处的项目路线保留其路径。

编写您自己的站点地图来列出动态页面，例如每个博客文章一个 URL。

## 后续步骤

- [页面元数据](../routing/fbr/pages/metadata.md)：搜索引擎显示的标题和描述
- [配置](../reference/config.md)：`nexyconfig.py` 的每个设置
- [部署](../deployment/README.md)：为生产中的项目提供服务
