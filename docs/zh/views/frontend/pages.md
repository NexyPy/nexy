# 前端页面

**页面**是Nexy应用程序的基本单位。它是由 `src/routes/` 下的文件定义的 URL 可寻址资源。 

无论使用哪种客户端框架，每个页面都遵循相同的通用生命周期和架构约束。

## 页面生命周期

当用户导航到页面时，Nexy 执行以下步骤：

1.  **路由匹配**：路由器识别URL对应的文件。
2.  **数据获取**：服务器执行页面的逻辑（Python frontmatter 或框架加载器）来获取所需的数据。
3.  **组合**：页面包裹在最接近的`layout.nexy`（或框架布局）中。
4.  **渲染**：结果渲染为 HTML（通过 Jinja2、Markdown 或框架 SSR）。
5.  **Hydration**：如果页面使用客户端框架，浏览器会将交互逻辑附加到静态 HTML。

## 路由和 URL

路由是严格基于文件的。 URL 由 `src/routes/` 下的文件路径减去扩展名确定。

### 动态片段
要创建因参数（例如用户配置文件）而异的路由，请使用方括号：
- `src/routes/user/[id].tsx` → `/user/123`

段 (`123`) 的值可通过 `@nexy/client` 中的 `useParams()` 挂钩提供给页面。

### 路由组
路由器会忽略括号中的文件夹，但允许您出于组织目的或共享布局对文件进行分组：
- `src/routes/(auth)/login.tsx` → `/login`

## 页面元数据
每个页面都可以定义 Nexy 注入到文档 shell 中的元数据（标题、描述、OpenGraph 标签）。在 `.nexy` 文件中，这是在 frontmatter 中完成的；在框架文件中，它是通过 `metadata` 导出提供的。

## 框架实施
上述概念是普遍适用的。要了解如何在您的特定框架中实现页面，请参阅 **Differences** 指南：

- [反应差异](../react/differences.md)
- [Vue 差异](../vue/differences.md)
- [细小的差异](../svelte/differences.md)
- [明显的差异](../solid/differences.md)
- [预差异](../preact/differences.md)