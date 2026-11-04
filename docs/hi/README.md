# नेक्सी दस्तावेज़ीकरण

**फुलस्टैक वेब अनुप्रयोगों के लिए एक पायथन ढांचा।**

नेक्सी एक पायथन बैकएंड और ब्राउज़र फ्रंटएंड के बीच के सीम के बारे में है। दो सर्वर के बजाय, दो
सिस्टम और दो रूट टेबल बनाएं, आपको एक मूल मिलता है: फास्टएपीआई और स्टारलेट एप्लिकेशन की सेवा करते हैं,
वाइट क्लाइंट बनाता है, और `src/routes/` के अंतर्गत एक फ़ाइल एक रूट है - `.nexy` एक पेज है, `.py` एक रूट है
एपीआई हैंडलर.

- **पायथन पहले।** पेज, एंडपॉइंट, फॉर्म और क्रियाएं पायथन हैं, और एक सर्वर-रेंडर पेज की जरूरत है
  कोई फ्रंटएंड ढांचा नहीं.
- **तीन राउटर, एक एकीकरण।** फ़ाइल-आधारित, मॉड्यूलर, या एक मौजूदा फास्टएपीआई `APIRouter`।
- **एक फ्रंटएंड जब आप एक चाहते हैं।** रिएक्ट, व्यू, स्वेल्ट, सॉलिड या प्रीएक्ट, प्रति पृष्ठ द्वीपों के रूप में, या के लिए
  संपूर्ण प्रोजेक्ट क्लाइंट मोड में.
- **रेंडरिंग, एक मॉडल।** सर्वर रेंडरिंग, कैश्ड पेज और द्वीप प्रति पेज तय किए जाते हैं; ग्राहक
  रूटिंग एक प्रोजेक्ट स्विच है।
- **टाइप की गई क्रियाएं।** एक फॉर्म पोस्ट और एक टाइप की गई क्लाइंट कॉल एक ही पायथन फ़ंक्शन तक पहुंचती है।

`src/routes/` के अंतर्गत एक फ़ाइल से प्रारंभ करें, और प्रोजेक्ट बढ़ने पर संरचना जोड़ें।

## आरंभ करना

### पहला कदम
| पेज | आप क्या करेंगे |
|---|---|
| [इंस्टॉलेशन](getting-started/installation.md) | यूवी और नेक्सी सीएलआई इंस्टॉल करें, फिर अपना पहला प्रोजेक्ट बनाएं |
| [त्वरित शुरुआत](getting-started/quick-start.md) | एक प्रोजेक्ट बनाएं, इसे लाइव रीलोड के साथ चलाएं, और इसे उत्पादन के लिए बनाएं |
| [ट्यूटोरियल](getting-started/tutorial.md) | 10 मिनट में एंडपॉइंट, साझा डेटा और प्रोडक्शन बिल्ड के साथ एक नोट्स पेज बनाएं |

### मॉडल को समझें
| पेज | आप क्या करेंगे |
|---|---|
| [मुख्य अवधारणाएं](getting-started/core-concepts.md) | मानसिक मॉडल प्राप्त करें: मार्ग, पृष्ठ, दृश्य, घटक, हैंडलर, समापन बिंदु |
| [नेक्सी कैसे काम करती है](getting-started/how-nexy-works.md) | यूआरएल से उस फ़ाइल तक एक अनुरोध का पालन करें जो इसका उत्तर देती है |
| [आर्किटेक्चर](architecture.md) | जानें कि कौन सी परत क्या करती है, और नेक्सी आपके एप्लिकेशन पर क्या छोड़ता है |
| [प्रोजेक्ट संरचना](getting-started/project-structure.md) | जानें कि प्रोजेक्ट में प्रत्येक फ़ोल्डर और फ़ाइल किसके लिए है |
| [एक राउटर चुनें](routing/README.md) | फ़ाइल-आधारित, मॉड्यूलर या कस्टम राउटर चुनें |
| [एक दृश्य प्रारूप चुनें](views/README.md) | किसी पृष्ठ के लिए `.nexy`, मार्कडाउन या क्लाइंट फ्रेमवर्क चुनें |

### कहीं और से आ रहा हूं
| पेज | आप क्या करेंगे |
|---|---|
| [दूसरे ढांचे से आ रहा है](getting-started/coming-from-other-frameworks.md) | फास्टएपीआई, नेक्स्ट.जेएस और एक्सप्रेस आदतों का नेक्सी में अनुवाद करें |

## रूटिंग

