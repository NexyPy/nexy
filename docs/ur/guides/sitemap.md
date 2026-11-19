# میں Nexy سائٹ میں sitemap.xml اور robots.txt کیسے شامل کروں؟

`useSiteUrl` کو `nexyconfig.py` میں سیٹ کریں: Nexy پھر پیش کرتا ہے `/sitemap.xml`، جس میں پروجیکٹ کے ہر جامد صفحہ کی فہرست ہوتی ہے، اور ایک `/robots.txt` جو سرچ انجنوں کو اس کی طرف اشارہ کرتا ہے۔

## اسے `useSiteUrl` کے ساتھ آن کریں۔

`useSiteUrl` سائٹ کی عوامی اصل ہے، ایک سرچ انجن دیکھتے ہیں:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` اور `nx start` پھر دونوں فائلوں کا جواب دیں۔ بغیر `useSiteUrl` دونوں میں سے کوئی بھی موجود نہیں ہے، اس لیے کوئی پروجیکٹ کبھی بھی غلطی سے اپنے دیو سرور کا URL شائع نہیں کرتا ہے۔

## سائٹ کا نقشہ کیا درج کرتا ہے۔

سائٹ کا نقشہ ہر صفحہ کو `useSiteUrl` پر ایک مطلق URL کے طور پر دیتا ہے:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

ایک راستہ اس وقت درج ہوتا ہے جب وہ ایک مقررہ راستے پر `GET` کو HTML کا جواب دیتا ہے:

<!-- router:fbr,custom -->
- ایک صفحہ (`.nexy`، `.md`، `.mdx`، `.tsx`، `.jsx`، `.vue`، `.svelte`) درج ہے۔
- ایک متحرک صفحہ، جیسا کہ `src/routes/users/[id].nexy`، چھوڑ دیا جاتا ہے: Nexy اپنی قدروں کو نہیں جان سکتا۔
- ایک Python روٹ ہینڈلر JSON کا جواب دیتا ہے، لہذا اسے چھوڑ دیا جاتا ہے۔
<!-- /router -->

<!-- router:modular -->
- ایک کنٹرولر روٹ جو HTML کا جواب دیتا ہے، `@UseResponse(response_class=HTMLResponse)` کے ساتھ، درج ہے۔
- پاتھ پیرامیٹر والا راستہ، جیسا کہ `/users/{id}`، چھوڑ دیا جاتا ہے: Nexy اپنی قدروں کو نہیں جان سکتا۔
- ایک راستہ جو JSON کا جواب دیتا ہے چھوڑ دیا گیا ہے۔
<!-- /router -->

API اسکیما (`include_in_schema=False`) سے چھپا ہوا راستہ بھی چھوڑ دیا گیا ہے۔

## `robots.txt` یہ کام کرتا ہے۔

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## اس کے بجائے اپنا لکھیں۔

آپ کی اپنی فائل ہمیشہ جیت جاتی ہے، اور Nexy اسے کبھی بھی اوور رائٹ نہیں کرتا:

- `public/robots.txt` یا `public/sitemap.xml` کو ویسا ہی پیش کیا جاتا ہے، جس طرح `public/` کی ہر فائل ہے۔
- `/robots.txt` یا `/sitemap.xml` پر پروجیکٹ کا ایک راستہ اپنا راستہ رکھتا ہے۔

متحرک صفحات کی فہرست بنانے کے لیے اپنا سائٹ کا نقشہ لکھیں، جیسے کہ فی بلاگ پوسٹ ایک URL۔

## اگلے اقدامات

- [صفحہ میٹا ڈیٹا](../routing/fbr/pages/metadata.md): عنوان اور تفصیل سرچ انجن دکھاتے ہیں۔
- [ترتیب ](../reference/config.md): `nexyconfig.py` کی ہر ترتیب
- [تعینات کریں ](../deployment/README.md): پیداوار میں پروجیکٹ کی خدمت کریں۔
