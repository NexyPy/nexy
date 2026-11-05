# تنصیب

## تقاضے

| ضرورت | کیوں |
|---|---|
| Python 3.12+ | `requires-python` میں `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | پروجیکٹ بناتا ہے، اس کے پیکجز انسٹال کرتا ہے اور Nexy چلاتا ہے۔ |
| Node.js 18+ | صرف کلائنٹ فریم ورک کے لیے (React، Vue، Svelte، Solid، Preact) |

کلائنٹ فریم ورک کے بغیر کسی پروجیکٹ کو Node.js کی ضرورت ہی نہیں ہے۔

## پہلے uv انسٹال کریں۔

`uvx` کوئی الگ ٹول نہیں ہے: یہ uv کے ساتھ آتا ہے، لہذا کسی بھی چیز سے پہلے uv کو انسٹال کریں۔

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

اسے `uv --version` اور `uvx --version` سے چیک کریں۔

## ایک پروجیکٹ بنائیں

```bash
uvx nexy new my-app
```

`uvx` Nexy کو عارضی ماحول میں چلاتا ہے اور پیچھے کچھ نہیں چھوڑتا ہے۔ اتنا ہی کافی ہے۔ **بنائیں** ایک پروجیکٹ (`new`، `init`) اور کچھ نہیں: عارضی ماحول Nexy رکھتا ہے اور کوئی دوسرا پیکج نہیں۔ `nexy new` پروجیکٹ کا اپنا ورچوئل ماحول بناتا ہے، `.venv`، اور وہاں اپنے پیکجز انسٹال کرتا ہے۔

`nexy new my-app` چار سوالات پوچھتا ہے: راؤٹر (فائل پر مبنی یا ماڈیولر)، پروجیکٹ کی قسم (ویب یا API)، کلائنٹ فریم ورک، ORM۔ Python اور نوڈ انحصار کی تنصیب پھر ایک لائن فی قدم اور اس کی مدت کے ساتھ چلتی ہے۔ دیکھیں [CLI](../reference/cli.md)۔

رجسٹرڈ ٹیمپلیٹ کے ساتھ پرامپٹس کو چھوڑیں:

```bash
uvx nexy new my-app --template <name>
```

## پروجیکٹ کے ورچوئل ماحول کے اندر کام کریں۔

ہر دوسری کمانڈ (`nexy dev`، `nexy build`، `nexy migrate`...) کو **پروجیکٹ کے ورچوئل ماحول کے اندر** چلنا چاہیے۔ یہ وہ جگہ ہے جہاں آپ کے اپنے پیکیج رہتے ہیں: آپ کا ORM، آپ کی لائبریریاں، اور Nexy جس کے ساتھ پروجیکٹ بنایا گیا تھا۔ اس کے باہر، ایک پروجیکٹ جس کی ضرورت ہے `sqlmodel` `ModuleNotFoundError: No module named 'sqlmodel'` کے ساتھ ناکام ہوجاتی ہے۔

پروجیکٹ فولڈر سے فی ٹرمینل ایک بار اسے چالو کریں:

| شیل | حکم |
|---|---|
| پاور شیل، سی ایم ڈی (ونڈوز) | `.venv\Scripts\activate` |
| میکوس، لینکس | `source .venv/bin/activate` |

اس کے بعد پرامپٹ `(.venv)` سے شروع ہوتا ہے۔ وہاں سے:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

کھولیں <http://localhost:3000>۔

ایکٹیویشن کو چھوڑنے کے لیے، اسے uv کو ایک کمانڈ کے لیے کرنے دیں: `uv run nexy dev`۔

> [!NOTE]
> `nexy` اور `nx` ایک ہی بائنری ہیں۔ `uv tool install nexy` کے ساتھ نصب ایک کاپی اپنے ماحول میں رہتی ہے، جیسے `uvx`، اس لیے اسے پروجیکٹ بنانے اور پروجیکٹ کے ماحول سے باقی سب کچھ چلانے کے لیے استعمال کریں۔

## Nexy کو موجودہ پروجیکٹ میں شامل کریں۔

اسے پروجیکٹ کے ورچوئل ماحول سے چلائیں، اس کے پیکجوں میں Nexy کے ساتھ (`uv add nexy`):

```bash
nexy init
```

## اگلے اقدامات

- [فوری آغاز](quick-start.md)
- [ٹیوٹوریل](tutorial.md)
- [پروجیکٹ ڈھانچہ](project-structure.md)
- [مسئلہ حل کرنا](../guides/troubleshooting.md)
