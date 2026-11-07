# Nexy کے ساتھ ایک نوٹس ایپ بنائیں، حصہ 2: صفحات اور لے آؤٹ

حصہ 2 وہ صفحہ شامل کرتا ہے جو نوٹس کی فہرست دیتا ہے، اور دکھاتا ہے کہ لے آؤٹ اسے HTML دستاویز میں کیسے لپیٹتا ہے۔

**شروع کرنے سے پہلے:** [حصہ 1](create-the-project.md) کا پروجیکٹ، `nexy dev` چل رہا ہے۔

## نوٹس کا صفحہ شامل کریں۔

<!-- router:fbr,custom -->
صفحہ `src/routes/` کے تحت ایک فائل ہے، اور اس کا راستہ اس کا URL ہے۔ نوٹس کا صفحہ بنائیں:

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

`notes/index.nexy` جوابات `/notes`۔
<!-- /router -->

<!-- router:modular -->
ایک کنٹرولر URL کا جواب دیتا ہے اور ایک منظر واپس کرتا ہے۔ نوٹوں کو ان کا اپنا فولڈر دیں، ایک نظر کے ساتھ:

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

اور کنٹرولر جو اسے `/notes` پر پیش کرتا ہے:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

ایک کنٹرولر صرف ایک بار جواب دیتا ہے جب ماڈیول اس کی فہرست دیتا ہے۔ اسے روٹ ماڈیول میں شامل کریں:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

کھولیں <http://localhost:3000/notes>: آپ کو دو گولیاں نظر آنی چاہئیں۔ دو `---` لائنوں کے درمیان کا حصہ Python ہے، سرور پر چلائیں؛ باقی HTML ہے جس میں Jinja2 ٹیگ ہیں جیسے `{% for %}` اور `{{ note }}`۔

## لے آؤٹ کو تبدیل کریں۔

<!-- router:fbr,custom -->
`src/routes/layout.nexy` ایچ ٹی ایم ایل دستاویز کا مالک ہے: `<html>`، `<head>` اور `<body>`۔ Nexy اس کے ہر صفحے کو لپیٹتا ہے، جہاں وہ `{{children | safe}}` لکھتا ہے۔
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` ایچ ٹی ایم ایل دستاویز کا مالک ہے: `<html>`، `<head>` اور `<body>`۔ کنٹرولر اپنے نقطہ نظر کو `children` کے طور پر پاس کر کے اس میں لپیٹتا ہے۔
<!-- /router -->

لے آؤٹ کو کھولیں اور لائن `<title>Nexy App</title>` کو اس میں تبدیل کریں:

```html
<title>Notes</title>
```

محفوظ کریں: براؤزر کا ٹیب اب ہر صفحے پر *نوٹس* پڑھتا ہے۔

## ہیڈر کے نیچے صفحات کا کمرہ دیں۔

لے آؤٹ کا ہیڈر طے شدہ ہے: یہ ونڈو کے اوپری حصے میں، صفحہ کے اوپر رہتا ہے۔ سٹارٹر کے صفحات اس کے نیچے اپنی جگہ متعین کرتے ہیں۔ نوٹس ایپ کے صفحات اس کے لیے ایک کلاس کا اشتراک کرتے ہیں، `app-page`، جسے ٹیوٹوریل کا ہر صفحہ اپنے مواد کے ارد گرد رکھتا ہے۔ اسے `src/globale.css` کے آخر میں شامل کریں، اسٹائل شیٹ ہر صفحہ پہلے سے ہی لوڈ ہوتا ہے:

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

Tailwind، جسے سٹارٹر استعمال کرتا ہے، فارم فیلڈز کی سرحدوں کو ہٹاتا ہے: یہ اصول انہیں واپس دیتے ہیں، تاکہ اگلے حصوں کی شکلیں دیکھی جا سکیں۔

## جو آپ نے سیکھا۔

<!-- router:fbr,custom -->
- `src/routes/` کے تحت ایک `.nexy` فائل ایک صفحہ ہے۔ اس کا فولڈر اور نام اس کا URL ہے۔
- جڑ `layout.nexy` ایچ ٹی ایم ایل دستاویز میں ہر صفحے کو لپیٹ دیتی ہے۔
<!-- /router -->
<!-- router:modular -->
- ایک کنٹرولر URL کا جواب دیتا ہے اور `useViews` کے ساتھ `.nexy` منظر پیش کرتا ہے۔ ایک ماڈیول اس کی فہرست دیتا ہے۔
- لے آؤٹ بھی ایک نظارہ ہے: کنٹرولر صفحہ کے منظر کو بطور `children` منتقل کرتا ہے۔
<!-- /router -->
- ایک `.nexy` فائل `---` کے درمیان Python ہے، پھر Jinja2 کے ساتھ HTML۔
- `src/globale.css` ہر صفحہ کا اشتراک کردہ اسٹائل رکھتا ہے، جیسے `app-page`۔

## اگلے اقدامات

- [حصہ 3: متحرک راستے اور ایک API](dynamic-routes.md)
- [.nexy فائلیں](../views/nexy/README.md): پرپس، اجزاء اور انداز
