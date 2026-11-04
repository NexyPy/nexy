# 继承

`src/routes/` 中的几个文件适用于其目录下的所有内容。他们都解决相同的问题
way：Nexy 从路线目录开始，一直走到 `src/routes/`。

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| 文件 | 规则 |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | 从根到页面的每个布局都会包裹它，**最外面的第一个** |
| `middleware.py` | 从根到路由的每个文件都包装请求，**最外面的第一个**，在依赖项之前 |
| `dependencies.py` | 从根到路由的每个文件都运行，**最外面的第一个**，然后是处理程序自己的守卫|
| `notfound.nexy`、`errors.nexy` | **最近的**获胜，每个状态代码|

对于上面的页面，布局嵌套为
`root layout > (shop) layout > cart layout > page`，并且依赖项运行为
`root > (shop) > cart > handler guards`。

## 为什么最外面的第一个

外部布局绘制框架，外部依赖关系决定谁可以进来。把它们
首先意味着内部目录可以依赖它们：需要身份验证的目录在
读取用户的处理程序。

## 布局

文件夹族堆栈的所有布局文件：请参阅[布局](layouts/README.md)。不同的家庭都会这样做
不混合： `layout.vue` 永远不会包装 `.tsx` 页面，并且项目具有 `layout.nexy` 或客户端
布局，不能同时使用两者 ([modes](modes.md))。

## 中间件文件

请参阅[中间件文件](middleware/README.md)：它们在依赖项之前运行并且可以回答
没有到达路线。

## 依赖关系

有关处理程序文件中的顺序，请参阅[依赖项](dependencies/README.md)，包括`@UseGuard`
和`@Middleware`。

## 错误页面

`notfound.nexy` 和 `errors.nexy` 在路由根目录安装一次；子目录中的副本
优化该前缀的页面。请参阅[错误页面](errors/README.md)。

## 后续步骤

- [布局](layouts/README.md)
- [依赖项](dependencies/README.md)
- [错误页面](errors/README.md)