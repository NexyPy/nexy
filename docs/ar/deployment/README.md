# نشر

أمران: `nx build` ينتج المصنوعات، `nx start` يخدمها.

**قبل البدء:** مشروع يتم إنشاؤه محليًا باستخدام `nx build`، و- بالنسبة لصفحات العميل -
سلسلة أدوات الواجهة الأمامية التي تم تثبيتها `nx new`.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

يحتاج وقت التشغيل إلى لغة بايثون فقط. يقدم Uvicorn التطبيق المترجم والأصول الثابتة؛ لا عقدة
العملية ولا توجد عملية Vite متضمنة.

## ما ينتجه البناء

`__nexy__/` يحتوي على وحدات المسار المترجمة، وحزمة العميل ضمن `__nexy__/client/`، و
HTML معروض مسبقًا لمسارات إطار العمل. انسخ المشروع - المصدر بالإضافة إلى `__nexy__/` - أو أنشئ بداخله
الصورة.

## عامل الميناء

تحتاج مرحلة البناء إلى Node (لـ Vite) وPython (للمترجم). تحتاج مرحلة التشغيل إلى لغة بايثون
فقط.

```dockerfile filename="ملف الإرساء"
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

`uv` يجلب لغة بايثون مُدارة عندما لا تحتوي الصورة الأساسية على أي شيء، ولهذا السبب يمكن أن تبدأ مرحلة البناء
من صورة العقدة.

## وراء وكيل عكسي

قم بتشغيل `nx start` على المضيف المحلي واترك Nginx أو Caddy أو وكيل النظام الأساسي ينهي TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

تأكد من أن الوكيل يعيد توجيه ترقيات WebSocket إذا كنت تستخدم معالجات `SOCKET`، وأنه يعيد توجيهها
المضيف الأصلي - يقوم FastAPI ببناء عناوين URL مطلقة منه.

## فحص الصحة

أضف ملف معالج، `src/routes/api/health.py`، واختبر `/api/health` - بدلاً من الصفحة التي قد
تقديم ببطء:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

## استضافة ثابتة

كل صفحة هي HTML، ولكن Nexy يفترض وجود خادم للتوجيه ومعالجات API.

> [!ملاحظة]
> لا يوجد `--static` وضع البناء. يجب إنشاء تصدير ثابت بحت
> خط الأنابيب الخاص بك من مخرج `nx build`.

## قائمة المراجعة

-  [ ] `nx build` في CI، لا توجد تحذيرات للمسارات التي تتوقع عرضها على الخادم
-  [ ] `nx start` يخرج بالرمز 1، ولا يبدأ بأي شيء، عندما لا يمكن تحميل ملف المسار
- [ ] `NEXY_ACTION_SECRET` مجموعة، أو `__nexy__/action.key` أبقى مع البناء
-  [ ] `useDocs = False` في الإنتاج إذا لم يكن مخطط API عامًا
-  [ ] `useTrustedHost` و `useHTTPSRedirect` تم ضبطهما للنشر العام
- [ ] `__nexy__/` غير ملتزم

## الخطوات التالية

- [التكوين](../reference/config.md): HTTPS، المضيفين الموثوقين، الجلسات
- [Frontend](../guides/frontend.md): ما يبنيه فايت
- [الاختبار](../guides/testing.md): الأوامر المطلوب تشغيلها في CI