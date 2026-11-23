import { useEffect } from "react";

// The code blocks are server HTML, written in Markdown. This island draws nothing: once it runs, it
// adds a copy button to each block of the page. Without JavaScript the code is still there to select.
export default function CodeCopy() {
  useEffect(() => {
    const blocks = [...document.querySelectorAll<HTMLPreElement>(".prose pre")];
    const buttons = blocks.map((block) => {
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = "Copy";
      button.setAttribute("aria-live", "polite");
      button.className =
        "absolute right-2 top-2 h-8 rounded-md border border-border bg-background px-2.5 font-sans text-xs text-foreground-second hover:text-foreground";
      button.addEventListener("click", async () => {
        const code = block.querySelector("code")?.innerText ?? "";
        try {
          await navigator.clipboard.writeText(code.trimEnd());
          button.textContent = "Copied";
        } catch {
          button.textContent = "Select to copy";
        }
        setTimeout(() => (button.textContent = "Copy"), 2000);
      });
      block.classList.add("relative");
      block.append(button);
      return button;
    });
    return () => buttons.forEach((button) => button.remove());
  }, []);

  return null;
}
