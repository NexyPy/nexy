"""Browser helper shared by the runtimes that cannot hydrate a whole document.

Preact, Vue and Svelte cannot take over ``document`` the way React and Solid do. The server still
sends the complete document; the browser builds the page body itself and swaps it in for the one
that was sent.
"""

TAKEOVER_RUNTIME = """
    // Builds the page in a detached <body>, then swaps it for the live one. <html> and <head> stay
    // as the server sent them; the attributes of the old body are kept when the new one lacks them.
    function nexyTakeOver(render) {
        const fresh = document.createElement("body");
        const result = render(fresh);
        // Preact renders its own <html><body> inside the target; the others render body content.
        const own = fresh.querySelector(":scope > html > body") || fresh;
        const live = document.body;
        for (const attr of Array.from(live.attributes)) {
            if (!own.hasAttribute(attr.name)) own.setAttribute(attr.name, attr.value);
        }
        live.replaceWith(own);
        return result;
    }
"""
