# फ्रंटएंड लेआउट

एक **लेआउट** एक आवरण है जो एक या अधिक पृष्ठों के आसपास साझा संरचना को परिभाषित करता है। लेआउट स्थिति को संरक्षित करके और नेविगेशन के दौरान पूर्ण-पृष्ठ पुनः लोड से बचकर "ऐप-जैसा" अनुभव सक्षम करते हैं।

## नेस्टिंग तर्क

लेआउट `src/routes/` के अंतर्गत निर्देशिका ट्री के आधार पर एक पदानुक्रमित संरचना का पालन करते हैं।

1.  **रूट लेआउट**: प्रत्येक प्रोजेक्ट का एक रूट लेआउट होता है (उदाहरण के लिए, `src/routes/layout.nexy`)। दस्तावेज़ शेल को परिभाषित करने के लिए ज़िम्मेदार यह एकमात्र लेआउट है: `<html>`, `<head>`, और `<body>`।
2.  **नेस्टेड लेआउट**: किसी भी फ़ोल्डर में अपनी `layout.*` फ़ाइल हो सकती है। यह लेआउट उस फ़ोल्डर के सभी पृष्ठों और उप-लेआउट को लपेटता है।
3.  **इनहेरिटेंस**: एक पेज रूट से नीचे अपने फ़ोल्डर तक सभी लेआउट द्वारा लपेटा जाता है।

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

एक नेस्टेड लेआउट यूआई का केवल अपना हिस्सा खींचता है और पेज को वहां रखता है जहां `children` जाता है:

```tsx filename="src/routes/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## साझा स्थिति और संरचना

लेआउट स्थिर होने के लिए डिज़ाइन किए गए हैं। क्लाइंट मोड में, समान लेआउट साझा करने वाले दो पेजों के बीच नेविगेट करते समय, लेआउट को **नहीं** दोबारा प्रस्तुत किया जाता है; केवल बाल सामग्री बदलती है. सर्वर मोड में प्रत्येक नेविगेशन एक नया दस्तावेज़ है।

- **स्लॉट**: लेआउट एक स्लॉट प्रदान करते हैं जहां नेस्टेड पेज इंजेक्ट किया जाता है: `children` जेएसएक्स में, और `children` प्रोप `.nexy` लेआउट में।
- **राज्य संरक्षण**: क्योंकि लेआउट माउंटेड रहता है, इसके भीतर मौजूद कोई भी राज्य (उदाहरण के लिए, हेडर में एक खोज क्वेरी) नेविगेशन के दौरान संरक्षित रहता है।

`.nexy` लेआउट में समान स्लॉट:

```nexy filename="src/routes/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

नीचे दिया गया खोज फ़ील्ड वह रखता है जो उपयोगकर्ता ने डैशबोर्ड पृष्ठों के बीच चलते समय टाइप किया था, क्योंकि इसे रखने वाला लेआउट कभी भी अनमाउंट नहीं होता है:

```tsx filename="src/routes/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## स्थैतिक बाधाएँ

उन मार्गों के लिए जो पहले से रेंडर किए गए हैं (एसएसजी), रूट लेआउट कुकीज़ या हेडर जैसे अनुरोध-समय डेटा पर निर्भर नहीं हो सकता है। इसे एक स्थिर शेल के रूप में प्रस्तुत किया जाना चाहिए जिसे क्लाइंट तब हाइड्रेट करता है।

इसके बजाय, स्थिर शेल की स्क्रिप्ट में, ब्राउज़र से थीम पढ़ें:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## रूपरेखा कार्यान्वयन

स्लॉट और नेस्टिंग का कार्यान्वयन रूपरेखा के अनुसार थोड़ा भिन्न होता है। अपनी चुनी हुई तकनीक के लिए **अंतर** मार्गदर्शिका देखें:

- [React मतभेद](../react/differences.md)
- [Vue मतभेद](../vue/differences.md)
- [Svelte मतभेद](../svelte/differences.md)
- [Solid मतभेद](../solid/differences.md)
- [Preact अंतर](../preact/differences.md)
