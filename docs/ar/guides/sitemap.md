# كيف أقوم بإضافة sitemap.xml وrobots.txt إلى موقع Nexy؟

تعيين `useSiteUrl` في `nexyconfig.py`: يقوم Nexy بعد ذلك بتقديم `/sitemap.xml`، الذي يسرد كل صفحة ثابتة من المشروع، و `/robots.txt` الذي يوجه محركات البحث إليها.

## تشغيله مع `useSiteUrl`

`useSiteUrl` هو الأصل العام للموقع، وهو ما تراه محركات البحث:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` و `nx start` ثم قم بالإجابة على كلا الملفين. بدون `useSiteUrl` لا يوجد أي منهما، لذلك لا ينشر المشروع أبدًا عنوان URL لخادم التطوير الخاص به عن طريق الخطأ.

## ما يسرده خريطة الموقع

يمنح خريطة الموقع كل صفحة كعنوان URL مطلق على `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

يتم إدراج المسار عندما يجيب HTML على `GET` على مسار ثابت:

<!-- router:fbr,custom -->
- صفحة (`.nexy`، `.md`، `.mdx`، `.tsx`، `.jsx`، `.vue`، `.svelte`) مدرجة؛
- تم استبعاد صفحة ديناميكية، مثل `src/routes/users/[id].nexy`: لا يمكن لـ Nexy معرفة قيمها؛
- يجيب معالج المسار Python على JSON، لذلك يتم استبعاده.
<!-- /router -->

<!-- router:modular -->
- تم إدراج مسار وحدة التحكم الذي يجيب على HTML، مع `@UseResponse(response_class=HTMLResponse)`؛
- تم استبعاد المسار الذي يحتوي على معلمة مسار، مثل `/users/{id}`: لا يمكن لـ Nexy معرفة قيمه؛
- تم استبعاد المسار الذي يجيب على JSON.
<!-- /router -->

تم استبعاد المسار المخفي من مخطط واجهة برمجة التطبيقات (`include_in_schema=False`) أيضًا.

## و `robots.txt` يخدم

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## اكتب بنفسك بدلا من ذلك

يفوز ملفك الخاص دائمًا، ولا يقوم Nexy بالكتابة فوقه أبدًا:

- يتم تقديم `public/robots.txt` أو `public/sitemap.xml` كما هو، كما هو الحال مع كل ملف من `public/`؛
- مسار المشروع عند `/robots.txt` أو `/sitemap.xml` يحافظ على مساره.

اكتب خريطة الموقع الخاصة بك لسرد الصفحات الديناميكية، مثل عنوان URL واحد لكل مشاركة مدونة.

## الخطوات التالية

- [البيانات الوصفية للصفحة](../routing/fbr/pages/metadata.md): تظهر محركات البحث العنوان والوصف
- [التكوين](../reference/config.md): كل إعداد من `nexyconfig.py`
- [نشر](../deployment/README.md): يخدم المشروع في الإنتاج
