# Islas e hidratación

## Definición

Una isla es un componente del cliente (React, Vue, Svelte, Solid o Preact) importado a un `.nexy`
página. El servidor representa su HTML; el navegador hace que ese componente sea interactivo. El resto del
La página permanece HTML.

Las islas existen en modo servidor. En modo cliente, los componentes *son* las páginas: consulte [CSR](csr.md).

## Cómo funciona

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```

Nexy renderiza el componente en el momento de la compilación, almacena su HTML y lo coloca dentro de la página. la pagina
La respuesta lleva ese HTML más los accesorios como un atributo JSON. En el navegador, el tiempo de ejecución de la isla.
carga el componente y se hace cargo del contenedor.

`directive` decide **cuándo** eso sucede. Sin uno, la isla se hidrata en cuanto termina su tiempo de ejecución
está listo.

## Ciclo de vida de renderizado

1. En el momento de la compilación, cada componente del cliente se representa en HTML y se escribe en `__nexy__/client/static/`.
2. Una solicitud muestra la página `.nexy`; El HTML de la isla se inserta en lugar de la etiqueta.
3. La respuesta lleva el HTML, los accesorios y la directiva como atributos.
4. En el navegador, el tiempo de ejecución programa la hidratación de acuerdo con la directiva.
5. La hidratación reemplaza el HTML estático con el componente en vivo; el resto de la página está intacta.

En desarrollo no hay una instantánea de compilación: el contenedor está vacío y el componente se representa en el
navegador. La página tiene el mismo aspecto, pero la primera pintura difiere de la producción.

## Cuándo usar

- Una página que es principalmente contenido y tiene uno o dos puntos interactivos.
- Un widget que debe existir en HTML para rastreadores y aún funcionar.
- Un componente que necesita el navegador pero que no debe arrastrar la página completa a la representación del cliente.

## Configuración

| Directiva | Hidratos |
|---|---|
| ninguno, o `client:load` | inmediatamente |
| `client:idle` | cuando el navegador está inactivo (`requestIdleCallback`, tiempo de espera de 2 s) |
| `client:visible` | cuando la isla ingresa a la ventana gráfica, 200 px antes |
| `client:media` | cuando una consulta de medios coincide; configúrelo con el accesorio `media` |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` tiene por defecto `(min-width: 768px)` cuando `media` está ausente y se hidrata una vez. en un
navegador sin `IntersectionObserver`, `client:visible` vuelve a estar inactivo.

Nexy consume `directive` y `media`: no se pasan a su componente.

## Ejemplo

```tsx filename="src/components/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

```nexy filename="src/rutas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```

## Limitaciones

- **`client:only` nunca se hidrata.** Se acepta, pero el tiempo de ejecución lo omite, por lo que el HTML del servidor permanece.
  inerte. Utilice una ruta de cliente ([CSR](csr.md)) cuando un componente no pueda renderizarse en el servidor.
- **`client:manual` no tiene ningún disparador público.** También se omite automáticamente y el identificador que
  se reanuda es interno.
- **Los accesorios deben ser JSON.** Están serializados con `json.dumps`; un valor que no se puede serializar es
  cae, y la isla recibe `{}` - silenciosamente.
- **Una isla no es un componente cliente con estado compartido.** Dos islas no comparten estado sin un
  mecanismo que usted mismo agrega.
- **El servidor no vuelve a renderizar la isla.** Su HTML es la instantánea de compilación, más cualquier
  El componente lo hace una vez hidratado.
- **Una página de islas es una página de CSR disfrazada.** Si cada bloque necesita comunicarse entre sí, elige
  modo cliente en su lugar.

## Próximos pasos

- [Rendering](README.md): los cuatro modos
- [Componentes](../views/nexy/components.md): cómo una página `.nexy` importa una
- [Reaccionar](../views/react/differences.md), [Vue](../views/vue/differences.md),
  [Esbelto](../views/svelte/differences.md), [Sólido](../views/solid/differences.md),
  [Preacto](../views/preact/differences.md)