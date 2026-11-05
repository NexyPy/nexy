# Barra de herramientas de desarrollo

`nexy dev` agrega una barra de herramientas a cada página HTML. Se encuentra en la esquina inferior izquierda, muestra la ruta en la que se encuentra y cuánto tiempo tardó el servidor, y se abre en un panel. Nunca es parte de una respuesta de producción.

| Pestaña | Muestra |
|---|---|
| Página | URL, ruta, controlador, el archivo del que proviene (con un enlace que lo abre en su editor), estado, hora del servidor, primer byte, primera pintura, contenido principal, cambio de diseño (calificado en verde, ámbar o rojo), DOM listo |
| Rutas | cada ruta de la app con sus métodos, un filtro y la actual marcada; cada uno enlaza a su archivo |
| Errores | errores del servidor desde que `nexy dev` se inició y los errores que generó el navegador |
| Configuración | tema (coincidir con la página, oscuro o claro), posición, tamaño, ocultar, restablecer |

## Muévelo

Arrastra el botón: sigue el puntero y se ajusta a la esquina más cercana cuando lo sueltas. El panel se abre hacia el centro de la pantalla desde donde esté el botón. La posición se mantiene en este navegador. También puedes elegir una esquina en **Configuración**.

`Shift` + `Alt` + `D` oculta y muestra la barra de herramientas. `Esc` cierra el panel.

## Errores

Un error no detectado en el navegador abre un cuadro de diálogo sobre la página con el mensaje y la pila; con varios errores, revíselos (1 de 3). Un error del servidor responde con una página del mismo tipo: el error, dónde se generó y el código que lo rodea.

## Apágalo

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

La barra de herramientas es un bloque de estilo y un script agregado antes de `</body>`: sin solicitud externa, sin dependencia. JSON, archivos y todas las respuestas que no sean HTML se dejan en paz.

## Próximos pasos

- [Configuración](../reference/config.md): todas las opciones
- [Probando](testing.md): prueba una página o un componente
