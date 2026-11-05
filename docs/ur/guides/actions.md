# اعمال

ایک `@Action` ایک Python فنکشن کو `POST` اختتامی نقطہ میں بدل دیتا ہے۔ ایک معیاری API ہینڈلر کے برعکس، اسے ٹائپ شدہ کمیونیکیشن پل کے طور پر ڈیزائن کیا گیا ہے: Nexy خود بخود TypeScript کلائنٹ تیار کرتا ہے، ان پٹ کی توثیق کرتا ہے، اور جواب کو ہینڈل کرتا ہے۔

**اس سے پہلے کہ آپ شروع کریں:** ایک پروجیکٹ جسے [کوئیک اسٹارٹ](../getting-started/quick-start.md) نے بنایا ہے۔ اعمال `src/actions/` میں صفحات کے ساتھ رہتے ہیں۔

```diagram filename="ایکشن سائیکل"
Client (UI)  ─── 1. Call (Typed Input) ───► [ Nexy Bridge ]
                                                  │
                                                  ▼
                                      2. Validate & Execute (Python)
                                                  │
                                                  ▼
Client (UI)  ◄─── 5. Consume (Typed Result) ◄── 4. Serialize ◄── 3. Result
```

## ایکشن سائیکل

### 1. وضاحت کریں۔
ایک عمل ایک عام Python فنکشن ہے جسے `@Action` سے نشان زد کیا گیا ہے۔ Nexy API معاہدہ کی وضاحت کے لیے اپنے دستخط کا استعمال کرتا ہے۔

```python filename="src/actions/user.py"
from pydantic import BaseModel
from nexy.decorators import Action, revalidate

class User(BaseModel):
    name: str
    age: int = 0

@Action
async def create_user(name: str, age: int = 0) -> User:
    revalidate()
    return User(name=name, age=age)
```

پیرامیٹرز ان پٹ ہیں، جس کی توثیق Pydantic سے ہوتی ہے۔ `request` یا `response` نامی ایک پیرامیٹر انجکشن ہے اور ان پٹ کا حصہ نہیں ہے۔

### 2. توثیق کریں۔
جب ایکشن کو کال کیا جاتا ہے، Nexy فنکشن کی قسم کے اشارے کے خلاف ان پٹ کو درست کرتا ہے۔ اگر کوئی فیلڈ غائب ہے یا اس میں غلط قسم ہے تو، کارروائی عمل میں نہیں آتی ہے، اور ایک `422 Unprocessable Entity` لوٹا دیا جاتا ہے۔

### 3. پھانسی دینا
منطق سرور پر چلتی ہے۔ چونکہ یہ ایک معیاری Python فنکشن ہے، اس لیے آپ کسی بھی لائبریری کو استعمال کرسکتے ہیں، ڈیٹا بیس تک رسائی حاصل کرسکتے ہیں، یا دوسری خدمات کو کال کرسکتے ہیں۔ آپ `revalidate()` کا استعمال کرکے صفحہ کی تازہ کاری کو بھی متحرک کرسکتے ہیں۔

### 4. سیریلائز کریں۔
واپسی کی قدر خود بخود JSON پر سیریلائز ہو جاتی ہے۔ Pydantic ماڈلز کو مقامی طور پر ہینڈل کیا جاتا ہے، اور معیاری Python اقسام کو ان کے JSON مساوی کے ساتھ میپ کیا جاتا ہے۔

### 5. استعمال کرنا
فرنٹ اینڈ کو مکمل قسم کی حفاظت کے ساتھ نتیجہ ملتا ہے۔ Nexy آپ کے دستخطوں سے `__nexy__/src/actions.ts` لکھتا ہے، اور `@nexy/actions` اسے حل کرتا ہے۔

```tsx filename="src/routes/users.tsx"
import { useAction } from "@nexy/client";
import { create_user } from "@nexy/actions";

export default function NewUser() {
  const { run, pending, error, data } = useAction(create_user);

  return (
    <button disabled={pending} onClick={() => run({ name: "Ada" })}>
      {error ? error.message : data ? `Created ${data.name}` : "Create"}
    </button>
  );
}
```

ہک کے بغیر، ایک عمل صرف ایک `async` فعل ہے: `const user = await create_user({ name: "Ada" })`۔

| فریم ورک | کیا `useAction` لوٹاتا ہے |
|---|---|
| React، Preact | `{ pending, data, error, run, reset }` |
| Solid | ایک جیسا، `pending()`، `data()` اور `error()` بطور رسائی |
| Vue | وہی، `pending`، `data` اور `error` بطور حوالہ |
| Svelte | ایک اسٹور: `$save.pending`، `$save.data`، `$save.error`، جمع `save.run(input)` اور `save.reset()` |

`useAction(action, { onSuccess, onError })` دو کال بیکس بھی لیتا ہے۔ `run` کبھی نہیں پھینکتا: ایک ناکامی `error` میں اترتی ہے اور `run` `undefined` کے ساتھ حل ہوجاتی ہے۔

قسمیں Python سے آتی ہیں: `str` ہے `string`، `int` اور `float` ہیں `number`، `list[T]` ہے `T[]`، ایک Pydantic ماڈل یا `Enum` ایک نامزد قسم ہے، اور ان پٹ میں پہلے سے طے شدہ فیلڈ اختیاری ہے۔ ایک قسم Pydantic بیان نہیں کر سکتی `unknown` بن جاتی ہے۔

## غلطیاں اور ناکامیاں

ایک عمل مختلف مراحل میں ناکام ہو سکتا ہے۔ آپ کو اپنے UI میں ان کے درمیان فرق کرنا چاہئے:

