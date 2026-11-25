# 页面转换如何工作？

Nexy 使用浏览器的视图转换 API 进行客户端导航，因此受支持的浏览器会以动画方式进行页面交换，除非访问者更喜欢减少运动。

## 当转换运行时

第一个文档是正常的服务器响应，没有转换。从那时起，客户端路由器处理的每个导航都会交换 `document.startViewTransition()` 内的页面：指向客户端路由的链接、`router.push()` 或 `router.replace()` 以及后退和前进按钮。路由器首先渲染下一个页面及其布局，然后移动 URL，以便新页面在显示之前准备就绪。

React、Preact、Solid、Vue 和 Svelte 共享同一路由器，因此所有五个适配器的行为都是相同的。没有启用转换的设置。

## 当它回落时

- 没有 `startViewTransition()` 的浏览器直接渲染页面。
- 使用 `prefers-reduced-motion: reduce`，路由器直接渲染页面。
- 较新的导航跳过的转换不会记录错误：页面仍然正确。

无论是否有转换，URL、历史记录、滚动位置和 `nexy:navigated` 事件的行为方式都相同。

## 设计过渡效果

Nexy 不提供动画 CSS。浏览器应用其默认交叉淡入淡出，您可以在自己的样式表中替换它：

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## 后续步骤

- [链接和导航](linking-and-navigating.md)
- [挂钩](hooks.md)
