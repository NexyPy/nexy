# फ़ाइल कन्वेंशन

`src/routes/` के अंतर्गत आरक्षित नाम और नियम।

## फ़ाइलें रूट करें

| फ़ाइल | बन जाता है |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | इसकी निर्देशिका का मार्ग |
| `about.nexy` | `/about` |
| `[slug].nexy` | गतिशील खंड `{slug}` |
| `[...path].nexy` | सब पकड़ो `{path:path}` |
| `(group)/page.nexy` | `/page`: समूह यूआरएल में दिखाई नहीं देता है |
| `name.py` | एपीआई हैंडलर; फ़ंक्शन नाम `GET`, `POST`, ... विधियां हैं |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | जब फ़्रेमवर्क को `useFF` के साथ सक्षम किया जाता है तो क्लाइंट रूट |

## आरक्षित फ़ाइलें

| फ़ाइल | भूमिका | विवरण |
|---|---|---|
| `layout.nexy` | सर्वर मोड: इसके नीचे प्रत्येक पृष्ठ को लपेटता है; रूट वाला HTML दस्तावेज़ का स्वामी है | [लेआउट.नेक्सी](../views/nexy/layouts.md) |
| `layout.tsx` | क्लाइंट मोड (React): रूट वाले के पास HTML दस्तावेज़ होता है, नेस्टेड वाले पेजों को लपेटते हैं | [लेआउट.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | क्लाइंट मोड: नेस्टेड लेआउट | [लेआउट.व्यू](../views/vue/differences.md), [लेआउट.स्वेल्टे](../views/svelte/differences.md) |
| `notfound.nexy` | इसकी निर्देशिका के लिए 404 पेज | [त्रुटि पृष्ठ](../routing/fbr/errors/README.md) |
| `errors.nexy` | इसकी निर्देशिका के लिए 500 पेज | [त्रुटि पृष्ठ](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | इसकी निर्देशिका के लिए 403 पेज | [प्रति फ़ोल्डर त्रुटि पृष्ठ](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | इसकी निर्देशिका के लिए 401 पृष्ठ | [प्रति फ़ोल्डर त्रुटि पृष्ठ](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | आरक्षित; अभी तक कोई रनटाइम प्रभाव नहीं है | [त्रुटि पृष्ठ](../routing/fbr/errors/README.md) |
| `middleware.py` | एक `async def middleware(request, call_next)` निर्देशिका और नीचे के अनुरोधों को लपेटते हुए | [मिडिलवेयर फ़ाइलें](../routing/fbr/middleware/README.md) |
| `dependencies.py` | एक `dependencies = [fn, ...]` सूची निर्देशिका और उसके बच्चों पर लागू होती है | [निर्भरताएं](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python पैकेज मार्कर | |
| `favicon.ico` | `/favicon.ico` में सेवा दी गई | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` और `useLoadingExtensions` इन नामों के लिए अधिक एक्सटेंशन आरक्षित करते हैं। [कॉन्फिग](config.md) देखें।

## उपेक्षित फ़ाइलें

- `_` या `.` से शुरू होने वाली फ़ाइल या फ़ोल्डर: इसे आंशिक, ड्राफ्ट और सहायकों के लिए उपयोग करें।
- एक फ़ाइल जिसका एक्सटेंशन प्रोजेक्ट के लिए सक्रिय नहीं है: इसे एक चेतावनी के साथ छोड़ दिया जाता है।

## प्रति यूआरएल एक फ़ाइल

दो फ़ाइलें जो समान URL पर हल होती हैं, दोनों पंजीकृत होती हैं। `blog.nexy` को `blog/index.nexy` के आगे न रखें।

## बाहर `src/routes/`

| फ़ोल्डर | प्रयोजन |
|---|---|
| `src/components/` | पृष्ठों द्वारा आयातित घटक; कभी मार्ग नहीं |
| `src/apps/` | [मॉड्यूलर राउटर](../routing/modular/README.md) के नियंत्रक और मॉड्यूल |
| `public/` | स्थिर फ़ाइलें, रूट पर दी गई: `public/logo.svg` `/logo.svg` है (`/public/` के अंतर्गत भी) |
| `__nexy__/` | उत्पन्न आउटपुट; प्रतिबद्ध मत हो |

## अगले चरण

- [रूटिंग](../routing/README.md)
- [परियोजना संरचना](../getting-started/project-structure.md)
