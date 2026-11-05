# 组件

Nexy 导出一小组返回 HTML 字符串的帮助程序。每一个在 `.nexy` 模板中都有两种使用方式：作为 Jinja 调用，或作为 HTML 样式标记。

## 两种语法，一种函数

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

两条线产生相同的标记：

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

编译器将 `<Audio ... />` 重写为 `{{ Audio(...) }}`，因此标记形式不是第二个 API：属性是函数的关键字参数。

## 标签形式规则

| 标签中的 | 变为 |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`，一个真正的布尔值 |
| `width=640` | `width=640`，一个数字 |
| `src="{{ url }}"` | `src=(url)`，在 Jinja | 中评估
| 任何其他 `value` | `"value"`、字符串 |

- 标签必须以大写字母开头，并在 frontmatter 中导入；否则编译器会引发 `Missing Import: <Name> used but not declared.`
- 标签形式是 **自闭合**。 `<Audio src="/a.mp3" />` 和 `{{ Audio("/a.mp3") }}` 是等价的；不支持在辅助标记内写入子项。
- 此处，裸露的 HTML 属性不是布尔值：`controls` 变为 `controls=""`，这是错误的。写 `controls=True`。

> [！注意]
> `class_name` 是 CSS 类的记录关键字。额外的关键字参数成为 HTML 属性，因此 `class="nav"` 也会到达输出。

## 图片

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` 默认情况下使用延迟加载渲染 `<img>`。

## 链接

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` 呈现由客户端路由器处理的 `<a data-nexy-link>`。使用 `prefetch=True`，悬停或触摸链接会通过 `window.__nexy_prefetch`温暖目标。

> [！注意]
> 标签形式将标签视为 `children`，而不是元素内容：`<Link href="/about" children="About" />`。要将标记放入链接内，请使用带有 `children=` 或呈现 `<Slot />` 的 `.nexy` 组件的调用表单。

## 音频和视频

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` 和 `Video(src, width=None, height=None, ...)` 渲染原生玩家。 `sources` 添加 `<source>` 标签，其中包含从每个扩展派生的 MIME 类型。

## 自己写的组件

可重用的 `.nexy` 组件是 `src/components/`: Python 属性下的文件，上面是 HTML，下面是 HTML。它像任何其他 Python 模块一样导入。

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` 没有默认值，因此页面必须通过它； `tone` 回落到 `"neutral"`。标签之间的标记到达 `<Slot />`（大写 S）内部。有关 props、slots 和标签形式的规则，请参阅 [.nexy 文件](README.md#components)。

## 导入客户端组件

从 `.nexy` 文件中，按路径导入框架组件；编译器将其安装在客户端并将属性作为 props 传递：

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` 在 Python 中执行相同的操作：

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

相同的导入语法将 `.json`、`.css` 和图像文件解析为其 URL。

## 模板和 Vite

`Template().render(path, context)` 渲染模板文件（Jinja2 或 Markdown 渲染为 `.md` 路由的 HTML）。 `Template().invalidate(path)` 将其从缓存中删除。

`Vite()` 返回当前模式的客户端标签：开发中的 HMR 脚本、生产中构建的客户端包。 Nexy 为每个页面调用它；你很少直接需要它。

## 尚未实施

`Form` 和 `Script` 是导出的占位符，没有任何行为。不要依赖他们。

## 后续步骤

- [.nexy 文件](README.md)：使用这些助手的位置
- [React](../react/differences.md)：导入 `.tsx` 组件
- [前端](../../guides/frontend.md)：如何捆绑客户端组件