### फ़ाइल-आधारित {fbr}
| पृष्ठ | आप क्या करेंगे |
|---|---|
| [फ़ाइल-आधारित रूटिंग](routing/fbr/README.md) | फ़ाइल पथ को यूआरएल में बदलें |
| [पेज](routing/fbr/pages/README.md) | एक पेज लिखें |
| [गतिशील मार्ग](routing/fbr/pages/dynamic-routes.md) | उपयोग करें `[slug]`, `[...path]` और मार्ग समूह |
| [पेज मेटाडेटा](routing/fbr/pages/metadata.md) | पेज का शीर्षक, विवरण सेट करें और छवि साझा करें {new} |
| [लेआउट्स](routing/fbr/layouts/README.md) | पेजों के बीच एक फ्रेम साझा करें |
| [विरासत](routing/fbr/inheritance.md) | लेआउट, निर्भरता और त्रुटि पृष्ठों का रिज़ॉल्यूशन क्रम पढ़ें |
| [सर्वर मोड और क्लाइंट मोड](routing/fbr/modes.md) | `useCSR`, और प्रत्येक मोड क्या अनुमति देता है |
| [लिंक करना और नेविगेट करना](routing/fbr/navigation/linking-and-navigating.md) | पेजों को लिंक करना, क्लाइंट पर नेविगेट करना, प्रीफ़ेच करना |
| [हुक्स](routing/fbr/navigation/hooks.md) | पथ, क्वेरी, कुकीज़ और सत्र पढ़ें |

