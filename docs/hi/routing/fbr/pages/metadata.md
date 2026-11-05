# पेज मेटाडेटा

एक पेज अपने शीर्षक और उसके हेड टैग को नाम देता है, और रूट लेआउट उन्हें एक बार लिखता है।

## इसे पेज में कहें

ऐसे पृष्ठ के लिए जो कभी नहीं बदलता, फ्रंटमैटर के शीर्ष पर एक शाब्दिक लिखें:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

जब शीर्षक डेटा पर निर्भर करता है, तो इसके बजाय `setMetadata` पर कॉल करें:

```nexy filename="src/routes/posts/[स्लग].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

एक मॉड्यूलर नियंत्रक `useViews(...)` लौटाने से पहले `setMetadata(...)` को कॉल करता है।

## इसे लेआउट में लिखें

रूट लेआउट `<head>` का स्वामी है। एक पंक्ति लिखती है कि पेज ने क्या कहा, बच गया:

```nexy filename="src/routes/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

एक पेज अपने लेआउट से पहले चलता है, इसलिए लेआउट को पता चल जाता है कि पेज ने क्या मांगा है। एक पृष्ठ जो कुछ नहीं कहता है उसे आपके `nexyconfig.py` का `useTitle` मिलता है, और कोई अन्य टैग नहीं मिलता है।

## खेत

| मैदान | के रूप में लिखा गया है |
|---|---|
| `title` | `<title>`; `title_template="%s \| My site"` के साथ शीर्षक को `%s` में रखा गया है |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, उदाहरण के लिए `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | एक `<meta property="og:...">` प्रति कुंजी: `{"image": "/cover.png"}` देता है `og:image` |
| `twitter` | एक `<meta name="twitter:...">` प्रति कुंजी |
| `extra` | विशेषता निर्देशों की एक सूची, एक `<meta>` प्रत्येक: `[{"name": "theme-color", "content": "#fff"}]` |

बाद की कॉल किसी मान को प्रतिस्थापित कर देती है; `og`, `twitter` और `extra` जो कुछ है उसमें जोड़ें। एक फ़ील्ड जो अस्तित्व में नहीं है वह `TypeError` उठाती है, इसलिए टाइपो चुपचाप कुछ नहीं करता है।

## डिफ़ॉल्ट रूप से सुरक्षित

प्रत्येक मान HTML से बच गया है, इसलिए URL या डेटाबेस से बनाया गया शीर्षक टैग को बंद नहीं कर सकता है और स्क्रिप्ट को इंजेक्ट नहीं कर सकता है। एक मान एक बार बच जाता है, जब लेआउट कॉल करता है `html()`: इसे स्वयं न टालें।

## अगले चरण

- [पेज](README.md)
- [लेआउट](../layouts/README.md)
- [त्रुटि पृष्ठ](../errors/README.md)
