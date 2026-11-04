# 页面元数据

页面命名其标题和头标签，根布局将它们写入一次。

## 在页面中说出来

对于永远不会改变的页面，在 frontmatter 的顶部写一个文字：

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

当标题取决于数据时，请改为调用 `setMetadata`：

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

模块化控制器在返回 `useViews(...)` 之前调用 `setMetadata(...)`。

## 写在布局中

根布局拥有 `<head>`。一行写着页面所说的内容，转义了：

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

页面在其布局之前运行，因此布局可以找到页面所要求的内容。一个页面说
没有任何东西可以获取您的 `nexyconfig.py` 的 `useTitle`，也没有其他标签。

## 字段

| 字段 | 写为 |
|---|---|
| `title` | `<title>`； `title_template="%s \| My site"` 的标题放在 `%s` | 中
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`，例如 `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | 每个键一个 `<meta property="og:...">`：`{"image": "/cover.png"}` 给出 `og:image` |
| `twitter` | 每个键一个 `<meta name="twitter:...">` |
| `extra` | 属性字典列表，每个 `<meta>`：`[{"name": "theme-color", "content": "#fff"}]` |

稍后的调用会替换一个值； `og`、`twitter` 和 `extra` 添加到现有内容。一个领域
不存在引发 `TypeError`，因此拼写错误不会默默地执行任何操作。

## 默认安全

每个值都是 HTML 转义的，因此从 URL 或数据库构建的标题无法关闭标签
并注入脚本。当布局调用 `html()` 时，值会转义一次：不要转义它
你自己。

## 后续步骤

- [页数](README.md)
- [布局](../layouts/README.md)
- [错误页面](../errors/README.md)