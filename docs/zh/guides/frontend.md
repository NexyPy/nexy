# 前端

Nexy 不为客户提供自己的组件系统。它建立在 Vite 之上：React、Vue、Svelte、Solid 和 Preact 均受支持，并且普通页面根本无需客户端框架即可工作。

## 启用框架

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` 默认为 `True`；配置框架时将其保持打开状态。

## 路线文件

| 扩展 | 渲染 |
|---|---|
| `.nexy`、`.md` | 由 Nexy 在请求时间 |
| `.mdx`、`.tsx`、`.jsx`、`.vue`、`.svelte` | 由客户端框架提供；在构建时预渲染为 HTML，然后由客户端包接管 |

框架路由是一个普通页面，而不是仅客户端的孤岛：HTML 在包运行之前就存在，因此第一次绘制不会等待 JavaScript。

每个框架设置：[React](../views/react/differences.md)、[Vue](../views/vue/differences.md)、[Svelte](../views/svelte/differences.md)、[Solid](../views/solid/differences.md)、[Preact](../views/preact/differences.md)。

## 发展

`nx dev` 在一个端口上启动一台服务器：

1. 该应用程序会重新编译您更改的路由、服务器和客户端；
2. Vite 在内部端口上运行并为框架模块提供服务；
3. Nexy 通过其自己的来源代理 Vite 的端点。

浏览器只与端口 `3000` 通信。无需打开第二个 URL，也无需配置 CORS。

## 构建

`nx build` 产生：

- 框架路由的预渲染 HTML；
- 客户端捆绑包，其资产位于 `__nexy__/client/` 下；
- 已编译的 Python 路线。

Vite 处理客户端包； SSR HTML 由 esbuild 按文件生成。

> [！注意]
> 服务器渲染失败的路由将被报告为仅客户端路由，而不是整个构建失败。

## 造型

`nexy new` 请求样式模式并为您选择的客户端框架进行设置：Tailwind、UnoCSS 或纯 CSS。设计标记（颜色、字体、深色主题）是脚手架创建的文件 `src/globale.css` 中的 CSS 变量。

| 模式 | 起始页用 | 写入
|---|---|
| 标记中的 Tailwind、UnoCSS | 实用程序类，标记映射到类名 |
| 纯 CSS | 语义类名称和 `src/globale.css` | 中的 CSS

添加页面时请遵循项目的模式：实用程序项目中的实用程序类，纯 CSS 项目中的 CSS。保留实用程序无法在组件的 `<style>` 块中表达的组件 CSS。在服务器项目（`.nexy` 页）中，UnoCSS 读取类的 `.nexy` 文件； Tailwind 自行找到它们。

## 字体、图像、脚本

将静态文件放入 `public/` - 它们在开发和生产中由 `/` 提供。

## 后续步骤

- [Views](../views/README.md)：选择页面格式
- [配置](../reference/config.md)：`useFF`、`useVite`、别名
- [部署](../deployment/README.md)：构建产生什么
