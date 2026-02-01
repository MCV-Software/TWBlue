# Contexto de trabajo

## Objetivo final
Igualar la experiencia de Bluesky con Mastodon en la interfaz (menus, dialogos, buffers y accesos), manteniendo las diferencias solo cuando el protocolo lo exige. Mastodon es la referencia.

## Estado actual
Se completaron los puntos de la lista pendiente (falta.md eliminado). Ahora se esta trabajando en igualar accesibilidad y flujo de compose usando como referencia srcantiguo/.

## Cambios recientes (sesion actual)
- Compose Bluesky vuelve a ser local por buffer (sin capa intermedia) y el envio es en thread.
- Nuevo helper `controller/blueski/messages.py::post` para centralizar dialogo y payload.
- DM de chats Bluesky en thread con refresco de buffer.
- Autologin para todas las sesiones (excepto ignoradas) para iniciar buffers al abrir.
- Correccion de "Actualizar buffer" cuando la sesion no tiene `KIND`.
- Menu de nueva cuenta muestra solo "Bluesky" (sin duplicados).

## Cambios anteriores
- Accesibilidad mejorada en Bluesky: onFocus, auto_read, menu contextual, open_in_browser, add_new_item, update_item, get_buffer_name, copy.
- Nuevos archivos: `src/sessions/blueski/utils.py`, `src/wxUI/dialogs/blueski/menus.py`.
- Correcciones de sonido: self.sound en todos los buffers.
- Perfil de usuario mejorado y acciones de usuario completas.
- Autocompletado en dialogos de timeline y acciones de usuario.
- Persistencia de busquedas y paginacion completa en buffers.
- Reposts/Likes abren buffers con paginacion bajo "Timelines".
- Restauracion de followers/following propios sin duplicar.
- Estructura del arbol: "Searches" agregado.
- Menus de Bluesky ocultan opciones no aplicables via sentinel "HIDE".

## Puntos pendientes
- Verificar funcionamiento completo de onFocus con la aplicacion en ejecucion.
- Implementar soporte de templates para usuarios y notificaciones (como Mastodon).
- Confirmar que actualizacion de buffers en Mastodon se mantiene correcta.
- Considerar OCR para imagenes si es necesario.

## Notas tecnicas
- onFocus se conecta via `self.buffer.set_focus_function(self.onFocus)` en bind_events().
- auto_read se llama desde process_items() automaticamente si hay nuevos items.
- Menu contextual con clic derecho o tecla de menu (WXK_WINDOWS_MENU).
- utils.is_audio_or_video() y utils.is_image() detectan multimedia en posts de Bluesky.
- Sonidos indicadores (indicate_audio, indicate_img) en blueski.defaults.
- update_menus en `src/controller/mainController.py` interpreta "HIDE" para ocultar entradas.
- Buffers de Reposts/Likes usan PostUserListBuffer con cursor para paginacion.
- Busquedas se guardan en session.settings["other_buffers"]["searches"].
- Perfil de usuario descarga imagenes en thread separado para no bloquear UI.
- Paginacion usa patron: next_cursor guardado en start_stream(), usado en get_more_items().
- Menu "load_previous_items" activa get_more_items() en el buffer actual.
