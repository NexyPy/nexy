# نشر

أمران: `nx build` ينتج المصنوعات، `nx start` يخدمها.

**قبل أن تبدأ:** مشروع يتم إنشاؤه محليًا باستخدام `nx build`، و- بالنسبة لصفحات العميل - سلسلة أدوات الواجهة الأمامية التي تم تثبيتها `nx new`.

```bash
nx build
nx start --host 0.0.0.0 --port 8000
```

يحتاج وقت التشغيل إلى Python فقط. Uvicorn يخدم التطبيق المترجم والأصول الثابتة؛ لا توجد عملية عقدة ولا توجد عملية Vite متضمنة.

## ما ينتج البناء

`__nexy__/` يحتوي على وحدات المسار المجمعة، وحزمة العميل ضمن `__nexy__/client/`، وHTML المعروض مسبقًا لمسارات إطار العمل. انسخ المشروع - المصدر بالإضافة إلى `__nexy__/` - أو أنشئ داخل الصورة.

## Docker

تحتاج مرحلة البناء إلى العقدة (لـ Vite) و Python (للمترجم). تحتاج مرحلة التشغيل إلى Python فقط.

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

`uv` يجلب Python مُدارًا عندما لا تحتوي الصورة الأساسية على أي شيء، ولهذا السبب يمكن أن تبدأ مرحلة البناء من صورة العقدة.

## خلف وكيل عكسي

قم بتشغيل `nx start` على المضيف المحلي واترك Nginx أو Caddy أو وكيل النظام الأساسي ينهي TLS:

```bash
nx start --host 127.0.0.1 --port 8000
```

تأكد من أن الوكيل يعيد توجيه ترقيات WebSocket إذا كنت تستخدم معالجات `SOCKET`، وأنه يعيد توجيه المضيف الأصلي - FastAPI ينشئ عناوين URL مطلقة منه.

## فحص الصحة

<!-- router:fbr,custom -->
قم بإضافة ملف معالج، `src/routes/api/health.py`، ومسبار `/api/health` - بدلاً من الصفحة التي قد يتم عرضها ببطء:

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```
<!-- /router -->

<!-- router:modular -->
أضف وحدة تحكم، واختبر `/health/` - بدلاً من العرض الذي قد يتم عرضه ببطء:

```python filename="src/apps/health_controller.py"
from nexy.decorators import Controller


@Controller("/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```

أدرجها في `controllers` من الوحدة الجذرية.
<!-- /router -->

## استضافة ثابتة

كل صفحة هي HTML، ولكن Nexy يفترض وجود خادم للتوجيه ومعالجات API.

> [!NOTE]
> لا يوجد `--static` وضع البناء. يجب إنشاء تصدير ثابت تمامًا في خط الأنابيب الخاص بك من الإخراج `nx build`.

## قائمة التحقق

- [ ] `nx build` في CI، لا توجد تحذيرات للمسارات التي تتوقع عرضها على الخادم
- [ ] `nx start` يخرج بالكود 1، ولا يبدأ بأي شيء، عندما لا يمكن تحميل ملف المسار
- [ ] `NEXY_ACTION_SECRET` مجموعة، أو `__nexy__/action.key` محفوظة مع البناء
- [ ] `useDocs = False` في الإنتاج إذا لم يكن مخطط API عامًا
- [ ] `useTrustedHost` و `useHTTPSRedirect` تم ضبطهما للنشر العام
- [ ] `__nexy__/` غير ملتزم

## الخطوات التالية

- [التكوين ](../reference/config.md): HTTPS، المضيفين الموثوقين، الجلسات
- [الواجهة](../guides/frontend.md): ما يبنيه Vite
- [الاختبار](../guides/testing.md): الأوامر التي سيتم تشغيلها في CI
