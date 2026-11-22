# میں Nexy میں سرور کوڈ کو کیسے ڈیبگ کروں؟

`nx dev` کے سرور کوڈ کو ٹرمینل میں `breakpoint()` کے ساتھ، یا VS کوڈ اور `debugpy` کے ساتھ ڈیبگ کریں: دیو سرور آپ کے Python کو اپنے عمل میں چلاتا ہے، اس لیے اس سے منسلک ڈیبگر آپ کے صفحات، API ہینڈلرز اور ایکشنز میں رک جاتا ہے۔

## آپ کا کوڈ `nx dev` کیسے چلتا ہے۔

`nx dev` بغیر کسی علیحدہ کارکن کے اپنے عمل میں یوویکورن شروع کرتا ہے۔ جب ایک Python فائل یا `.nexy` صفحہ تبدیل ہوتا ہے، تو یہ آپ کے پروجیکٹ کے ماڈیولز کو بھول جاتا ہے اور اسی عمل میں دوبارہ درآمد کرتا ہے۔ `nx dev` سے منسلک ڈیبگر اس لیے دوبارہ لوڈ کے دوران منسلک رہتا ہے، اور فائل میں سیٹ بریک پوائنٹ نئے کوڈ میں اپنی جگہ برقرار رکھتا ہے۔

ایک `.nexy` فائل کو `__nexy__/` کے تحت ایک Python ماڈیول میں مرتب کیا جاتا ہے، اسی راستے پر، جو چلتا ہے:

<!-- router:fbr,custom -->
| آپ لکھیں۔ | Nexy دوڑتا ہے۔ |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`، فنکشن `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | فائل خود |
<!-- /router -->

<!-- router:modular -->
| آپ لکھیں۔ | Nexy دوڑتا ہے۔ |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | فائل خود |
<!-- /router -->

ایک `.nexy` فائل کا فرنٹ میٹر (دو `---` لائنوں کے درمیان Python اس ماڈیول کے فنکشن کا باڈی بن جاتا ہے۔ `__nexy__/` ہر تبدیلی پر دوبارہ لکھا جاتا ہے: اس میں کبھی ترمیم نہ کریں۔

## `breakpoint()` کے ساتھ ٹرمینل میں رکیں

`breakpoint()` کو جہاں آپ رکنا چاہتے ہیں، `.py` فائل میں یا `.nexy` فائل کے فرنٹ میٹر میں رکھیں:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

صفحہ کھولیں۔ درخواست انتظار کرتی ہے اور `nx dev` کا ٹرمینل pdb دکھاتا ہے، مرتب شدہ ماڈیول میں:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

کھولیں `/users`۔ درخواست انتظار کرتی ہے اور `nx dev` کا ٹرمینل اس لائن پر pdb دکھاتا ہے۔ ایک منظر کے فرنٹ میٹر میں، پی ڈی بی `__nexy__/src/apps/` کے تحت مرتب کردہ ماڈیول کو دکھاتا ہے۔
<!-- /router -->

کسی قدر کو پرنٹ کرنے کے لیے `p page`، اگلی لائن کے لیے `n`، درخواست کو جاری رکھنے کے لیے `c` ٹائپ کریں۔ جب آپ کام کر لیں تو لائن کو ہٹا دیں: اگلی درخواست دوبارہ وہیں رک جاتی ہے۔

## VS کوڈ کے ساتھ ڈیبگ کریں۔

پروجیکٹ کے ماحول میں `debugpy` انسٹال کریں:

```bash
uv add --dev debugpy
```

پھر لانچ کنفیگریشن شامل کریں۔ `nexy.modules.cli` `nx` کمانڈ کے پیچھے ماڈیول ہے، لہذا یہ لینکس، میک او ایس اور ونڈوز پر ایک جیسا کام کرتا ہے:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

F5 دبائیں۔ اپنی `.py` فائلوں میں، اور `.nexy` فائل کے لیے `__nexy__/` کے تحت مرتب کردہ ماڈیول میں بریک پوائنٹس سیٹ کریں: VS کوڈ `.nexy` فائل میں نہیں رک سکتا، کیونکہ یہ Python جب تک مرتب نہیں ہوتا۔ مرتب کردہ ماڈیول کے لائن نمبرز فرنٹ میٹر کی پیروی کرتے ہیں، لہذا آپ کے صفحہ میں ترمیم کرنے کے بعد وہاں ایک بریک پوائنٹ منتقل ہو سکتا ہے۔ `breakpoint()` فرنٹ میٹر میں نہیں ہے۔

## دوسرے ٹرمینل سے منسلک کریں۔

ڈیو سرور کو خود شروع کرنے اور بعد میں ڈیبگر منسلک کرنے کے لیے:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` اس وقت تک آغاز رکھتا ہے جب تک کہ ڈیبگر منسلک نہ ہو جائے۔ ایک بار شروع کرنے کے لئے اسے چھوڑ دو. VS کوڈ میں، `"request": "attach"` اور `"connect": { "host": "127.0.0.1", "port": 5678 }` کی ترتیب کے ساتھ منسلک کریں۔

debugpy خبردار کر سکتا ہے کہ "منجمد ماڈیولز استعمال ہو رہے ہیں"۔ اگر معیاری لائبریری میں بریک پوائنٹ چھوٹ جائے تو Python کو `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) سے شروع کریں۔ آپ کے اپنے کوڈ میں بریک پوائنٹس متاثر نہیں ہوتے ہیں۔

## اگلے اقدامات

- [ٹربل شوٹنگ](troubleshooting.md): لوگوں کی پہلی پریشانی
- [ٹیسٹنگ](testing.md): ایک بار جب آپ کو بگ مل جائے تو اسے ٹیسٹ میں دوبارہ پیش کریں۔
- [.nexy فائلیں](../views/nexy/README.md): فرنٹ میٹر، props اور ٹیمپلیٹس
