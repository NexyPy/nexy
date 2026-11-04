# विरासत

`src/routes/` में कई फ़ाइलें उनकी निर्देशिका के नीचे मौजूद सभी चीज़ों पर लागू होती हैं। वे सभी एक ही संकल्प लेते हैं
रास्ता: नेक्सी मार्ग की निर्देशिका से शुरू होती है और `src/routes/` तक चलती है।

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

| फ़ाइल | नियम |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | जड़ से पृष्ठ तक प्रत्येक लेआउट इसे लपेटता है, **सबसे पहले सबसे बाहरी** |
| `middleware.py` | रूट से रूट तक प्रत्येक फ़ाइल अनुरोध को लपेटती है, ** सबसे पहले **, निर्भरता से पहले |
| `dependencies.py` | रूट से रूट तक प्रत्येक फ़ाइल चलती है, **पहले सबसे बाहरी**, फिर हैंडलर के अपने गार्ड |
| `notfound.nexy`, `errors.nexy` | **निकटतम** एक जीतता है, प्रति स्टेटस कोड |

उपरोक्त पृष्ठ के लिए, लेआउट इस प्रकार हैं
`root layout > (shop) layout > cart layout > page`, और निर्भरताएँ इस प्रकार चलती हैं
`root > (shop) > cart > handler guards`.

## बाहरीतम पहले क्यों

एक बाहरी लेआउट फ्रेम खींचता है और एक बाहरी निर्भरता यह तय करती है कि कौन अंदर आ सकता है। उन्हें लगाना
पहले का मतलब है कि आंतरिक लोग उन पर भरोसा कर सकते हैं: एक निर्देशिका जिसे प्रमाणीकरण की आवश्यकता होती है वह पहले चलती है
हैंडलर जो उपयोगकर्ता को पढ़ता है।

## लेआउट

फ़ोल्डर परिवार स्टैक की सभी लेआउट फ़ाइलें: [लेआउट](layouts/README.md) देखें। अलग-अलग परिवार करते हैं
मिश्रण नहीं: एक `layout.vue` कभी भी `.tsx` पेज को लपेटता नहीं है, और एक प्रोजेक्ट में या तो `layout.nexy` या क्लाइंट होता है
लेआउट, दोनों कभी नहीं ([मोड](modes.md))।

## मिडिलवेयर फ़ाइलें

[मिडिलवेयर फ़ाइलें](middleware/README.md) देखें: वे निर्भरता से पहले चलती हैं और उत्तर दे सकती हैं
मार्ग तक पहुंचे बिना.

## निर्भरताएं

हैंडलर फ़ाइल में ऑर्डर के लिए [निर्भरताएं](dependencies/README.md) देखें, जिसमें `@UseGuard` भी शामिल है
और `@Middleware`।

## त्रुटि पृष्ठ

`notfound.nexy` और `errors.nexy` रूट रूट पर एक बार स्थापित होते हैं; उपनिर्देशिका में एक प्रति
उस उपसर्ग के लिए पृष्ठ को परिष्कृत करता है। [त्रुटि पृष्ठ](errors/README.md) देखें।

## अगले चरण

- [लेआउट](layouts/README.md)
- [निर्भरताएं](dependencies/README.md)
- [त्रुटि पृष्ठ](errors/README.md)