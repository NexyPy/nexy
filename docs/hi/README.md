# नेक्सी दस्तावेज़ीकरण

**फुलस्टैक वेब अनुप्रयोगों के लिए एक Python ढांचा।**

नेक्सी आपके पेजों और आपके एपीआई को एक Python प्रोजेक्ट में रखता है, जो एक सर्वर द्वारा परोसा जाता है। संस्करण 2.2 FastAPI पर बनाया गया है: प्रत्येक एपीआई रूट एक FastAPI रूट है, जो OpenAPI स्कीमा में सूचीबद्ध है जिसे स्केलर `/docs` पर दिखाता है।

- **Python पहले।** पृष्ठ, समापन बिंदु, रूप और क्रियाएं Python हैं, और एक पृष्ठ को JavaScript की आवश्यकता नहीं है।
- **जब आप एक फ्रंटएंड चाहते हैं।** React, Vue, Svelte, Solid या Preact, एक घटक के लिए या पूरी साइट के लिए।
- **एक फ़ाइल, एक यूआरएल।** `src/routes/` के अंतर्गत एक फ़ाइल एक मार्ग है: `.nexy` एक पृष्ठ है, `.py` एक एपीआई समापन बिंदु है।
- **विकसित करने के लिए जगह।** एक फ़ाइल से प्रारंभ करें; प्रोजेक्ट बढ़ने पर मॉड्यूल पर जाएँ, या मौजूदा FastAPI राउटर में प्लग इन करें।

अब यहां? [नेक्सी क्या है?](getting-started/what-is-nexy.md) पढ़ें, फिर [त्वरित शुरुआत](getting-started/quick-start.md) पढ़ें।

## आरंभ करना

### पहला कदम
| पेज | तुम क्या करोगे |
|---|---|
| [नेक्सी क्या है?](getting-started/what-is-nexy.md) | जानिए नेक्सी क्या है, यह किस पर बनी है और आपको क्या मिलता है |
| [स्थापना](getting-started/installation.md) | uv और नेक्सी सीएलआई स्थापित करें, फिर अपना पहला प्रोजेक्ट बनाएं |
| [त्वरित शुरुआत](getting-started/quick-start.md) | एक प्रोजेक्ट बनाएं, इसे लाइव रीलोड के साथ चलाएं और उत्पादन के लिए इसका निर्माण करें |
| [ट्यूटोरियल](getting-started/tutorial.md) | 10 मिनट में एंडपॉइंट, साझा डेटा और प्रोडक्शन बिल्ड के साथ एक नोट्स पेज बनाएं |

### मॉडल को समझें
| पेज | तुम क्या करोगे |
|---|---|
| [मूल अवधारणाएँ](getting-started/core-concepts.md) | मानसिक मॉडल प्राप्त करें: मार्ग, पृष्ठ, दृश्य, घटक, हैंडलर, समापन बिंदु |
| [परियोजना संरचना](getting-started/project-structure.md) | जानें कि किसी प्रोजेक्ट में प्रत्येक फ़ोल्डर और फ़ाइल किस लिए है |
| [एक राउटर चुनें](routing/README.md) | फ़ाइल-आधारित, मॉड्यूलर या कस्टम राउटर चुनें |
| [एक दृश्य प्रारूप चुनें](views/README.md) | किसी पृष्ठ के लिए `.nexy`, Markdown या क्लाइंट फ़्रेमवर्क चुनें |

### कहीं और से आ रहा है
| पेज | तुम क्या करोगे |
|---|---|
| [किसी अन्य ढाँचे से आ रहा है](getting-started/coming-from-other-frameworks.md) | FastAPI, Next.js और एक्सप्रेस आदतों का नेक्सी में अनुवाद करें |

## रूटिंग

### फ़ाइल-आधारित {fbr}
| पेज | तुम क्या करोगे |
|---|---|
| [फ़ाइल-आधारित रूटिंग](routing/fbr/README.md) | फ़ाइल पथ को URL में बदलें |
| [पन्ने](routing/fbr/pages/README.md) | एक पेज लिखें |
| [गतिशील मार्ग](routing/fbr/pages/dynamic-routes.md) | `[slug]`, `[...path]` और रूट समूहों का उपयोग करें |
| [पेज मेटाडेटा](routing/fbr/pages/metadata.md) | पृष्ठ का शीर्षक, विवरण सेट करें और छवि साझा करें {new} |
| [लेआउट](routing/fbr/layouts/README.md) | पेजों के बीच एक फ़्रेम साझा करें |
| [वंशानुक्रम](routing/fbr/inheritance.md) | लेआउट, निर्भरता और त्रुटि पृष्ठों का रिज़ॉल्यूशन क्रम पढ़ें |
| [सर्वर मोड और क्लाइंट मोड](routing/fbr/modes.md) | `useCSR`, और प्रत्येक मोड क्या अनुमति देता है |
| [लिंक करना और नेविगेट करना](routing/fbr/navigation/linking-and-navigating.md) | पेज लिंक करें, क्लाइंट पर नेविगेट करें, प्रीफ़ेच करें |
| [हुक्स](routing/fbr/navigation/hooks.md) | पथ, क्वेरी, कुकीज़ और सत्र पढ़ें |

