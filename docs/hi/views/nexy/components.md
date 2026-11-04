# घटक

नेक्सी सहायकों का एक छोटा सा सेट निर्यात करता है जो HTML स्ट्रिंग्स लौटाता है। प्रत्येक का उपयोग दो तरीकों से किया जाता है
`.nexy` टेम्पलेट: जिंजा कॉल के रूप में, या HTML-शैली टैग के रूप में।

## दो वाक्यविन्यास, एक कार्य

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

दोनों पंक्तियाँ समान मार्कअप उत्पन्न करती हैं:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

कंपाइलर `<Audio ... />` को `{{ Audio(...) }}` पर फिर से लिखता है, इसलिए टैग फॉर्म दूसरा एपीआई नहीं है:
विशेषताएँ फ़ंक्शन के कीवर्ड तर्क हैं।

## टैग फॉर्म के नियम

| टैग में | बन जाता है |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, एक वास्तविक बूलियन |
| `width=640` | `width=640`, एक संख्या |
| `src="{{ url }}"` | `src=(url)`, जिंजा में मूल्यांकन किया गया |
| कोई अन्य `value` | `"value"`, एक स्ट्रिंग |

- टैग एक बड़े अक्षर से शुरू होना चाहिए और फ्रंटमैटर में आयात किया जाना चाहिए; अन्यथा
  कंपाइलर बढ़ाता है `Missing Import: <Name> used but not declared.`
- टैग फॉर्म **स्वयं-समापन** है। `<Audio src="/a.mp3" />` और
  `{{ Audio("/a.mp3") }}` समतुल्य हैं; हेल्पर टैग के अंदर बच्चों को लिखना समर्थित नहीं है।
- एक खाली HTML विशेषता यहां बूलियन नहीं है: `controls` `controls=""` बन जाता है, जो गलत है।
  `controls=True` लिखें.

> [!नोट]
> `class_name` सीएसएस कक्षाओं के लिए प्रलेखित कीवर्ड है। अतिरिक्त कीवर्ड तर्क
> HTML विशेषताएँ बन जाती हैं, इसलिए `class="nav"` भी आउटपुट तक पहुँच जाता है।

## छवि

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` एक प्रस्तुत करता है
`<img>` डिफ़ॉल्ट रूप से आलसी लोडिंग के साथ।

## लिंक

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` एक `<a data-nexy-link>` प्रस्तुत करता है
क्लाइंट राउटर द्वारा नियंत्रित किया जाता है। `prefetch=True` के साथ, लिंक को घुमाने या छूने से लक्ष्य गर्म हो जाता है
`window.__nexy_prefetch` के माध्यम से।

> [!नोट]
> टैग फॉर्म लेबल को `children` के रूप में लेता है, तत्व सामग्री के रूप में नहीं:
> `<Link href="/about" children="About" />`। किसी लिंक के अंदर मार्कअप डालने के लिए, कॉल फॉर्म का उपयोग करें
> `children=` या एक `.nexy` घटक जो `<Slot />` प्रस्तुत करता है।

## ऑडियो और वीडियो

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`ऑडियो(src, नियंत्रण = सही, ऑटोप्ले = गलत, लूप = गलत, म्यूट = गलत, प्रीलोड = "मेटाडेटा",
class_name=कोई नहीं, स्रोत=कोई नहीं, **attrs)` and `वीडियो(src, चौड़ाई=कोई नहीं, ऊंचाई=कोई नहीं, ...)' मूल प्रस्तुत करें
खिलाड़ी. `sources` प्रत्येक एक्सटेंशन से प्राप्त MIME प्रकार के साथ `<source>` टैग जोड़ता है।

## एक घटक जिसे आप स्वयं लिखते हैं

एक पुन: प्रयोज्य `.nexy` घटक `src/components/` के अंतर्गत एक फ़ाइल है: शीर्ष पर पायथन प्रॉप्स, नीचे HTML।
इसे किसी अन्य पायथन मॉड्यूल की तरह आयात किया जाता है।

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```

`title` में कोई डिफ़ॉल्ट नहीं है, इसलिए पेज को इसे पास करना होगा; `tone` वापस `"neutral"` पर आ जाता है। मार्कअप
टैग के बीच में `<Slot />` (कैपिटल एस) आता है। देखिये
[.nexy फ़ाइलें](README.md#components) प्रॉप्स, स्लॉट और टैग फॉर्म के नियमों के लिए।

## क्लाइंट घटक आयात करना

`.nexy` फ़ाइल से, पथ द्वारा एक फ्रेमवर्क घटक आयात करें; कंपाइलर इसे क्लाइंट पर माउंट करता है और
विशेषताओं को प्रॉप्स के रूप में पास करता है:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` पायथन में भी यही करता है:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

वही आयात सिंटैक्स `.json`, `.css` और छवि फ़ाइलों को उनके यूआरएल में हल करता है।

## टेम्पलेट और वाइट

`Template().render(path, context)` एक टेम्प्लेट फ़ाइल प्रस्तुत करता है (Jinja2, या मार्कडाउन HTML के लिए प्रस्तुत किया गया है
`.md` मार्ग)। `Template().invalidate(path)` इसे कैश से हटा देता है।

`Vite()` वर्तमान मोड के लिए क्लाइंट टैग लौटाता है: विकास में एचएमआर स्क्रिप्ट, निर्मित
उत्पादन में ग्राहक बंडल। नेक्सी इसे प्रत्येक पृष्ठ के लिए कॉल करता है; आपको शायद ही इसकी सीधे तौर पर आवश्यकता हो।

## अभी तक लागू नहीं किया गया

`Form` और `Script` बिना किसी व्यवहार के निर्यात किए गए प्लेसहोल्डर हैं। उन पर भरोसा मत करो.

## अगले चरण

- [.nexy फ़ाइलें](README.md): जहां इन सहायकों का उपयोग किया जाता है
- [प्रतिक्रिया](../react/differences.md): `.tsx` घटकों को आयात करना
- [फ्रंटएंड](../../guides/frontend.md): क्लाइंट घटकों को कैसे बंडल किया जाता है