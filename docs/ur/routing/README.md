# روٹنگ

Nexy کے دو مقامی راؤٹرز ہیں۔ آپ فی فیچر میں سے ایک منتخب کر سکتے ہیں۔ وہ ایک ہی درخواست میں ایک ساتھ رہ سکتے ہیں۔

**یقین نہیں ہے؟ فائل پر مبنی استعمال کریں۔ روٹنگ** یہ بغیر کسی سیٹ اپ کے صفحات اور API کے اختتامی نکات کا احاطہ کرتا ہے۔ ماڈیولر راؤٹر شامل کریں جب بیک اینڈ کو کنٹرولرز، انجیکشن سروسز یا گارڈز کی ضرورت ہو۔

| آپ تعمیر کر رہے ہیں | استعمال کریں |
|---|---|
| صفحات، مواد، چند اختتامی نقطوں والی سائٹ | فائل پر مبنی |
| تمام راستوں پر مشترکہ خدمات کے ساتھ ایک بڑا API | ماڈیولر |
| دونوں: لوگوں کے لیے صفحات، مشینوں کے لیے ایک منظم API | فائل پر مبنی اور ماڈیولر ایک ساتھ |

```diagram filename="فائل پر مبنی روٹر، ایک نظر میں"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| راؤٹر | ذریعہ | | کے ذریعہ فعال
|---|---|---|
| [فائل پر مبنی (FBR)](fbr/README.md) | `src/routes/` | کے تحت ہر فائل ڈائریکٹری موجود ہے |
| [ماڈیولر](modular/README.md) | کنٹرولرز اور ماڈیولز | `useRouter = AppModule` `nexyconfig.py` | میں

جب بھی `src/routes/` موجود ہوتا ہے تو ایف بی آر کو اسکین کیا جاتا ہے، یہاں تک کہ ماڈیولر راؤٹر لگا ہوا ہو۔

## بقائے باہمی اور ترجیحات

آپ FBR، ماڈیولر، اور کسٹم انٹیگریشن کو یکجا کر سکتے ہیں۔ Nexy ان راستوں کو اس ترتیب سے رجسٹر کرتا ہے جس ترتیب سے وہ دریافت ہوتے ہیں۔ اگر دو راؤٹرز ایک ہی URL پاتھ کی وضاحت کرتے ہیں، تو پہلا رجسٹرڈ جیت جاتا ہے۔ 

*نوٹ: Nexy فی الحال URL کے تصادم کی تشخیص فراہم نہیں کرتا ہے۔ کسی راستے کا دعوی کرنے کا پہلا راستہ صرف دوسروں پر سایہ ڈالتا ہے۔*

## فائل پر مبنی روٹنگ

روٹ ایک فائل ہے۔ یو آر ایل اس کا راستہ ہے `src/routes/` کے نیچے، مائنس ایکسٹینشن۔ Next.js کی طرح، ایک پروجیکٹ دو طریقوں میں سے ایک میں ہوتا ہے، جس کا انتخاب `useCSR` کے ساتھ ہوتا ہے:

| | `useCSR = False` (پہلے سے طے شدہ) | `useCSR = True` |
|---|---|---|
| آپ کے کلائنٹ فریم ورک کے صفحات | `.nexy`، `.md`، `.mdx` | فائلیں |
| روٹ لے آؤٹ | `layout.nexy` | `layout.tsx` (React) |
| کلائنٹ کے اجزاء | کی اجازت ہے، جیسا کہ صفحات کے اندر جزیرے | صفحات خود |
| API روٹس | `.py` | `.py` |

دیکھیں [سرور موڈ اور کلائنٹ موڈ](fbr/modes.md)۔

| سیکشن | جس کا احاطہ کرتا ہے |
|---|---|
| [fbr/صفحات](fbr/pages/README.md) | صفحات، [متحرک راستے](fbr/pages/dynamic-routes.md) اور روٹ گروپس |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` روٹ ہینڈلرز، [تصدیق اور غلطیاں](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` اور گارڈز، ڈائرکٹری سے وراثت میں ملے |
| [fbr/midleware](fbr/middleware/README.md) | `middleware.py`، ڈائرکٹری | سے وراثت میں ملا۔
| [fbr/غلطیاں](fbr/errors/README.md) | `notfound.nexy`، `errors.nexy`، JSON کی خرابیاں |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | لنکنگ، کلائنٹ نیویگیشن، [ہکس](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket ہینڈلر |
| [fbr/inheritance](fbr/inheritance.md) | ترتیب، انحصار اور غلطی کے صفحات کیسے وراثت میں آتے ہیں |

## ماڈیولر روٹنگ

کنٹرولرز، ماڈیولز اور انحصار انجکشن، NestJS کے انداز میں۔ دیکھیں [ماڈیولر روٹنگ](modular/README.md) اور [Nexy اور NestJS](modular/vs-nestjs.md)۔

## حسب ضرورت انٹیگریشن

آپ اپنے Nexy پروجیکٹ میں موجودہ FastAPI روٹر کو بھی ضم کر سکتے ہیں۔ دیکھیں [کسٹم روٹنگ انضمام](custom/README.md)۔

## اگلے اقدامات

- [فائل پر مبنی روٹنگ](fbr/README.md)
- [رینڈرنگ](../rendering/README.md)
- [ملاحظات](../views/README.md): فائلوں کے اندر کیا جاتا ہے۔
