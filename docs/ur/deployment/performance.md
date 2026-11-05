# کارکردگی

`nx start` پہلے سے طے شدہ طور پر کیا کرتا ہے، کیا سوئچ آن کرنا ہے، اور کیا پیمائش کی گئی تھی۔

## ڈیفالٹس

| تشویش | طے شدہ | اسے تبدیل کریں۔ |
|---|---|---|
| عمل | لینکس اور میک او ایس پر ایک Uvicorn کارکن فی سی پی یو، ایک ونڈوز پر | `nx start` ایپ کو Uvicorn کے ذریعے چلاتا ہے۔ |
| کمپریشن | بند | [کنفیگ](../reference/config.md) میں `useGZip = {"minimum_size": 1000}`، یا ریورس پراکسی پر سکیڑیں |
| جامد فائلیں۔ | `ETag` اور `Last-Modified` کے ساتھ پیش کیا گیا، نہیں `Cache-Control` | ہیشڈ بنڈلز کے لیے ریورس پراکسی یا CDN پر طویل المدت کیشنگ سیٹ کریں۔ |
| HTML صفحات | فی درخواست فراہم کی گئی، کوئی کیش نہیں۔ | [ISR](../rendering/isr.md) کے ساتھ `revalidate = N` |
| API دستاویزات | پر | پیداوار میں `useDocs = False` |
| رن ٹائم پر نوڈ | کوئی نہیں | `nx build` کلائنٹ کے اجزاء کو پہلے سے پیش کرتا ہے۔ |

ٹیبل کے دو سوئچز `nexyconfig.py` میں، اور ایک صفحہ میں ISR:

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

## ناپا

ایک لوکل رن، ایک Uvicorn ورکر، ونڈوز، Python 3.13، اسی مشین پر Python لوڈ جنریٹر سے کنکشن کو زندہ رکھیں۔ تبدیلیوں کا موازنہ کرنے کے لیے نمبروں کو ایک بنیادی لائن کے طور پر سمجھیں، نہ کہ دوسرے فریم ورک کے خلاف ایک معیار کے طور پر۔

ٹیبل کا Nexy JSON روٹ یہ فائل ہے:

```python filename="src/routes/api/ping.py"
async def GET():
    return {"ok": True}
```

| راستہ | ہم آہنگی | فی سیکنڈ کی درخواستیں | p50 | p99 |
|---|---|---|---|---|
| ننگا FastAPI JSON راستہ | 16 | ~4,500 | 3.4 ms | 5.1 ms |
| Nexy JSON راستہ (`src/routes/api/ping.py`) | 16 | ~2,900 | 5.2 ms | 9.8 ms |
| Nexy SSR صفحہ (16 KB، 16 اجزاء) | 1 | ~500 | 1.9 ms | 3.0 ms |
| Nexy SSR صفحہ (16 KB، 16 اجزاء) | 64 | ~670 | 94 ایم ایس | 126 ایم ایس |

ٹیبل پڑھنا:

- Nexy کی اپنی تہوں (پاتھ سیاق و سباق، مڈل ویئر) کی قیمت ایک ننگے FastAPI راستے کے تھرو پٹ کا تقریباً ایک تہائی ہے۔
- سرور کی طرف سے پیش کردہ صفحہ کی قیمت تقریباً 2 ایم ایس سی پی یو ہے، جو تقریباً 16 ٹیمپلیٹ رینڈرز (ایک فی جزو) پر پھیلی ہوئی ہے۔ کم اجزاء والے صفحات متناسب طور پر سستے ہیں۔
- کارکنوں کے ساتھ تھرو پٹ اسکیل۔ لینکس پر، `nx start` پہلے سے ہی فی سی پی یو شروع ہوتا ہے۔

## عملی مشورہ

1. Nginx، Caddy یا اپنے پلیٹ فارم کے کنارے کو سامنے رکھیں: TLS، HTTP/2، Brotli اور `/__nexy__/client/` اثاثوں کے لیے طویل المدت کیشنگ ان کی طاقت ہے۔ دیکھیں [تعینات](README.md)۔
2. ان صفحات کے لیے [ISR](../rendering/isr.md) کا استعمال کریں جو منٹ میں ایک بار سے بھی کم تبدیل ہوتے ہیں۔
3. [جزیروں](../rendering/islands.md) کے ساتھ سستی سے ہائیڈریٹ کریں تو پہلا بوجھ کم JavaScript۔
4. فی صفحہ `.nexy` اجزاء کی تعداد کو مناسب رکھیں: ہر ایک ایک الگ ٹیمپلیٹ رینڈر ہے۔
5. اپنے راستوں کی پیمائش کریں۔ ایک مقامی لوڈ جنریٹر جو رابطوں کو زندہ رکھتا ہے ایک صفحہ کے دو ورژن کا موازنہ کرنے کے لیے کافی ہے۔

مشورہ 1 کے ساتھ Nginx: ہیشڈ کلائنٹ کے بنڈل ایک سال کے لیے محفوظ کیے جاتے ہیں، باقی Nexy کو جاتا ہے۔

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

## اگلے اقدامات

- [تعیناتی](README.md)
- [انجام دینا ](../rendering/README.md)
- [ترتیب ](../reference/config.md)
