# پروجیکٹ کا ڈھانچہ

Nexy پروجیکٹ میں ہر فائل میں ایک کام ہوتا ہے۔ یہ صفحہ جو کہتا ہے۔

## ٹاپ لیول

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

فولڈر کا انتخاب کرنے کے لیے پوچھیں کہ فائل کیا ہے:

- **کوئی چیز جسے براؤزر کھول سکتا ہے** - ایک راستہ: `src/routes/`۔
- **ایک ٹکڑا جو کئی راستوں سے استعمال ہوتا ہے** - ایک جزو یا ماڈیول: `src/components/`، `src/`۔
- **ایک فائل پیش کی گئی جیسا کہ یہ ہے** - `public/`۔
- **ماڈیولر روٹر کا ایک کنٹرولر** - `src/apps/`۔
- **پیدا کردہ** - `__nexy__/`؛ کبھی اس میں ترمیم نہ کریں

> [!WARNING]
> `src/routes/` اسکین کیا جاتا ہے: وہاں رکھا ہوا مددگار راستہ بن جاتا ہے۔ ایک مددگار رکھیں جو باہر کا راستہ نہیں ہے `src/routes/`، یا اس کا نام `_` سے شروع کریں۔

## `src/routes/`

ہر فائل ایک راستہ بن جاتی ہے، سوائے ذیل کے محفوظ ناموں کے۔ فائل پاتھ مائنس ایکسٹینشن یو آر ایل ہے - دیکھیں [روٹنگ](../routing/README.md)۔

| فائل | کردار |
|---|---|
| `layout.nexy` | بہن بھائی اور بچوں کے صفحات کو سمیٹتا ہے |
| `errors.nexy` | ڈائریکٹری کے لیے 500 صفحہ |
| `notfound.nexy` | ڈائریکٹری کے لیے 404 صفحہ |
| `dependencies.py` | نے ڈائریکٹری کے لیے FastAPI انحصار کا اشتراک کیا |
| `__init__.py` | Python پیکیج مارکر |
| `loading.nexy` | محفوظ - راستوں سے خارج، لیکن اس کا ابھی تک کوئی رن ٹائم اثر نہیں ہے |

ہر صفحہ کا نام بھی فی فریم ورک موجود ہے۔ `react()` کنفیگر ہونے کے ساتھ، `layout.jsx` اور `layout.tsx` بالکل `layout.nexy` کی طرح محفوظ ہیں۔ فہرستیں `nexy/core/config.py` (`LAYOUT_FILE_NAMES`، `ERROR_FILE_NAMES`، `NOTFOUND_FILE_NAMES`، `LOADING_FILE_NAMES`) میں بنائی گئی ہیں۔

> [!NOTE]
> `notfound.nexy` اور `errors.nexy` صرف اس وقت انسٹال ہوتے ہیں جب روٹس روٹ پر ایک کاپی موجود ہو۔ ذیلی ڈائرکٹری میں ایک کاپی پھر اس سابقے کے لیے صفحہ کو بہتر بناتی ہے۔

## `src/apps/`

ڈائرکٹری `nexy new` ماڈیولر راؤٹر کے لیے استعمال کرتی ہے: کنٹرولرز، ماڈیولز اور پرووائیڈرز اپنے روٹس کو ڈیکوریٹرز کے ذریعے `nexy.decorators` سے رجسٹر کرتے ہیں، پھر مجموعی `APIRouter` کو `nexyconfig.py` میں `useRouter` کے ساتھ لگایا جاتا ہے۔

ایک پروجیکٹ میں دونوں راؤٹرز ہو سکتے ہیں: `useRouter` ماڈیولر راؤٹر کو ماؤنٹ کرتا ہے، اور جب بھی وہ ڈائرکٹری موجود ہوتی ہے `src/routes/` کو اسکین کیا جاتا ہے۔ دیکھیں [ماڈیولر روٹنگ](../routing/modular/README.md)۔

## `public/`

یہاں فائلیں سائٹ روٹ سے پیش کی جاتی ہیں: `/favicon.ico`، `/robots.txt`، تصاویر، فونٹس۔

## `__nexy__/`

`nx build` (اور `nx dev` کے ذریعہ اس کی ضرورت کے حصوں کے لئے) کے ذریعہ تیار کردہ۔ اس میں شامل ہیں:

- مرتب شدہ روٹ ماڈیولز، بطور Python پیکیج (`__nexy__/src/routes/...`)؛
- پیدا کردہ کلائنٹ کے اندراج پوائنٹس (`main.ts`، `vite.ts`، `*.auto.ts`)؛
- `client/` ایک Vite تعمیر کے بعد - اثاثے، ظاہر، پہلے سے پیش کردہ HTML؛
- `build-cache.json`۔

پوری ڈائرکٹری کو ڈسپوزایبل سمجھیں: اسے حذف کریں، اسے دوبارہ بنائیں۔ ہاتھ سے اس میں ترمیم کرنے سے اگلی تعمیر میں تبدیلی ختم ہوجاتی ہے۔ اسے `.gitignore` میں شامل کریں۔

## اگلے اقدامات

- [روٹنگ](../routing/README.md): راستہ کیسے یو آر ایل بنتا ہے۔
- [تشکیل](../reference/config.md): ہر پروجیکٹ کا آپشن
- [فرنٹ اینڈ](../guides/frontend.md): Vite، اسٹائلنگ اور کلائنٹ کی تعمیر
