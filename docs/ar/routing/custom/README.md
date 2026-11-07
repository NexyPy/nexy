# قم بتضمين جهاز توجيه FastAPI موجود في Nexy

لتضمين جهاز توجيه FastAPI موجود في Nexy، قم بتعيين `useRouter` على ذلك `APIRouter` في فئة `NexyConfig` من `nexyconfig.py`: يتم تقديم مساراته كما هي، بجوار ملفات `src/routes/`.

## متى تستخدم جهاز توجيه مخصص

- **الترحيل التدريجي**: ينتقل تطبيق FastAPI إلى مسار Nexy عن طريق المسار، وتستمر مساراته القديمة في الرد في هذه الأثناء.
- **إعادة استخدام الكود**: تعرض الحزمة بالفعل `APIRouter` للمصادقة أو الفوترة.
- **الواجهة الخلفية التي تحتفظ بها**: تظل واجهة برمجة التطبيقات (API) عادية FastAPI، ويضيف Nexy الصفحات.

## تعيين `useRouter` في `nexyconfig.py`

جهاز التوجيه هو أي FastAPI `APIRouter`، مكتوبًا بالطريقة التي تكتب بها واحدًا بالفعل:

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` هو حقل من فئة `NexyConfig`، مثل كل إعدادات المشروع:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` ثم يجيب على `GET /api/status` و `GET /api/users/{id}`، ويسردهما `/docs`.

> [!NOTE]
> `useRouter` في `nexyconfig.py` هو إعداد. `from nexy import useRouter` شيء آخر: الخطاف الذي تستخدمه صفحة `.nexy` لقراءة المسار الحالي. لا تقم باستيراده لتكوين جهاز التوجيه.

## عدة أجهزة التوجيه

`useRouter` يأخذ جهاز توجيه واحد. جمع عدة تحت أحد الوالدين مع `include_router`:

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## الصفحات وملفات المسار بجانبه

لا تزال `src/routes/` قيد القراءة أثناء تعيين `useRouter`: صفحة `.nexy` أو إجابات ملف المسار `.py` بجوار المسارات المضمنة.

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

حدان عند ضبط `useRouter`:

- الصفحات غير مغلفة بـ `layout.nexy`؛
- `useCSR = True` مرفوض: `nx dev` و `nx build` جواب `useCSR requires file-based routing`.

يتم الرد على عنوان URL مرة واحدة. امنح جهاز التوجيه المضمن بادئة، هنا `/api`، واحتفظ بملفات `src/routes/` بعيدًا عن المسارات التي يستخدمها.

## تطبيق كامل FastAPI

`useRouter` يأخذ تطبيق `APIRouter`، وليس تطبيق `FastAPI`. توجد مسارات التطبيق في السمة `router` الخاصة به:

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

تظل البرامج الوسيطة الخاصة بالتطبيق ومعالجات الاستثناءات وأحداث بدء التشغيل في الخلف: انقلها إلى `useMiddlewares` والحقول الأخرى في `nexyconfig.py`.

## التبعيات والمصادقة وقاعدة البيانات

يعمل جهاز التوجيه في عملية Nexy، لذلك تعمل `Depends` وأنظمة الأمان وجلسات قاعدة البيانات كما في التطبيق الأصلي:

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## اختبره

```python filename="الاختبارات/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## الخطوات التالية

- [من FastAPI إلى Nexy](../../coming-from/fastapi.md): انقل المسارات إلى الملفات، واحدًا تلو الآخر
- [التوجيه القائم على الملف](../fbr/README.md)
- [التوجيه المعياري](../modular/README.md): `useRouter = AppModule`
