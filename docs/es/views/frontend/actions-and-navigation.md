# Acciones y Navegación

La interacción en Nexy se maneja a través de un sistema unificado de **Acciones** y **Navegación**, lo que garantiza que el frontend y el backend permanezcan sincronizados sin código de pegamento API manual.

## El contrato de acción

Una **Acción** es una función del lado del servidor que maneja una mutación (por ejemplo, actualizar una base de datos). 

1.  **Entrada escrita**: las acciones se definen en Python con sugerencias de tipo. Nexy genera un cliente TypeScript coincidente, por lo que obtienes autocompletado y validación en tu IDE.
2.  **Ejecución atómica**: una acción es una única solicitud `POST`.
3.  **Manejo de resultados**: las acciones devuelven un resultado escrito que el cliente puede usar para actualizar la interfaz de usuario.

## Navegación del lado del cliente

La navegación en Nexy es "inteligente". En lugar de recargar completamente el navegador, Nexy intercambia el contenido de la página actual mientras mantiene montados los diseños activos.

- **El componente `Link`**: utilice el componente `Link` específico del marco para realizar transiciones del lado del cliente.
- **Navegación programática**: use la función `navigate()` de `@nexy/client` para cambiar páginas en respuesta a la lógica (por ejemplo, después de un inicio de sesión exitoso).

## Coordinación: Acción → Navegación

El patrón más común es realizar una acción y luego llevar al usuario a una nueva página.

**El flujo de revalidación:**
1.  El cliente llama a una Acción.
2.  La acción se ejecuta en el servidor y llama a `revalidate("/path")`.
3.  El servidor devuelve el resultado junto con una señal para actualizar la ruta especificada.
4.  El cliente actualiza el contenido de la página para reflejar el nuevo estado.

## Implementación del marco

La API para invocar acciones y navegar varía según el marco. Consulte la guía **Diferencias** para la tecnología elegida:

- [React Diferencias](../react/differences.md)
- [Vue Diferencias](../vue/differences.md)
- [Svelte Diferencias](../svelte/differences.md)
- [Solid Diferencias](../solid/differences.md)
- [Preact Diferencias](../preact/differences.md)
