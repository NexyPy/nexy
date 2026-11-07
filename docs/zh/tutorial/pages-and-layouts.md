# 使用 Nexy 构建笔记应用程序，第 2 部分：页面和布局

第 2 部分添加列出注释的页面，并显示布局如何将其包装在 HTML 文档中。

**开始之前：** [第 1 部分 ](create-the-project.md) 的项目，`nexy dev` 正在运行。

## 添加备注页面

<!-- router:fbr,custom -->
页面是 `src/routes/`下的文件，其路径是其URL。创建笔记页面：

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` 回答 `/notes`。
<!-- /router -->

<!-- router:modular -->
控制器响应 URL 并返回视图。为笔记提供自己的文件夹，并带有视图：

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

以及在 `/notes` 处渲染它的控制器：

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

控制器仅在模块列出后才会应答。将其添加到根模块：

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

打开 <http://localhost:3000/notes>：您应该看到两个子弹。两 `---` 行之间的部分是 Python，在服务器上运行；其余的是带有 Jinja2 标签的 HTML，例如 `{% for %}` 和 `{{ note }}`。

## 更改布局

<!-- router:fbr,custom -->
`src/routes/layout.nexy` 拥有 HTML 文档：`<html>`、`<head>` 和 `<body>`。 Nexy 将每一页都包裹在其中，其中写有 `{{children | safe}}`。
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` 拥有 HTML 文档：`<html>`、`<head>` 和 `<body>`。控制器通过将视图作为 `children` 传递来将其视图包装在其中。
<!-- /router -->

打开布局并将行 `<title>Nexy App</title>` 更改为：

```html
<title>Notes</title>
```

保存：浏览器的选项卡现在在每个页面上显示为“注释”。

## 在标题下方留出页面空间

布局的标题是固定的：它位于窗口顶部、页面上方。入门篇的页面在其下方设置了自己的空间；笔记应用程序的页面共享一个类，`app-page`，教程的每一页都围绕其内容放置。将其添加到 `src/globale.css` 的末尾，每个页面的样式表都已加载：

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

初学者使用的 Tailwind 删除了表单字段的边框：这些规则将它们返回，因此可以看到下一部分的表单。

## 你学到了什么

<!-- router:fbr,custom -->
- `src/routes/` 下的 `.nexy` 文件是一个页面；它的文件夹和名称就是它的 URL。
- 根 `layout.nexy` 包含 HTML 文档中的每个页面。
<!-- /router -->
<!-- router:modular -->
- 控制器响应 URL 并使用 `useViews` 渲染 `.nexy` 视图；一个模块列出了它。
- 布局也是一个视图：控制器将页面视图作为 `children` 传递给它。
<!-- /router -->
- `.nexy` 文件是 `---` 之间的 Python，然后是 HTML 和 Jinja2。
- `src/globale.css` 保存每个页面共享的样式，例如 `app-page`。

## 后续步骤

- [第 3 部分：动态路由和 API](dynamic-routes.md)
- [.nexy 文件](../views/nexy/README.md)：道具、组件和样式
