# Contexto de trabajo

## Objetivo final
Igualar la experiencia de Bluesky con Mastodon en la interfaz (men?s, di?logos, buffers y accesos), manteniendo las diferencias s?lo cuando el protocolo lo exige. Mastodon es la referencia.

## Estado actual
Se est? siguiendo `falta.md` por orden. Los puntos 1 a 5 ya est?n marcados como "Hecho".

## Cambios recientes
- Activado autocompletado en el di?logo "Ver timeline..." y validaci?n de usuario.
- Reposts/Likes ahora abren buffers con paginaci?n bajo "Timelines".
- Restauraci?n de followers/following propios sin duplicar.
- Estructura del ?rbol: se a?adi? "Searches" en Bluesky.
- Men?s: para Bluesky, las opciones no aplicables se ocultan (etiqueta vac?a) usando el sentinel "HIDE" en `handler.menus`.

## Puntos pendientes (seg?n falta.md)
- 6) Perfil de usuario (igualar estructura si el protocolo permite).
- 7) Di?logo de acciones de usuario (autocompletado/b?squeda avanzada).
- 8) Consistencia de nombres/etiquetas.
- 9) Paginaci?n en listados restantes.
- 10) Accesibilidad/teclado.
- 11) Persistencia total (b?squedas y otros buffers).

## Notas t?cnicas
- `update_menus` en `src/controller/mainController.py` interpreta `"HIDE"` para ocultar entradas (label vac?o + disabled).
- Buffers de Reposts/Likes usan `PostUserListBuffer` y `get_post_likes/get_post_reposts` con cursor.
- El nodo "Searches" ahora existe en Bluesky y se usa al crear b?squedas.

