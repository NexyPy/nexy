# व्यू

Nexy सर्वर पर Vue 3 एकल-फ़ाइल घटकों को प्रस्तुत करता है, फिर Vue उन्हें ब्राउज़र में ले लेता है।
प्रत्येक फ्रेमवर्क में पेज, लेआउट, द्वीप और क्रियाएँ समान हैं: यह पेज सेटअप को कवर करता है, फिर
वे भाग जो [साझा अनुबंध](../frontend/pages.md) से भिन्न हैं।

| मोड | `nexyconfig.py` | पेज हैं | व्यू है |
|---|---|---|---|
| सर्वर (डिफ़ॉल्ट) | `useCSR = False` | `.nexy` फ़ाइलें | [द्वीप](../../rendering/islands.md) उन पृष्ठों के अंदर |
| क्लाइंट | `useCSR = True` | `.vue` फ़ाइलें | संपूर्ण पृष्ठ, [लेआउट्स](../frontend/layouts.md) और एक क्लाइंट राउटर के साथ |

## एक प्रोजेक्ट शुरू करें

```bash
nx new my-app --template web-fbr-vue
```

टेम्प्लेट Vue द्वीपों के साथ एक सर्वर-मोड प्रोजेक्ट है। `nx new my-app` को बिना टेम्पलेट के चलाएँ
इसके बजाय संकेतों का उत्तर दें: राउटर, प्रोजेक्ट प्रकार, क्लाइंट-साइड रूटिंग का उपयोग करना है या नहीं
ढाँचा।

## मौजूदा प्रोजेक्ट में Vue सक्षम करें

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import vue


class NexyConfig(NexyConfigModel):
    useFF = vue()
    useAliases = {"@": "src"}
```

```ts filename="vite.config.ts"
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import nexy from "./__nexy__/vite";

export default defineConfig({
  plugins: [nexy(), vue()],
  customLogger: nexy.log(),
});
```

`nx new` यह फ़ाइल लिखता है; नेक्सी स्वयं `__nexy__/vite.ts` लिखता है, इसलिए इसे संपादित न करें।

| पैकेज | संस्करण `nx new` लिखता है |
|---|---|
| `vue` | `^3.5.33` |
| `@vitejs/plugin-vue` | `^6.0.0` |

## नियम

- **प्रति प्रोजेक्ट एक ढांचा।** `useFF` बिल्कुल एक ढांचा लेता है; `useFF = [vue(), react()]` रुकता है
  स्टार्टअप पर सर्वर.
- **प्रति फ़ाइल एक घटक।** एक `.vue` फ़ाइल अपने घटक को डिफ़ॉल्ट के रूप में निर्यात करती है; जिस नाम से आप इसे आयात करते हैं
  नीचे केवल वह टैग है जिसे आप लिखते हैं।
- **घटक `src/routes/`** के बाहर रहते हैं, आमतौर पर `src/components/` में, इसलिए वे पेज नहीं हैं।
- **एक सर्वर-मोड प्रोजेक्ट में कोई `.vue` पेज नहीं है**, और क्लाइंट-मोड प्रोजेक्ट में कोई `.nexy` पेज नहीं है: नेक्सी
  प्रारंभ करने से इंकार कर देता है और फ़ाइल को नाम देता है। [मोड](../../routing/fbr/modes.md) देखें।

## पेज

क्लाइंट मोड (`useCSR = True`) में, एक पेज एक `.vue` फ़ाइल है।

### पेज घटक

पेज `<script setup>` ब्लॉक द्वारा परिभाषित घटक है।

```vue filename="src/routes/index.vue"
<template>
  <h1>Hello</h1>
</template>
```

### गतिशील खंड

यूआरएल पैरामीटर पेज पर प्रॉप्स के रूप में पहुंचते हैं। आप उन्हें `defineProps` का उपयोग करके घोषित कर सकते हैं:

```vue filename="src/routes/blog/[slug].vue"
<script setup lang="ts">
defineProps<{ slug: string }>();
</script>

<template>
  <h1>{{ slug }}</h1>
</template>
```

वैकल्पिक रूप से, किसी भी घटक में `@nexy/client` से `useParams` हुक का उपयोग करें।

## लेआउट

### कार्यान्वयन

रूट लेआउट दस्तावेज़ शेल को परिभाषित करता है। नेस्टेड लेआउट सामग्री को उनके डिफ़ॉल्ट स्लॉट में लपेटते हैं।

```vue filename="src/routes/layout.vue"
<template>
  <html>
    <body>
      <header>My app</header>
      <main><slot /></main>
    </body>
  </html>
</template>
```

## द्वीप

सर्वर मोड में, `.nexy` फ़ाइल में आयात किया गया एक Vue घटक एक द्वीप है।

### आयात करना

`.nexy` फ़ाइल के फ्रंटमैटर में घटकों को आयात करें:

```nexy filename="src/routes/index.nexy"
---
from "@/components/Counter.vue" import Counter
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

किसी एक्शन कॉल की स्थिति को प्रबंधित करने के लिए `useAction` हुक का उपयोग करें। Vue में, लौटाई गई स्थिति
(`pending`, `data`, `error`) परिकलित रेफरी हैं।

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
  </form>
</template>
```

### नेविगेशन

क्लाइंट-साइड ट्रांज़िशन के लिए `Link` घटक का उपयोग करें:

```vue
<template>
  <Link href="/about" active-class="active">About</Link>
</template>
```

प्रोग्रामेटिक नेविगेशन के लिए, `useRouter` हुक का उपयोग करें:

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/dashboard");
```

### यूआरएल पहुंच

सभी स्थान हुक परिकलित रेफरी लौटाते हैं:

- `usePathname()`: वर्तमान पथ
- `useParams()`: गतिशील खंड
- `useSearchParams()`: क्वेरी स्ट्रिंग
- `useLocation()`: पूर्ण स्थान वस्तु

## अगले चरण

- [दृश्य](../README.md): उन प्रारूपों की तुलना करें जिनका उपयोग पृष्ठ कर सकता है
- [फ्रंटेंड](../../guides/frontend.md): वाइट और क्लाइंट बिल्ड