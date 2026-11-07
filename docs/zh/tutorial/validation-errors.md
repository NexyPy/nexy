# 使用 Nexy 构建笔记应用程序，第 7 部分：显示验证错误

第 7 部分拒绝空白或太长的注释，并说明了为什么在表格上方、同一页上仍然没有 JavaScript。

**开始之前：**[第 6 部分](create-a-note.md)的应用程序。

## 两种错误

操作的类型提示已经拒绝错误的形状：没有 `text` 字段的表单在 `create_note` 运行之前回答 `422`。您可以在操作中编写有关值本身的规则，例如“非空白”。

## 检查Action中的注释

失败会将访问者发送回列表，并在 URL 中注明原因；成功返回到没有它的列表：

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` 告诉浏览器使用 `GET` 加载下一页，因此刷新不会再次发布表单。

## 在表格上方显示原因

`useSearchParams()` 读取当前请求的查询字符串：

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`| e` 转义消息：查询字符串来自访问者，因此它永远不会作为 HTML 写入页面。 `role="alert"` 让屏幕阅读器宣布它。

`required` 和 `maxlength` 让浏览器在大多数错误离开之前停止它们。该操作再次检查：请求不一定来自您的表单。

添加三个空格的注释：列表返回时在表单上方显示“*注释不能为空。*”。

## 你学到了什么

- 类型提示拒绝使用 `422` 的错误形状；有关值的规则放在操作中。
- 一个 Action 可以用 `RedirectResponse` 来回答； `303` 表格后避免第二次发布。
- `useSearchParams()` 读取查询字符串，`| e` 转义访问者发送的内容。

## 后续步骤

- [第8部分：编辑和删除注释](edit-and-delete.md)
- [异常和错误](../reference/exceptions.md)：操作和页面可以回答的每个状态
