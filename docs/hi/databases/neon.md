# नेक्सी के साथ नियॉन का प्रयोग करें

नियॉन सर्वर रहित है PostgreSQL: एक नेक्सी प्रोजेक्ट इसे [PostgreSQL](postgresql.md) की तरह उपयोग करता है, `psycopg` ड्राइवर के साथ, `DATABASE_URL` में नियॉन की पूल की गई कनेक्शन स्ट्रिंग, और एक पूल जो डेटाबेस को स्लीप में जाने से बचाता है।

## कनेक्शन तार प्राप्त करें

नियॉन कंसोल में, **कनेक्ट** प्रत्येक शाखा के लिए दो स्ट्रिंग दिखाता है:

| स्ट्रिंग | मेज़बान | इसके लिए इसका उपयोग करें |
|---|---|---|
| जमा हुआ | `ep-xxx-pooler.region.aws.neon.tech` | ऐप: PgBouncer के माध्यम से कई छोटे कनेक्शन |
| प्रत्यक्ष | `ep-xxx.region.aws.neon.tech` | प्रवास और लंबे सत्र |

एकमात्र अंतर होस्ट नाम में `-pooler` है।

## ड्राइवर स्थापित करें

```bash
uv add "psycopg[binary]"
```

HTTP पर नियॉन का सर्वर रहित ड्राइवर JavaScript के लिए है; Python से कनेक्शन टीसीपी और टीएलएस पर सामान्य PostgreSQL है।

## दो यूआरएल

```bash filename=".env"
DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3-pooler.eu-central-1.aws.neon.tech/app?sslmode=require
DIRECT_DATABASE_URL=postgresql+psycopg://app_owner:secret@ep-cool-sun-a1b2c3.eu-central-1.aws.neon.tech/app?sslmode=require
```

नियॉन अपनी स्ट्रिंग्स को `postgresql://...` के रूप में कॉपी करता है: `postgresql` के बाद `+psycopg` जोड़ें। जब कंसोल इसे जोड़ता है तो `sslmode=require`, और `channel_binding=require` रखें।

## इंजन

निष्क्रिय होने पर नियॉन गणना निलंबित हो जाती है, जिससे आपके पूल के कनेक्शन बंद हो जाते हैं। `pool_pre_ping` उपयोग करने से पहले ही खराब हो चुके कनेक्शन को बदल देता है, और `pool_recycle` नियॉन से पहले कनेक्शन हटा देता है:

```python filename="src/configs/db.py"
import os

from dotenv import load_dotenv
from sqlmodel import create_engine

load_dotenv()

engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_size=5,
    max_overflow=5,
    pool_pre_ping=True,
    pool_recycle=300,
)
```

निलंबन के बाद पहला अनुरोध गणना शुरू होने तक कुछ सौ मिलीसेकेंड तक प्रतीक्षा करता है। यदि यह आपके लिए मायने रखता है तो उत्पादन शाखा पर ऑटोसस्पेंड बंद करें।

## एक मॉडल और एक हैंडलर

शेष PostgreSQL है। एक मॉडल:

```python filename="src/models/visit_model.py"
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Visit(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    path: str
    at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True)),
    )
```

```python filename="src/configs/session.py"
from collections.abc import Iterator

from sqlmodel import Session

from src.configs.db import engine


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
```

```python filename="src/routes/api/visits.py"
from sqlmodel import Session, func, select

from nexy.http import Depends
from src.configs.session import get_session
from src.models.visit_model import Visit


async def POST(path: str, session: Session = Depends(get_session)):
    session.add(Visit(path=path))
    session.commit()
    return {"visits": session.exec(select(func.count()).select_from(Visit)).one()}
```

## माइग्रेशन सीधे URL से होते हैं

पूल किए गए होस्ट के सामने PgBouncer ग्राहकों के बीच कनेक्शन साझा करता है, जो छोटे प्रश्नों के लिए उपयुक्त है, माइग्रेशन के लंबे सत्र के लिए नहीं। `nx migrate` पढ़ता है `DATABASE_URL`, इसलिए इसे उस कमांड के लिए सीधे होस्ट पर इंगित करें:

```bash
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate -m "create visits"
DATABASE_URL="$DIRECT_DATABASE_URL" nx migrate --upgrade
```

`alembic/env.py` `src/configs/db.py` के इंजन का उपयोग करता है, जो समान चर को पढ़ता है।

## पूलर के पीछे तैयार किए गए बयान

psycopg एक क्वेरी तैयार करता है जिसे वह पांच बार चला चुका है। यदि पूल किया गया होस्ट उत्तर देता है `prepared statement "_pg3_0" does not exist`, तो उसे बंद कर दें:

```python filename="src/configs/db.py"
engine = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"prepare_threshold": None},
)
```

`asyncpg` के साथ, सेटिंग `connect_args={"statement_cache_size": 0}` है।

## विकास और पूर्वावलोकन के लिए शाखाएँ

नियॉन शाखा एक डेटाबेस की एक प्रति है, जो एक सेकंड में बनाई जाती है। प्रति डेवलपर, या प्रति पुल अनुरोध, परीक्षण डेटा को उत्पादन से दूर रखता है:

```bash
neonctl branches create --name dev-ada
neonctl connection-string dev-ada --pooled
```

उस स्ट्रिंग को डेवलपर के `.env` में, या पूर्वावलोकन परिनियोजन के वातावरण में रखें।

## परीक्षण

उनके लिए बनाई गई शाखा के विरुद्ध परीक्षण चलाएँ, एक लेन-देन के अंदर जिसे वापस लाया जाता है: [लेन-देन में परीक्षण](postgresql.md#tests-in-a-transaction) देखें।

## अगले चरण

- [उपयोग करें PostgreSQL नेक्सी के साथ](postgresql.md): प्रकार, खोज, अपसर्ट और एसिंक
- [डेटाबेस](../guides/databases.md)
- [तैनाती](../deployment/README.md)
