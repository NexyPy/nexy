# .nexy 文件

`.nexy` 文件是一个组件：Python 在顶部，HTML 在中间，CSS 在底部。

**开始之前：** 由[快速启动](../../getting-started/quick-start.md)创建的项目。 `.nexy` 文件不需要构建配置：`nx dev` 在保存时对其进行编译。

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/blog/post_view.nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

控制器从其路径传递 `slug`：

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```
<!-- /router -->

## 前题

两条 `---` 行之间的所有内容都是 Python。编译组件时会解析导入；其余的针对每个请求运行，因此它可以读取请求状态。

| 什么 | 示例 |
|---|---|
| 导入模块 | `import json`，`from datetime import datetime` |
| 导入组件 | `from "@/components/card.nexy" import Card` |
| 申报财产 | `title: prop[str] = "Default"` |
| 计算一个值 | `year = datetime.now().year` |
| 阅读请求 | `pathname = usePathname()` |
| 缓存页面 (ISR) | `revalidate = 60` |

## 属性

属性是组件的 API。 `prop[type]` 声明类型，`= value` 给出默认值。没有默认值的属性必须由父级传递。

以别名开头的导入通过 `useAliases` 解析。设置 `nx new` 将映射 `@` 写入 `src`，这使得 `@/components/card.nexy` 意味着 `src/components/card.nexy`。

## 模板

frontmatter 下面是带有 Jinja2 的 HTML。来自 frontmatter 的变量和属性都在范围内。

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

自动转义为 **off**：模板是项目自己的 HTML，因此 `{{ value }}` 按编写插入。使用 `{{ value | e }}` 自己逃避不受信任的值。 `| safe` 因此没有任何改变。

> [!NOTE]
> 将包含 `{{` 或 `{%` 的 JavaScript 包装在 `{% raw %}...{% endraw %}` 中。 Vue 和 Svelte 等框架使用相同的大括号。

## 组件

任何名称以大写字母开头的导入的可调用对象都可以用作标签。编译器将其重写为 Jinja 调用：属性成为关键字参数。

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

最后一行正是 `{{ Audio("/theme.mp3", controls=True) }}`。这两种语法对于内置的 `Image`、`Link`、`Audio` 和 `Video` 帮助器都有效 - 请参阅 [组件](components.md#two-syntaxes-one-function)。

子组件通过子组件内的 `<Slot />`（大写 S）以及布局内的 `{{ children }}` 进行渲染。

在属性 `<Icon path="{{ icon }}" size="{{ size }}" />` 内传递带有 Jinja 的计算值。诸如 `path=icon` 之类的裸名称是文本 `icon`，而不是变量。要为组件提供 CSS 类，请声明 `class_name` 属性：`class` 是 Python 关键字。

> [!NOTE]
> 辅助标签总是自动关闭的。将内容传递给 `Link` 会通过其 `children` 参数 (`<Link href="/about" children="About" />`)，而不是通过元素内容。

## 风格

`<style>` 块与声明它们的页面一起发出。它们没有作用域：两个组件中使用的类名是一个类。为您的类添加前缀或命名空间。

## 节省时间的规则

- 每个文件一个组件。文件名是组件名称，采用 PascalCase (`CopyChip.nexy`)。 `.nexy` 组件作为 Python 模块导入：名称中的连字符 (`copy-chip.nexy`) 无法编译。
- 在使用 props 之前声明它们：未声明的变量呈现为空字符串，因为 Jinja2 的 undefined 在这里是沉默的。
- 将副作用保留在函数内部 - frontmatter 在每次请求时都会再次运行。

## 后续步骤

- [Markdown 和 MDX](markdown.md)：内容页
- [ISR](../../rendering/isr.md)：每个路径缓存一个页面
- [CSR](../../rendering/csr.md)：客户端渲染
