# 测试

`nx test` 使用 pytest 运行服务器测试，并在您要求时使用 vitest 进行客户端测试。

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## 运行什么

| 部分 | 命令 | 条件 |
|---|---|---|
| 服务器 | `pytest` | 如果存在，则在 `tests/` 上运行，否则在项目根目录上运行；未安装 pytest 时跳过并出现警告 |
| 客户 | `npx vitest run` | 仅与 `--client` 一起，并且仅当 `vitest.config.ts` 存在或 `vitest` 出现在 `package.json` 中时 |

没有内置的端到端运行器。使用 `TestClient` 驱动服务器并自行添加 Playwright 或 Cypress 以实现浏览器行为。

## 测试服务器

测试客户端在进程中与 ASGI 应用程序对话：无需启动服务器，无需选择端口。

```python filename="测试/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` 是组装的应用程序，在第一次读取时构建。它从工作目录读取 `nexyconfig.py`，因此从项目根目录运行 pytest。

当测试更改配置或路由时，构建一个新的应用程序，而不是重用模块级应用程序：

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` 重新组装路由、中间件、会话和翻译，因此每次调用都从项目目录的当前状态开始。

## 断言什么

页面返回 HTML。断言状态，然后断言您关心的内容：

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

API 处理程序返回 JSON。验证失败是 `422`，丢失的路由是 `404`，当该文件存在时，由 `notfound.nexy` 应答：

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

对于操作，直接测试该函数 - 它是一个普通函数 - 并通过从公开它的页面读取其生成的路径来测试 HTTP 端点：

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

使用 JSON 的调用会返回结果，而 `422` 会返回无效字段。

> [!NOTE]
> 操作路径是特定于项目并生成的。切勿在测试中对 `/_nx_<hash>` 进行硬编码。

## 测试 `.nexy` 组件

`nexy.testing.render` 使用它导入的组件编译一个组件，并返回其 HTML。 props 是关键字参数， `children=` 填充该槽：

```python filename="测试/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

从项目根目录运行 pytest：编译后的文件转到 `__nexy__/`，与 `nx dev` 一样。读取请求 (`usePathname`, `useSession`) 的组件需要使用 `TestClient` 进行页面测试。

## 测试客户端

`nx test --client` 需要您自己的 vitest 设置。最小组件测试：

```tsx filename="src/组件/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` 和测试库是项目依赖项：`nexy new` 不安装测试堆栈。添加 `vitest.config.ts` 和您需要的环境（组件的 jsdom 或 happy-dom）。

## 持续集成

对于项目管道来说，两个命令就足够了：

```bash
nx build
nx test
```

`nx build` 因编译错误而失败； `nx test` 在断言失败时失败并以非零值退出。 `nx check` 将 mypy 和 `tsc` 添加到运行中。

Nexy 本身的工作使用不同的命令：请参阅 [CONTRIBUTING](../../CONTRIBUTING.md)。

## 后续步骤

- [CLI](../reference/cli.md)：`nx test` 的每个标志
- [API](../routing/fbr/handlers/README.md)：端点返回什么
- [部署](../deployment/README.md)：在 CI 中测试之前构建
