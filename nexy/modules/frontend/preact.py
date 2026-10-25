from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME
from nexy.modules.frontend.takeover import TAKEOVER_RUNTIME


def preact() -> FrontendFramework:
    return FrontendFramework(
        name="preact",
        render=(
            ISLANDS_RUNTIME + TAKEOVER_RUNTIME + "(function(){"
            "const w=window as any;"
            "const gi=w.__nexy_import||((p: any)=>import(/* @vite-ignore */ p));"
            "async function m(el: any){"
            'if(!el||el.dataset.nexyMounted==="1")return;'
            'el.dataset.nexyMounted="1";'
            'const key=el.getAttribute("data-nexy-key")||"";'
            'const path=el.dataset.nexyPath||"";'
            'const symbol=el.getAttribute("data-nexy-symbol")||"";'
            'const propsStr=el.dataset.nexyProps||"{}";'
            "let props={};"
            "try{props=JSON.parse(propsStr)}catch(e){}"
            "const ref= key || path;"
            "const mod=await gi(ref);"
            "const Comp=(mod&&mod.default)!==undefined?mod.default:(symbol&&mod&&mod[symbol]);"
            'const preact=await import("preact");'
            'const lk=(el.getAttribute("data-nexy-layouts")||"").split(",").filter(Boolean);'
            "const ls=await Promise.all(lk.map(async(k: string)=>{const lm=await gi(k);"
            "return (lm&&lm.default)||lm;}));"
            "let tree=preact.h(Comp,props);"
            "for(let i=ls.length-1;i>=0;i--){tree=preact.h(ls[i],{params:props},tree);}"
            "preact.render(tree,el);"
            "}"
            # Client-routed projects: the root layout.tsx owns <html>. Preact cannot hydrate a whole
            # document, so it renders the page and the browser swaps its <body> in.
            "async function mountDocument(boot: any){"
            "try{"
            'const preact=await import("preact");'
            "const pick=(mod: any)=>(mod&&mod.default)||mod;"
            "const Page=pick(await gi(boot.page));"
            "const ls=await Promise.all("
            "(boot.layouts||[]).map(async(k: string)=>pick(await gi(k))));"
            "const props=boot.props||{};"
            "let t=preact.h(Page,props);"
            "for(let i=ls.length-1;i>=0;i--){t=preact.h(ls[i],{params:props},t);}"
            "w.document.__nexyPreact=nexyTakeOver("
            "(body: any)=>{preact.render(t,body);return body;});"
            '}catch(e){console.error("[Nexy] Failed to mount the document:",e);}'
            "}"
            "w.__nexy_render=async(Comp: any,container: any,props: any,layouts: any)=>{"
            'const preact=await import("preact");'
            "if(w.document.__nexyPreact){"
            "let t=preact.h(Comp,props||{});"
            "const chain=layouts||[];"
            "for(let i=chain.length-1;i>=0;i--){t=preact.h(chain[i],{params:props||{}},t);}"
            "preact.render(t,w.document.__nexyPreact);"
            "return;}"
            'const host=container.querySelector(":scope > [data-nexy-fw=\\"preact\\"]")||container;'
            "let tree=preact.h(Comp,props||{});"
            "const chain=layouts||[];"
            "for(let i=chain.length-1;i>=0;i--){tree=preact.h(chain[i],{params:props||{}},tree);}"
            "preact.render(tree,host);"
            "};"
            "w.__nexy_renderers=w.__nexy_renderers||{};"
            "w.__nexy_renderers.preact=w.__nexy_render;"
            "function init(){"
            'const boot=w.document.getElementById("__nexy_page");'
            "if(boot){"
            'try{mountDocument(JSON.parse(boot.textContent||"{}"));}'
            'catch(e){console.error("[Nexy] Invalid page description:",e);}'
            "return;}"
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"preact\\"]");'
            "nodes.forEach((el: any)=>{"
            'if(el.hasAttribute("data-nexy-island")){'
            'const directive=el.getAttribute("data-nexy-directive");'
            'if(directive==="client:only")return;'
            "el.__nexyHydrate=()=>m(el);"
            "}else{m(el);}"
            "});"
            "nexyIslands.init(w.document);"
            "}"
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            "}else{init()}"
            "})();"
        ),
        extension=["jsx", "tsx"],
    )
