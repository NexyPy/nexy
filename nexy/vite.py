import json
import os
from pathlib import Path

from nexy.core.config import Config


def Vite() -> str:
    config = Config()
    if not os.path.exists("vite.config.ts"):
        return ""

    if not config.useVite:
        return ""

    manifest_path = Path("__nexy__/client/.vite/manifest.json")
    prod_server = Path("__nexy__/nexy.prod")
    prod_mode = prod_server.is_file()

    if prod_mode:
        if not manifest_path.is_file():
            return ""
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
            if entry and "file" in entry:
                file_rel = entry["file"].lstrip("/")
                css_files = entry.get("css") or []
                inline = os.getenv("NEXY_INLINE_CLIENT", "").strip() in ("1", "true", "TRUE")
                if inline:
                    css_blocks = []
                    for c in css_files:
                        p = Path("__nexy__/client").joinpath(c.lstrip("/"))
                        if p.is_file():
                            css_blocks.append(f"<style>{p.read_text(encoding='utf-8')}</style>")
                    js_path = Path("__nexy__/client").joinpath(file_rel)
                    js_code = js_path.read_text(encoding="utf-8") if js_path.is_file() else ""
                    return "".join(css_blocks) + f'<script type="module">\n{js_code}\n</script>'
                else:
                    src = f"/{file_rel}"
                    css_links = "".join(
                        f'<link rel="stylesheet" href="/{c.lstrip("/")}" />' for c in css_files
                    )
                    return f'{css_links}<script type="module" src="{src}"></script>'
        except Exception:
            return ""

    # Development Mode
    hmr_script = """
    <script type="module">
        (function() {
            const host = window.location.host;
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${host}/_nexy/hmr`);

            ws.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'nexy:reload') {
                    console.log(`[Nexy HMR] Reloading due to change in: ${data.path}`);

                    try {
                        const res = await fetch(window.location.href, {
                            headers: { 'X-Nexy-HMR': '1' }
                        });
                        const html = await res.text();

                        const parser = new DOMParser();
                        const newDoc = parser.parseFromString(html, 'text/html');

                        document.body.innerHTML = newDoc.body.innerHTML;

                        const scripts = document.body.querySelectorAll('script');
                        scripts.forEach(oldScript => {
                            const newScript = document.createElement('script');
                            Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                            newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                            oldScript.parentNode.replaceChild(newScript, oldScript);
                        });

                        console.log("[Nexy HMR] DOM updated successfully.");
                    } catch (err) {
                        console.warn("[Nexy HMR] Partial reload failed, falling back to full reload.", err);
                        window.location.reload();
                    }
                }
            };

            ws.onclose = () => console.log("[Nexy HMR] Connection closed.");
        })();
    </script>
    """

    return f"""
    {hmr_script}
    <link rel="stylesheet" href="/__nexy__/client/main.css" />
    <script type="module" src="/__nexy__/client/main.js"></script>
    """
