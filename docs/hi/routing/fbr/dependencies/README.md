# निर्भरता और रक्षक

FastAPI निर्भरता वाले मार्गों पर प्रमाणीकरण, डेटाबेस सत्र और अन्य सेटअप साझा करें। वे दो स्तरों पर काम करते हैं, और निर्देशिका स्तर लेआउट की तरह विरासत में मिला है।

| स्तर | जहां | | पर लागू होता है
|---|---|---|
| निर्देशिका | `dependencies.py` | निर्देशिका में प्रत्येक मार्ग और नीचे, पृष्ठ शामिल हैं |
| हैंडलर | `Depends`, `@UseGuard`, `@Middleware` | एक हैंडलर |

## प्रति निर्देशिका: `dependencies.py`

एक `dependencies.py` सादे कार्यों की एक `dependencies` सूची घोषित करता है। नेक्सी प्रत्येक को `Depends` में लपेटता है।

```python filename="src/routes/admin/dependents.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!NOTE]
> कार्यों को स्वयं सूचीबद्ध करें। सूची में एक `Depends(...)` ऑब्जेक्ट को नजरअंदाज कर दिया गया है।

`src/routes/admin/` के अंतर्गत प्रत्येक रूट के लिए अब हेडर, `.py` हैंडलर और `.nexy` पेजों की आवश्यकता होती है।

## विरासत

निर्भरताएँ रूट रूट से रूट की निर्देशिका तक एकत्र की जाती हैं, **सबसे बाहरी पहले**, बिल्कुल लेआउट की तरह, और हैंडलर के अपने गार्ड सबसे अंत में चलते हैं:

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

`GET /admin/users` के लिए क्रम है `root`, `admin`, `users`, हैंडलर के `@UseGuard` फ़ंक्शन, इसके `@Middleware` फ़ंक्शन, फिर हैंडलर। एक रूट समूह (`(group)/`) किसी अन्य की तरह एक निर्देशिका है, इसलिए इसका `dependencies.py` भाग लेता है।

## प्रति हैंडलर

किसी भी FastAPI ऐप की तरह, हस्ताक्षर में `Depends` का उपयोग करें:

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## एक हैंडलर पर गार्ड और मिडलवेयर

`@UseGuard` और `@Middleware` किसी हैंडलर के हस्ताक्षर को बदले बिना उस पर FastAPI निर्भरताएँ जोड़ते हैं। दोनों निर्भरताएँ हैं, ASGI मिडलवेयर नहीं:

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

वास्तविक एएसजीआई मिडलवेयर (CORS, GZip, सत्र, आपका अपना) के लिए `useMiddlewares` और `use*` विकल्पों का उपयोग [मिडलवेयर और सुरक्षा](../../../guides/middleware-and-security.md) में करें।

## निर्भरता का असफल होना

एक निर्भरता किसी अनुरोध को बढ़ाकर अस्वीकार कर देती है। `HTTPException` आपके द्वारा उठाए गए स्टेटस के साथ उत्तर देता है, एपीआई क्लाइंट के लिए JSON के रूप में (`Accept: application/json`) और ब्राउज़र के लिए एक त्रुटि पृष्ठ के रूप में। [सत्यापन और त्रुटियाँ](../handlers/validation-and-errors.md) देखें।

## अगले चरण

- [विरासत](../inheritance.md)
- [हैंडलर](../handlers/README.md)
- [मिडिलवेयर और सुरक्षा](../../../guides/middleware-and-security.md)
