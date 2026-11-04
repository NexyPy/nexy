# 项目结构

Nexy 项目中的每个文件都有一项工作。此页说明了哪个。

## 顶级

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

要选择文件夹，请询问文件是什么：

- **浏览器可以打开的东西** - 路线：`src/routes/`。
- **由多个路线使用的片段** - 组件或模块：`src/components/`、`src/`。
- **文件按原样使用** - `public/`。
- **模块化路由器的控制器** - `src/apps/`。
- **生成** - `__nexy__/`；永远不要编辑它。

> [！警告]
> `src/routes/`被扫描：放置在那里的助手成为一条路线。放置一个不是路线的助手
> 在`src/routes/`之外，或者其名称以`_`开头。

## `src/routes/`

除了下面的保留名称之外，每个文件都成为一条路由。文件路径减去扩展名是
URL - 请参阅[路由](../routing/README.md)。

| 文件 | 角色 |
|---|---|
| `layout.nexy` | 包装兄弟页面和子页面 |
| `errors.nexy` | 目录 | 500 页
| `notfound.nexy` | 目录 | 的 404 页
| `dependencies.py` | 目录 | 的共享 FastAPI 依赖项
| `__init__.py` | Python 包标记 |
| `loading.nexy` | 保留 - 从路由中排除，但它还没有运行时效果 |

每个页面名称也存在于每个框架中。配置 `react()` 后，`layout.jsx` 和 `layout.tsx`
与 `layout.nexy` 完全相同。这些列表内置于 `nexy/core/config.py`
（`LAYOUT_FILE_NAMES`、`ERROR_FILE_NAMES`、`NOTFOUND_FILE_NAMES`、`LOADING_FILE_NAMES`）。

> [！注意]
> `notfound.nexy` 和 `errors.nexy` 仅当副本存在于
> 路由根。然后，子目录中的副本会优化该前缀的页面。

## `src/apps/`

目录 `nexy new` 用于模块化路由器：控制器、模块和提供者寄存器
它们通过来自 `nexy.decorators` 的装饰器进行路由，然后安装聚合 `APIRouter`
与`useRouter`在`nexyconfig.py`中。

一个项目可以拥有两个路由器：`useRouter` 安装模块化路由器，并扫描 `src/routes/`
每当该目录存在时。请参阅[模块化路由](../routing/modular/README.md)。

## `public/`

这里的文件由站点根目录提供：`/favicon.ico`、`/robots.txt`、图像、字体。

## `__nexy__/`

由 `nx build` 生成（以及由 `nx dev` 生成其所需的部分）。它包含：

- 编译的路由模块，作为Python包（`__nexy__/src/routes/...`）；
- 生成的客户端入口点（`main.ts`、`vite.ts`、`*.auto.ts`）；
- `client/` Vite 构建后 - 资产、清单、预渲染 HTML；
- `build-cache.json`。

将整个目录视为一次性目录：删除它，重建它。手动编辑会丢失更改
在下一个版本中。将其添加到`.gitignore`。

## 后续步骤

- [路由](../routing/README.md)：路径如何变成 URL
- [配置](../reference/config.md)：每个项目选项
- [前端](../guides/frontend.md)：Vite、样式和客户端构建