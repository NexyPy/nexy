# أنشئ تطبيق ملاحظات باستخدام Nexy، الجزء 2: الصفحات والتخطيطات

يضيف الجزء الثاني الصفحة التي تسرد الملاحظات، ويوضح كيفية تغليف التخطيط لها في مستند HTML.

**قبل البدء:** مشروع [الجزء 1](create-the-project.md)، مع تشغيل `nexy dev`.

## أضف صفحة الملاحظات

<!-- router:fbr,custom -->
الصفحة عبارة عن ملف ضمن `src/routes/`، ومسارها هو عنوان URL الخاص بها. إنشاء صفحة الملاحظات:

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` الإجابات `/notes`.
<!-- /router -->

<!-- router:modular -->
تجيب وحدة التحكم على عنوان URL وترجع طريقة عرض. قم بإعطاء الملاحظات مجلدًا خاصًا بها، مع عرض:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

ووحدة التحكم التي تعرضها في `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

تجيب وحدة التحكم فقط عندما تسردها الوحدة النمطية. أضفه إلى الوحدة الجذرية:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

فتح <http://localhost:3000/notes>: يجب أن تشاهد رصاصتين. الجزء الذي بين السطرين `---` هو Python، يتم تشغيله على الخادم؛ والباقي هو HTML مع علامات Jinja2 مثل `{% for %}` و `{{ note }}`.

## تغيير التخطيط

<!-- router:fbr,custom -->
`src/routes/layout.nexy` يملك مستند HTML: `<html>`، `<head>` و `<body>`. Nexy يغلف كل صفحة فيه، حيث يكتب `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` يمتلك مستند HTML: `<html>`، `<head>` و `<body>`. تقوم وحدة التحكم بتغليف طريقة العرض الخاصة بها عن طريق تمرير العرض كـ `children`.
<!-- /router -->

افتح التخطيط وقم بتغيير السطر `<title>Nexy App</title>` إلى:

```html
<title>Notes</title>
```

حفظ: أصبحت علامة تبويب المتصفح تقرأ الآن *ملاحظات* في كل صفحة.

## امنح مساحة الصفحات أسفل الرأس

تم إصلاح رأس التخطيط: فهو يظل في أعلى النافذة، فوق الصفحة. تحدد صفحات البداية مساحة خاصة بها أسفلها؛ وتشترك صفحات تطبيق الملاحظات في فئة واحدة لذلك، `app-page`، والتي تضع كل صفحة من صفحات البرنامج التعليمي حول محتواها. قم بإضافته في نهاية `src/globale.css`، ورقة الأنماط التي يتم تحميلها بالفعل في كل صفحة:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind، الذي يستخدمه المبتدئ، يزيل حدود حقول النموذج: هذه القواعد تعيدها، بحيث يمكن رؤية أشكال الأجزاء التالية.

## ما تعلمته

<!-- router:fbr,custom -->
- الملف `.nexy` ضمن `src/routes/` عبارة عن صفحة؛ المجلد والاسم هما عنوان URL الخاص به.
- يقوم الجذر `layout.nexy` بتغليف كل صفحة في مستند HTML.
<!-- /router -->
<!-- router:modular -->
- تجيب وحدة التحكم على عنوان URL وتقدم عرض `.nexy` باستخدام `useViews`؛ وحدة تسرد ذلك.
- التخطيط هو عرض أيضًا: يقوم جهاز التحكم بتمرير عرض الصفحة إليه كـ `children`.
<!-- /router -->
- ملف `.nexy` هو Python بين `---`، ثم HTML مع Jinja2.
- `src/globale.css` يحمل الأنماط التي تشاركها كل صفحة، مثل `app-page`.

## الخطوات التالية

- [الجزء 3: المسارات الديناميكية وواجهة برمجة التطبيقات](dynamic-routes.md)
- [ملفات .nexy](../views/nexy/README.md): الدعائم والمكونات والأنماط
