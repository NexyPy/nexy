# الأمان

كيف تحافظ Nexy على حجم سطح الهجوم الخاص بها صغيرًا، والإصدارات التي تتطلبها، وكيفية التحقق من المشروع.

## طوابق النسخة

يعتمد Nexy على FastAPI وStarlette وJinja2 وVite وReact. الكلمة هي الإصدار الأدنى من Nexy
يسمح؛ كل واحد يجيب على استشارة منشورة.

| الباقة | الطابق | لماذا |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): يقوم رأس `Host` بتغيير مسار تقارير Starlette إلى البرامج الوسيطة، مما يتجاوز التفويض المكتوب على `request.url.path`. تم إدراجه على أنه مستغل من قبل CISA. |
| `fastapi` | 0.133.0 | الإصدار الأول الذي يقبل ستارليت ثابتة |
| `jinja2` | 3.1.6 | الهروب من خلال مرشح `attr` (CVE-2025-27516) |
| `vite` (المشاريع الداعمة) | 6.4.3 | `server.fs.deny` تجاوز مسارات Windows البديلة (CVE-2026-53571)؛ يؤثر تجاوز سلسلة الاستعلام السابقة (CVE-2026-39364) على Vite 7.1-7.3.1 و8.0.0-8.0.4 فقط |
| `react`، `react-dom` | 19.2.5 | تتعلق إرشادات React لعام 2026 بالحزم `react-server-dom-*`، التي لا يستخدمها Nexy؛ الأرضية تحافظ على الخط مصححًا |

تحقق من الإصدارات التي تم حلها:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## القواعد التي يتبعها Nexy

- **لا تثق أبدًا في رأس المضيف للمسارات.** يقرأ Nexy `scope["path"]`، وليس `request.url.path`، في
  البرامج الوسيطة الخاصة بها (البرامج الوسيطة للدليل). افعل نفس الشيء في ملكك.
- **الهروب مما يصل إلى HTML.** الدعائم التي تم تمريرها إلى مكونات العميل، `Link` السمات، `Image`،
  سمات `Audio` و`Video` ومراسي جدول المحتويات وتفاصيل `HTTPException` كلها
  نجا HTML. `| safe` في القالب يوقف هذا: لا تستخدمه أبدًا عند إدخال المستخدم.
- **نقاط نهاية المطور هي للاسترجاع فقط وضيقة.** نقطة نهاية عرض المطورين
  (`/__nexy__/render`) يقبل فقط الملفات ضمن `src/routes/` ذات الامتداد `.tsx` أو `.jsx`، و
  لا يمكن الوصول إليه إلا من خلال خادم التطوير، الذي يرفض الرؤوس `Host` الأجنبية.
- **لا تتسرب تفاصيل الخطأ.** تظهر صفحة الخطأ التي تفشل في حد ذاتها رمز الحالة فقط.
- **إجابات الإنتاج تحمل رؤوسًا آمنة.** `X-Content-Type-Options: nosniff` و
  `Referrer-Policy: strict-origin-when-cross-origin`، إلا إذا قام الكود الخاص بك بتعيين الكود الخاص به. `Server`
  لم يتم إرسال الرأس. أضف `Strict-Transport-Security` و`Content-Security-Policy` في ملفك
  الوكيل أو البرامج الوسيطة: يعتمدان على المجال الخاص بك.
- **يُظهر العطل مرجعًا، وليس الخطأ.** راجع [صفحات الأخطاء](../routing/fbr/errors/README.md#unhandled-exceptions).
- **لا يوجد `eval` ولا `shell=True` في كود بايثون الخاص بـ Nexy.** تعمل البرامج الخارجية بقائمة الوسائط.

## إجراء عمليات التدقيق

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

يقوم مستودع Nexy الخاص بتشغيل الأول والثالث في عمليات التحقق الخاصة به. يتم التعامل مع الاستشارة الجديدة في الطابق العلوي عن طريق رفع
الأرضية في `pyproject.toml` أو في السقالة `package.json`، ثم إعادة إنشاء القفل.

## النشر بأمان

- اضبط `useTrustedHost` على المجالات الخاصة بك: فهو يرفض رؤوس `Host` غير المتوقعة قبل أي مسار.
-  لا تكشف خادم Vite dev: `nx dev` يبقيه في حالة استرجاع خلف أصل Nexy.
- قم بتعيين `useDocs = False` إذا كان مخطط واجهة برمجة التطبيقات (API) لا ينبغي أن يكون عامًا.

انظر [البرمجيات الوسيطة والأمن](../guides/middleware-and-security.md).

## المصادر

-  [CVE-2026-48710 (BadHost) في ستارليت](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite الاستشارية GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) و
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
-  [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [حزم خادم React CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## الخطوات التالية

-  [البرمجيات الوسيطة والأمن](../guides/middleware-and-security.md)
-  [نشر](../deployment/README.md)
- [التكوين](config.md)