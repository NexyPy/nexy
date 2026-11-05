# গার্ড এবং মেটাডেটা

ডেকোরেটর যারা একটি রুটকে রক্ষা করে এবং এটি OpenAPI স্কিমাতে বর্ণনা করে।

## রক্ষীরা

`@UseGuard(*guards)` একটি নিয়ামক (প্রতিটি পদ্ধতি) বা একটি পদ্ধতিতে কাজ করে। প্রতিটি গার্ডকে একটি FastAPI `Depends` হিসাবে যুক্ত করা হয়, তাই এটি প্রয়োজনীয় প্যারামিটারগুলি ঘোষণা করে এবং কলটি প্রত্যাখ্যান করার জন্য উত্থাপন করে:

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

## মিডলওয়্যার ডেকোরেটর

`@Middleware(*middlewares)` একইভাবে আচরণ করে: এগুলি FastAPI নির্ভরতা, ASGI মিডলওয়্যার নয়। আসল ASGI মিডলওয়্যারের জন্য [কনফিগ](../../reference/config.md) বা [মিডলওয়্যার এবং নিরাপত্তা](../../guides/middleware-and-security.md) এ `useMiddlewares` ব্যবহার করুন।

## রুট মেটাডেটা

`@UseRoute(...)` মেটাডেটা OpenAPI সেট করে। এতে পথের পরিবর্তন হয় না।

| যুক্তি | অর্থ |
|---|---|
| `name` | রুটের নাম |
| `tags` | OpenAPI ট্যাগ |
| API রেফারেন্সে `summary`, `description` | পাঠ্য |
| `deprecated` | অপারেশনটিকে অবচ্যুত চিহ্নিত করুন |
| `include_in_schema` | স্কিমা থেকে রুট লুকান |
| `operation_id` | স্পষ্ট অপারেশন আইডি |
| `openapi_extra` | অতিরিক্ত OpenAPI ক্ষেত্র |

## প্রতিক্রিয়া

`@UseResponse(...)` সেট করে `status_code`, `response_class`, `response_model`, `responses` এবং সিরিয়ালাইজেশন অপশন।

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

উত্পন্ন API রেফারেন্স `/docs` এ পরিবেশিত হয় যদি না `useDocs = False` হয়।

## পরবর্তী পদক্ষেপ

- [নির্ভরতা ইনজেকশন](dependency-injection.md)
- [API রুট](../fbr/handlers/README.md): ফাইল-ভিত্তিক হ্যান্ডলারদের জন্য একই বিকল্প
