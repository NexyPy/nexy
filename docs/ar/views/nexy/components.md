# المكونات

يقوم Nexy بتصدير مجموعة صغيرة من المساعدين الذين يقومون بإرجاع سلاسل HTML. يتم استخدام كل واحد بطريقتين في قالب `.nexy`: كمكالمة Jinja، أو كعلامة نمط HTML.

## تركيبان، وظيفة واحدة

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

يعيد المترجم كتابة `<Audio ... />` إلى `{{ Audio(...) }}`، وبالتالي فإن نموذج العلامة ليس واجهة برمجة تطبيقات ثانية: السمات هي وسيطات الكلمة الرئيسية للوظيفة.

## قواعد نموذج العلامة

| في العلامة | يصبح |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`، منطقية حقيقية |
| `width=640` | `width=640`، عدد |
| `src="{{ url }}"` | `src=(url)`، تم التقييم في Jinja |
| أي `value` | `"value"`، سلسلة |

- يجب أن تبدأ العلامة بحرف كبير وأن يتم استيرادها في المادة الأمامية؛ وإلا فإن المترجم يرفع `Missing Import: <Name> used but not declared.`
- نموذج العلامة هو **الإغلاق الذاتي**. `<Audio src="/a.mp3" />` و `{{ Audio("/a.mp3") }}` متساويان؛ كتابة الأطفال داخل علامة المساعدة غير مدعومة.
- سمة HTML المجردة ليست منطقية هنا: `controls` تصبح `controls=""`، ​​وهذا خطأ. اكتب `controls=True`.

> [!NOTE]
> `class_name` هي الكلمة الأساسية الموثقة لفئات CSS. تصبح وسيطات الكلمات الرئيسية الإضافية سمات HTML، لذلك يصل `class="nav"` أيضًا إلى المخرجات.

## صورة

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` يعرض `<img>` مع التحميل البطيء بشكل افتراضي.

## رابط

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` يعرض `<a data-nexy-link>` تتم معالجته بواسطة جهاز توجيه العميل. مع `prefetch=True`، يؤدي التمرير أو لمس الرابط إلى تسخين الهدف من خلال `window.__nexy_prefetch`.

> [!NOTE]
> يأخذ نموذج العلامة التسمية كـ `children`، وليس كمحتوى عنصر: `<Link href="/about" children="About" />`. لوضع علامة داخل رابط، استخدم نموذج الاستدعاء مع `children=` أو مكون `.nexy` الذي يعرض `<Slot />`.

## الصوت والفيديو

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` و `Video(src, width=None, height=None, ...)` يقدمان لاعبين أصليين. `sources` يضيف `<source>` علامات بنوع MIME المشتق من كل ملحق.

## مكون تكتبه بنفسك

المكون `.nexy` القابل لإعادة الاستخدام هو ملف ضمن `src/components/`: دعائم Python في الأعلى، وHTML أدناه. يتم استيراده مثل أي وحدة Python أخرى.

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

`title` ليس له افتراضي، لذا يجب على الصفحة اجتيازه؛ `tone` يرجع إلى `"neutral"`. تصل العلامات بين العلامات داخل `<Slot />` (الحرف الكبير S). راجع [ملفات .nexy](README.md#components) للتعرف على الدعائم والفتحات وقواعد نموذج العلامة.

## استيراد مكون العميل

من ملف `.nexy`، قم باستيراد مكون إطار العمل حسب المسار؛ يقوم المترجم بتثبيته على العميل ويمرر السمات كدعائم:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` يفعل نفس الشيء في Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

نفس بناء جملة الاستيراد يحل `.json`، `.css` وملفات الصور إلى عناوين URL الخاصة بها.

## القالب و Vite

`Template().render(path, context)` يعرض ملف قالب (Jinja2، أو Markdown يتم عرضه إلى HTML للمسارات `.md`). `Template().invalidate(path)` يسقطه من ذاكرة التخزين المؤقت.

`Vite()` يقوم بإرجاع علامات العميل للوضع الحالي: البرنامج النصي HMR قيد التطوير، وحزمة العميل المضمنة في الإنتاج. يطلق عليه Nexy لكل صفحة؛ نادرا ما تحتاج إليها بشكل مباشر.

## لم يتم تنفيذها بعد

`Form` و `Script` عبارة عن عناصر نائبة مُصدَّرة بدون أي سلوك. لا تعتمد عليهم.

## الخطوات التالية

- [.nexy files](README.md): حيث يتم استخدام هؤلاء المساعدين
- [React](../react/differences.md): استيراد مكونات `.tsx`
- [الواجهة الأمامية](../../guides/frontend.md): كيفية تجميع مكونات العميل
