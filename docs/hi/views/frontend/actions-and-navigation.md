# क्रियाएँ और नेविगेशन

नेक्सी में इंटरैक्शन को **एक्शन** और **नेविगेशन** की एक एकीकृत प्रणाली के माध्यम से नियंत्रित किया जाता है, जो यह सुनिश्चित करता है कि फ्रंटएंड और बैकएंड मैनुअल एपीआई ग्लू कोड के बिना सिंक में रहें।

## कार्रवाई अनुबंध

एक **एक्शन** एक सर्वर-साइड फ़ंक्शन है जो उत्परिवर्तन को संभालता है (उदाहरण के लिए, डेटाबेस को अपडेट करना)। 

1.  **टाइप किया गया इनपुट**: क्रियाओं को Python में प्रकार के संकेतों के साथ परिभाषित किया गया है। नेक्सी एक मेल खाने वाला TypeScript क्लाइंट तैयार करता है, जिससे आपको अपने आईडीई में स्वत: पूर्ण और सत्यापन मिलता है।
2.  **परमाणु निष्पादन**: एक कार्रवाई एक एकल `POST` अनुरोध है।
3.  **परिणाम प्रबंधन**: क्रियाएँ एक टाइप किया हुआ परिणाम लौटाती हैं जिसका उपयोग ग्राहक यूआई को अपडेट करने के लिए कर सकता है।

```python filename="src/actions/todos.py"
from pydantic import BaseModel
from nexy.decorators import Action


class Todo(BaseModel):
    title: str
    done: bool = False


@Action
async def add_todo(title: str) -> Todo:
    return Todo(title=title)
```

पृष्ठ इसे घोषित इनपुट Python के साथ कॉल करता है, और टाइप किया हुआ `Todo` वापस प्राप्त करता है:

```tsx filename="src/routes/todos.tsx"
import { useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

export default function Todos() {
  const { run, pending, data } = useAction(add_todo);
  return (
    <button disabled={pending} onClick={() => run({ title: "Write the docs" })}>
      {data ? `Added ${data.title}` : "Add"}
    </button>
  );
}
```

## क्लाइंट-साइड नेविगेशन

नेक्सी में नेविगेशन "बुद्धिमान" है। पूर्ण ब्राउज़र पुनः लोड करने के बजाय, नेक्सी सक्रिय लेआउट को माउंट करते हुए वर्तमान पृष्ठ की सामग्री को स्वैप करता है।

- **`Link` घटक**: क्लाइंट-साइड ट्रांज़िशन करने के लिए फ़्रेमवर्क-विशिष्ट `Link` घटक का उपयोग करें।
- **प्रोग्रामेटिक नेविगेशन**: तर्क के जवाब में पेज बदलने के लिए `@nexy/client` से `useRouter()` का उपयोग करें और `push()` पर कॉल करें (उदाहरण के लिए, एक सफल लॉगिन के बाद)।

```tsx filename="src/components/Nav.tsx"
import { Link } from "@nexy/client";

export function Nav() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about" activeClassName="active">About</Link>
    </nav>
  );
}
```

```tsx filename="src/components/Done.tsx"
import { useRouter } from "@nexy/client";

export function Done() {
  const router = useRouter();
  return <button onClick={() => router.push("/dashboard")}>Continue</button>;
}
```

## समन्वय: क्रिया → नेविगेशन

सबसे आम पैटर्न एक क्रिया करना और फिर उपयोगकर्ता को एक नए पृष्ठ पर नेविगेट करना है।

**पुनर्वैधीकरण प्रवाह:**
1.  क्लाइंट एक एक्शन कॉल करता है।
2.  कार्रवाई सर्वर पर निष्पादित होती है और `revalidate("/path")` को कॉल करती है।
3.  सर्वर पुराने पथों का नामकरण करते हुए `x-nexy-revalidate` हेडर के साथ परिणाम लौटाता है।
4.  क्लाइंट नई स्थिति को प्रतिबिंबित करने के लिए पृष्ठ सामग्री को अपडेट करता है।

```python filename="src/actions/session.py"
from nexy.decorators import Action, revalidate


@Action
async def sign_in(email: str, password: str) -> bool:
    ok = check_password(email, password)
    revalidate("/dashboard")
    return ok
```

```tsx filename="src/routes/login.tsx"
import { useAction, useRouter } from "@nexy/client";
import { sign_in } from "@nexy/actions";

export default function Login() {
  const router = useRouter();
  const { run } = useAction(sign_in, {
    onSuccess: (ok) => {
      if (ok) router.push("/dashboard");
    },
  });
  return <button onClick={() => run({ email: "ada@example.com", password: "..." })}>Sign in</button>;
}
```

`check_password` का अर्थ है आपका अपना चेक। त्रुटियों, JavaScript और सुरक्षा के बिना फ़ॉर्म के लिए [क्रियाएँ](../../guides/actions.md) देखें।

## रूपरेखा कार्यान्वयन

क्रियाओं को कॉल करने और नेविगेट करने के लिए एपीआई फ्रेमवर्क के अनुसार भिन्न-भिन्न होती है। अपनी चुनी हुई तकनीक के लिए **अंतर** मार्गदर्शिका देखें:

- [React मतभेद](../react/differences.md)
- [Vue मतभेद](../vue/differences.md)
- [Svelte मतभेद](../svelte/differences.md)
- [Solid मतभेद](../solid/differences.md)
- [Preact मतभेद](../preact/differences.md)
