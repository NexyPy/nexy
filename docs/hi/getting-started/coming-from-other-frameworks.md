# दूसरे ढाँचे से आ रहा है

नेक्सी FastAPI प्लस फ़ाइल-आधारित रूटिंग, सर्वर-रेंडर किए गए पेज और वैकल्पिक React, Vue, Svelte, Solid या Preact द्वीप हैं। यह पृष्ठ वही दर्शाता है जो आप पहले से जानते हैं।

## से FastAPI

| FastAPI | नेक्सी |
|---|---|
| `@app.get("/users")` एक मॉड्यूल में आप | `GET` फ़ंक्शन को `src/routes/users.py` | में आयात करते हैं
| `app.include_router(router)` | फ़ाइल पथ यूआरएल है; पंजीकरण के लिए कुछ भी नहीं |
| पथ परम `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | अभी भी `Depends(...)`: हैंडलर FastAPI हैंडलर हैं |
| Jinja2 `TemplateResponse` | समापन बिंदु के बगल में एक `.nexy` पृष्ठ |
| `uvicorn main:app` | `nx dev` के साथ चलाएँ, फिर `nx build && nx start` |

`src/routes/*.py` के अंतर्गत सब कुछ सामान्य है FastAPI: निर्भरताएं, Pydantic मॉडल, मिडलवेयर और `/docs` काम करते रहते हैं।

## से Next.js

| Next.js | नेक्सी |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` या `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (`<html>` का मालिक है) | `src/routes/layout.tsx` के साथ `useCSR = True` (React), या `src/routes/layout.nexy` सर्वर मोड में |
| नेस्टेड `layout.tsx` | नेस्टेड `layout.tsx` / `layout.vue` / `layout.svelte` क्लाइंट मोड में, नेस्टेड `layout.nexy` सर्वर मोड में |
| `use client` सर्वर पेज में घटक | [द्वीप](../rendering/islands.md) सर्वर मोड में |
| रूट हैंडलर `route.ts` | `src/routes/api/x.py`, Python | में लिखा गया है
| `(group)` फ़ोल्डर्स | वही: `(group)/` |
| सर्वर क्रियाएँ | [`@Action`](../guides/actions.md) फ़ंक्शंस को किसी फ़ॉर्म से या टाइप किए गए क्लाइंट फ़ंक्शंस के रूप में बुलाया जाता है |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

बैकएंड Python है, इसलिए आपका एपीआई आपके डेटा और एमएल कार्य के साथ कोड साझा करता है। क्लाइंट घटक पूरे पृष्ठ React पेड़ के बजाय द्वीपों के रूप में हाइड्रेट होते हैं।

## एक्सप्रेस या नोड बैकएंड से

| एक्सप्रेस | नेक्सी |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` के साथ `async def GET(id)` |
| `app.use(middleware)` | FastAPI मिडलवेयर, `nexyconfig.py` | से पंजीकृत
| `res.json(obj)` | एक निर्देश या Pydantic मॉडल लौटाएं |
| ईजेएस / पग दृश्य | `.nexy` (Jinja2) पृष्ठ |
| `npm run dev` | `nx dev` |

## राउटर चुनना

| | का उपयोग करें जब |
|---|---|
| फ़ाइल-आधारित राउटर | पृष्ठों और समापन बिंदुओं को फ़ाइलों से मैप किया गया; डिफ़ॉल्ट |
| मॉड्यूलर राउटर | नियंत्रक, मॉड्यूल और निर्भरता इंजेक्शन, नेस्टजेएस-शैली |

दोनों को `nx new` द्वारा तैयार किया गया है और एक ही एंड-टू-एंड परीक्षणों द्वारा कवर किया गया है। [रूटिंग](../routing/README.md) और [मॉड्यूलर रूटिंग](../routing/modular/README.md) देखें।

## आगे कहाँ

- [त्वरित शुरुआत](quick-start.md): एक प्रोजेक्ट बनाएं और उसे चलाएं
- [परियोजना संरचना](project-structure.md): जहां प्रत्येक फ़ाइल संबंधित है
- [रूटिंग](../routing/README.md): राउटर चुनें
