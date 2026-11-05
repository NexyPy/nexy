# व्यंजन विधि

लगभग हर ऐप को तीन चीज़ों की ज़रूरत होती है, संपूर्ण फ़ाइलों के रूप में जिन्हें आप कॉपी कर सकते हैं। `filename` के साथ नीचे दिया गया प्रत्येक कोड ब्लॉक एक नए प्रोजेक्ट में लिखा गया है और परीक्षण सूट द्वारा प्रयोग किया जाता है, इसलिए आप जो पढ़ते हैं वही चलता है।

वे सादे एपीआई हैंडलर का उपयोग करते हैं; समान फ़ंक्शन किसी पृष्ठ के पीछे [मोड](../routing/fbr/modes.md) में काम करते हैं।

## एक सत्र के साथ साइन इन करें

एक विज़िटर एक नाम और एक पासवर्ड पोस्ट करता है, सर्वर उन्हें एक हस्ताक्षरित कुकी में याद रखता है, और `/api/account` के तहत सब कुछ किसी और के लिए बंद है।

सत्र चालू करें. उन्हें `itsdangerous` (`uv add itsdangerous`) की आवश्यकता है:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me-in-production"}
```

साइन इन करें और बाहर जाएं:

```python filename="src/routes/api/login.py"
from pydantic import BaseModel

from nexy.http import HTTPException, Request

USERS = {"ada": "lovelace"}


class Credentials(BaseModel):
    name: str
    password: str


async def POST(request: Request, body: Credentials):
    if USERS.get(body.name) != body.password:
        raise HTTPException(status_code=401, detail="Wrong name or password")
    request.session["user"] = body.name
    return {"user": body.name}
```

```python filename="src/routes/api/logout.py"
from nexy.http import Request


async def POST(request: Request):
    request.session.clear()
    return {"signed_out": True}
```

एक [`dependencies.py`](../routing/fbr/dependencies/README.md) से पूरे फ़ोल्डर की सुरक्षा करें:

```python filename="src/routes/api/account/dependents.py"
from nexy.http import HTTPException, Request


def current_user(request: Request) -> str:
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Sign in first")
    return request.session["user"]


dependencies = [current_user]
```

```python filename="src/routes/api/account/index.py"
from nexy.http import Request


async def GET(request: Request):
    return {"user": request.session["user"]}
```

> [!नोट]
> वास्तविक पासवर्ड को स्रोत से दूर रखें। एक हैश (`argon2`, `bcrypt`) संग्रहित करें और परिवेश से गुप्त कुंजी पढ़ें। सत्र कुकी हस्ताक्षरित है, एन्क्रिप्टेड नहीं।

## बनाने, पढ़ने और हटाने के साथ एक JSON एपीआई

एक मॉड्यूल में एक स्टोर, एक संग्रह मार्ग और एक आइटम मार्ग। जब डेटा पुनः आरंभ होना चाहिए तो शब्दकोश को [डेटाबेस](databases.md) से बदलें।

```python filename="src/notes.py"
from pydantic import BaseModel


class Note(BaseModel):
    id: int
    title: str


NOTES: dict[int, Note] = {}
```

```python filename="src/routes/api/notes/index.py"
from pydantic import BaseModel

from src.notes import NOTES, Note


class NewNote(BaseModel):
    title: str


async def GET() -> list[Note]:
    return list(NOTES.values())


async def POST(body: NewNote) -> Note:
    note = Note(id=max(NOTES, default=0) + 1, title=body.title)
    NOTES[note.id] = note
    return note
```

```python filename="src/routes/api/notes/[id].py"
from nexy.http import HTTPException

from src.notes import NOTES, Note


async def GET(id: int) -> Note:
    if id not in NOTES:
        raise HTTPException(status_code=404, detail="No such note")
    return NOTES[id]


async def DELETE(id: int) -> dict[str, bool]:
    if NOTES.pop(id, None) is None:
        raise HTTPException(status_code=404, detail="No such note")
    return {"deleted": True}
```

आपके कोड के चलने से पहले एक बॉडी जो `NewNote` में फिट नहीं होती, उसे `422` के साथ अस्वीकार कर दिया जाता है, और रिटर्न एनोटेशन दस्तावेजी प्रतिक्रिया बन जाता है। [सत्यापन और त्रुटियाँ](../routing/fbr/handlers/validation-and-errors.md) देखें।

## एक फ़ाइल प्राप्त करें

अपलोड के लिए `python-multipart` (`uv add python-multipart`) की आवश्यकता है। आकार स्वयं जांचें, और कभी भी क्लाइंट के फ़ाइल नाम को पथ के रूप में उपयोग न करें:

```python filename="src/routes/api/upload.py"
from pathlib import Path

from nexy.http import HTTPException, UploadFile

MAX_BYTES = 1_000_000


async def POST(file: UploadFile) -> dict[str, int | str]:
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large")
    name = Path(file.filename or "upload").name
    return {"name": name, "size": len(data)}
```

`Path(...).name` क्लाइंट द्वारा नाम में रखे गए किसी भी फ़ोल्डर को हटा देता है, जैसे कि `../../etc/passwd`। बाइट्स को आपके द्वारा जेनरेट किए गए नाम के अंतर्गत सहेजें, इस नाम के अंतर्गत नहीं।

## अगले चरण

- [क्रियाएँ](actions.md): प्रपत्रों और बटनों के लिए टाइप किया गया सर्वर फ़ंक्शन
- [मिडिलवेयर और सुरक्षा](middleware-and-security.md): सीओआरएस, होस्ट, सत्र
- [परीक्षण](testing.md): उसी तरह अपने स्वयं के संचालकों का परीक्षण करें
