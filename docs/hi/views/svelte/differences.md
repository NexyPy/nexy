# Svelte

नेक्सी सर्वर पर Svelte 5 घटकों को प्रस्तुत करता है, फिर Svelte उन्हें ब्राउज़र में ले लेता है। पेज, लेआउट, द्वीप और क्रियाएं हर ढांचे में समान हैं: यह पेज सेटअप को कवर करता है, फिर वे हिस्से जो [साझा अनुबंध ](../frontend/pages.md) से भिन्न होते हैं।

| मोड | `nexyconfig.py` | पेज हैं | Svelte है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.svelte` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट प्रारंभ करें

```bash
nx new my-app --template web-fbr-svelte
```

टेम्प्लेट Svelte द्वीपों वाला एक सर्वर-मोड प्रोजेक्ट है। इसके बजाय संकेतों का उत्तर देने के लिए टेम्पलेट के बिना `nx new my-app` चलाएं: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं, फिर फ्रेमवर्क।

## किसी मौजूदा प्रोजेक्ट में Svelte सक्षम करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte


class NexyConfig(NexyConfigModel):
    useFF = svelte()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import { svelte } from "@sveltejs/vite-plugin-svelte";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), svelte()],
  customLogger: nexy.log(),
});
```

`nx new` यह फ़ाइल लिखता है; नेक्सी स्वयं `__nexy__/vite.ts` लिखता है, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `svelte` | `^5.20.2` |
| `@sveltejs/vite-plugin-svelte` | `^5.0.0` |

## नियम

- **Svelte 5.** घटक रून्स का उपयोग करते हैं: `$props()`, `$state()`, और बच्चों के लिए स्निपेट।
- **प्रति प्रोजेक्ट एक ढाँचा।** `useFF` बिल्कुल एक ढाँचा लेता है; `useFF = [svelte(), vue()]` स्टार्टअप पर सर्वर को रोक देता है।
- **प्रति फ़ाइल एक घटक।** जिस नाम के अंतर्गत आप `.svelte` फ़ाइल आयात करते हैं, वह केवल वह टैग है जिसे आप लिखते हैं।
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पृष्ठ नहीं हैं।
- **सर्वर-मोड प्रोजेक्ट में कोई `.svelte` पेज** नहीं है, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी शुरू करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।

## पन्ने

क्लाइंट मोड (`useCSR = True`) में, एक पेज एक `.svelte` फ़ाइल है।

### पृष्ठ घटक

पृष्ठ `.svelte` फ़ाइल के स्क्रिप्ट ब्लॉक द्वारा परिभाषित घटक है।

```svelte filename="src/routes/index.svelte"
<script lang="ts">
</script>

<h1>Hello</h1>
```

### गतिशील खंड

यूआरएल पैरामीटर `$props()` रूण के माध्यम से प्रॉप्स के रूप में पृष्ठ तक पहुंचते हैं:

```svelte filename="src/routes/blog/[slug].svelte"
<script lang="ts">
  let { slug }: { slug: string } = $props();
</script>

<h1>{slug}</h1>
```

वैकल्पिक रूप से, किसी भी घटक में `@nexy/client` से `$params` स्टोर का उपयोग करें।

## लेआउट

### क्रियान्वयन

रूट लेआउट दस्तावेज़ शेल को परिभाषित करता है। नेस्टेड लेआउट `children` स्निपेट का उपयोग करके सामग्री को लपेटते हैं।

```svelte filename="src/routes/layout.svelte"
<script lang="ts">
  import type { Snippet } from "svelte";
  let { children }: { children?: Snippet } = $props();
</script>

<html>
  <body>
    <header>My app</header>
    <main>{@render children?.()}</main>
  </body>
</html>
```

## द्वीप

सर्वर मोड में, एक Svelte घटक को एक में आयात किया जाता है `.nexy` फ़ाइल एक द्वीप है।

### आयात करना

`.nexy` फ़ाइल के फ्रंटमैटर में घटकों को आयात करें:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.svelte" import Counter
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

किसी एक्शन कॉल की स्थिति को प्रबंधित करने के लिए `useAction` हुक का उपयोग करें। Svelte में, यह एक स्टोर लौटाता है (`$` के साथ पढ़ें)।

```svelte
<script lang="ts">
  import { useAction } from "@nexy/client";
  import { add_todo } from "@nexy/actions";

  let title = $state("");
  const save = useAction(add_todo, { onSuccess: () => (title = "") });
</script>

<form onsubmit={(e) => { e.preventDefault(); save.run({ title }); }}>
  <input bind:value={title} />
  <button disabled={$save.pending}>Add</button>
</form>
```

### नेविगेशन

क्लाइंट-साइड ट्रांज़िशन के लिए `Link` घटक का उपयोग करें:

```svelte
<script lang="ts">
  import Link from "@nexy/Link.svelte";
</script>

<Link href="/about" activeClass="active">About</Link>
```

प्रोग्रामेटिक नेविगेशन के लिए, `@nexy/client` से `router` ऑब्जेक्ट का उपयोग करें:

```ts
import { router } from "@nexy/client";

router.push("/dashboard");
```

### यूआरएल पहुंच

सभी स्थान डेटा स्टोर के रूप में प्रदान किया गया है:

- `$pathname`: वर्तमान पथ
- `$params`: गतिशील खंड
- `$searchParams`: क्वेरी स्ट्रिंग
- `$location`: पूर्ण स्थान वस्तु

## अगले चरण

- [दृश्य](../README.md): उन स्वरूपों की तुलना करें जिनका उपयोग पृष्ठ कर सकता है
- [फ्रंटएंड](../../guides/frontend.md): Vite और क्लाइंट बिल्ड
