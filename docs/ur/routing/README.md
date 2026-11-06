# روٹنگ

Nexy کے دو مقامی راؤٹرز ہیں۔ آپ فی فیچر میں سے ایک منتخب کر سکتے ہیں۔ وہ ایک ہی درخواست میں ایک ساتھ رہ سکتے ہیں۔

**یقین نہیں ہے؟ فائل پر مبنی استعمال کریں۔ روٹنگ** یہ بغیر کسی سیٹ اپ کے صفحات اور API کے اختتامی نکات کا احاطہ کرتا ہے۔ ماڈیولر راؤٹر شامل کریں جب بیک اینڈ کو کنٹرولرز، انجیکشن سروسز یا گارڈز کی ضرورت ہو۔

| آپ تعمیر کر رہے ہیں۔ | استعمال کریں۔ |
|---|---|
| صفحات، مواد، چند اختتامی پوائنٹس والی سائٹ | فائل پر مبنی |
| تمام راستوں پر مشترکہ خدمات کے ساتھ ایک بڑا API | ماڈیولر |
| دونوں: لوگوں کے لیے صفحات، مشینوں کے لیے ایک منظم API | فائل پر مبنی اور ماڈیولر ایک ساتھ |

<!-- router:fbr,custom -->
```diagram filename="فائل پر مبنی روٹر، ایک نظر میں"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="ماڈیولر روٹر، ایک نظر میں"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| راؤٹر | ماخذ | کی طرف سے فعال |
|---|---|---|
| [فائل پر مبنی (FBR)](fbr/README.md) | ہر فائل کے تحت `src/routes/` | ڈائریکٹری موجود ہے |
| [ماڈیولر](modular/README.md) | کنٹرولرز اور ماڈیولز | `useRouter = AppModule` میں `nexyconfig.py` |

جب بھی `src/routes/` موجود ہوتا ہے تو ایف بی آر کو اسکین کیا جاتا ہے، یہاں تک کہ ماڈیولر راؤٹر لگا ہوا ہو۔

## بقائے باہمی اور ترجیحات

آپ FBR، ماڈیولر، اور کسٹم انٹیگریشن کو یکجا کر سکتے ہیں۔ Nexy ان راستوں کو اس ترتیب سے رجسٹر کرتا ہے جس ترتیب سے وہ دریافت ہوتے ہیں۔ اگر دو راؤٹرز ایک ہی URL پاتھ کی وضاحت کرتے ہیں، تو پہلا رجسٹرڈ جیت جاتا ہے۔ 

*نوٹ: Nexy فی الحال URL کے تصادم کی تشخیص فراہم نہیں کرتا ہے۔ کسی راستے کا دعوی کرنے کا پہلا راستہ صرف دوسروں پر سایہ ڈالتا ہے۔*

<!-- router:fbr,custom -->
## فائل پر مبنی روٹنگ

روٹ ایک فائل ہے۔ یو آر ایل اس کا راستہ ہے `src/routes/` کے نیچے، مائنس ایکسٹینشن۔ Next.js کی طرح، ایک پروجیکٹ دو طریقوں میں سے ایک میں ہوتا ہے، جس کا انتخاب `useCSR` کے ساتھ ہوتا ہے:

| | `useCSR = False` (پہلے سے طے شدہ) | `useCSR = True` |
|---|---|---|
| صفحات | `.nexy`، `.md`، `.mdx` | آپ کے کلائنٹ فریم ورک کی فائلیں۔ |
| روٹ لے آؤٹ | `layout.nexy` | `layout.tsx` (React) |
| کلائنٹ کے اجزاء | صفحات کے اندر جزائر کے طور پر اجازت دی گئی ہے۔ | صفحات خود |
| API کے راستے | `.py` | `.py` |

دیکھیں [سرور موڈ اور کلائنٹ موڈ](fbr/modes.md)۔

| سیکشن | یہ کیا احاطہ کرتا ہے |
|---|---|
| [fbr/صفحات](fbr/pages/README.md) | صفحات، [متحرک راستے](fbr/pages/dynamic-routes.md) اور روٹ گروپس |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` روٹ ہینڈلر، [توثیق اور غلطیاں](fbr/handlers/validation-and-errors.md) |
| [fbr/انحصار](fbr/dependencies/README.md) | `dependencies.py` اور گارڈز، ڈائرکٹری کے ذریعہ وراثت میں ملے |
| [fbr/midleware](fbr/middleware/README.md) | `middleware.py`، ڈائرکٹری سے وراثت میں ملا |
| [fbr/غلطیاں](fbr/errors/README.md) | `notfound.nexy`، `errors.nexy`، JSON کی غلطیاں |
| [fbr/نیویگیشن](fbr/navigation/linking-and-navigating.md) | لنک کرنا، کلائنٹ نیویگیشن، [ہکس](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket ہینڈلر |
| [fbr/وراثت](fbr/inheritance.md) | لے آؤٹ، انحصار اور خرابی والے صفحات کیسے وراثت میں آتے ہیں۔ |
<!-- /router -->

## ماڈیولر روٹنگ

کنٹرولرز، ماڈیولز اور انحصار انجیکشن، NestJS کے انداز میں۔ دیکھیں [ماڈیولر روٹنگ](modular/README.md) اور [Nexy اور NestJS](modular/vs-nestjs.md)۔

<!-- router:modular -->
| سیکشن | یہ کیا احاطہ کرتا ہے |
|---|---|
| [ماڈیولر](modular/README.md) | `@Controller`، `@Module`، درآمدات اور برآمدات |
| [ماڈیولر/انحصار-انجیکشن](modular/dependency-injection.md) | `@Injectable`، اسکوپس اور کنٹینر |
| [ماڈیولر/گارڈز اور میٹا ڈیٹا](modular/guards-and-metadata.md) | `@UseGuard`، `@UseResponse` اور OpenAPI میٹا ڈیٹا |

ایک کنٹرولر `.nexy` منظر کو `useViews` کے ساتھ لوٹاتا ہے، اور اسے ہاتھ سے اس کے لے آؤٹ میں منتقل کرتا ہے: فولڈر کے ذریعہ کوئی `layout.nexy` لاگو نہیں ہوتا ہے۔
<!-- /router -->

## حسب ضرورت انضمام

آپ اپنے Nexy پروجیکٹ میں موجودہ FastAPI روٹر کو بھی ضم کر سکتے ہیں۔ دیکھیں [کسٹم روٹنگ انضمام](custom/README.md)۔

## اگلے اقدامات

<!-- router:fbr,custom -->
- [فائل پر مبنی روٹنگ](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [ماڈیولر روٹنگ ](modular/README.md)
<!-- /router -->
- [انجام دینا](../rendering/README.md)
- [مناظر](../views/README.md): فائلوں کے اندر کیا جاتا ہے۔
