# گارڈز اور میٹا ڈیٹا

ڈیکوریٹر جو کسی راستے کی حفاظت کرتے ہیں اور اسے OpenAPI اسکیما میں بیان کرتے ہیں۔

## گارڈز

`@UseGuard(*guards)` ایک کنٹرولر (ہر طریقہ) یا ایک طریقہ پر کام کرتا ہے۔ ہر گارڈ کو بطور FastAPI `Depends` شامل کیا جاتا ہے، لہٰذا یہ اپنی ضرورت کے پیرامیٹرز کا اعلان کرتا ہے اور کال کو مسترد کرنے کے لیے اٹھاتا ہے:

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## مڈل ویئر ڈیکوریٹر

`@Middleware(*middlewares)` اسی طرح برتاؤ کرتا ہے: یہ FastAPI انحصار ہیں، ASGI مڈل ویئر نہیں۔ حقیقی ASGI مڈل ویئر کے لیے [کنفیگ](../../reference/config.md) یا [Midleware and security](../../guides/middleware-and-security.md) میں `useMiddlewares` کا استعمال کریں۔

## روٹ میٹا ڈیٹا

`@UseRoute(...)` میٹا ڈیٹا OpenAPI سیٹ کرتا ہے۔ اس سے راستہ نہیں بدلتا۔

| دلیل | مطلب |
|---|---|
| `name` | راستے کا نام |
| `tags` | OpenAPI ٹیگز |
| `summary`، `description` | API حوالہ میں متن |
| `deprecated` | آپریشن کو فرسودہ نشان زد کریں۔ |
| `include_in_schema` | اسکیما سے راستے کو چھپائیں |
| `operation_id` | واضح آپریشن آئی ڈی |
| `openapi_extra` | اضافی OpenAPI فیلڈز |

## جوابات

`@UseResponse(...)` سیٹ `status_code`، `response_class`، `response_model`، `responses` اور سیریلائزیشن کے اختیارات۔

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller("/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

تیار کردہ API کا حوالہ `/docs` پر پیش کیا جاتا ہے جب تک کہ `useDocs = False`۔

## اگلے اقدامات

- [انحصار انجکشن](dependency-injection.md)
- [API روٹس](../fbr/handlers/README.md): فائل پر مبنی ہینڈلرز کے لیے وہی اختیارات
