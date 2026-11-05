# लिंक करना और नेविगेट करना

क्लाइंट रूटिंग (`useCSR = True`) के साथ, दो पेजों के बीच एक लिंक दस्तावेज़ को पुनः लोड करने के बजाय ब्राउज़र में पेज को स्वैप करता है। लेआउट अपनी स्थिति बनाए रखते हैं.

## सादे लिंक पहले से ही काम करते हैं

आपके प्रोजेक्ट के प्रत्येक पृष्ठ पर `<a href>` क्लाइंट पर नेविगेट करता है, बिना किसी घटक और मार्कर के:

```html
<a href="/about">About</a>
```

ब्राउज़र पर एक लिंक छोड़ा जाता है, और पृष्ठ सामान्य रूप से लोड होता है, जब:

- एक संशोधक कुंजी रखी हुई है, या बटन मुख्य नहीं है;
- इसमें `target` (`_self` के अलावा), `download`, `rel="external"` या `data-nexy-reload` है;
- `href` एक अन्य मूल है, एक `mailto:` या `tel:` लिंक, या केवल एक `#fragment`;
- पथ किसी भी क्लाइंट रूट से मेल नहीं खाता है, इसलिए सर्वर इसका उत्तर देता है।

## `Link`

`Link` वही एंकर है जो एक साधारण व्यक्ति नहीं कर सकता: इसका `href` आपके मार्गों के विरुद्ध जांचा जाता है, यह लक्ष्य पृष्ठ को गर्म करता है, और यह जानता है कि यह वर्तमान पृष्ठ पर कब इंगित करता है। जब आप `nx dev` या `nx build` चलाते हैं तो नेक्सी आपके फ्रेमवर्क का `Link` `__nexy__/src` में उत्पन्न करता है।

| फ़्रेमवर्क | आयात |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| प्रोप | मतलब |
|---|---|
| `href` | प्रोजेक्ट का एक रूट (टाइपो एक प्रकार की त्रुटि है), वैकल्पिक रूप से `?query` या `#fragment`, या एक बाहरी यूआरएल के साथ। |
| `replace` | इतिहास प्रविष्टि को जोड़ने के बजाय बदलें। |
| `scroll` | `false` नेविगेट करने के बाद स्क्रॉल स्थिति बनाए रखता है। डिफ़ॉल्ट: `true`। |
| `prefetch` | `'intent'` (डिफ़ॉल्ट) पृष्ठ को होवर, फ़ोकस या स्पर्श पर लोड करता है; `'viewport'` जब लिंक स्क्रॉल होकर दृश्य में आता है; `false` कभी नहीं। |
| `activeClassName` | जब लिंक वर्तमान पृष्ठ या उसके नीचे एक पृष्ठ (`activeClass` में Vue और Svelte) पर इंगित करता है तो कक्षा में जोड़ा जाता है। |
| `exact` | केवल सटीक पृष्ठ पर सक्रिय। |

वर्तमान पृष्ठ पर इंगित करने वाला लिंक `aria-current="page"` भी मिलता है।

## हुक

स्थान हर ढाँचे में, उस ढाँचे के मुहावरे में उपलब्ध है। पहले के दौरान, सर्वर-साइड अनुरोध के यूआरएल के साथ हुक उत्तर प्रस्तुत करता है, ताकि पेज बिना किसी बेमेल के हाइड्रेट हो जाए।

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| पथ | `usePathname()` | `usePathname()` एक एक्सेसर लौटाता है | `usePathname()` एक रेफरी लौटाता है | `$pathname` स्टोर |
| रूट पैरामीटर्स | `useParams()` | `useParams()` एक्सेसर | `useParams()` रेफरी | `$params` स्टोर |
| क्वेरी | `useSearchParams()` | `useSearchParams()` एक्सेसर | `useSearchParams()` रेफरी | `$searchParams` स्टोर |
| सब कुछ | `useLocation()` | `useLocation()` एक्सेसर | `useLocation()` रेफरी | `$location` स्टोर |
| नेविगेट करें | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

क्वेरी एक `URLSearchParams` है। `useRouter()` और `router` दें `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` और `prefetch(href)`; `push` और `replace` `{ scroll: false }` स्वीकार करते हैं।

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` एक `<img>` प्रस्तुत करता है जो डिफ़ॉल्ट रूप से आलसी है और इसका आकार ज्ञात होने पर लेआउट को स्थानांतरित नहीं करता है।

| फ़्रेमवर्क | आयात |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` आवश्यक है; सजावटी छवि के लिए `alt=""` का उपयोग करें। इसके गायब होने पर नेक्सी एक बार चेतावनी देती है।
- `width` और `height` दोनों के साथ, विशेषताएँ ब्राउज़र को पहलू अनुपात देती हैं और छवि तरल बनी रहती है (`height: auto; max-width: 100%`)।
- `priority` छवि को अब उच्च प्राथमिकता पर लोड करता है, जो आगमन पर दिखाई देती है।
- `fill` `width` और `height` को नजरअंदाज करते हुए, छवि को उसके स्थित मूल को कवर कर देता है।
- `sizes` और `srcSet` गुजरते हैं। नेक्सी छवियों का आकार बदलता या परिवर्तित नहीं करता है।

## `.nexy` पेज से लिंक

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` `<a href="/about" data-nexy-link="true">` प्रस्तुत करता है। प्रत्येक विशेषता और `href` HTML से बच गए हैं।

## राउटर क्या करता है

नेविगेशन पर, राउटर:

1. क्लाइंट मार्गों के विरुद्ध पथ से मेल खाता है (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. पृष्ठ और उसके [लेआउट्स](../layouts/README.md) **पहले** को आयात और प्रस्तुत करता है, और उसके बाद ही यूआरएल को `history.pushState` के साथ ले जाता है, इसलिए पता बार कभी भी विफल पृष्ठ नहीं दिखाता है;
3. `nexy:navigated` इवेंट को `document` पर भेजता है;
4. शीर्ष पर, या `#fragment` लक्ष्य तक स्क्रॉल करता है।

एक नया नेविगेशन पुराने नेविगेशन को रद्द कर देता है जो अभी भी प्रस्तुत हो रहा है। यदि कोई पृष्ठ प्रस्तुत नहीं हो पाता है, तो ब्राउज़र इसके बदले सर्वर से इसके लिए पूछता है। पीछे और आगे के बटन उस प्रविष्टि के पृष्ठ को प्रस्तुत करते हैं और उसकी स्क्रॉल स्थिति को पुनर्स्थापित करते हैं।

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

राउटर केवल क्लाइंट रूट वाले प्रोजेक्ट में शुरू होता है, इसलिए सर्वर-रेंडर प्रोजेक्ट ब्राउज़र का अपना बैक बटन और स्क्रॉल रिस्टोरेशन रखता है।

## अगले चरण

- [लेआउट](../layouts/README.md)
- [सीएसआर](../../../rendering/csr.md)
- [घटक](../../../views/nexy/components.md)
