# 使用 Nexy 构建笔记应用程序，第 13 部分：在键入时搜索笔记

第 13 部分在注释上方添加了一个搜索框：React 岛会在浏览器中过滤用户每次按键时的每个注释，而不向服务器发出请求。

**开始之前：**[第 12 部分](password-reset.md)的应用程序。该项目是在 [第 1 部分 ](create-the-project.md) 中使用 React 创建的，因此 React 已安装。

## 一座岛屿，以及为什么在这里

页面的其余部分仍然是由服务器呈现的 HTML：列表、表单、注释页面。只有搜索框需要浏览器，所以只有搜索框是 React。这是一个“孤岛”：服务器页面内的一个客户端组件，可以自行交互。

## 搜索组件

```tsx filename="src/components/NoteSearch.tsx"
import { useState } from "react"

type Note = { id: number; text: string }

export default function NoteSearch({ notes }: { notes: Note[] }) {
  const [query, setQuery] = useState("")
  const words = query.trim().toLowerCase()
  const found = words ? notes.filter((note) => note.text.toLowerCase().includes(words)) : []
  return (
    <section className="note-search" aria-label="Search the notes">
      <label>
        Search
        <input type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <div aria-live="polite">
        {words && found.length === 0 && <p>No note matches “{query}”.</p>}
        {found.length > 0 && (
          <ul>
            {found.map((note) => (
              <li key={note.id}>
                <a href={`/notes/${note.id}`}>{note.text}</a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
```

React 将 `{note.text}` 作为文本写入：注释 `<b>x</b>` 显示其括号，无需添加 `| e`。

`found` 仅在输入内容后进行计算，这对于构建很重要：`nx build` 将每个岛渲染为 HTML 一次，并使用占位符而不是其 props。在第一次渲染期间读取 list prop 的组件会获取占位符而不是列表，并且不传送 HTML。仅在按键后才读取 `notes`，因此构建会呈现其搜索框，并且页面会在任何 JavaScript 运行之前显示它。

`aria-live="polite"` 使屏幕阅读器在结果发生变化时读取结果，而不会中断。

## 将岛屿放在页面上

该页面将注释作为道具传递：字典列表，Nexy 将其转换为浏览器的 JSON。每个笔记都会进入，而不仅仅是当前页面的五个笔记，因此搜索涵盖了所有笔记：

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from "@/components/NoteSearch.tsx" import NoteSearch
from nexy import useSearchParams
from src.guard import signed_in_user
from src.notes import all_notes, notes_page

user_id = signed_in_user()
params = useSearchParams()
error = params.get("error", "")
asked = params.get("page", "1")
number = max(int(asked), 1) if asked.isdigit() else 1
found = notes_page(user_id, number)
notes = found[0]
more = found[1]
searchable = [{"id": note.id, "text": note.text} for note in all_notes(user_id)]
---
<section class="app-page">
  <h1>Notes</h1>

  <form method="post" action="{{ __actions_path['sign_out'] }}">
    <button type="submit">Sign out</button>
  </form>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <NoteSearch notes="{{ searchable }}" directive="client:idle" />

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% else %}
  <p>No notes yet: write the first one above.</p>
  {% endfor %}

  <nav class="note-pages" aria-label="Pages of notes">
    {% if number > 1 %}<a href="/notes?page={{ number - 1 }}" rel="prev">Newer</a>{% endif %}
    {% if more %}<a href="/notes?page={{ number + 1 }}" rel="next">Older</a>{% endif %}
  </nav>
</section>
```
<!-- /router -->

`from "@/components/NoteSearch.tsx" import NoteSearch` 将 React 组件导入 `.nexy` 页面；标签将其属性作为 props 传递。 `notes="{{ searchable }}"` 传递 Python 列表本身，而不是字符串。 `directive="client:idle"` 一旦浏览器没有什么更紧急的事情要做，岛就会变得互动。

打开 <http://localhost:3000/notes> 并输入注释的几个字母：每次按键时，匹配的注释都会显示在框下方。清除盒子，结果就会消失。

> [!NOTE]
> 岛屿的 props 以 JSON 形式在页面中传播。发送每张纸条都适合其中的数百人；对于数千个，请使用查询和 `LIKE` 过滤器在服务器上进行搜索。

## 你学到了什么

- 岛是服务器页面内的客户端组件：此处，React 仅用于搜索框。
- `.nexy` 页面通过路径导入它，并将 Python 值作为 props 传递，序列化为 JSON。
- 该构建会渲染一个岛一次，并为其 props 提供占位符：在第一次渲染后读取列表 props，并且该岛会附带 HTML。

## 后续步骤

- [第 14 部分：勾选注释而不重新加载页面](tick-a-note.md)
- [岛屿和水化](../rendering/islands.md)：指令、道具和限制
