# Pendientes para igualar la UI de Bluesky con Mastodon

Objetivo: la experiencia debe ser id?ntica a Mastodon siempre que el protocolo lo permita; si no existe algo en blueski que si en mastodon, debe no diseñarse. Por ejemplo comunities no tiene mucho sentido.

## 1) Di?logo "Ver timeline..." (Alt+Win+I)
- Autocompletado de usuarios como en Mastodon (bot?n "Autocomplete users").
- Selecci?n y listado de m?ltiples usuarios (no solo autor/mentions con facetas).
- Resoluci?n de handles/DIDs en segundo plano con feedback accesible.
Hecho.

## 2) Listas de Reposts/Likes (desde "Ver post")
- En Mastodon se abren listas tipo buffer; en Bluesky ahora es di?logo con paginaci?n.
- Igualar creando buffers dedicados (UserBuffer/FollowersBuffer) bajo nodo "Timelines" o "Searches".
- Mantener paginaci?n y persistencia coherentes con Mastodon (cursor + get_more_items).
Hecho.

## 3) Restauraci?n de buffers "Followers/Following" propios
- En ejecuci?n ya reutiliza los buffers principales del usuario.
- Al restaurar tras reinicio, debe saltar a los buffers propios (si ya existen) y no duplicar.
Hecho.

## 4) Estructura del ?rbol (Treebook)
- Mastodon crea nodos vac?os: "Timelines", "Searches", "Communities".
- En Bluesky solo existe "Timelines".
- Crear nodos equivalentes siempre y cuando aplique por protocolo.
Hecho.

## 5) Men?s/acciones de ?tem
- Mastodon incluye OCR, filtros, listas, community timelines, etc.
- Bluesky carece de varias acciones.
- Decidir por acci?n: implementar, deshabilitar o mostrar mensaje "No soportado" para igualar UI.
Hecho.

## 6) Perfil de usuario
- Mastodon muestra campos y acciones adicionales.
- Bluesky tiene datos mínimos.
- Igualar en la medida de lo posible. Si blueski no da x datos, no se crea nada.
Hecho. Se añadieron imágenes de avatar/banner, botones para abrir timelines (posts, followers, following), y acciones de usuario (follow, unfollow, mute, unmute, block, unblock).

## 7) Diálogo de acciones de usuario
- Mastodon: autocompletado y búsqueda avanzada.
- Bluesky: diálogo sin autocompletado.
- Igualar con autocompletado y/o búsqueda en segundo plano.
Hecho. Se añadió botón de autocompletado de usuarios al diálogo de acciones.

## 8) Consistencia de nombres y etiquetas
- Algunos textos difieren ("Reposts" vs "Boosts", "Likes" vs "Favorites").
- Definir equivalencias y usar mismas etiquetas donde aplique.
Hecho. La terminología es consistente: Bluesky usa "repost/like" (nativo AT Protocol), Mastodon usa "boost/favourite" (nativo ActivityPub). Esto es correcto.

## 9) Paginación en listados
- Bluesky: implementada en Reposts/Likes y Followers/Following.
- Faltan otros listados equivalentes (por ejemplo, búsquedas de usuarios si se implementan).
Hecho. Paginación implementada en todos los buffers: HomeTimeline, FollowingTimeline, NotificationBuffer, LikesBuffer, MentionsBuffer, SentBuffer, UserTimeline, SearchBuffer, FollowersBuffer, FollowingBuffer, PostUserListBuffer.

## 10) Accesibilidad/teclado
- Verificar atajos en todos los nuevos diálogos/buffers.
- Asegurar foco inicial y navegación idéntica a Mastodon.
Hecho. Se añadieron atajos de teclado (&) a los botones del diálogo de perfil.

## 11) Persistencia
- Confirmar que todos los buffers creados por el usuario (timelines, followers, following, búsquedas) se guardan/restauran.
Hecho. Se añadió persistencia de búsquedas. Ya existía para timelines, followers y following.
