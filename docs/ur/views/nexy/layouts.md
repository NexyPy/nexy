# layout.nexy

سرور موڈ (`useCSR = False`) کی ترتیب فائل۔ جڑ HTML دستاویز کا مالک ہے۔

## روٹ لے آؤٹ

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`، `<html>`، `<head>` اور `<body>` یہاں رہتے ہیں اور کہیں نہیں۔
- `<Vite />` کلائنٹ کے اسکرپٹس اور اسٹائل کو ایک بار انجیکشن کرتا ہے، `<head>` میں۔
- `{{ children | safe }}` وہ جگہ ہے جہاں صفحہ، یا اگلا نیسٹڈ لے آؤٹ، رینڈر ہوتا ہے۔

## نیسٹڈ لے آؤٹ

ایک ذیلی ڈائرکٹری میں ایک `layout.nexy` لپیٹ دیتا ہے جو ذیلی درخت کو اپنے والدین کے اندر پیش کرتا ہے۔ یہ دستاویز کے ٹیگز کو نہیں دہراتا ہے:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` `layout.nexy > blog/layout.nexy > page` کے طور پر پیش کرتا ہے۔

## اجزاء اور جزائر

ایک لے آؤٹ `.nexy` اجزاء (ایک ہیڈر، ایک فوٹر) اور کلائنٹ کے اجزاء درآمد کر سکتا ہے۔ کسی لے آؤٹ میں کلائنٹ کا جزو کسی دوسرے کی طرح ایک [جزیرہ](../../rendering/islands.md) ہوتا ہے:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## لے آؤٹ کے بغیر

`layout.nexy` کے بغیر ایک پروجیکٹ اب بھی ایک درست دستاویز کے ساتھ جواب دیتا ہے: Nexy `<!DOCTYPE html>`، ویو پورٹ میٹا اور Vite ٹیگز کے ساتھ کم سے کم شیل پر واپس آتا ہے۔ جیسے ہی آپ کو عنوان، فونٹس یا نیویگیشن کی ضرورت ہو لے آؤٹ شامل کریں۔

## ماڈیولر راؤٹر میں

کنٹرولرز اپنے خیالات کا انتخاب کرتے ہیں، اس لیے وہ ترتیب خود ترتیب دیتے ہیں:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## جو یہ نہیں کر سکتا

- یہ `layout.tsx`، `layout.vue` یا `layout.svelte` کے ساتھ ایک ساتھ نہیں رہ سکتا: سرور موڈ پروجیکٹ کے پاس کوئی کلائنٹ روٹس ([موڈز](../../routing/fbr/modes.md)) نہیں ہوتے ہیں۔
- یہ کلائنٹ پر نہیں چلتا ہے: تعامل کے لیے جزیرے کا استعمال کریں۔

## اگلے اقدامات

- [لے آؤٹ](../../routing/fbr/layouts/README.md)
- [وراثت](../../routing/fbr/inheritance.md)
- [.nexy فائلیں](README.md)
