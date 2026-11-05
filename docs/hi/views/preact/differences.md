# Preact

नेक्सी सर्वर पर Preact 10 घटकों को प्रस्तुत करता है, फिर Preact उन्हें ब्राउज़र में ले लेता है। पेज, लेआउट, द्वीप और क्रियाएं हर ढांचे में समान हैं: यह पेज सेटअप को कवर करता है, फिर वे हिस्से जो [साझा अनुबंध ](../frontend/pages.md) से भिन्न होते हैं।

| मोड | `nexyconfig.py` | पेज हैं | Preact है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.tsx` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट प्रारंभ करें

```bash
nx new my-app --template web-fbr-preact
```

टेम्प्लेट Preact द्वीपों वाला एक सर्वर-मोड प्रोजेक्ट है। इसके बजाय संकेतों का उत्तर देने के लिए टेम्पलेट के बिना `nx new my-app` चलाएं: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं, फिर फ्रेमवर्क।

## किसी मौजूदा प्रोजेक्ट में Preact सक्षम करें

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

## लिखें Preact

एक Preact घटक एक रिएक्ट-शैली फ़ंक्शन है। यहाँ जो अंतर मायने रखते हैं:

```tsx filename="src/components/Counter.tsx"
import { useState } from "preact/hooks";

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start);
  return <button class="counter" onClick={() => setCount(count + 1)}>{count}</button>;
}
```

- हुक `preact/hooks` से आते हैं, जैसे `ComponentChildren` से `preact` तक।
- HTML विशेषताएँ लिखें: `class`, `for`, `charset`। `Link` अपनी कक्षाएं `class` से पढ़ता है।

## नियम

- **प्रति प्रोजेक्ट एक ढाँचा।** `useFF` बिल्कुल एक ढाँचा लेता है; `useFF = [preact(), react()]` स्टार्टअप पर सर्वर को रोक देता है। `useFF = preact()` के साथ, प्रत्येक `.tsx` फ़ाइल Preact है।
- **पृष्ठ `.tsx` हैं।** केवल `src/routes/` के अंतर्गत एक `.tsx` फ़ाइल एक पृष्ठ बन जाती है; `.jsx` एक घटक के लिए ठीक है।
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पृष्ठ नहीं हैं।
- **सर्वर-मोड प्रोजेक्ट में कोई `.tsx` पेज** नहीं है, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी शुरू करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।
- **एक `.mdx` पृष्ठ `"preact"` से आयात होता है।** नेक्सी एक `.mdx` फ़ाइल को Preact के साथ तभी संकलित करता है जब वह उस आयात को देखता है, उदाहरण के लिए `import { h } from "preact"`, और अन्यथा React के साथ। [Markdown और MDX](../nexy/markdown.md) देखें।

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

सर्वर मोड में, एक Preact घटक को एक में आयात किया जाता है `.nexy` फ़ाइल एक द्वीप है।

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

क्लाइंट-साइड ट्रांज़िशन के लिए `Link` घटक का उपयोग करें। ध्यान दें कि Preact `className` के बजाय `class` का उपयोग करता है:

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
- [फ्रंटएंड](../../guides/frontend.md): Vite और क्लाइंट बिल्ड
