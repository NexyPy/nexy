# ठोस

नेक्सी सर्वर पर सॉलिड 1.9 घटकों को प्रस्तुत करता है, फिर सॉलिड उन्हें ब्राउज़र में ले लेता है। पन्ने,
प्रत्येक ढाँचे में लेआउट, द्वीप और क्रियाएँ समान हैं: यह पृष्ठ सेटअप को कवर करता है, फिर भागों को
जो कि [साझा अनुबंधों](../frontend/pages.md) से भिन्न है।

| मोड | `nexyconfig.py` | पेज हैं | सॉलिड हैं |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.tsx` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट शुरू करें

```bash
nx new my-app --template web-fbr-solid
```

टेम्प्लेट सॉलिड आइलैंड्स के साथ एक सर्वर-मोड प्रोजेक्ट है। `nx new my-app` को बिना टेम्पलेट के चलाएँ
इसके बजाय संकेतों का उत्तर दें: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं
ढाँचा।

## मौजूदा प्रोजेक्ट में सॉलिड सक्षम करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import solid


class NexyConfig(NexyConfigModel):
    useFF = solid()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import solid from "vite-plugin-solid";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), solid()],
  customLogger: nexy.log(),
});
```

क्लाइंट मोड में लिखें `solid({ ssr: true })`: सॉलिड सर्वर के लिए एक घटक को अलग तरीके से संकलित करता है
और ब्राउज़र के लिए, और क्लाइंट मोड दोनों की आवश्यकता है। `nx new` यह फ़ाइल लिखता है; नेक्सी लिखते हैं
`__nexy__/vite.ts` स्वयं, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (देव निर्भरता) |

## संकेतों में सोचें

एक सॉलिड कंपोनेंट फ़ंक्शन **एक बार** चलता है। बाद में जो परिवर्तन होता है उसे सिग्नल के माध्यम से पढ़ा जाता है, और केवल
इसे पढ़ने वाले भाव अद्यतन होते हैं:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- सिग्नल को कॉल करें, `count()`, जेएसएक्स के अंदर, इसके ऊपर वाले वेरिएबल में नहीं।
- प्रॉप्स को `props.start` के रूप में पढ़ें। डिस्ट्रक्चरिंग `{ start }` मान को एक बार पढ़ता है और अपडेट खो देता है।
- सॉलिड HTML विशेषताएँ लिखता है: `class`, `for`, `charset`, न कि `className`।

## नियम

- **प्रति प्रोजेक्ट एक ढांचा।** `useFF` बिल्कुल एक ढांचा लेता है; `useFF = [solid(), react()]`
  स्टार्टअप पर सर्वर बंद कर देता है। `useFF = solid()` के साथ, प्रत्येक `.tsx` फ़ाइल ठोस है।
- **पेज हैं `.tsx`।** `src/routes/` के अंतर्गत केवल `.tsx` फ़ाइल ही पेज बनती है; `.jsx` के लिए ठीक है
  घटक.
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पेज नहीं हैं।
- **एक सर्वर-मोड प्रोजेक्ट में कोई `.tsx` पेज नहीं है**, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी
  प्रारंभ करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।
- **नहीं `.mdx` सॉलिड के साथ।** एमडीएक्स रिएक्ट या प्रीएक्ट के लिए संकलित करता है; `.md` पेज काम करते हैं।

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

यूआरएल पैरामीटर `useParams` हुक के माध्यम से उपलब्ध हैं, जो एक एक्सेसर लौटाता है:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## लेआउट

### कार्यान्वयन

रूट लेआउट दस्तावेज़ शेल को परिभाषित करता है। नेस्टेड लेआउट सामग्री को लपेटते हैं।

```tsx filename="src/routes/layout.tsx"
import type { JSX } from "solid-js";

export default function RootLayout(props: { children: JSX.Element }) {
  return (
    <html>
      <body>
        <header>My app</header>
        <main>{props.children}</main>
      </body>
    </html>
  );
}
```

`props.children` को नष्ट न करें, क्योंकि सॉलिड इसे आलस्य से पढ़ता है।

## द्वीप

सर्वर मोड में, `.nexy` फ़ाइल में आयात किया गया एक ठोस घटक एक द्वीप है।

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

## कार्य और नेविगेशन

### कॉलिंग क्रियाएं

किसी एक्शन कॉल की स्थिति को प्रबंधित करने के लिए `useAction` हुक का उपयोग करें। सॉलिड में, यह एक्सेसर्स लौटाता है (कॉल करें)।
उन्हें कार्यों के रूप में)।

```tsx
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const save = useAction(add_todo);
// ...
<button disabled={save.pending()}>Add</button>
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

सभी स्थान हुक रिटर्न एक्सेसर्स:

- `usePathname()`: वर्तमान पथ
- `useParams()`: गतिशील खंड
- `useSearchParams()`: क्वेरी स्ट्रिंग
- `useLocation()`: पूर्ण स्थान वस्तु

## अगले चरण

- [दृश्य](../README.md): उन प्रारूपों की तुलना करें जिनका उपयोग पृष्ठ कर सकता है
- [फ्रंटएंड](../../guides/frontend.md): वाइट और क्लाइंट बिल्ड