### हैंडलर और त्रुटियाँ {fbr}
| पेज | आप क्या करेंगे |
|---|---|
| [रूट हैंडलर](routing/fbr/handlers/README.md) | एक पायथन एंडपॉइंट जोड़ें |
| [सत्यापन और त्रुटियां](routing/fbr/handlers/validation-and-errors.md) | उत्तर `422` और `404`, और एक `HTTPException` | बढ़ाएं
| [वेबसॉकेट हैंडलर](routing/fbr/realtime/websocket.md) | एक `SOCKET` कनेक्शन को संभालें |
| [निर्भरताएं और गार्ड](routing/fbr/dependencies/README.md) | एक हैंडलर से पहले `dependencies.py` चलाएं, और इसे प्राप्त करें |
| [मिडिलवेयर फ़ाइलें](routing/fbr/middleware/README.md) | अनुरोधों को `middleware.py` के साथ रैप करें, जो निर्देशिका द्वारा विरासत में मिला है |
| [त्रुटि पृष्ठ](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy` और JSON त्रुटियों के साथ उत्तर दें |
| [प्रति फ़ोल्डर त्रुटि पृष्ठ](routing/fbr/errors/folder-pages.md) | एज केस: उप-फ़ोल्डरों से त्रुटियां |

### मॉड्यूलर राउटर {modular}
नियंत्रक और मॉड्यूल.
| पेज | आप क्या करेंगे |
|---|---|
| [मॉड्यूलर रूटिंग](routing/modular/README.md) | माउंट नियंत्रक और मॉड्यूल |
| [निर्भरता इंजेक्शन](routing/modular/dependency-injection.md) | सेवाओं, उनके दायरे और कंटेनर को परिभाषित करें |
| [गार्ड और मेटाडेटा](routing/modular/guards-and-metadata.md) | मार्गों की सुरक्षा और दस्तावेजीकरण |
| [मॉड्यूलर राउटर बनाम नेस्टजेएस](routing/modular/vs-nestjs.md) | नेस्टजेएस के साथ तुलना |

### कस्टम राउटर एकीकरण {custom}
| पेज | आप क्या करेंगे |
|---|---|
| [कस्टम रूटिंग](routing/custom/README.md) | एक मौजूदा फास्टएपीआई ऐप शामिल करें |

## फ्रंटेंड

### साझा अनुबंध
| पेज | यह क्या परिभाषित करता है |
|---|---|
| [फ्रंटेंड पेज](views/frontend/pages.md) | एक फ़ाइल, एक रूट: प्रॉप्स, रेंडरिंग, मेटाडेटा |
| [फ्रंटएंड लेआउट्स](views/frontend/layouts.md) | दस्तावेज़ शेल, नेस्टिंग, और एक लेआउट क्या नहीं कर सकता है |
| [क्रियाएं और नेविगेशन](views/frontend/actions-and-navigation.md) | टाइप की गई कार्रवाई को कॉल करें, पेज लिंक करें, यूआरएल पढ़ें |

### नेक्सी दृश्य
| पृष्ठ | आप क्या करेंगे |
|---|---|
| [.nexy फ़ाइलें](views/nexy/README.md) | पायथन, जिंजा2 और प्रॉप्स के साथ एक पेज लिखें |
| [घटक](views/nexy/components.md) | उपयोग करें `Image`, `Link`, `Audio`, `Video` और `Import` |
| [layout.nexy](views/nexy/layouts.md) | सर्वर-मोड लेआउट लिखें |
| [मार्कडाउन और एमडीएक्स](views/nexy/markdown.md) | सामग्री पृष्ठ लिखें |

### ढांचे में अंतर
| पेज | क्या बदलता है |
|---|---|
| [प्रतिक्रिया अंतर](views/react/differences.md) | घटक, हुक और `layout.tsx` {new} |
| [व्यू अंतर](views/vue/differences.md) | एसएफसी, रेफरी और `layout.vue` {new} |
| [विस्तृत अंतर](views/svelte/differences.md) | रूण, भंडार और `layout.svelte` {new} |
| [ठोस अंतर](views/solid/differences.md) | सिग्नल, एक्सेसर्स और `layout.tsx` {new} |
| [प्रैक्टिक मतभेद](views/preact/differences.md) | हुक, सिग्नल और `layout.tsx` {new} |

## प्रतिपादन

### मोड
| पृष्ठ | आप क्या निर्णय लेंगे |
|---|---|
| [रेंडरिंग](rendering/README.md) | कौन सा रेंडरिंग मोड एक पेज में फिट बैठता है |
| [एसएसआर](rendering/ssr.md) | सर्वर रेंडरिंग, डिफ़ॉल्ट |
| [आईएसआर](rendering/isr.md) | पुराने-पुनर्वैधीकरण के साथ कैश पेज |
| [सीएसआर](rendering/csr.md) | क्लाइंट-साइड रूटिंग |
| [द्वीप](rendering/islands.md) | निष्क्रिय, दृश्य या मीडिया क्वेरी पर हाइड्रेट करें |

## मार्गदर्शिकाएँ

### फ़ॉर्म और डेटा
| पेज | आप क्या करेंगे |
|---|---|
| [क्रियाएँ](guides/actions.md) | किसी फॉर्म या टाइप किए गए टाइपस्क्रिप्ट फ़ंक्शन से पायथन फ़ंक्शन को कॉल करें |
| [डेटाबेस](guides/databases.md) | एक ओआरएम चुनें और माइग्रेशन चलाएं |

### सुरक्षा और तैनाती
| पेज | आप क्या करेंगे |
|---|---|
| [मिडिलवेयर और सुरक्षा](guides/middleware-and-security.md) | सीओआरएस, जीज़िप, विश्वसनीय होस्ट और सत्र सेट करें |
| [तैनाती](deployment/README.md) | निर्माण, कंटेनरीकरण और सेवा |
| [प्रदर्शन](deployment/performance.md) | डिफ़ॉल्ट को मापें और समायोजित करें |

### निर्माण और परीक्षण करें
| पेज | आप क्या करेंगे |
|---|---|
| [वाइट और स्टाइलिंग](guides/frontend.md) | वाइट, स्टाइलिंग और क्लाइंट बिल्ड सेट करें |
| [परीक्षण](guides/testing.md) | पाइटेस्ट के साथ परीक्षण, `TestClient` और विटेस्ट |

### उपकरण और सहायता
| पृष्ठ | आप क्या करेंगे |
|---|---|
| [डेवलप टूलबार](guides/devtools.md) | `nexy dev` के टूलबार का उपयोग करें, और इसे बंद करें |
| [कोडिंग एजेंट](guides/ai-agents.md) | क्लाउड कोड, कोडेक्स और ओपनकोड को अपने प्रोजेक्ट के नियम बताएं |
| [समस्या निवारण](guides/troubleshooting.md) | लोगों की पहली समस्याओं को ठीक करें |

## संदर्भ

### कमांड और कॉन्फ़िगरेशन
| पेज | इसमें क्या सूचीबद्ध है |
|---|---|
| [सीएलआई](reference/cli.md) | आदेश, झंडे, संकेत और निकास कोड |
| [कॉन्फिग](reference/config.md) | प्रत्येक `nexyconfig.py` फ़ील्ड और उसका डिफ़ॉल्ट |

### पायथन एपीआई और त्रुटियां
| पेज | इसमें क्या सूचीबद्ध है |
|---|---|
| [पायथन एपीआई](reference/python-api.md) | हर नाम नेक्सी निर्यात करता है, मॉड्यूल द्वारा |
| [अपवाद और त्रुटियां](reference/exceptions.md) | प्रत्येक विफलता, उसकी स्थिति और उसका उत्तर देने वाली फ़ाइल |

### परंपराएँ और अवधारणाएँ
| पृष्ठ | आप क्या करेंगे |
|---|---|
| [फ़ाइल परंपराएं](reference/file-conventions.md) | आरक्षित फ़ाइलें और रूटिंग नियम |
| [शब्दावली](reference/glossary.md) | ये दस्तावेज़ जिन शब्दों का उपयोग करते हैं |
| [सुरक्षा](reference/security.md) | संस्करण फर्श, नेक्सी द्वारा अनुसरण किए जाने वाले नियम, ऑडिट |

## लेआउट
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## उन्नत

### उन्नत {advanced}

| पेज | आप क्या करेंगे |
|---|---|
| [2.2 में अपग्रेड करना](getting-started/upgrading.md) | 2.1 से 2.2 पर माइग्रेट करना |
| [अंतर्राष्ट्रीयकरण (i18n)](guides/i18n.md) | अपनी पसंद की लाइब्रेरी के साथ अनुवाद जोड़ें |
| [रेसिपी](guides/recipes.md) | उदाहरण और पैटर्न, ट्यूटोरियल नहीं |

*ये पृष्ठ डिफ़ॉल्ट पठन पथ का हिस्सा नहीं हैं। एक "सभी दस्तावेज़" लिंक आपको सब कुछ देखने की अनुमति देता है।*