### हैंडलर और त्रुटियाँ {fbr}
| पेज | तुम क्या करोगे |
|---|---|
| [मार्ग संचालक](routing/fbr/handlers/README.md) | एक Python समापनबिंदु जोड़ें |
| [सत्यापन और त्रुटियाँ](routing/fbr/handlers/validation-and-errors.md) | `422` और `404` का उत्तर दें, और एक `HTTPException` बढ़ाएँ |
| [WebSocket संचालक](routing/fbr/realtime/websocket.md) | `SOCKET` कनेक्शन संभालें |
| [निर्भरताएँ और रक्षक](routing/fbr/dependencies/README.md) | हैंडलर से पहले `dependencies.py` चलाएँ और उसे इनहेरिट करें |
| [मिडलवेयर फ़ाइलें](routing/fbr/middleware/README.md) | अनुरोधों को `middleware.py` के साथ लपेटें, जो निर्देशिका द्वारा विरासत में मिला है |
| [त्रुटि पृष्ठ](routing/fbr/errors/README.md) | `notfound.nexy`, `errors.nexy` और JSON त्रुटियों के साथ उत्तर दें |
| [प्रति फ़ोल्डर त्रुटि पृष्ठ](routing/fbr/errors/folder-pages.md) | एज केस: उप-फ़ोल्डर्स से त्रुटियाँ |

### मॉड्यूलर राउटर {modular}
नियंत्रक और मॉड्यूल.
| पेज | तुम क्या करोगे |
|---|---|
| [मॉड्यूलर रूटिंग](routing/modular/README.md) | नियंत्रक और मॉड्यूल माउंट करें |
| [निर्भरता इंजेक्शन](routing/modular/dependency-injection.md) | सेवाओं, उनके दायरे और कंटेनर को परिभाषित करें |
| [गार्ड और मेटाडेटा](routing/modular/guards-and-metadata.md) | मार्गों को सुरक्षित रखें और दस्तावेजित करें |
| [मॉड्यूलर राउटर बनाम NestJS](routing/modular/vs-nestjs.md) | NestJS से तुलना |

### कस्टम राउटर एकीकरण {custom}
| पेज | तुम क्या करोगे |
|---|---|
| [कस्टम रूटिंग](routing/custom/README.md) | एक मौजूदा FastAPI ऐप शामिल करें |

## अग्रभाग

### साझा अनुबंध
| पेज | यह क्या परिभाषित करता है |
|---|---|
| [फ्रंटएंड पेज](views/frontend/pages.md) | एक फ़ाइल, एक रूट: प्रॉप्स, रेंडरिंग, मेटाडेटा |
| [फ्रंटएंड लेआउट](views/frontend/layouts.md) | दस्तावेज़ शेल, नेस्टिंग, और एक लेआउट क्या नहीं कर सकता |
| [क्रियाएँ और नेविगेशन](views/frontend/actions-and-navigation.md) | टाइप की गई कार्रवाई को कॉल करें, पेज लिंक करें, यूआरएल पढ़ें |

### नेक्सी विचार
| पेज | तुम क्या करोगे |
|---|---|
| [.nexy फ़ाइलें](views/nexy/README.md) | Python, Jinja2 और प्रॉप्स के साथ एक पेज लिखें |
| [घटक](views/nexy/components.md) | `Image`, `Link`, `Audio`, `Video` और `Import` का उपयोग करें |
| [लेआउट.नेक्सी](views/nexy/layouts.md) | सर्वर-मोड लेआउट लिखें |
| [Markdown और MDX](views/nexy/markdown.md) | सामग्री पृष्ठ लिखें |

### ढाँचे में अंतर
| पेज | क्या बदलता है |
|---|---|
| [React मतभेद](views/react/differences.md) | घटक, हुक और `layout.tsx` {new} |
| [Vue मतभेद](views/vue/differences.md) | एसएफसी, रेफरी और `layout.vue` {new} |
| [Svelte मतभेद](views/svelte/differences.md) | रूण, भंडार और `layout.svelte` {new} |
| [Solid मतभेद](views/solid/differences.md) | सिग्नल, एक्सेसर्स और `layout.tsx` {new} |
| [Preact मतभेद](views/preact/differences.md) | हुक, सिग्नल और `layout.tsx` {new} |

## प्रतिपादन

