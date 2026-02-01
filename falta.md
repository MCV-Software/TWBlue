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
- Bluesky tiene datos m?nimos.
- Igualar en la medida de lo posible. Si blueski no da x datos, no se crea nada.

## 7) Di?logo de acciones de usuario
- Mastodon: autocompletado y b?squeda avanzada.
- Bluesky: di?logo sin autocompletado.
- Igualar con autocompletado y/o b?squeda en segundo plano.

## 8) Consistencia de nombres y etiquetas
- Algunos textos difieren ("Reposts" vs "Boosts", "Likes" vs "Favorites").
- Definir equivalencias y usar mismas etiquetas donde aplique.

## 9) Paginaci?n en listados
- Bluesky: implementada en Reposts/Likes y Followers/Following.
- Faltan otros listados equivalentes (por ejemplo, b?squedas de usuarios si se implementan).

## 10) Accesibilidad/teclado
- Verificar atajos en todos los nuevos di?logos/buffers.
- Asegurar foco inicial y navegaci?n id?ntica a Mastodon.

## 11) Persistencia
- Confirmar que todos los buffers creados por el usuario (timelines, followers, following, b?squedas) se guardan/restauran.
