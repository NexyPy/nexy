# 页数

页面文件返回 HTML。您使用的文件类型会改变其生成方式：请参阅
[观点](../../../views/README.md)。本节涵盖适用于每个页面的路由规则
格式。

| 页 | 涵盖内容 |
|---|---|
| [动态路线](dynamic-routes.md) | `[slug]`、`[...path]`、路线组、类型化段 |
| [错误页面](../errors/README.md) | `notfound.nexy`、`errors.nexy`、API 客户端的 JSON |
| [布局](../layouts/README.md) | 每种布局文件类型一页 |
| [继承](../inheritance.md) |布局和依赖关系如何堆叠|

## 最小页面

```nexy filename="src/routes/about.nexy"
---
title: prop[str] = "About"
---
<h1>{{ title }}</h1>
```

供应地点为`/about`。 `---` 行之间的 frontmatter 是 Python；下面的标记是
金贾2。请参阅[.nexy 文件](../../../views/nexy/README.md)。

## 页面格式

| 模式 | 文件 | 产生 |
|---|---|---|
| 服务器 | `.nexy` | 服务器从 Python 和 Jinja2 渲染 HTML |
|服务器|`.md`，`.mdx`|内容页|
| 客户端 | `.tsx`、`.jsx`、`.vue`、`.svelte` | 框架组件，在浏览器中呈现和导航 |

这两种模式不能在一个项目中混合使用。请参阅[服务器模式和客户端模式](../modes.md)。
客户端组件仍然可以出现在服务器模式下，如 [islands](../../../rendering/islands.md)
在 `.nexy` 页面内。

## 增量缓存

将 `revalidate = 60` 添加到 `.nexy` 页面，以使用 stale-while-revalidate 对其进行缓存。参见
[ISR](../../../rendering/isr.md)。

## 读取请求

页面通过钩子读取路径、查询字符串、cookie 和会话。参见
[钩子](../navigation/hooks.md)。

## 后续步骤

- [动态路线](dynamic-routes.md)
- [错误页面](../errors/README.md)
- [模块化路由](../../modular/README.md)：控制器而不是文件