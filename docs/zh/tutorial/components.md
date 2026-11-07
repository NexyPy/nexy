# 使用 Nexy 构建笔记应用程序，第 4 部分：组件

第 4 部分将每个注释转变为可重用组件，即一个可像 Python 名称一样导入并像 HTML 标签一样使用的 `.nexy` 文件。

**开始之前：**[第 3 部分](dynamic-routes.md)的应用程序。

## 编写组件

组件是路由之外的 `.nexy` 文件。它的 props 用 `prop[...]` 声明，调用者将它们作为属性传递：

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

`<style>` 块随使用该卡的每个页面一起发送。它没有作用域：`.note` 是整个页面的一个类，因此请给出仅它使用的组件名称的类。

## 在列表中使用它

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` 是第 1 部分的导入别名：它指向 `src/`。文件名是组件名称，采用 PascalCase：`NoteCard.nexy` 导出 `NoteCard`。

打开 <http://localhost:3000/notes>：每个音符现在都是一张卡片。

## 你学到了什么

- 路由之外的 `.nexy` 文件是一个组件；它的 `prop[...]` 是它的属性。
- `from "@/components/x.nexy" import X` 导入它； `<X />` 渲染它。
- `<style>` 块没有作用域：在其后命名组件的类。

## 后续步骤

- [第 5 部分：将注释存储在 SQLite](store-the-notes.md) 中
- [组件](../views/nexy/components.md)：`Image`、`Link` 和内置助手
