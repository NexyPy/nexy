# مناظر

فائل فارمیٹ کو منتخب کرنے سے پہلے، یہ فرق کرنا ضروری ہے کہ Nexy وسائل کو کیسے ہینڈل کرتا ہے اور اسے کیسے پیش کرتا ہے۔

| اصطلاح | تعریف |
|---|---|
| **صفحہ** | ایپلیکیشن کا ایک URL ایڈریس ایبل وسیلہ۔ اس کی تعریف `src/routes/` کے تحت فائل کے ذریعے کی گئی ہے۔ |
| **دیکھیں** | ایک صفحہ کے لیے رسپانس باڈی تیار کرنے کا عمل۔ ایک منظر منطق اور ڈیٹا کو HTML یا JSON میں تبدیل کرتا ہے۔ |
| **اجزاء** | ایک دوبارہ قابل استعمال UI بلڈنگ بلاک جو ایک منظر تحریر کرنے کے لیے استعمال ہوتا ہے۔ اجزاء مقامی Nexy مددگار یا فریم ورک کے لیے مخصوص (React، Vue، وغیرہ) ہو سکتے ہیں۔ |
| **روٹ ہینڈلر** | ایک Python فنکشن جو ایک مخصوص طریقہ (جیسے، `GET`، `POST`) کے لیے HTTP درخواست کو ہینڈل کرتا ہے۔ |
| **اختتامی نقطہ** | یو آر ایل اور ایک HTTP طریقہ کا انوکھا امتزاج جس کا روٹ ہینڈلر جواب دیتا ہے۔ |

**یقین نہیں ہے؟ لکھیں `.nexy` فائل** اسے کسی کلائنٹ کے فریم ورک کی ضرورت نہیں ہے، اور آپ بعد میں جزیرے کے طور پر اس کے اندر React، Vue، Svelte، Solid یا Preact جز شامل کرسکتے ہیں۔

```diagram filename="کون سی فائل کس صفحے کے لیے"
server logic + HTML          →  .nexy      (Python frontmatter + Jinja2)
prose that changes rarely    →  .md        (GitHub-flavoured Markdown)
prose + components           →  .mdx       (React or Preact)
app-like page, client router →  .tsx .vue .svelte (framework files)
API handler                  →  .py        (GET, POST, …)
```

## فارمیٹس

| فارمیٹ | فائل | سرور رینڈر | کلائنٹ فریم ورک | نوٹس |
|---|---|---|---|---|
| `.nexy` | [.nexy فائلیں](nexy/README.md) | Jinja2 + Python منطق، سلسلہ بندی | اختیاری | مقامی Nexy صفحہ کی شکل |
| `.md` | [Markdown اور MDX](nexy/markdown.md) | cmarkgfm درخواست کے وقت | لے آؤٹ کے ذریعے اختیاری | خالص Markdown، GFM، ترتیب سے لپیٹ |
| `.mdx` | [Markdown اور MDX](nexy/markdown.md) | فریم ورک SSR | React یا Preact | Markdown اجزاء کے ساتھ |
| `.tsx` | [React](react/differences.md)، [Solid](solid/differences.md) یا [Preact](preact/differences.md) | کلائنٹ موڈ: فریم ورک، نوڈ | React، Solid یا Preact | اجزاء کے راستے |
| `.vue` | [Vue](vue/differences.md) | کلائنٹ موڈ: فریم ورک، نوڈ | Vue | SFC روٹس |
| `.svelte` | [Svelte](svelte/differences.md) | کلائنٹ موڈ: فریم ورک، نوڈ | Svelte | SFC روٹس |

بلٹ ان `Image`، `Link`، `Audio`، `Video` اور `Import` مددگار: [اجزاء](nexy/components.md)۔

## اختلاط کی شکلیں

آپ ایک ہی پروجیکٹ میں مختلف ٹیکنالوجیز کو ملا سکتے ہیں:
- **جزائر**: آپ React یا Vue جز کو `.nexy` صفحہ کے اندر درآمد کر سکتے ہیں۔ سرور شیل کو پیش کرتا ہے، اور فریم ورک کلائنٹ پر جزو کو ہائیڈریٹ کرتا ہے۔
- **مشترکہ منطق**: `.py` فائلوں میں روٹ ہینڈلرز مشترکہ ایپلیکیشن اسٹیٹ یا API کالز کے ذریعے کسی بھی فارمیٹ میں صفحات کو ڈیٹا فراہم کر سکتے ہیں۔

## ایک فریم ورک کو فعال کریں۔

`useFF` کو `nexyconfig.py` میں سیٹ کریں اور انحصار شامل کرنے کے لیے `nexy new` چلائیں:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
```

ایک فریم ورک فعال ہونے کے ساتھ، Vite اپنے کلائنٹ بنڈلز کو ہینڈل کرتا ہے۔ کلائنٹ موڈ میں اس کی ایکسٹینشن روٹس بن جاتی ہے۔ سرور موڈ میں وہی فائلیں ہیں جو آپ جزائر کے طور پر درآمد کرتے ہیں - `src/routes/` کے تحت ایک فریم ورک فائل وہاں مسترد کردی جاتی ہے۔ دیکھیں [سرور موڈ اور کلائنٹ موڈ](../routing/fbr/modes.md)۔

> [!نوٹ]
> [CSR](../rendering/csr.md) موڈ میں، صرف فریم ورک روٹ فائلیں نیویگیبل کلائنٹ سائیڈ ہیں۔

## لے آؤٹ

ڈائرکٹری میں ایک `layout.*` اس کے نیچے صفحات لپیٹتا ہے۔ دیکھیں [لے آؤٹس](../routing/fbr/layouts/README.md)۔

## اگلے اقدامات

- [.nexy فائلیں](nexy/README.md): Python + Jinja2 + پرپس
- [Markdown اور MDX](nexy/markdown.md): مواد کے صفحات
- [اجزاء](nexy/components.md): بلٹ ان ایچ ٹی ایم ایل مددگار