1.  **توثیق کی غلطیاں (422)**: ان پٹ Python دستخط سے مماثل نہیں ہے۔ `error.fields` ہر غلط فیلڈ کو اپنے پیغام میں نقشہ بناتا ہے۔
2.  **کاروباری غلطیاں (`HTTPException`)**: آپ کے کوڈ نے کال سے انکار کردیا، مثال کے طور پر `403 Forbidden` یا `409 Conflict`۔
3.  **سرور کی خرابیاں (500)**: آپ کے Python کوڈ میں ایک غیر ہینڈل شدہ استثناء واقع ہوا۔
4.  **نیٹ ورک کی خرابیاں**: درخواست کبھی بھی سرور تک نہیں پہنچی، مثال کے طور پر ٹائم آؤٹ یا گمشدہ کنکشن۔
5.  **اجازت کی غلطیاں (401, 403)**: آپ کے اپنے چیک نے کال کرنے والے کو مسترد کردیا۔ Nexy آپ کے لیے اس کا فیصلہ نہیں کرتا ہے۔

ذیل میں بیان کردہ اصلی چیک ایک CSRF تحفظ ہے، اجازت نہیں: یہ کہتا ہے کہ کال کہاں سے آئی، کبھی بھی کس کو کرنے کی اجازت نہیں ہے۔

## ایک کارروائی کے بعد صفحہ کو ریفریش کریں۔

ایک عمل کہتا ہے کہ اس کی تبدیلی نے کن صفحات کو باسی بنا دیا، جیسا کہ Next.js `revalidatePath` کے ساتھ کرتا ہے:

```python
revalidate()            # the page that is open
revalidate("/users")    # that page, if it is the one open
```

جواب ایک `x-nexy-revalidate` ہیڈر میں راستے رکھتا ہے۔ کلائنٹ پھر روٹر کے ذریعے موجودہ صفحہ کو دوبارہ بازیافت کرتا ہے، یا کلائنٹ روٹر نہ ہونے پر اسے دوبارہ لوڈ کرتا ہے۔

## بغیر فارم JavaScript

ایک عمل ایک معیاری HTML فارم بھی لیتا ہے، لہذا صفحہ کسی بھی اسکرپٹ کے لوڈ ہونے سے پہلے کام کرتا ہے:

```html
<form method="post" action="{{ __actions_path['create_user'] }}">
  <input name="name">
  <button type="submit">Create</button>
</form>
```

ایک `.nexy` ٹیمپلیٹ میں `__actions_path["name"]` راستہ ہے، `__actions["name"]` فنکشن، اور فنکشن بھی اپنے نام سے دائرہ کار میں ہے۔

کامیابی پر، وزیٹر کو اس صفحہ پر واپس بھیجا جاتا ہے جس پر فارم تھا، اسٹیٹس `303` کے ساتھ۔ مختلف طریقے سے جواب دینے کے لیے، `Response` آبجیکٹ (مثلاً، `RedirectResponse("/done", status_code=303)`) لوٹائیں۔

## سیکورٹی

### راستے کی دھندلاپن اجازت نہیں ہے۔
ایکشن پاتھ `/_nx_` ہے جس کے بعد فنکشن کے ماڈیول کا ایک ہیش، اس کا نام اور پروجیکٹ کا راز ہے۔ یہ `NEXY_ACTION_SECRET` کے ذریعہ ترتیب دیا گیا ہے، یا `__nexy__/action.key` میں رکھا گیا ہے، جو `nx build` بناتا ہے تو کلائنٹ بنڈل اور `nx start` متفق ہیں: اس فائل کو تعمیر کے ساتھ رکھیں۔ راستہ اختتامی نقطہ کو آرام دہ دریافت سے چھپاتا ہے، اور **پیدا کردہ راستہ اجازت دینے کا طریقہ کار نہیں ہے**۔

جو کوئی راستہ جانتا ہے وہ عمل کو کہہ سکتا ہے۔ آپ **ضروری ہے** عمل کے اندر صارف کی شناخت اور اجازتوں کی تصدیق کریں:
```python
@Action
async def delete_user(user_id: str, request: Request):
    if not request.state.user.is_admin:
        raise HTTPException(403, "Admin rights required")
    # ...
```

### اصل تحفظ
کراس سائٹ ریکوسٹ فورجری (CSRF) کو روکنے کے لیے، Nexy ان درخواستوں سے انکار کرتا ہے جن کی `Origin` دوسری سائٹ ہے یا براؤزر `Sec-Fetch-Site: cross-site` کو `403` سے نشان زد کرتا ہے۔ ان سائٹس کی فہرست بنائیں جو آپ کے اعمال کو `NEXY_ALLOWED_ORIGINS` میں کال کرسکتی ہیں۔ بغیر `Origin` (جیسے `curl`) کالیں قبول کی جاتی ہیں۔

## غلطیاں درآمد کریں۔

سٹارٹ اپ پر Nexy اعمال کو تلاش کرنے کے لیے `src/` کے ہر ماڈیول کو درآمد کرتا ہے۔ ایک ماڈیول جو درآمد کرنے میں ناکام رہتا ہے اس کی اطلاع دی جاتی ہے، اور باقی اب بھی لوڈ ہوتے ہیں:

```text
  x src.actions.billing: src/actions/billing.py:3  ModuleNotFoundError: No module named 'stripe'
```

## اگلے اقدامات

- [API](../routing/fbr/handlers/README.md): واضح ہینڈلرز
- [ٹیسٹنگ](testing.md#what-to-assert): کسی عمل کی جانچ کیسے کی جائے۔
- [تشکیل](../reference/config.md): مڈل ویئر اور تصدیق کے اختیارات
