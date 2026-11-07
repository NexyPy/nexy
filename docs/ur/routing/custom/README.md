# Nexy میں ایک موجودہ FastAPI راؤٹر شامل کریں۔

Nexy میں موجودہ FastAPI راؤٹر کو شامل کرنے کے لیے، `useRouter` کو `APIRouter` کی `NexyConfig` کلاس میں `nexyconfig.py` پر سیٹ کریں: اس کے روٹس `src/routes/` کی فائلوں کے ساتھ ہی پیش کیے جاتے ہیں۔

## کسٹم راؤٹر کب استعمال کریں۔

- **بتدریج ہجرت**: ایک FastAPI ایپ بذریعہ راستے Nexy کی طرف جاتی ہے، اور اس کے پرانے راستے اس دوران جواب دیتے رہتے ہیں۔
- **کوڈ کا دوبارہ استعمال**: ایک پیکج تصدیق یا بلنگ کے لیے پہلے سے ہی ایک `APIRouter` کو ظاہر کرتا ہے۔
- **ایک بیک اینڈ جو آپ رکھتے ہیں**: API سادہ رہتا ہے FastAPI، اور Nexy صفحات کو شامل کرتا ہے۔

## `nexyconfig.py` میں `useRouter` سیٹ کریں

راؤٹر کوئی بھی FastAPI `APIRouter` ہے، جس طرح سے آپ پہلے سے لکھتے ہیں:

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

`useRouter` پروجیکٹ کی ہر ترتیب کی طرح `NexyConfig` کلاس کا ایک فیلڈ ہے:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` پھر جواب دیتا ہے `GET /api/status` اور `GET /api/users/{id}`، اور `/docs` ان کی فہرست دیتا ہے۔

> [!NOTE]
> `useRouter` `nexyconfig.py` میں ایک ترتیب ہے۔ `from nexy import useRouter` ایک اور چیز ہے: ہک ایک `.nexy` صفحہ موجودہ روٹ کو پڑھنے کے لیے استعمال کرتا ہے۔ روٹر کو ترتیب دینے کے لیے اسے درآمد نہ کریں۔

## کئی راؤٹرز

`useRouter` ایک راؤٹر لیتا ہے۔ `include_router` کے ساتھ ایک والدین کے تحت کئی کو جمع کریں:

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

## اس کے ساتھ والے صفحات اور روٹ فائلز

`src/routes/` ابھی بھی پڑھا جاتا ہے جب کہ `useRouter` سیٹ ہوتا ہے: ایک `.nexy` صفحہ یا ایک `.py` روٹ فائل شامل راستوں کے ساتھ جواب دیتا ہے۔

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

دو حدود جبکہ `useRouter` مقرر ہیں:

- صفحات `layout.nexy` سے لپیٹے نہیں جاتے۔
- `useCSR = True` سے انکار کیا جاتا ہے: `nx dev` اور `nx build` جواب `useCSR requires file-based routing`۔

ایک URL کا جواب ایک بار دیا جاتا ہے۔ شامل روٹر کو یہاں `/api` کا سابقہ ​​دیں، اور `src/routes/` کی فائلوں کو اس کے استعمال کردہ راستوں سے دور رکھیں۔

## ایک پوری FastAPI ایپ

`useRouter` ایک `APIRouter` لیتا ہے، نہ کہ `FastAPI` ایپ۔ کسی ایپ کے روٹس اس کی `router` صفت پر بیٹھتے ہیں:

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

ایپ کے اپنے مڈل ویئر، استثنیٰ ہینڈلرز اور سٹارٹ اپ ایونٹس پیچھے رہتے ہیں: انہیں `useMiddlewares` اور `nexyconfig.py` کے دیگر شعبوں میں منتقل کریں۔

## انحصار، تصنیف اور ڈیٹا بیس

روٹر Nexy کے عمل میں چلتا ہے، لہذا `Depends`، سیکورٹی اسکیمیں اور ڈیٹا بیس سیشن اصل ایپ کی طرح کام کرتے ہیں:

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

## اس کی جانچ کریں۔

```python filename="tests/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## اگلے اقدامات

- [سے FastAPI سے Nexy](../../coming-from/fastapi.md): راستوں کو فائلوں میں منتقل کریں، ایک ایک کرکے
- [فائل پر مبنی روٹنگ](../fbr/README.md)
- [ماڈیولر روٹنگ](../modular/README.md): `useRouter = AppModule`
