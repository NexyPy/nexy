from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME


def solid() -> FrontendFramework:
    return FrontendFramework(
        name="solid",
        render=(
            ISLANDS_RUNTIME + "(function(){"
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
            "const ref=key||path;"
            "const [mod, sw, {createComponent}] = await Promise.all(["
            "gi(ref),"
            'import("solid-js/web"),'
            'import("solid-js")'
            "]);"
            "const Comp=(mod&&mod.default)!==undefined?mod.default:(symbol&&mod&&mod[symbol]);"
            'el.innerHTML="";'
            "sw.render(() => createComponent(Comp, props), el);"
            "}"
            "function init(){"
            'const nodes=w.document.querySelectorAll("[data-nexy-fw=\\"solid\\"]");'
            "for(let i=0; i<nodes.length; i++){"
            'if(nodes[i].hasAttribute("data-nexy-island")){'
            'const directive=nodes[i].getAttribute("data-nexy-directive");'
            'if(directive==="client:only")continue;'
            "nodes[i].__nexyHydrate=()=>m(nodes[i]);"
            "}else{m(nodes[i]);}"
            "}"
            "nexyIslands.init(w.document);"
            "}"
            'if(w.document.readyState==="loading"){'
            'w.document.addEventListener("DOMContentLoaded",init);'
            "}else{init()}"
            "})();"
        ),
        extension=["jsx", "tsx"],
    )
