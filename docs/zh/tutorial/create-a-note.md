# 使用 Nexy 构建笔记应用程序，第 6 部分：从表单创建笔记

第 6 部分在列表上方添加了一个表单：它发送到标记为 `@Action` 的 Python 函数，该函数保存注释，并且访问者返回到列表，其中包含新注释。

**开始之前：** [第 5 部分](store-the-notes.md) 的应用程序及其数据库。

## 保存笔记

添加一个函数，用于保存一个注释并将其返回，位于读取它们的两个注释旁边：

<!-- router:fbr,custom -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.configs.db import engine
from src.models.note_model import Note


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/notes.py"
from sqlmodel import Session, select

from src.apps.notes.note_model import Note
from src.configs.db import engine


def all_notes() -> list[Note]:
    with Session(engine) as session:
        return list(session.exec(select(Note).order_by(Note.id)))


def find(note_id: int) -> Note | None:
    with Session(engine) as session:
        return session.get(Note, note_id)


def add_note(text: str) -> Note:
    note = Note(text=text)
    with Session(engine) as session:
        session.add(note)
        session.commit()
        session.refresh(note)
    return note
```
<!-- /router -->

## 把它变成一个行动

Action 是浏览器可以调用的 Python 函数。 `@Action` 将其用作 `POST`，根据类型提示检查输入，然后运行它：

```python filename="src/actions/notes.py"
from nexy.decorators import Action
from src.notes import add_note


@Action
async def create_note(text: str) -> int:
    return add_note(text).id
```

启动时，Nexy 导入 `src/` 的每个模块并为其找到的操作提供服务：对于任何路由器都没有需要声明的路由。 `src/actions/` 是本教程保存它们的地方。

## 将表格发布到它

`.nexy` 模板知道每个 Action 的路径为 `__actions_path["name"]`。那里会发布一个纯 HTML 表单，因此该页面可以在加载任何脚本之前运行：

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
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
from src.notes import all_notes

notes = all_notes()
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

输入被命名为 `text`，就像 `create_note` 的参数一样：这就是字段到达它的方式。

## 将注释显示为文本，而不是 HTML

从现在开始，访客输入的内容就是注释。 `.nexy` 模板按原样写入值，因此注释 `<script>…</script>` 将在打开列表的每个人的浏览器中运行。 `| e` 对其进行转义：`<` 变为 `&lt;`，并且注释显示为文本。

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text | e }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/[id].nexy"
---
from nexy import notFound
from src.notes import find

id: prop[int]
note = find(id)
if note is None:
    notFound()
---
<section class="app-page">
  <h1>{{ note.text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/note_view.nexy"
---
text: prop[str]
---
<section class="app-page">
  <h1>{{ text | e }}</h1>
  <a href="/notes">All notes</a>
</section>
```
<!-- /router -->

转义来自访问者或数据库的每个值。 `| safe` 则相反：将其保留为您自己编写的 HTML。

## 尝试一下

输入*阅读文档*并按 **添加**。该操作保存注释，然后将 `303` 回复回 `/notes`，浏览器再次显示列表，第三个注释位于底部。

## 你学到了什么

- `@Action` 将 Python 函数转换为 `POST` 端点，其类型提示作为输入。
- 表单通过 `__actions_path["name"]` 向其发送，不带 JavaScript，并返回 `303`。
- 表单的字段名称是操作的参数名称。
- `| e` 显示访问者输入的文本内容：转义所有并非来自您的值。

## 后续步骤

- [第 7 部分：显示验证错误](validation-errors.md)
- [操作](../guides/actions.md)：来自浏览器的键入调用、错误和安全性
