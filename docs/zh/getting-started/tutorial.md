# Nexy 教程：逐步构建笔记应用程序

Nexy 教程从一个空文件夹构建一个笔记应用程序到生产版本，一次一个部分，每个部分都以一个运行的应用程序结束。

新来内克西？ [快速启动](quick-start.md) 显示它在三分钟内运行；回到这里了解它是如何工作的。

## 本教程如何运作

- **一个不断增长的应用程序。** 每个部分都为之前部分的笔记应用程序添加了一项功能。
- **您的路由器。** 这些部件遵循在菜单顶部选择的路由器：基于文件、模块化或自定义。切换到那里，各个部分的文件都会随之改变。
- **运行的代码。** 每个上面有名称的文件都是一个完整的文件，测试套件会在新项目上按顺序重播各个部分：您复制的就是运行的。
- **停在任何地方。** 每个部分需要 10 到 20 分钟，并以在浏览器中检查的内容结束。

## 零件

### 第一单元：基础知识

| 部分 | 您添加的内容 | 你学到了什么 |
|---|---|---|
| [1.创建项目](../tutorial/create-the-project.md) | 一个运行的项目 | `nexy new`，`nexy dev` |
| [2. 页面和布局](../tutorial/pages-and-layouts.md) | 注释页 | 页面、视图、布局 |
| [3.动态路由和API](../tutorial/dynamic-routes.md) | `/notes/1` 和 `/api/notes` | URL 段、JSON 路由、`notFound` |
| [4. 组件](../tutorial/components.md) | 每张笔记一张卡 | `.nexy` 组件及其道具 |

### 第二单元：数据

| 部分 | 您添加的内容 | 你学到了什么 |
|---|---|---|
| [5. 将笔记存储在 SQLite](../tutorial/store-the-notes.md) 中 | 模型、迁移、种子 | SQLModel，`nx migrate` |
| [6. 从表单创建注释](../tutorial/create-a-note.md) | 保存注释的表单 | 没有 JavaScript 的动作、形式 |
| [7. 显示验证错误](../tutorial/validation-errors.md) | 表格上方的消息 | 操作中的规则，`303`，`useSearchParams` |
| [8.编辑和删除注释](../tutorial/edit-and-delete.md) | 注释的形式 | 每页多个操作，隐藏字段 |
| [9. 对笔记进行分页](../tutorial/paginate-the-notes.md) | 每页五个注释 | `offset` 和 `limit`，页面之间的链接 |

### 第三单元：用户

| 部分 | 您添加的内容 | 你学到了什么 |
|---|---|---|
| [10. 创建帐户并登录](../tutorial/accounts.md) | 注册、登录、退出 | 会话、密码散列 |
| [11.给每个用户自己的注释](../tutorial/own-notes.md) | 属于用户的注释 | 外键，`redirect`，`401` |
| [12. 通过电子邮件重置忘记的密码](../tutorial/password-reset.md) | 通过电子邮件发送的重置链接 | `smtplib`，过期的签名令牌 |

### 第四单元：互动性

| 部分 | 您添加的内容 | 你学到了什么 |
|---|---|---|
| [13. 键入时搜索笔记](../tutorial/search-the-notes.md) | 当您键入内容时会进行过滤的搜索框 | React 岛屿，来自 Python 的道具 |
| [14. 勾选注释而不重新加载页面](../tutorial/tick-a-note.md) | 每个笔记上都有一个“完成”按钮 | 渐进增强，针对表单和 `fetch` 的一个操作 |

### 接下来

| 单位 | 应用程序获得什么 |
|---|---|
| 5. 超出要求 | 通过电子邮件在后台共享的笔记、每日摘要、实时更新 |
| 6. 船舶 | 测试、错误页面和日志、安全标头、Docker 构建 |

## 后续步骤

- [第 1 部分：创建项目](../tutorial/create-the-project.md)
- [核心概念](core-concepts.md)：教程使用的词语
