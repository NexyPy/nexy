# React

नेक्सी सर्वर पर React 19 घटकों को प्रस्तुत करता है, फिर React उन्हें ब्राउज़र में हाइड्रेट करता है। पेज, लेआउट, द्वीप और क्रियाएं हर ढांचे में समान हैं: यह पेज सेटअप को कवर करता है, फिर वे हिस्से जो [साझा अनुबंध ](../frontend/pages.md) से भिन्न होते हैं।

| मोड | `nexyconfig.py` | पेज हैं | React है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.tsx` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट प्रारंभ करें

```bash
nx new my-app --template web-fbr-react
```

टेम्प्लेट React द्वीपों वाला एक सर्वर-मोड प्रोजेक्ट है। इसके बजाय संकेतों का उत्तर देने के लिए टेम्पलेट के बिना `nx new my-app` चलाएं: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं, फिर फ्रेमवर्क।

## किसी मौजूदा प्रोजेक्ट में React सक्षम करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), react()],
  customLogger: nexy.log(),
});
```

`nx new` यह फ़ाइल लिखता है; नेक्सी स्वयं `__nexy__/vite.ts` लिखता है, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `react`, `react-dom` | `^19.2.5` |
| `@vitejs/plugin-react` | `^5.2.0` |
| `@types/react`, `@types/react-dom` | देव निर्भरताएं |

## नियम

- **प्रति प्रोजेक्ट एक ढाँचा।** `useFF` बिल्कुल एक ढाँचा लेता है; `useFF = [react(), vue()]` स्टार्टअप पर सर्वर को रोक देता है।
- **पृष्ठ `.tsx` हैं।** React घटकों के लिए `.tsx` और `.jsx` का स्वामी है, लेकिन `src/routes/` के अंतर्गत केवल `.tsx` फ़ाइल एक पृष्ठ बन जाती है।
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पृष्ठ नहीं हैं।
- **सर्वर-मोड प्रोजेक्ट में कोई `.tsx` पेज** नहीं है, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी शुरू करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।

## पन्ने

क्लाइंट मोड (`useCSR = True`) में, एक पेज एक `.tsx` फ़ाइल है।

### पृष्ठ घटक

पृष्ठ फ़ाइल का डिफ़ॉल्ट निर्यात है. यदि कोई डिफ़ॉल्ट निर्यात मौजूद नहीं है, तो नेक्सी पहला नामित निर्यात चुनता है।

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Hello</h1>;
}
```

### गतिशील खंड

यूआरएल पैरामीटर `useParams` हुक के माध्यम से उपलब्ध हैं:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

## लेआउट

### क्रियान्वयन

रूट लेआउट दस्तावेज़ शेल को परिभाषित करता है। नेस्टेड लेआउट अपने नीचे की सामग्री को लपेटते हैं।

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

## द्वीप

सर्वर मोड में, एक React घटक को एक में आयात किया जाता है `.nexy` फ़ाइल एक द्वीप है।

### आयात करना

`.nexy` फ़ाइल के फ्रंटमैटर में घटकों को आयात करें:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### जलयोजन निर्देश

द्वीप के हाइड्रेट होने को नियंत्रित करने के लिए `directive` प्रोप का उपयोग करें:

- `client:load` (डिफ़ॉल्ट): तुरंत
- `client:idle`: जब ब्राउज़र निष्क्रिय हो
- `client:visible`: जब यह दृश्य में स्क्रॉल करता है
- `client:media`: जब मीडिया क्वेरी मेल खाती है

## क्रियाएँ और नेविगेशन

### कॉलिंग क्रियाएं

किसी एक्शन कॉल की स्थिति को प्रबंधित करने के लिए `useAction` हुक का उपयोग करें:

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const { run, pending, error, data } = useAction(add_todo);
// ...
<button onClick={() => run({ title: "New Task" })}>Add</button>
```

### नेविगेशन

क्लाइंट-साइड ट्रांज़िशन के लिए `Link` घटक का उपयोग करें:

```tsx
import { Link } from "@nexy/client";

<Link href="/about">About</Link>
```

प्रोग्रामेटिक नेविगेशन के लिए, `useRouter` हुक का उपयोग करें:

```tsx
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### यूआरएल पहुंच

- `usePathname()`: वर्तमान पथ
- `useParams()`: गतिशील खंड
- `useSearchParams()`: क्वेरी स्ट्रिंग
- `useLocation()`: पूर्ण स्थान वस्तु

## अगले चरण

- [दृश्य](../README.md): उन प्रारूपों की तुलना करें जिनका उपयोग पृष्ठ कर सकता है
- [फ्रंटएंड](../../guides/frontend.md): Vite और क्लाइंट बिल्ड