### मोड
| पेज | आप क्या निर्णय लेंगे |
|---|---|
| [प्रतिपादन](rendering/README.md) | कौन सा रेंडरिंग मोड एक पेज पर फिट बैठता है |
| [एसएसआर](rendering/ssr.md) | सर्वर रेंडरिंग, डिफ़ॉल्ट |
| [आईएसआर](rendering/isr.md) | बासी-जबकि-पुनर्वैधीकरण के साथ कैश पेज |
| [सीएसआर](rendering/csr.md) | क्लाइंट-साइड रूटिंग |
| [द्वीप](rendering/islands.md) | निष्क्रिय, दृश्यमान या मीडिया क्वेरी पर हाइड्रेट करें |

## मार्गदर्शक

### फॉर्म और डेटा
| पेज | तुम क्या करोगे |
|---|---|
| [क्रियाएँ](guides/actions.md) | किसी फॉर्म या टाइप किए गए TypeScript फ़ंक्शन से Python फ़ंक्शन को कॉल करें |
| [डेटाबेस](guides/databases.md) | एक ORM चुनें और माइग्रेशन चलाएँ |

### सुरक्षा एवं तैनाती
| पेज | तुम क्या करोगे |
|---|---|
| [मिडलवेयर और सुरक्षा](guides/middleware-and-security.md) | CORS, GZip, विश्वसनीय होस्ट और सत्र सेट करें |
| [तैनाती](deployment/README.md) | बनाएं, कंटेनरीकृत करें और परोसें |
| [प्रदर्शन](deployment/performance.md) | डिफ़ॉल्ट को मापें और ट्यून करें |

### बनाएं और परीक्षण करें
| पेज | तुम क्या करोगे |
|---|---|
| [Vite और स्टाइल](guides/frontend.md) | Vite, स्टाइलिंग और क्लाइंट बिल्ड सेट करें |
| [परीक्षण](guides/testing.md) | pytest, `TestClient` और विटेस्ट के साथ परीक्षण करें |

### टूलींग और सहायता
| पेज | तुम क्या करोगे |
|---|---|
| [देव टूलबार](guides/devtools.md) | `nexy dev` के टूलबार का उपयोग करें, और इसे बंद करें |
| [कोडिंग एजेंट](guides/ai-agents.md) | Claude Code, Codex और OpenCode अपने प्रोजेक्ट के नियम बताएं |
| [समस्या निवारण](guides/troubleshooting.md) | लोगों द्वारा झेली गई पहली समस्याओं को ठीक करें |

## संदर्भ

### कमांड और कॉन्फिग
| पेज | यह क्या सूचीबद्ध करता है |
|---|---|
| [सीएलआई](reference/cli.md) | आदेश, झंडे, संकेत और निकास कोड |
| [कॉन्फ़िग](reference/config.md) | प्रत्येक `nexyconfig.py` फ़ील्ड और उसका डिफ़ॉल्ट |

### Python एपीआई और त्रुटियां
| पेज | यह क्या सूचीबद्ध करता है |
|---|---|
| [Python एपीआई](reference/python-api.md) | प्रत्येक नाम नेक्सी मॉड्यूल द्वारा निर्यात करता है |
| [अपवाद और त्रुटियाँ](reference/exceptions.md) | प्रत्येक विफलता, उसकी स्थिति, और वह फ़ाइल जो उसका उत्तर देती है |

### परंपराएँ और अवधारणाएँ
| पेज | तुम क्या करोगे |
|---|---|
| [फ़ाइल कन्वेंशन](reference/file-conventions.md) | आरक्षित फ़ाइलें और रूटिंग नियम |
| [शब्दावली](reference/glossary.md) | ये दस्तावेज़ जिन शब्दों का उपयोग करते हैं |
| [सुरक्षा](reference/security.md) | संस्करण फ़्लोर, नेक्सी द्वारा अनुसरण किए जाने वाले नियम, ऑडिट |

## लेआउट
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
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

| पेज | तुम क्या करोगे |
|---|---|
| [नेक्सी कैसे काम करती है](getting-started/how-nexy-works.md) | देखें कि फ़ाइल और पृष्ठ के बीच क्या होता है, और नेक्सी आपके लिए क्या छोड़ता है |
| [2.2 में अपग्रेड किया जा रहा है](getting-started/upgrading.md) | 2.1 से 2.2 पर माइग्रेट करें |
| [अंतर्राष्ट्रीयकरण (i18n)](guides/i18n.md) | अपनी पसंद की लाइब्रेरी से अनुवाद जोड़ें |
| [व्यंजन विधि](guides/recipes.md) | उदाहरण और पैटर्न, ट्यूटोरियल नहीं |

*ये पृष्ठ डिफ़ॉल्ट पठन पथ का हिस्सा नहीं हैं। एक "सभी दस्तावेज़" लिंक आपको सब कुछ देखने की अनुमति देता है।*
