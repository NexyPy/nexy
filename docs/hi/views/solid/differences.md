# Solid

नेक्सी सर्वर पर Solid 1.9 घटकों को प्रस्तुत करता है, फिर Solid उन्हें ब्राउज़र में ले लेता है। पेज, लेआउट, द्वीप और क्रियाएं हर ढांचे में समान हैं: यह पेज सेटअप को कवर करता है, फिर वे हिस्से जो [साझा अनुबंध ](../frontend/pages.md) से भिन्न होते हैं।

<!-- router:fbr,custom -->
| मोड | `nexyconfig.py` | पन्ने हैं | Solid है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [उन पन्नों के अंदर द्वीप](../../rendering/islands.md) |
| ग्राहक | `useCSR = True` | `.tsx` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |
<!-- /router -->

<!-- router:modular -->
मॉड्यूलर राउटर के साथ, Solid घटक `.nexy` दृश्यों के अंदर [द्वीप](../../rendering/islands.md) होते हैं, एक नियंत्रक रिटर्न देता है: कोई पेज फ़ाइल नहीं है और कोई क्लाइंट राउटर नहीं है।
<!-- /router -->

## एक प्रोजेक्ट प्रारंभ करें

<!-- router:fbr,custom -->
```bash
nx new my-app --template web-fbr-solid
```
<!-- /router -->

<!-- router:modular -->
```bash
nx new my-app --template web-modular-solid
```
<!-- /router -->

टेम्प्लेट Solid द्वीपों वाला एक सर्वर-मोड प्रोजेक्ट है। इसके बजाय संकेतों का उत्तर देने के लिए टेम्पलेट के बिना `nx new my-app` चलाएं: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं, फिर फ्रेमवर्क।

## किसी मौजूदा प्रोजेक्ट में Solid सक्षम करें

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

क्लाइंट मोड में लिखें `solid({ ssr: true })`: Solid सर्वर और ब्राउज़र के लिए एक घटक को अलग-अलग संकलित करता है, और क्लाइंट मोड को दोनों की आवश्यकता होती है। `nx new` यह फ़ाइल लिखता है; नेक्सी स्वयं `__nexy__/vite.ts` लिखता है, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `solid-js` | `^1.9.12` |
| `vite-plugin-solid` | `^2.11.0` (देव निर्भरता) |

## संकेतों में सोचो

एक Solid घटक फ़ंक्शन **एक बार** चलता है। बाद में जो परिवर्तन होता है उसे एक सिग्नल के माध्यम से पढ़ा जाता है, और केवल इसे पढ़ने वाले भाव ही अपडेट होते हैं:

```tsx filename="src/components/Counter.tsx"
import { createSignal } from "solid-js";

export default function Counter(props: { start?: number }) {
  const [count, setCount] = createSignal(props.start ?? 0);
  return <button onClick={() => setCount(count() + 1)}>{count()}</button>;
}
```

- सिग्नल को कॉल करें, `count()`, जेएसएक्स के अंदर, इसके ऊपर किसी वेरिएबल में नहीं।
- प्रॉप्स को `props.start` के रूप में पढ़ें। डिस्ट्रक्चरिंग `{ start }` मान को एक बार पढ़ता है और अपडेट खो देता है।
- Solid HTML विशेषताएँ लिखता है: `class`, `for`, `charset`, न कि `className`।

## नियम

- **प्रति प्रोजेक्ट एक ढाँचा।** `useFF` बिल्कुल एक ढाँचा लेता है; `useFF = [solid(), react()]` स्टार्टअप पर सर्वर को रोक देता है। `useFF = solid()` के साथ, प्रत्येक `.tsx` फ़ाइल Solid है।
<!-- router:fbr,custom -->
- **पृष्ठ `.tsx` हैं।** `src/routes/` के अंतर्गत केवल एक `.tsx` फ़ाइल एक पृष्ठ बन जाती है; `.jsx` एक घटक के लिए ठीक है।
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पृष्ठ नहीं हैं।
- **सर्वर-मोड प्रोजेक्ट में कोई `.tsx` पेज** नहीं है, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी शुरू करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।
<!-- /router -->
<!-- router:modular -->
- **घटक `src/components/`** में रहते हैं, और एक दृश्य उन्हें द्वीपों के रूप में आयात करता है।
<!-- /router -->
- **नहीं `.mdx` के साथ Solid।** MDX संकलित होकर React या Preact; `.md` पेज काम करते हैं।

<!-- router:fbr,custom -->
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

यूआरएल पैरामीटर `useParams` हुक के माध्यम से उपलब्ध हैं, जो एक एक्सेसर लौटाता है:

```tsx filename="src/routes/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const params = useParams<{ slug: string }>();
  return <h1>{params().slug}</h1>;
}
```

## लेआउट

### क्रियान्वयन

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

`props.children` को नष्ट न करें, क्योंकि Solid इसे आलस्य से पढ़ता है।
<!-- /router -->

## द्वीप

सर्वर मोड में, एक Solid घटक को एक में आयात किया जाता है `.nexy` फ़ाइल एक द्वीप है।

### आयात करना

`.nexy` फ़ाइल के फ्रंटमैटर में घटकों को आयात करें:

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<Counter start=3 />
```
<!-- /router -->

### जलयोजन निर्देश

द्वीप के हाइड्रेट होने को नियंत्रित करने के लिए `directive` प्रोप का उपयोग करें:

- `client:load` (डिफ़ॉल्ट): तुरंत
- `client:idle`: जब ब्राउज़र निष्क्रिय हो
- `client:visible`: जब यह दृश्य में स्क्रॉल करता है
- `client:media`: जब मीडिया क्वेरी मेल खाती है

## क्रियाएँ और नेविगेशन

### कॉलिंग क्रियाएं

किसी एक्शन कॉल की स्थिति को प्रबंधित करने के लिए `useAction` हुक का उपयोग करें। Solid में, यह एक्सेसर्स लौटाता है (उन्हें फ़ंक्शंस के रूप में कॉल करें)।

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

- [दृश्य](../README.md): उन स्वरूपों की तुलना करें जिनका उपयोग पृष्ठ कर सकता है
- [फ्रंटएंड](../../guides/frontend.md): Vite और क्लाइंट बिल्ड
