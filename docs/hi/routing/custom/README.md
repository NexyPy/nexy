# नेक्सी में मौजूदा FastAPI राउटर शामिल करें

नेक्सी में मौजूदा FastAPI राउटर को शामिल करने के लिए, `nexyconfig.py` के `NexyConfig` वर्ग में `useRouter` को उस `APIRouter` पर सेट करें: इसके रूट वैसे ही परोसे जाते हैं, जैसे वे हैं, `src/routes/` की फाइलों के बगल में।

## कस्टम राउटर का उपयोग कब करें

- **क्रमिक माइग्रेशन**: एक FastAPI ऐप मार्ग से नेक्सी मार्ग पर चला जाता है, और इसके पुराने मार्ग इस बीच जवाब देते रहते हैं।
- **कोड का पुन: उपयोग**: प्रमाणीकरण या बिलिंग के लिए एक पैकेज पहले से ही एक `APIRouter` को उजागर करता है।
- **एक बैकएंड जो आप रखते हैं**: एपीआई सादा रहता है FastAPI, और नेक्सी पेज जोड़ता है।

## `useRouter` को `nexyconfig.py` में सेट करें

राउटर कोई भी FastAPI `APIRouter` है, जिस तरह से आप पहले से ही लिखते हैं:

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

`useRouter` प्रोजेक्ट की हर सेटिंग की तरह, `NexyConfig` वर्ग का एक क्षेत्र है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` फिर `GET /api/status` और `GET /api/users/{id}` का उत्तर देता है, और `/docs` उन्हें सूचीबद्ध करता है।

> [!NOTE]
> `useRouter` में `nexyconfig.py` एक सेटिंग है। `from nexy import useRouter` एक और चीज़ है: `.nexy` पृष्ठ वर्तमान मार्ग को पढ़ने के लिए जिस हुक का उपयोग करता है। राउटर को कॉन्फ़िगर करने के लिए इसे आयात न करें।

## कई राउटर

`useRouter` एक राउटर लेता है। `include_router` के साथ एक माता-पिता के अधीन कई लोगों को इकट्ठा करें:

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

## इसके आगे वाले पेज और रूट फ़ाइलें

`src/routes/` अभी भी पढ़ा जाता है जबकि `useRouter` सेट है: एक `.nexy` पृष्ठ या एक `.py` रूट फ़ाइल शामिल मार्गों के बगल में उत्तर देती है।

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

`useRouter` निर्धारित होने पर दो सीमाएँ:

- पन्ने `layout.nexy` द्वारा लपेटे नहीं गए हैं;
- `useCSR = True` को अस्वीकार कर दिया गया है: `nx dev` और `nx build` उत्तर देते हैं `useCSR requires file-based routing`।

एक URL का उत्तर एक बार दिया जाता है. शामिल राउटर को एक उपसर्ग दें, यहां `/api`, और `src/routes/` की फ़ाइलों को उसके द्वारा उपयोग किए जाने वाले पथ से दूर रखें।

## एक संपूर्ण FastAPI ऐप

`useRouter` एक `APIRouter` लेता है, `FastAPI` ऐप नहीं। किसी ऐप के रूट उसकी `router` विशेषता पर आधारित होते हैं:

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

ऐप के स्वयं के मिडलवेयर, अपवाद हैंडलर और स्टार्टअप इवेंट पीछे रहते हैं: उन्हें `useMiddlewares` और `nexyconfig.py` के अन्य क्षेत्रों में ले जाएं।

## निर्भरताएँ, प्रमाणीकरण और डेटाबेस

राउटर नेक्सी प्रक्रिया में चलता है, इसलिए `Depends`, सुरक्षा योजनाएं और डेटाबेस सत्र मूल ऐप की तरह काम करते हैं:

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

## इसका परीक्षण करें

```python filename="परीक्षण/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## अगले चरण

- [से FastAPI से नेक्सी](../../coming-from/fastapi.md): रूटों को फ़ाइलों तक एक-एक करके ले जाएं
- [फ़ाइल-आधारित रूटिंग](../fbr/README.md)
- [मॉड्यूलर रूटिंग](../modular/README.md): `useRouter = AppModule`
