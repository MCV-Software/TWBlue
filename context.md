# Contexto de trabajo

## Objetivo final
Igualar la experiencia de Bluesky con Mastodon en la interfaz (menús, diálogos, buffers y accesos), manteniendo las diferencias sólo cuando el protocolo lo exige. Mastodon es la referencia.

## Estado actual
Se está siguiendo `falta.md` por orden. Los puntos 1 a 8 y 10-11 están marcados como "Hecho". Punto 9 parcialmente completado.

## Cambios recientes (sesión actual)
- Perfil de usuario mejorado: imágenes de avatar/banner, botones de timeline (posts, followers, following).
- Acciones de usuario en perfil: follow, unfollow, mute, unmute, block, unblock.
- Autocompletado añadido al diálogo de acciones de usuario.
- Atajos de teclado (&) añadidos a botones del perfil.
- Persistencia de búsquedas implementada (se guardan y restauran al reiniciar).

## Cambios anteriores
- Activado autocompletado en el diálogo "Ver timeline..." y validación de usuario.
- Reposts/Likes ahora abren buffers con paginación bajo "Timelines".
- Restauración de followers/following propios sin duplicar.
- Estructura del árbol: se añadió "Searches" en Bluesky.
- Menús: para Bluesky, las opciones no aplicables se ocultan usando el sentinel "HIDE".

## Puntos pendientes
- 9) Paginación en timelines principales (home, notifications, user timelines, search) - parcial.

## Notas técnicas
- `update_menus` en `src/controller/mainController.py` interpreta `"HIDE"` para ocultar entradas.
- Buffers de Reposts/Likes usan `PostUserListBuffer` con cursor para paginación.
- Las búsquedas ahora se guardan en `session.settings["other_buffers"]["searches"]`.
- Perfil de usuario descarga imágenes en thread separado para no bloquear UI.

