# उपदेश

Nexy सर्वर पर Preact 10 घटकों को प्रस्तुत करता है, फिर Preact उन्हें ब्राउज़र में ले लेता है। पन्ने,
प्रत्येक ढाँचे में लेआउट, द्वीप और क्रियाएँ समान हैं: यह पृष्ठ सेटअप को कवर करता है, फिर भागों को
जो कि [साझा अनुबंधों](../frontend/pages.md) से भिन्न है।

| मोड | `nexyconfig.py` | पेज हैं | प्रीएक्ट है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.tsx` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट शुरू करें

```bash
nx new my-app --template web-fbr-preact
```

टेम्प्लेट प्रीएक्ट आइलैंड्स के साथ एक सर्वर-मोड प्रोजेक्ट है। `nx new my-app` को बिना टेम्पलेट के चलाएँ
इसके बजाय संकेतों का उत्तर दें: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं
ढाँचा।

## मौजूदा प्रोजेक्ट में प्रीएक्ट सक्षम करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import preact


class NexyConfig(NexyConfigModel):
    useFF = preact()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import preact from "@preact/preset-vite";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), preact()],
  customLogger: nexy.log(),
});
```

`nx new` यह फ़ाइल लिखता है; नेक्सी स्वयं `__nexy__/vite.ts` लिखता है, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `preact` | `^10.25.4` |
| `@preact/preset-vite` | `^2.10.1` (देव निर्भरता) |
| `preact-render-to-string` | `^6.7.0` (डेव निर्भरता, सर्वर पर रेंडर) |

## प्रीएक्ट लिखें

प्रीएक्ट घटक एक रिएक्ट-शैली फ़ंक्शन है। यहाँ जो अंतर मायने रखते हैं:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- हुक `preact/hooks` से आते हैं, `ComponentChildren` जैसे प्रकार `preact` से आते हैं।
- HTML विशेषताएँ लिखें: `class`, `for`, `charset`। `Link` अपनी कक्षाएं `class` से पढ़ता है।

## नियम

- **प्रति प्रोजेक्ट एक ढांचा।** `useFF` बिल्कुल एक ढांचा लेता है; `useFF = [preact(), react()]`
  स्टार्टअप पर सर्वर बंद कर देता है। `useFF = preact()` के साथ, प्रत्येक `.tsx` फ़ाइल प्रीएक्ट है।
- **पेज हैं `.tsx`।** `src/routes/` के अंतर्गत केवल `.tsx` फ़ाइल ही पेज बनती है; `.jsx` के लिए ठीक है
  घटक.
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पेज नहीं हैं।
- **एक सर्वर-मोड प्रोजेक्ट में कोई `.tsx` पेज नहीं है**, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी
  प्रारंभ करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।
- **एक `.mdx` पृष्ठ `"preact"` से आयात होता है।** नेक्सी एक `.mdx` फ़ाइल को प्रीएक्ट के साथ तभी संकलित करता है जब वह
  उस आयात को देखता है, उदाहरण के लिए `import { h } from "preact"`, और अन्यथा प्रतिक्रिया के साथ। देखिये
  [मार्कडाउन और एमडीएक्स](../nexy/markdown.md)।

## पेज

क्लाइंट मोड (`useCSR = True`) में, एक पेज एक `.tsx` फ़ाइल है।

### पेज घटक

पृष्ठ फ़ाइल का डिफ़ॉल्ट निर्यात है. यदि कोई डिफ़ॉल्ट निर्यात मौजूद नहीं है, तो नेक्सी पहला नाम चुनता है
निर्यात.

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

### कार्यान्वयन

रूट लेआउट दस्तावेज़ शेल को परिभाषित करता है। नेस्टेड लेआउट सामग्री को लपेटते हैं।

```tsx filename="src/routes/layout.tsx"
import type { ComponentChildren } from "preact";

export default function RootLayout({ children }: { children: ComponentChildren }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{children}</main>
      </body>
    </html>
  );
}
```

## द्वीप

सर्वर मोड में, `.nexy` फ़ाइल में आयात किया गया एक प्रीएक्ट घटक एक द्वीप है।

### आयात करना

`.nexy` फ़ाइल के फ्रंटमैटर में घटकों को आयात करें:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```

### हाइड्रेशन निर्देश

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

क्लाइंट-साइड ट्रांज़िशन के लिए `Link` घटक का उपयोग करें। ध्यान दें कि Preact इसके बजाय `class` का उपयोग करता है
`className`:

```tsx
import { Link } from "@nexy/client";

<Link href="/about" class="nav" activeClassName="active">About</Link>
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
- [फ्रंटएंड](../../guides/frontend.md): वाइट और क्लाइंट बिल्ड