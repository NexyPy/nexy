# سیکورٹی

Nexy اپنے حملے کی سطح کو کس طرح چھوٹا رکھتا ہے، اسے کن ورژنز کی ضرورت ہے، اور پروجیکٹ کو کیسے چیک کیا جائے۔

## ورژن فرش

Nexy کا انحصار FastAPI، Starlette، Jinja2، Vite اور React پر ہے۔ فلور سب سے کم ورژن ہے جس کی Nexy اجازت دیتا ہے۔ ہر ایک شائع شدہ ایڈوائزری کا جواب دیتا ہے۔

| پیکیج | فلور | کیوں |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): ایک تیار کردہ `Host` ہیڈر مڈل ویئر کی رپورٹوں کے راستے Starlette کو تبدیل کرتا ہے، جو `request.url.path` پر لکھی گئی اجازت کو نظرانداز کرتا ہے۔ CISA کے ذریعے استحصال کے طور پر درج۔ |
| `fastapi` | 0.133.0 | پہلی ریلیز جو ایک مقررہ کو قبول کرتی ہے Starlette |
| `jinja2` | 3.1.6 | `attr` فلٹر کے ذریعے سینڈ باکس فرار (CVE-2025-27516) |
| `vite` (سکافولڈ پروجیکٹس) | 6.4.3 | `server.fs.deny` ونڈوز کے متبادل راستوں پر بائی پاس (CVE-2026-53571)؛ پہلے کا استفسار-سٹرنگ بائی پاس (CVE-2026-39364) صرف Vite 7.1-7.3.1 اور 8.0.0-8.0.4 | کو متاثر کرتا ہے۔
| `react`، `react-dom` | 19.2.5 | 2026 React مشورے `react-server-dom-*` پیکجوں سے متعلق ہیں، جنہیں Nexy استعمال نہیں کرتا ہے۔ فرش لائن کو پیچ دار رکھتا ہے۔ |

اپنے حل شدہ ورژن چیک کریں:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Nexy کے قواعد کی پیروی کرتا ہے۔

- **کے لیے میزبان ہیڈر پر کبھی بھروسہ نہ کریں۔ راستے** Nexy اپنے مڈل ویئر (ڈائریکٹری مڈل ویئر) میں `scope["path"]` نہیں بلکہ `request.url.path` پڑھتا ہے۔ اپنے میں بھی ایسا ہی کرو۔
- **جو پہنچ جائے اس سے بچیں۔ ایچ ٹی ایم ایل** کلائنٹ کے اجزاء، `Link` اوصاف، `Image`، `Audio` اور `Video` اوصاف، ٹیبل آف کنٹینٹ اینکرز اور `HTTPException` تفصیلات کو بھیجے گئے پروپس سبھی HTML سے بچ گئے ہیں۔ ٹیمپلیٹ میں `| safe` اسے بند کر دیتا ہے: اسے صارف کے ان پٹ پر کبھی استعمال نہ کریں۔
- **ڈویلپر اینڈ پوائنٹس صرف لوپ بیک اور ہیں۔ تنگ** ڈیو رینڈر اینڈ پوائنٹ (`/__nexy__/render`) صرف `.tsx` یا `.jsx` ایکسٹینشن کے ساتھ `src/routes/` کے تحت فائلوں کو قبول کرتا ہے، اور صرف ڈیو سرور کے ذریعے ہی قابل رسائی ہے، جو غیر ملکی `Host` ہیڈر سے انکار کرتا ہے۔
- **غلطی کی تفصیلات نہیں ہیں۔ لیک** ایک غلطی کا صفحہ جو خود ناکام ہو جاتا ہے صرف اسٹیٹس کوڈ دکھاتا ہے۔
- **پیداوار کے جوابات محفوظ ہیں۔ ہیڈرز** `X-Content-Type-Options: nosniff` اور `Referrer-Policy: strict-origin-when-cross-origin`، جب تک کہ آپ کا کوڈ خود سیٹ نہ کرے۔ `Server` ہیڈر نہیں بھیجا گیا ہے۔ اپنے پراکسی یا مڈل ویئر میں `Strict-Transport-Security` اور ایک `Content-Security-Policy` شامل کریں: وہ آپ کے ڈومین پر منحصر ہیں۔
- **حادثہ ایک حوالہ دکھاتا ہے، غلطی نہیں** دیکھیں [Error pages](../routing/fbr/errors/README.md#unhandled-exceptions)۔
- **Nexy کے Python میں نہیں `eval` اور نہیں `shell=True` کوڈ** بیرونی پروگرام ایک دلیل کی فہرست کے ساتھ چلتے ہیں۔

## آڈٹ چلا رہے ہیں۔

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Nexy کا اپنا ذخیرہ اپنے چیک میں پہلا اور تیسرا چلاتا ہے۔ اوپر والے فرش پر ایک نئی ایڈوائزری کو `pyproject.toml` یا سہاروں میں `package.json` میں فرش کو اٹھا کر سنبھالا جاتا ہے، پھر تالے کو دوبارہ بنا کر۔

## محفوظ طریقے سے تعیناتی

- اپنے ڈومینز پر `useTrustedHost` سیٹ کریں: یہ کسی بھی راستے سے پہلے غیر متوقع `Host` ہیڈر کو مسترد کرتا ہے۔
- Vite دیو سرور کو بے نقاب نہ کریں: `nx dev` اسے Nexy اصل کے پیچھے لوپ بیک پر رکھتا ہے۔
- اگر API اسکیما عوامی نہیں ہونا چاہئے تو `useDocs = False` سیٹ کریں۔

دیکھیں [مڈل ویئر اور سیکورٹی ](../guides/middleware-and-security.md).

## ذرائع

- [CVE-2026-48710 (BadHost) Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/) میں
- [Vite مشاورتی GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) اور [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React سرور پیکجز CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## اگلے اقدامات

- [مڈل ویئر اور سیکورٹی](../guides/middleware-and-security.md)
- [تعینات کریں۔](../deployment/README.md)
- [ترتیب ](config.md)
