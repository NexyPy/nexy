# गार्ड और मेटाडेटा

डेकोरेटर जो किसी मार्ग की सुरक्षा करते हैं और ओपनएपीआई स्कीमा में उसका वर्णन करते हैं।

## रक्षक

`@UseGuard(*guards)` एक नियंत्रक (प्रत्येक विधि) या एक विधि पर काम करता है। प्रत्येक गार्ड को एक के रूप में जोड़ा जाता है
फास्टएपीआई `Depends`, इसलिए यह आवश्यक मापदंडों की घोषणा करता है और कॉल को अस्वीकार करने के लिए उठाता है:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## मिडिलवेयर डेकोरेटर

`@Middleware(*middlewares)` उसी तरह व्यवहार करता है: ये फास्टएपीआई निर्भरताएं हैं, एएसजीआई नहीं
मिडलवेयर. वास्तविक एएसजीआई मिडलवेयर के लिए `useMiddlewares` का उपयोग करें
[कॉन्फिग](../../reference/config.md) या [मिडिलवेयर और सुरक्षा](../../guides/middleware-and-security.md)।

## रूट मेटाडेटा

`@UseRoute(...)` ओपनएपीआई मेटाडेटा सेट करता है। यह रास्ता नहीं बदलता.

| तर्क | अर्थ |
|---|---|
| `name` | मार्ग का नाम |
| `tags` | ओपनएपीआई टैग |
| `summary`, `description` | एपीआई संदर्भ में पाठ |
| `deprecated` | ऑपरेशन को अस्वीकृत चिह्नित करें |
| `include_in_schema` | स्कीमा से मार्ग छुपाएं |
| `operation_id` | स्पष्ट ऑपरेशन आईडी |
| `openapi_extra` | अतिरिक्त ओपनएपीआई फ़ील्ड |

## प्रतिक्रियाएँ

`@UseResponse(...)` सेट `status_code`, `response_class`, `response_model`, `responses` और
क्रमांकन विकल्प.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

उत्पन्न एपीआई संदर्भ `/docs` पर परोसा जाता है जब तक कि `useDocs = False` नहीं।

## अगले चरण

- [निर्भरता इंजेक्शन](dependency-injection.md)
- [एपीआई मार्ग](../fbr/handlers/README.md): फ़ाइल-आधारित हैंडलर के लिए समान विकल्प