# .nexy الملفات

الملف `.nexy` عبارة عن مكون: Python في الأعلى، وHTML في المنتصف، وCSS في الأسفل.

**قبل البدء:** مشروع تم إنشاؤه بواسطة [البداية السريعة](../../getting-started/quick-start.md).
لا يحتاج الملف `.nexy` إلى تكوين بناء: `nx dev` يجمعه عند الحفظ.

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

## المقدمة

كل ما بين السطرين `---` هو بايثون. يتم حل الواردات عندما يكون المكون
مجمعة؛ يتم تشغيل الباقي لكل طلب، حتى يتمكن من قراءة حالة الطلب.

| ما | مثال |
|---|---|
| استيراد وحدة | `import json`، `from datetime import datetime` |
| استيراد مكون | `from "@/components/card.nexy" import Card` |
| إعلان خاصية | `title: prop[str] = "Default"` |
| حساب القيمة | `year = datetime.now().year` |
| اقرأ الطلب | `pathname = usePathname()` |
| تخزين الصفحة مؤقتًا (ISR) | `revalidate = 60` |

## الخصائص

الخصائص هي واجهة برمجة التطبيقات للمكون. `prop[type]` يعلن النوع، `= value` يعطي الافتراضي. أ
الخاصية بدون افتراضية يجب أن يتم تمريرها من قبل الوالدين.

يتم حل الواردات التي تبدأ باسم مستعار من خلال `useAliases`. الإعداد `nx new` يكتب الخرائط
`@` إلى `src`، مما يجعل `@/components/card.nexy` يعني `src/components/card.nexy`.

## قالب

أسفل المادة الأمامية يوجد HTML مع Jinja2. المتغيرات من المادة الأمامية والخصائص موجودة
النطاق.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

الهروب التلقائي **إيقاف**: القوالب هي HTML الخاص بالمشروع، لذلك يتم إدراج `{{ value }}` كـ
مكتوب. تخلص من القيم غير الموثوقة بنفسك مع `{{ value | e }}`. `| safe` لذلك لا يتغير شيء.

> [!ملاحظة]
> التفاف جافا سكريبت الذي يحتوي على `{{` أو `{%` في `{% raw %}...{% endraw %}`.
> أطر العمل مثل Vue وSvelte تستخدم نفس الأقواس.

## المكونات

يمكن استخدام أي قابل للاستدعاء مستورد يبدأ اسمه بحرف كبير كعلامة. المترجم
يعيد كتابتها إلى استدعاء Jinja: تصبح السمات وسيطات الكلمات الرئيسية.

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

والسطر الأخير هو بالضبط `{{ Audio("/theme.mp3", controls=True) }}`. كلا النحوين صالحان لـ
المساعدين المدمجين `Image` و `Link` و `Audio` و `Video` - راجع
[المكونات](components.md#two-syntaxes-one-function).

يتم عرض الأطفال من خلال `<Slot />` (الحرف الكبير S) داخل المكون الفرعي، ومن خلال `{{ children }}`
داخل التخطيط.

قم بتمرير قيمة محسوبة باستخدام Jinja داخل السمة: `<Icon path="{{ icon }}" size="{{ size }}" />`.
الاسم المجرد مثل `path=icon` هو النص `icon`، وليس المتغير. لإعطاء مكون CSS
فئة، قم بتعريف الدعامة `class_name`: `class` هي كلمة أساسية في لغة Python.

> [!ملاحظة]
> العلامة المساعدة تكون دائمًا ذاتية الإغلاق. تمرير المحتوى إلى `Link` يمر عبره
> `children` الوسيطة (`<Link href="/about" children="About" />`)، وليس من خلال محتوى العنصر.

##  الأنماط

`<style>` الكتل تنبعث مع الصفحة التي تعلن عنها. لم يتم تحديد نطاقها: اسم فئة
المستخدمة في مكونين هو فئة واحدة. البادئة أو مساحة الاسم للفصول الدراسية الخاصة بك.

## قواعد توفير الوقت

- مكون واحد لكل ملف. اسم الملف هو اسم المكون، في PascalCase (`CopyChip.nexy`). أ
  `.nexy` يتم استيراد المكون كوحدة نمطية لـ Python: لا توجد واصلة في الاسم (`copy-chip.nexy`)
  ترجمة.
- قم بتعريف الخاصيات قبل استخدامها: يتم عرض متغير غير معلن كسلسلة فارغة، لأن
  Jinja2 غير محدد صامت هنا.
- احتفظ بالآثار الجانبية داخل الوظائف - فالأمر الأمامي يعمل مرة أخرى عند كل طلب.

## الخطوات التالية

- [Markdown وMDX](markdown.md): صفحات المحتوى
- [ISR](../../rendering/isr.md): تخزين صفحة في كل مسار
- [CSR](../../rendering/csr.md): العرض من جانب العميل