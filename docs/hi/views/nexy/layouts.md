# लेआउट.नेक्सी

सर्वर मोड की लेआउट फ़ाइल (`useCSR = False`)। रूट वाला HTML दस्तावेज़ का स्वामी है।

## रूट लेआउट

```nexy filename="src/routes/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` और `<body>` यहीं रहते हैं और कहीं नहीं।
- `<Vite />` क्लाइंट स्क्रिप्ट और शैलियों को एक बार, `<head>` में इंजेक्ट करता है।
- `{{ children | safe }}` वह जगह है जहां पेज, या अगला नेस्टेड लेआउट प्रस्तुत होता है।

## नेस्टेड लेआउट

एक उपनिर्देशिका में एक `layout.nexy` उस उपवृक्ष को लपेटता है और उसके मूल के अंदर प्रस्तुत करता है। इसकी पुनरावृत्ति नहीं होती
दस्तावेज़ टैग:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` इसे `layout.nexy > blog/layout.nexy > page` के रूप में प्रस्तुत करता है।

## घटक और द्वीप

एक लेआउट `.nexy` घटकों (एक हेडर, एक पादलेख) और क्लाइंट घटकों को आयात कर सकता है। एक ग्राहक
लेआउट में घटक किसी अन्य की तरह एक [द्वीप](../../rendering/islands.md) है:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## बिना किसी लेआउट के

`layout.nexy` के बिना एक प्रोजेक्ट अभी भी एक वैध दस्तावेज़ के साथ उत्तर देता है: नेक्सी न्यूनतम पर वापस आ जाता है
`<!DOCTYPE html>`, व्यूपोर्ट मेटा और वाइट टैग के साथ शेल। जैसे ही आपको आवश्यकता हो, एक लेआउट जोड़ें
एक शीर्षक, फ़ॉन्ट या नेविगेशन.

## मॉड्यूलर राउटर में

नियंत्रक अपने विचार चुनते हैं, इसलिए वे लेआउट स्वयं बनाते हैं:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## यह क्या नहीं कर सकता

- यह `layout.tsx`, `layout.vue` या `layout.svelte` के साथ सह-अस्तित्व में नहीं रह सकता: एक सर्वर-मोड प्रोजेक्ट में है
  कोई क्लाइंट रूट नहीं ([मोड](../../routing/fbr/modes.md))।
- यह क्लाइंट पर नहीं चलता: अन्तरक्रियाशीलता के लिए एक द्वीप का उपयोग करें।

## अगले चरण

- [लेआउट](../../routing/fbr/layouts/README.md)
- [विरासत](../../routing/fbr/inheritance.md)
- [.nexy फ़ाइलें](README.md)