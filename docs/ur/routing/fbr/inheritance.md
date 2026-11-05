# وراثت

`src/routes/` میں کئی فائلیں ان کی ڈائرکٹری کے نیچے ہر چیز پر لاگو ہوتی ہیں۔ وہ سب اسی طرح حل کرتے ہیں: Nexy روٹ کی ڈائرکٹری سے شروع ہوتا ہے اور `src/routes/` تک چلتا ہے۔

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| فائل | اصول |
|---|---|
| `layout.nexy`، `layout.tsx`، `layout.vue`، `layout.svelte` | جڑ سے صفحہ تک ہر ترتیب اسے لپیٹ دیتی ہے، **سب سے پہلے** |
| `middleware.py` | روٹ سے روٹ تک ہر فائل درخواست کو لپیٹ دیتی ہے، **بیرونی پہلے**، انحصار سے پہلے |
| `dependencies.py` | ہر فائل روٹ سے روٹ تک چلتی ہے، **سب سے پہلے بیرونی**، پھر ہینڈلر کے اپنے محافظ |
| `notfound.nexy`، `errors.nexy` | **قریب ترین** ایک جیتتا ہے، فی اسٹیٹس کوڈ |

اوپر والے صفحے کے لیے، ترتیب `root layout > (shop) layout > cart layout > page` کے طور پر، اور انحصار `root > (shop) > cart > handler guards` کے طور پر چلتا ہے۔

## سب سے پہلے بیرونی کیوں؟

ایک بیرونی ترتیب فریم کو کھینچتی ہے اور بیرونی انحصار یہ فیصلہ کرتا ہے کہ کون بالکل اندر آسکتا ہے۔ ان کو پہلے رکھنے کا مطلب ہے کہ اندرونی لوگ ان پر بھروسہ کر سکتے ہیں: ایک ڈائرکٹری جس میں تصدیق کی ضرورت ہوتی ہے صارف کو پڑھنے والے ہینڈلر سے پہلے چلتی ہے۔

## لے آؤٹ

فولڈر فیملی اسٹیک کی تمام لے آؤٹ فائلیں: دیکھیں [لے آؤٹ](layouts/README.md)۔ مختلف خاندان آپس میں نہیں ملتے ہیں: ایک `layout.vue` کبھی بھی ایک `.tsx` صفحہ نہیں لپیٹتا، اور ایک پروجیکٹ میں یا تو `layout.nexy` یا کلائنٹ لے آؤٹ ہوتے ہیں، دونوں کبھی نہیں ([موڈز](modes.md))۔

## مڈل ویئر فائلیں۔

دیکھیں [مڈل ویئر فائلیں](middleware/README.md): وہ انحصار سے پہلے چلتی ہیں اور راستے تک پہنچے بغیر جواب دے سکتی ہیں۔

## انحصار

ہینڈلر فائل میں آرڈر کے لیے [انحصارات](dependencies/README.md) دیکھیں، بشمول `@UseGuard` اور `@Middleware`۔

## خرابی والے صفحات

`notfound.nexy` اور `errors.nexy` روٹس روٹ پر ایک بار انسٹال ہوتے ہیں۔ ذیلی ڈائرکٹری میں ایک کاپی اس سابقے کے لیے صفحہ کو بہتر کرتی ہے۔ دیکھیں [خرابی کے صفحات](errors/README.md)۔

## اگلے اقدامات

- [لے آؤٹ](layouts/README.md)
- [انحصارات](dependencies/README.md)
- [خرابی صفحات](errors/README.md)
