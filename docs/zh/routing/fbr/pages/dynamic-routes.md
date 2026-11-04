# 动态路线

写在方括号中的路径段匹配任何值并将其传递给页面或处理程序。

## 动态片段

`blog/[slug].nexy`服务`/blog/{slug}`。在页面中，将段声明为属性；在Python中
handler，将其作为参数。

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## 类型化段

注释决定类型。

| 其中 | 转换 |
|---|---|
| `.py` 处理程序 | 任何 FastAPI 类型注释 (`int`、`UUID`、`Enum`...) |
| `.nexy`页| `int`和`float`被转换；其他一切都保持字符串 |

与注释不匹配的值是**未找到**：`/api/users/abc`答案`404`，因为
动态路由捕获任何 URL，并且无法转换的 URL 根本不存在。参见
[验证和错误](../handlers/validation-and-errors.md)。

## 包罗万象的片段

`docs/[...path].nexy`服务`/docs/{path:path}`。剩余的段作为一串到达，
包括斜线。

```nexy filename="src/routes/docs/[...路径].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` 给出 `path == "a/b/c"`。

## 路由组

括号中的目录用于组织文件，但不会出现在 URL 中。它还参加
[继承](../inheritance.md)：它的`layout.*`和`dependencies.py`适用于里面的内容。

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

使用组为不同的部分提供不同的布局，而无需更改其 URL。

## 优先

静态路由胜过动态路由，动态路由胜过包罗万象：
`/blog/new` 匹配 `blog/[slug].nexy` 之前的 `blog/new.nexy`。

## 每个 URL 一个文件

解析为同一 URL 的两个文件都会注册。不要将 `blog.nexy` 放在旁边
`blog/index.nexy`，或将 `index.nexy` 和 `index.py` 混合使用同一路径。

## 后续步骤

- [页数](README.md)
- [错误页面](../errors/README.md)
- [文件约定](../../../reference/file-conventions.md)