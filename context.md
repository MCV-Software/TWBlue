# Contexto de trabajo

## Objetivo final
Igualar la experiencia de Bluesky con Mastodon en la interfaz (menús, diálogos, buffers y accesos), manteniendo las diferencias sólo cuando el protocolo lo exige. Mastodon es la referencia.

## Estado actual
Se completaron todos los puntos de falta.md. Ahora se está trabajando en igualar características de accesibilidad comparando con el código original de Mastodon en srcantiguo/.

## Cambios recientes (sesión actual)
- **Accesibilidad mejorada en Bluesky:**
  - Implementado método `onFocus()` para: actualizar tiempos relativos, leer posts largos en GUI, reproducir sonidos indicadores de audio/imagen.
  - Implementado método `auto_read()` para lectura automática de nuevos items.
  - Implementado menú contextual (`show_menu()`, `show_menu_by_key()`).
  - Añadido método `open_in_browser()` para abrir posts en navegador.
  - Añadido método `add_new_item()` para streaming.
  - Añadido método `update_item()` para actualizar items existentes.
  - Añadido método `get_buffer_name()` para nombres de buffer legibles.
  - Añadido método `copy()` para copiar al portapapeles.

- **Nuevos archivos creados:**
  - `src/sessions/blueski/utils.py` - Funciones utilitarias (is_audio_or_video, is_image, get_media_urls, find_urls).
  - `src/wxUI/dialogs/blueski/menus.py` - Menús contextuales (baseMenu, notificationMenu, userMenu, chatMenu).

- **Correcciones de sonido:**
  - Arreglado bug en base.py donde `self.sound = sound` usaba variable indefinida.
  - Añadido `self.sound` a todos los buffers (Conversation, chat, user, etc.).

## Cambios anteriores
- Perfil de usuario mejorado: imágenes de avatar/banner, botones de timeline (posts, followers, following).
- Acciones de usuario en perfil: follow, unfollow, mute, unmute, block, unblock.
- Autocompletado añadido al diálogo de acciones de usuario.
- Atajos de teclado (&) añadidos a botones del perfil.
- Persistencia de búsquedas implementada (se guardan y restauran al reiniciar).
- Paginación completa en todos los buffers: HomeTimeline, FollowingTimeline, NotificationBuffer, LikesBuffer, MentionsBuffer, SentBuffer, UserTimeline, SearchBuffer.
- Activado autocompletado en el diálogo "Ver timeline..." y validación de usuario.
- Reposts/Likes ahora abren buffers con paginación bajo "Timelines".
- Restauración de followers/following propios sin duplicar.
- Estructura del árbol: se añadió "Searches" en Bluesky.
- Menús: para Bluesky, las opciones no aplicables se ocultan usando el sentinel "HIDE".

## Puntos pendientes
- Verificar funcionamiento completo de onFocus con la aplicación en ejecución.
- Implementar soporte de templates para usuarios y notificaciones (como Mastodon).
- Considerar OCR para imágenes si es necesario.

## Notas técnicas
- `onFocus()` se conecta via `self.buffer.set_focus_function(self.onFocus)` en bind_events().
- `auto_read()` se llama desde `process_items()` automáticamente si hay nuevos items.
- Menú contextual aparece con clic derecho o tecla de menú (WXK_WINDOWS_MENU).
- `utils.is_audio_or_video()` y `utils.is_image()` detectan multimedia en posts de Bluesky.
- Los sonidos indicadores (`indicate_audio`, `indicate_img`) ya están en blueski.defaults.
- `update_menus` en `src/controller/mainController.py` interpreta `"HIDE"` para ocultar entradas.
- Buffers de Reposts/Likes usan `PostUserListBuffer` con cursor para paginación.
- Las búsquedas ahora se guardan en `session.settings["other_buffers"]["searches"]`.
- Perfil de usuario descarga imágenes en thread separado para no bloquear UI.
- Paginación usa patrón: `self.next_cursor` guardado en `start_stream()`, usado en `get_more_items()`.
- El menú "load_previous_items" activa `get_more_items()` en el buffer actual.

