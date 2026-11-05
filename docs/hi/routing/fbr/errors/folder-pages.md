# प्रति फ़ोल्डर त्रुटि पृष्ठ

एक फ़ोल्डर अपनी त्रुटियों का उत्तर स्वयं दे सकता है: अपने शब्दों में 404 वाला एक ब्लॉग, एक निजी क्षेत्र जो खाली `401` के बजाय साइन-इन फ़ॉर्म प्रदान करता है। साइट का शेष भाग वही पृष्ठ रखता है जो उसके पास पहले से था।

यह पृष्ठ उन फ़ाइलों में से एक को जोड़ता है और उसका उत्तर दिखाता है।

## नियम

**सबसे गहरी फ़ाइल जो URL से मेल खाती है उत्तर।** बाकी सब कुछ वैसा ही रहता है: समान स्थिति कोड, एक एपीआई क्लाइंट के लिए JSON, और एक बार श्रृंखला के किसी भी फ़ोल्डर में फ़ाइल न होने पर अंतर्निहित पृष्ठ।

![त्रुटि पृष्ठ का दायरा](../../../assets/error-page-scopes.svg)

`/blog/2024/hello` के लिए नेक्सी पेड़ पर चढ़ती है: `/blog/2024`, फिर `/blog`, फिर `/`। फ़ाइल रखने वाला पहला फ़ोल्डर उत्तर देता है। एक फ़ोल्डर पूर्ण रूप से मेल खाता है: `/blogger/hello` `/blog` के अंतर्गत नहीं है, इसलिए `blog/` में एक प्रतिलिपि कभी भी इसका उत्तर नहीं देती है।

## चार फ़ाइलें

| फ़ाइल | उत्तर | उस तक क्या पहुंचता है |
|---|---|---|
| `notfound.nexy` | `404` | एक यूआरएल जिसका रूट मेल नहीं खाता, `notFound()` |
| `errors.nexy` | `500` | एक अपवाद जिसे कुछ भी नहीं संभाला गया |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` आरक्षित रहता है: इसका अभी तक कोई रनटाइम प्रभाव नहीं है।

`src/routes/` में कहीं एक फ़ाइल नेक्सी के लिए उस स्थिति का उत्तर देने के लिए पर्याप्त है: रूट पर एक कॉपी पूरे प्रोजेक्ट का उत्तर देती है, एक फ़ोल्डर में एक कॉपी उस फ़ोल्डर का उत्तर देती है, और प्रत्येक कॉपी के बाहर एक यूआरएल को अंतर्निहित पृष्ठ मिलता है। `nexyconfig.py` में `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` और `useUnauthorizedExtensions` के साथ इन नामों के लिए एक और एक्सटेंशन आरक्षित करें।

## आपका पहला फ़ोल्डर पृष्ठ

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

प्रोजेक्ट चलाएँ और उस पोस्ट के लिए पूछें जो मौजूद नहीं है:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

फ़ोल्डर के बाहर एक URL वह पृष्ठ रखता है जो आपके पास पहले से है:

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## एक 401 जो कहीं ले जाता है

संरक्षित क्षेत्र का फ़ोल्डर उस पृष्ठ के साथ उत्तर देता है `401` जो अंदर जाने का रास्ता प्रदान करता है:

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependents.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

प्रत्येक कॉल और प्रत्येक स्टेटस के दो उत्तर होते हैं:

| कौन पूछता है | `401` एक फ़ाइल के साथ | `401` बिना फ़ाइल के |
|---|---|---|
| ब्राउज़र (`Accept: text/html`) | फ़ोल्डर का पृष्ठ | अंतर्निहित पृष्ठ |
| ग्राहक (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` दोनों उत्तरों में `WWW-Authenticate: Bearer` जोड़ता है। उपयोगकर्ता इनपुट से निर्मित विवरण पृष्ठ में HTML-एस्केप्ड है।

> [!टिप]
> `Accept: */*`, `curl` और कई HTTP लाइब्रेरीज़ का डिफ़ॉल्ट, न तो मांगता है और न ही HTML पेज प्राप्त करता है। जब आप JSON उत्तर चाहते हैं तो `-H "Accept: application/json"` जोड़ें।

## इसकी जांच करें

```python filename="परीक्षण/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## अगले चरण

- [त्रुटि पृष्ठ](README.md): प्रत्येक स्थिति को क्या ट्रिगर करता है, HTML या JSON
- [निर्भरताएं और गार्ड](../dependencies/README.md): पूरे फ़ोल्डर की सुरक्षा करें
- [परीक्षण](../../../guides/testing.md): `TestClient` पहले परीक्षण से
