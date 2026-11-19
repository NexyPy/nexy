# मैं नेक्सी में सर्वर कोड को कैसे डिबग करूं?

टर्मिनल में `nx dev` के सर्वर कोड को `breakpoint()` के साथ, या वीएस कोड और `debugpy` के साथ डीबग करें: डेव सर्वर आपके Python को अपनी प्रक्रिया में चलाता है, इसलिए इससे जुड़ा एक डिबगर आपके पृष्ठों, एपीआई हैंडलर और कार्यों में रुक जाता है।

## `nx dev` आपका कोड कैसे चलाता है

`nx dev` यूविकॉर्न को बिना किसी अलग कर्मचारी के अपनी प्रक्रिया में शुरू करता है। जब एक Python फ़ाइल या एक `.nexy` पृष्ठ बदलता है, तो यह आपके प्रोजेक्ट के मॉड्यूल को भूल जाता है और उन्हें उसी प्रक्रिया में फिर से आयात करता है। इसलिए `nx dev` से जुड़ा एक डिबगर पुनः लोड के दौरान जुड़ा रहता है, और फ़ाइल में सेट किया गया ब्रेकप्वाइंट नए कोड में अपना स्थान बनाए रखता है।

एक `.nexy` फ़ाइल को `__nexy__/` के अंतर्गत एक Python मॉड्यूल में उसी पथ पर संकलित किया जाता है, जो चलता है:

<!-- router:fbr,custom -->
| तुम लिखो | नेक्सी चलता है |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, फ़ंक्शन `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | फ़ाइल स्वयं |
<!-- /router -->

<!-- router:modular -->
| तुम लिखो | नेक्सी चलता है |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | फ़ाइल स्वयं |
<!-- /router -->

`.nexy` फ़ाइल का फ्रंटमैटर (दो `---` लाइनों के बीच का Python उस मॉड्यूल के फ़ंक्शन का मुख्य भाग बन जाता है। `__nexy__/` प्रत्येक परिवर्तन पर दोबारा लिखा जाता है: इसे कभी संपादित न करें।

## `breakpoint()` के साथ टर्मिनल में रुकें

`breakpoint()` को वहां रखें जहां आप रुकना चाहते हैं, `.py` फ़ाइल में या `.nexy` फ़ाइल के फ्रंटमैटर में:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

पेज खोलें. अनुरोध प्रतीक्षा करता है और `nx dev` का टर्मिनल संकलित मॉड्यूल में पीडीबी दिखाता है:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

`/users` खोलें। अनुरोध प्रतीक्षा करता है और `nx dev` का टर्मिनल उस लाइन पर पीडीबी दिखाता है। दृश्य के फ्रंटमैटर में, पीडीबी `__nexy__/src/apps/` के अंतर्गत संकलित मॉड्यूल दिखाता है।
<!-- /router -->

मान प्रिंट करने के लिए `p page` टाइप करें, अगली पंक्ति के लिए `n` टाइप करें, अनुरोध जारी रखने के लिए `c` टाइप करें। जब आपका काम पूरा हो जाए तो लाइन हटा दें: अगला अनुरोध फिर से वहीं रुक जाता है।

## वीएस कोड के साथ डीबग करें

प्रोजेक्ट के वातावरण में `debugpy` स्थापित करें:

```bash
uv add --dev debugpy
```

फिर एक लॉन्च कॉन्फ़िगरेशन जोड़ें। `nexy.modules.cli` `nx` कमांड के पीछे का मॉड्यूल है, इसलिए यह Linux, macOS और Windows पर समान रूप से काम करता है:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

F5 दबाएँ. अपनी `.py` फ़ाइलों में और `.nexy` फ़ाइल के लिए `__nexy__/` के अंतर्गत संकलित मॉड्यूल में ब्रेकप्वाइंट सेट करें: वीएस कोड `.nexy` फ़ाइल में नहीं रुक सकता, क्योंकि यह संकलित होने तक Python नहीं है। संकलित मॉड्यूल की पंक्ति संख्याएं फ्रंटमैटर का अनुसरण करती हैं, इसलिए पृष्ठ को संपादित करने के बाद वहां एक ब्रेकपॉइंट स्थानांतरित हो सकता है; `breakpoint()` सामने वाले मामले में ऐसा नहीं है।

## दूसरे टर्मिनल से जोड़ें

डेव सर्वर स्वयं शुरू करने और बाद में डिबगर संलग्न करने के लिए:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` डिबगर संलग्न होने तक स्टार्ट को रोके रखता है; इसे तुरंत शुरू करने के लिए छोड़ दें। वीएस कोड में, `"request": "attach"` और `"connect": { "host": "127.0.0.1", "port": 5678 }` के कॉन्फ़िगरेशन के साथ संलग्न करें।

डिबगपी चेतावनी दे सकती है कि "जमे हुए मॉड्यूल का उपयोग किया जा रहा है"। यदि मानक लाइब्रेरी में कोई ब्रेकप्वाइंट छूट गया है, तो Python को `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) से शुरू करें; आपके अपने कोड में ब्रेकप्वाइंट प्रभावित नहीं होते हैं।

## अगले चरण

- [समस्या निवारण](troubleshooting.md): लोगों द्वारा झेली जाने वाली पहली समस्या
- [परीक्षण](testing.md): एक बार बग मिल जाने पर उसे परीक्षण में पुन: उत्पन्न करें
- [.nexy फ़ाइलें](../views/nexy/README.md): फ्रंटमैटर, प्रॉप्स और टेम्प्लेट
