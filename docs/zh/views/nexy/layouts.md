# 布局.nexy

服务器模式的布局文件(`useCSR = False`)。根目录拥有 HTML 文档。

## 根布局

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`、`<html>`、`<head>` 和 `<body>` 住在这里，没有其他地方。
- `<Vite />` 在 `<head>` 中注入一次客户端脚本和样式。
- `{{ children | safe }}` 是页面或下一个嵌套布局的呈现位置。

## 嵌套布局

子目录中的 `layout.nexy` 包装该子树并在其父级内部呈现。它不重复文档标签：

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` 呈现为 `layout.nexy > blog/layout.nexy > page`。

## 组件和岛屿

布局可以导入 `.nexy` 组件（页眉、页脚）和客户端组件。布局中的客户端组件与其他组件一样是一个 [island](../../rendering/islands.md)：

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## 没有布局

没有 `layout.nexy` 的项目仍然会使用有效文档进行回答：Nexy 回退到带有 `<!DOCTYPE html>`、视口元和 Vite 标签的最小 shell。当您需要标题、字体或导航时，请立即添加布局。

## 在模块化路由器中

控制器选择他们的视图，因此他们自己组成布局：

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## 它不能做什么

- 它不能与 `layout.tsx`、`layout.vue` 或 `layout.svelte` 共存：服务器模式项目没有客户端路由 ([modes](../../routing/fbr/modes.md))。
- 它不在客户端上运行：使用孤岛进行交互。

## 后续步骤

- [布局](../../routing/fbr/layouts/README.md)
- [继承](../../routing/fbr/inheritance.md)
- [.nexy 文件](README.md)
