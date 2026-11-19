# मैं Nexy साइट पर sitemap.xml और robots.txt कैसे जोड़ूँ?

`useSiteUrl` को `nexyconfig.py` में सेट करें: नेक्सी फिर `/sitemap.xml` परोसता है, जो प्रोजेक्ट के प्रत्येक स्थिर पृष्ठ को सूचीबद्ध करता है, और एक `/robots.txt` जो खोज इंजन को इसकी ओर इंगित करता है।

## इसे `useSiteUrl` से चालू करें

`useSiteUrl` साइट का सार्वजनिक स्रोत है, जिसे खोज इंजन देखते हैं:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` और `nx start` फिर दोनों फाइलों का उत्तर दें। `useSiteUrl` के बिना कोई भी मौजूद नहीं है, इसलिए कोई प्रोजेक्ट कभी भी गलती से अपने डेव सर्वर का यूआरएल प्रकाशित नहीं करता है।

## साइटमैप क्या सूचीबद्ध करता है

साइटमैप प्रत्येक पृष्ठ को `useSiteUrl` पर एक पूर्ण URL के रूप में देता है:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

एक मार्ग तब सूचीबद्ध होता है जब वह एक निश्चित पथ पर HTML को `GET` का उत्तर देता है:

<!-- router:fbr,custom -->
- एक पृष्ठ (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) सूचीबद्ध है;
- एक गतिशील पृष्ठ, जैसे कि `src/routes/users/[id].nexy`, छोड़ दिया गया है: नेक्सी इसके मूल्यों को नहीं जान सकता है;
- एक Python रूट हैंडलर JSON का उत्तर देता है, इसलिए इसे छोड़ दिया जाता है।
<!-- /router -->

<!-- router:modular -->
- एक नियंत्रक मार्ग जो HTML का उत्तर देता है, `@UseResponse(response_class=HTMLResponse)` के साथ, सूचीबद्ध है;
- पथ पैरामीटर वाला एक मार्ग, जैसे कि `/users/{id}`, छोड़ दिया गया है: नेक्सी इसके मूल्यों को नहीं जान सकता है;
- JSON का उत्तर देने वाला मार्ग छूट गया है।
<!-- /router -->

एपीआई स्कीमा (`include_in_schema=False`) से छिपा हुआ एक मार्ग भी छोड़ दिया गया है।

## `robots.txt` यह कार्य करता है

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## इसके बजाय अपना खुद का लिखें

आपकी अपनी फ़ाइल हमेशा जीतती है, और नेक्सी इसे कभी अधिलेखित नहीं करती:

- `public/robots.txt` या `public/sitemap.xml` को वैसे ही परोसा जाता है, जैसे `public/` की प्रत्येक फ़ाइल को परोसा जाता है;
- `/robots.txt` या `/sitemap.xml` पर परियोजना का एक मार्ग अपना पथ रखता है।

गतिशील पृष्ठों को सूचीबद्ध करने के लिए अपना स्वयं का साइटमैप लिखें, जैसे प्रति ब्लॉग पोस्ट एक यूआरएल।

## अगले चरण

- [पृष्ठ मेटाडेटा](../routing/fbr/pages/metadata.md): शीर्षक और विवरण खोज इंजन दिखाते हैं
- [कॉन्फ़िग](../reference/config.md): `nexyconfig.py` की प्रत्येक सेटिंग
- [परिनियोजन](../deployment/README.md): उत्पादन में परियोजना की सेवा करें
