# تعینات کریں۔

دو حکم: `nx build` نمونے تیار کرتا ہے، `nx start` ان کی خدمت کرتا ہے۔

**شروع کرنے سے پہلے:** ایک پروجیکٹ جو مقامی طور پر `nx build` کے ساتھ بناتا ہے، اور - کلائنٹ کے صفحات کے لیے - فرنٹ اینڈ ٹول چین جو `nx new` انسٹال ہوتا ہے۔

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

رن ٹائم کی ضرورت ہے صرف Python۔ Uvicorn مرتب کردہ ایپ اور جامد اثاثوں کو پیش کرتا ہے۔ کوئی نوڈ عمل اور کوئی Vite عمل شامل نہیں ہے۔

## تعمیر کیا پیدا کرتی ہے۔

`__nexy__/` مرتب شدہ روٹ ماڈیولز، `__nexy__/client/` کے تحت کلائنٹ بنڈل، اور فریم ورک روٹس کے لیے پہلے سے پیش کردہ HTML پر مشتمل ہے۔ پروجیکٹ کو کاپی کریں - سورس پلس `__nexy__/` - یا تصویر کے اندر بنائیں۔

## Docker

تعمیراتی مرحلے کو نوڈ (Vite کے لیے) اور Python (مرتب کے لیے) کی ضرورت ہے۔ رن ٹائم مرحلے کو صرف Python کی ضرورت ہے۔

```dockerfile filename="ڈاکر فائل"
FROM node:22-bookworm-slim AS build
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project

COPY . .
RUN uv sync --frozen && uv run nx build

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /app /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["nx", "start", "--host", "0.0.0.0", "--port", "8000"]
```

`uv` ایک منظم Python حاصل کرتا ہے جب بنیادی تصویر میں کوئی نہیں ہوتا ہے، یہی وجہ ہے کہ تعمیر کا مرحلہ نوڈ امیج سے شروع ہوسکتا ہے۔

## ایک ریورس پراکسی کے پیچھے

لوکل ہوسٹ پر `nx start` چلائیں اور Nginx، Caddy یا پلیٹ فارم پراکسی کو TLS کو ختم کرنے دیں:

```bash
nx start --host 127.0.0.1 --port 8000
```

اس بات کو یقینی بنائیں کہ اگر آپ `SOCKET` ہینڈلرز استعمال کرتے ہیں تو پراکسی فارورڈز WebSocket کو اپ گریڈ کرتا ہے، اور یہ کہ یہ اصل میزبان کو فارورڈ کرتا ہے - FastAPI اس سے مطلق یو آر ایل بناتا ہے۔

## صحت کی جانچ

ایک ہینڈلر فائل شامل کریں، `src/routes/api/health.py`، اور پروب `/api/health` - اس صفحے کے بجائے جو آہستہ سے رینڈر ہو سکتا ہے:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## جامد ہوسٹنگ

ہر صفحہ HTML ہے، لیکن Nexy روٹنگ اور API ہینڈلرز کے لیے ایک سرور فرض کرتا ہے۔

> [!نوٹ]
> کوئی `--static` تعمیر کا موڈ نہیں ہے۔ آپ کی پائپ لائن میں `nx build` آؤٹ پٹ سے خالصتاً جامد برآمد پیدا کرنا ہوگی۔

## چیک لسٹ

- [ ] `nx build` CI میں، ان راستوں کے لیے کوئی انتباہ نہیں جو آپ سرور پر پیش کرنے کی توقع کرتے ہیں
- [ ] `nx start` کوڈ 1 کے ساتھ باہر نکلتا ہے، اور کچھ بھی شروع نہیں ہوتا ہے، جب روٹ فائل لوڈ نہیں ہو سکتی
- [ ] `NEXY_ACTION_SECRET` سیٹ، یا `__nexy__/action.key` تعمیر کے ساتھ رکھا
- [ ] `useDocs = False` پیداوار میں اگر API اسکیما عوامی نہیں ہونا چاہئے۔
- [] `useTrustedHost` اور `useHTTPSRedirect` عوامی تعیناتیوں کے لیے مقرر
- [ ] `__nexy__/` کا ارتکاب نہیں کیا۔

## اگلے اقدامات

- [Config](../reference/config.md): HTTPS، قابل اعتماد میزبان، سیشن
- [فرنٹ اینڈ ](../guides/frontend.md): کیا Vite بناتا ہے۔
- [ٹیسٹنگ](../guides/testing.md): CI میں چلانے کے لیے کمانڈز
