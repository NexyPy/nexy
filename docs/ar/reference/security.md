# الأمن

كيف تحافظ Nexy على حجم سطح الهجوم الخاص بها صغيرًا، والإصدارات التي تتطلبها، وكيفية التحقق من المشروع.

## طوابق الإصدار

يعتمد النكسي على FastAPI، Starlette، Jinja2، Vite و React. الأرضية هي أقل إصدار يسمح به Nexy؛ كل واحد يجيب على استشارة منشورة.

| الحزمة | الكلمة | لماذا |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): يقوم رأس `Host` بتغيير مسار التقارير Starlette إلى البرامج الوسيطة، مما يتجاوز التفويض المكتوب على `request.url.path`. تم إدراجه على أنه مستغل من قبل CISA. |
| `fastapi` | 0.133.0 | الإصدار الأول الذي يقبل ثابت Starlette |
| `jinja2` | 3.1.6 | الهروب من وضع الحماية من خلال مرشح `attr` (CVE-2025-27516) |
| `vite` (المشاريع السقالة) | 6.4.3 | `server.fs.deny` تجاوز المسارات البديلة لنظام التشغيل Windows (CVE-2026-53571)؛ يؤثر تجاوز سلسلة الاستعلام السابقة (CVE-2026-39364) فقط على Vite 7.1-7.3.1 و8.0.0-8.0.4 |
| `react`، `react-dom` | 19.2.5 | تتعلق تحذيرات 2026 React بالحزم `react-server-dom-*` التي لا يستخدمها Nexy؛ الأرضية تحافظ على الخط مصححًا |

تحقق من الإصدارات التي تم حلها:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## القواعد التي يتبعها Nexy

- **لا تثق أبدًا برأس المضيف للمسارات.** يقرأ Nexy `scope["path"]`، وليس `request.url.path`، في البرامج الوسيطة الخاصة به (البرامج الوسيطة للدليل). افعل نفس الشيء في ملكك.
- **الهروب مما يصل إلى HTML.** الدعائم التي تم تمريرها إلى مكونات العميل، `Link` السمات، `Image`، `Audio` والسمات `Video`، نقاط ربط جدول المحتويات وتفاصيل `HTTPException` كلها تم تجاوزها من HTML. لا يمكن الهروب من القالب `.nexy` من تلقاء نفسه: اكتب `{{ value | e }}` لأي قيمة تأتي من الزائر أو قاعدة البيانات، ولا يتم أبدًا `| safe` عند إدخال المستخدم.
- **نقاط نهاية المطور هي استرجاع فقط وضيقة.** تقبل نقطة نهاية عرض المطورين (`/__nexy__/render`) فقط الملفات الموجودة ضمن `src/routes/` ذات الامتداد `.tsx` أو `.jsx`، ولا يمكن الوصول إليها إلا من خلال خادم التطوير، الذي يرفض رؤوس `Host` الأجنبية.
- **تفاصيل الخطأ لا تتسرب.** تظهر صفحة الخطأ التي تفشل نفسها فقط رمز الحالة.
- **تحمل إجابات الإنتاج رؤوسًا آمنة.** `X-Content-Type-Options: nosniff` و `Referrer-Policy: strict-origin-when-cross-origin`، ما لم يحدد الكود الخاص بك خاصًا به. لم يتم إرسال رأس `Server`. أضف `Strict-Transport-Security` و `Content-Security-Policy` في الوكيل أو البرنامج الوسيط الخاص بك: يعتمدان على المجال الخاص بك.
- **يظهر العطل مرجعًا، وليس الخطأ.** راجع [صفحات الخطأ](../routing/fbr/errors/README.md#unhandled-exceptions).
- **لا يوجد `eval` ولا `shell=True` في كود Nexy Python.** تعمل البرامج الخارجية بقائمة الوسائط.

## تشغيل عمليات التدقيق

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

يقوم مستودع Nexy الخاص بتشغيل الأول والثالث في عمليات التحقق الخاصة به. يتم التعامل مع الاستشارة الجديدة في الطابق العلوي عن طريق رفع الأرضية في `pyproject.toml` أو في السقالة `package.json`، ثم إعادة إنشاء القفل.

## النشر بأمان

- اضبط `useTrustedHost` على نطاقاتك: فهو يرفض رؤوس `Host` غير المتوقعة قبل أي مسار.
- لا تكشف خادم التطوير Vite: `nx dev` يبقيه في حالة استرجاع خلف أصل Nexy.
- قم بتعيين `useDocs = False` إذا كان مخطط واجهة برمجة التطبيقات (API) لا يجب أن يكون عامًا.

انظر [البرامج الوسيطة والأمان](../guides/middleware-and-security.md).

## المصادر

- [CVE-2026-48710 (BadHost) في Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite الاستشارة GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) و [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React حزم الخادم CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## الخطوات التالية

- [الوسيطة والأمن](../guides/middleware-and-security.md)
- [نشر](../deployment/README.md)
- [التكوين](config.md)
