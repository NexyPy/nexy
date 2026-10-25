from nexy.core.models import FrontendFramework
from nexy.modules.frontend.islands import ISLANDS_RUNTIME


def preact() -> FrontendFramework:
    return FrontendFramework(
        name="preact",
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
            "w.__nexy_render=async(Comp: any,container: any,props: any,layouts: any)=>{"
            'const preact=await import("preact");'
            'const host=container.querySelector(":scope > [data-nexy-fw=\\"preact\\"]")||container;'
            "let tree=preact.h(Comp,props||{});"
            "const chain=layouts||[];"
            "for(let i=chain.length-1;i>=0;i--){tree=preact.h(chain[i],{params:props||{}},tree);}"
            "preact.render(tree,host);"
            "};"
            "function init(){"
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
