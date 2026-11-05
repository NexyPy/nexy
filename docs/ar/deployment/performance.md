# الأداء

ما يفعله `nx start` افتراضيًا، وما الذي يجب تشغيله، وما الذي تم قياسه.

## الافتراضيات

| قلق | الافتراضي | تغييره |
|---|---|---|
| العمليات | عامل Uvicorn واحد لكل وحدة معالجة مركزية على Linux وmacOS، وعامل واحد على Windows | `nx start` يقوم بتشغيل التطبيق من خلال Uvicorn |
| ضغط | خارج | `useGZip = {"minimum_size": 1000}` في [التكوين](../reference/config.md)، أو الضغط على الوكيل العكسي |
| الملفات الثابتة | خدم ب `ETag` و `Last-Modified`، لا `Cache-Control` | قم بتعيين التخزين المؤقت طويل الأمد على الوكيل العكسي أو CDN للحزم المجزأة |
| صفحات HTML | المقدمة لكل طلب، لا ذاكرة التخزين المؤقت | [ISR](../rendering/isr.md) مع `revalidate = N` |
| مستندات API | على | `useDocs = False` في الإنتاج |
| عقدة في وقت التشغيل | لا شيء | `nx build` يتم عرض مكونات العميل مسبقًا |

مفتاحا الجدول في `nexyconfig.py`، وISR في صفحة:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useGZip = {"minimum_size": 1000}
    useDocs = False
```

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

## قياس

تشغيل محلي، عامل Uvicorn واحد، Windows، Python 3.13، اتصالات مستمرة من مولد تحميل Python على نفس الجهاز. تعامل مع الأرقام كخط أساس لمقارنة التغييرات، وليس كمعيار مقابل الأطر الأخرى.

مسار Nexy JSON للجدول هو هذا الملف:

```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```

| الطريق | التزامن | طلبات في الثانية الواحدة | ص50 | ص99 |
|---|---|---|---|---|
| طريق JSON العاري FastAPI | 16 | ~ 4500 | 3.4 مللي ثانية | 5.1 مللي ثانية |
| مسار Nexy JSON (`src/routes/api/ping.py`) | 16 | ~ 2900 | 5.2 مللي ثانية | 9.8 مللي ثانية |
| صفحة Nexy SSR (16 كيلوبايت، 16 مكونًا) | 1 | ~500 | 1.9 مللي ثانية | 3.0 مللي ثانية |
| صفحة Nexy SSR (16 كيلوبايت، 16 مكونًا) | 64 | ~670 | 94 مللي ثانية | 126 مللي ثانية |

قراءة الجدول:

- تكلف طبقات Nexy الخاصة (سياق المسار والبرمجيات الوسيطة) حوالي ثلث إنتاجية المسار FastAPI المجرد.
- تكلف الصفحة المعروضة بواسطة الخادم حوالي 2 مللي ثانية من وحدة المعالجة المركزية، موزعة على ما يقرب من 16 نموذج عرض (واحد لكل مكون). الصفحات التي تحتوي على مكونات أقل تكون أرخص نسبيًا.
- موازين الإنتاجية مع العمال. في Linux، `nx start` يبدأ بالفعل تشغيل واحد لكل وحدة معالجة مركزية.

## نصيحة عملية

1. ضع Nginx، Caddy أو حافة النظام الأساسي الخاص بك في المقدمة: TLS، HTTP/2، Brotli والتخزين المؤقت طويل الأمد لأصول `/__nexy__/client/` هي نقاط قوتهم. انظر [نشر](README.md).
2. استخدم [ISR](../rendering/isr.md)] للصفحات التي تتغير أقل من مرة واحدة في الدقيقة.
3. قم بالترطيب بتكاسل باستخدام [الجزر](../rendering/islands.md) بحيث يتم شحن الحمولة الأولى بشكل أقل JavaScript.
4. اجعل عدد `.nexy` من المكونات لكل صفحة معقولًا: كل واحد منها عبارة عن عرض قالب منفصل.
5. قياس الطرق الخاصة بك. يعد مولد التحميل المحلي الذي يحافظ على الاتصالات حية كافيًا لمقارنة نسختين من الصفحة.

نصيحة 1 مع Nginx: يتم تخزين حزم العميل المجزأة مؤقتًا لمدة عام، ويذهب الباقي إلى Nexy.

```nginx filename="/etc/nginx/conf.d/my-app.conf"
server {
    listen 443 ssl http2;
    server_name example.com;

    location /__nexy__/client/ {
        proxy_pass http://127.0.0.1:3000;
        add_header Cache-Control "public, max-age=31536000, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## الخطوات التالية

- [نشر](README.md)
- [التقديم](../rendering/README.md)
- [التكوين](../reference/config.md)
