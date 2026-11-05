# ملفات .nexy

الملف `.nexy` هو مكون: Python في الأعلى، وHTML في المنتصف، وCSS في الأسفل.

**قبل أن تبدأ:** مشروع تم إنشاؤه بواسطة [البداية السريعة](../../getting-started/quick-start.md). لا يحتاج الملف `.nexy` إلى تكوين بناء: `nx dev` يجمعه عند الحفظ.

```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## فرونتماتر

كل ما بين السطرين `---` فهو Python. يتم حل الواردات عندما يتم تجميع المكون؛ يتم تشغيل الباقي لكل طلب، حتى يتمكن من قراءة حالة الطلب.

| ما | مثال |
|---|---|
| استيراد وحدة | `import json`، `from datetime import datetime` |
| استيراد مكون | `from "@/components/card.nexy" import Card` |
| إعلان خاصية | `title: prop[str] = "Default"` |
| حساب قيمة | `year = datetime.now().year` |
| اقرأ الطلب | `pathname = usePathname()` |
| تخزين الصفحة مؤقتًا (ISR) | `revalidate = 60` |

## خصائص

الخصائص هي واجهة برمجة التطبيقات للمكون. `prop[type]` يعلن النوع، `= value` يعطي الافتراضي. يجب أن يتم تمرير الخاصية التي لا تحتوي على افتراضي من قبل الأصل.

يتم حل الواردات التي تبدأ باسم مستعار من خلال `useAliases`. يقوم الإعداد `nx new` بكتابة الخرائط `@` إلى `src`، مما يجعل `@/components/card.nexy` يعني `src/components/card.nexy`.

## القالب

أسفل المادة الأمامية يوجد HTML مع Jinja2. المتغيرات من المادة الأمامية والخصائص موجودة في النطاق.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

ميزة الهروب التلقائي **متوقفة**: القوالب هي HTML الخاص بالمشروع، لذلك يتم إدراج `{{ value }}` كما هو مكتوب. تخلص من القيم غير الموثوقة بنفسك مع `{{ value | e }}`. `| safe` لذلك لا يتغير شيء.

> [!NOTE]
> التفاف JavaScript الذي يحتوي على `{{` أو `{%` في `{% raw %}...{% endraw %}`. تستخدم أطر العمل مثل Vue و Svelte نفس الأقواس.

## المكونات

يمكن استخدام أي قابل للاستدعاء مستورد يبدأ اسمه بحرف كبير كعلامة. يقوم المترجم بإعادة كتابتها إلى استدعاء Jinja: تصبح السمات وسيطات الكلمات الرئيسية.

```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

والسطر الأخير هو بالضبط `{{ Audio("/theme.mp3", controls=True) }}`. كلا الصيغتين صالحتان للمساعدات المضمنة `Image`، `Link`، `Audio` و `Video` - راجع [المكونات](components.md#two-syntaxes-one-function).

يتم عرض الأطفال من خلال `<Slot />` (الحرف S الكبير) داخل المكون الفرعي، ومن خلال `{{ children }}` داخل التخطيط.

قم بتمرير قيمة محسوبة باستخدام Jinja داخل السمة: `<Icon path="{{ icon }}" size="{{ size }}" />`. الاسم المجرد مثل `path=icon` هو النص `icon`، وليس المتغير. لإعطاء مكون فئة CSS، قم بتعريف الخاصية `class_name`: `class` هي الكلمة الأساسية Python.

> [!NOTE]
> تكون العلامة المساعدة دائمًا ذاتية الإغلاق. تمرير المحتوى إلى `Link` يمر عبر وسيطته `children` (`<Link href="/about" children="About" />`)، وليس من خلال محتوى العنصر.

## الأنماط

`<style>` الكتل تنبعث مع الصفحة التي تعلن عنها. لم يتم تحديد نطاقها: اسم الفئة المستخدم في مكونين هو فئة واحدة. البادئة أو مساحة الاسم للفصول الدراسية الخاصة بك.

## القواعد التي توفر الوقت

- مكون واحد لكل ملف. اسم الملف هو اسم المكون، في PascalCase (`CopyChip.nexy`). يتم استيراد مكون `.nexy` كوحدة نمطية Python: لا يتم تجميع الواصلة في الاسم (`copy-chip.nexy`).
- قم بتعريف الخاصيات قبل استخدامها: يتم عرض متغير غير معلن كسلسلة فارغة، لأن Jinja2 غير محدد هنا.
- احتفظ بالآثار الجانبية داخل الوظائف - حيث يتم تشغيل المادة الأمامية مرة أخرى عند كل طلب.

## الخطوات التالية

- [Markdown و MDX](markdown.md): صفحات المحتوى
- [ISR](../../rendering/isr.md): تخزين صفحة في كل مسار
- [CSR](../../rendering/csr.md): العرض من جانب العميل
