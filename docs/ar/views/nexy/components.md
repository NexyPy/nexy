# المكونات

يقوم Nexy بتصدير مجموعة صغيرة من المساعدين الذين يقومون بإرجاع سلاسل HTML. يتم استخدام كل واحد بطريقتين في
`.nexy` القالب: كنداء جينجا، أو كعلامة نمط HTML.

## نحيان، دالة واحدة

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

ينتج كلا الخطين نفس العلامات:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

يعيد المترجم كتابة `<Audio ... />` إلى `{{ Audio(...) }}`، وبالتالي فإن نموذج العلامة ليس واجهة برمجة تطبيقات ثانية:
السمات هي وسيطات الكلمة الأساسية للوظيفة.

## قواعد نموذج العلامة

| في العلامة | يصبح |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`، منطقية حقيقية |
| `width=640` | `width=640`، عدد |
| `src="{{ url }}"` | `src=(url)`، تم تقييمه في جينجا |
| أي غيره `value` | `"value"`، سلسلة |

- يجب أن تبدأ العلامة بحرف كبير ويتم استيرادها في المادة الأمامية؛ وإلا فإن
  المترجم يرفع `Missing Import: <Name> used but not declared.`
- نموذج العلامة هو **الإغلاق الذاتي**. `<Audio src="/a.mp3" />` و
  `{{ Audio("/a.mp3") }}` متكافئين؛ كتابة الأطفال داخل علامة المساعدة غير مدعومة.
- سمة HTML المجردة ليست منطقية هنا: `controls` تصبح `controls=""`، وهذا غير صحيح.
  اكتب `controls=True`.

> [!ملاحظة]
> `class_name` هي الكلمة الأساسية الموثقة لفئات CSS. وسيطات الكلمات الرئيسية الإضافية
>  تصبح سمات HTML، لذلك يصل `class="nav"` أيضًا إلى الإخراج.

## صورة

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` يجعل
`<img>` مع التحميل البطيء بشكل افتراضي.

##  الرابط

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` يجعل `<a data-nexy-link>`
يتم التعامل معها بواسطة جهاز توجيه العميل. مع `prefetch=True`، يؤدي التمرير أو لمس الرابط إلى تدفئة الهدف
من خلال `window.__nexy_prefetch`.

> [!ملاحظة]
> يأخذ نموذج العلامة التسمية كـ `children`، وليس كمحتوى عنصر:
> `<Link href="/about" children="About" />`. لوضع علامة داخل رابط، استخدم نموذج الاتصال مع
> `children=` أو مكون `.nexy` يعرض `<Slot />`.

##  الصوت والفيديو

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`الصوت (src، عناصر التحكم = صحيح، التشغيل التلقائي = خطأ، حلقة = خطأ، كتم الصوت = خطأ، التحميل المسبق = "بيانات التعريف"،
class_name=None, Resources=None, **attrs)` and `Video(src, width=None, height=None, ...)` تقديم أصلي
اللاعبين. `sources` يضيف `<source>` علامات بنوع MIME المشتق من كل امتداد.

## مكون تكتبه بنفسك

المكون `.nexy` القابل لإعادة الاستخدام هو ملف ضمن `src/components/`: دعائم Python في الأعلى، وHTML أدناه.
يتم استيراده مثل أي وحدة بايثون أخرى.

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` ليس له افتراضي، لذا يجب على الصفحة اجتيازه؛ `tone` يرجع إلى `"neutral"`. العلامات
بين العلامات يصل إلى داخل `<Slot />` (الحرف الكبير S). انظر
[ملفات .nexy](README.md#components) للدعائم والفتحات وقواعد نموذج العلامة.

## استيراد مكون العميل

من ملف `.nexy`، قم باستيراد مكون إطار العمل حسب المسار؛ يقوم المترجم بتثبيته على العميل و
يمرر السمات كدعائم:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` يفعل نفس الشيء في بايثون:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

نفس بناء جملة الاستيراد يحل `.json`، `.css` وملفات الصور إلى عناوين URL الخاصة بها.

##  القالب والفيت

`Template().render(path, context)` يعرض ملف قالب (Jinja2، أو Markdown يتم تقديمه إلى HTML لـ
`.md` الطرق). `Template().invalidate(path)` يسقطه من ذاكرة التخزين المؤقت.

`Vite()` يقوم بإرجاع علامات العميل للوضع الحالي: البرنامج النصي HMR قيد التطوير، المدمج
حزمة العميل في الإنتاج. يطلق عليه Nexy لكل صفحة؛ نادرا ما تحتاج إليها بشكل مباشر.

## لم يتم التنفيذ بعد

`Form` و `Script` عبارة عن عناصر نائبة مُصدَّرة بدون أي سلوك. لا تعتمد عليهم.

## الخطوات التالية

- [.nexy files](README.md): حيث يتم استخدام هؤلاء المساعدين
- [React](../react/differences.md): استيراد مكونات `.tsx`
- [Frontend](../../guides/frontend.md): كيفية تجميع مكونات العميل