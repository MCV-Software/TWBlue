# Integración de Bluesky en TWBlue

Este documento describe la implementación completa de soporte para Bluesky (AT Protocol) en TWBlue.

## Resumen

Se ha añadido soporte completo para la red social Bluesky, siguiendo la arquitectura MVC existente de TWBlue y manteniendo paridad de características con la implementación de Mastodon.

## Dependencias

- **atproto**: SDK oficial de Python para AT Protocol (Bluesky)
- Las dependencias existentes de TWBlue (wxPython, arrow, configobj, etc.)

## Estructura de Archivos

### Sesión (`src/sessions/blueski/`)

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Inicialización del módulo |
| `session.py` | Clase principal de sesión Bluesky con autenticación, API y gestión de cuenta |
| `compose.py` | Funciones de composición para formatear datos de API en cadenas legibles |
| `streaming.py` | Sistema de polling para actualizaciones en tiempo real |
| `utils.py` | Utilidades auxiliares (detección de medios, etc.) |

### Controladores de Buffers (`src/controller/buffers/blueski/`)

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Registro de tipos de buffer |
| `base.py` | Buffer base con funcionalidad común (acciones, menús, eventos) |
| `timeline.py` | Buffers de línea de tiempo (Home, Following, Notifications, etc.) |
| `user.py` | Buffers de usuarios (Followers, Following, Blocks) |
| `chat.py` | Buffers de mensajes directos |

### Controladores (`src/controller/blueski/`)

| Archivo | Descripción |
|---------|-------------|
| `__init__.py` | Inicialización del módulo |
| `handler.py` | Handler principal que crea buffers y gestiona acciones |
| `messages.py` | Visor de posts con detalles completos |
| `userActions.py` | Diálogo de acciones de usuario (seguir, silenciar, bloquear) |
| `userList.py` | Gestión de listas de usuarios |
| `settings.py` | Configuración de cuenta |
| `templateEditor.py` | Editor de plantillas |

### Interfaz de Usuario (`src/wxUI/`)

#### Paneles (`src/wxUI/buffers/blueski/panels.py`)

- `HomePanel`: Panel de línea de tiempo con botones Post, Repost, Reply, Like, Chat
- `NotificationPanel`: Panel de notificaciones (hereda de HomePanel)
- `UserPanel`: Panel de lista de usuarios con botones Post, Actions, Message
- `ChatPanel`: Panel de lista de conversaciones
- `ChatMessagePanel`: Panel de mensajes de chat individuales

#### Diálogos (`src/wxUI/dialogs/blueski/`)

| Archivo | Descripción |
|---------|-------------|
| `postDialogs.py` | Diálogo de composición de posts y visor de posts |
| `configuration.py` | Diálogo de configuración de cuenta |
| `menus.py` | Menús contextuales |
| `userActions.py` | Diálogo de acciones de usuario |
| `showUserProfile.py` | Diálogo de perfil de usuario |

### Configuración (`src/blueski.defaults`)

Archivo de configuración por defecto con secciones:
- `[blueski]`: Credenciales (handle, app_password, did, session_string)
- `[general]`: Tiempos relativos, posts por llamada, orden de timelines
- `[sound]`: Configuración de audio
- `[other_buffers]`: Timelines adicionales, búsquedas guardadas
- `[mysc]`: Idioma de corrector ortográfico
- `[reporting]`: Reportes de braille/voz
- `[templates]`: Plantillas de visualización

## Características Implementadas

### Autenticación
- Login con handle y App Password de Bluesky
- Persistencia de sesión mediante session_string
- Migración automática de configuración legacy

### Buffers Disponibles

1. **Home (Following)**: Timeline cronológico inverso de cuentas seguidas
2. **Discover**: Feed algorítmico de descubrimiento
3. **Mentions**: Menciones, respuestas y citas
4. **Notifications**: Todas las notificaciones (likes, reposts, follows, etc.)
5. **Sent**: Posts enviados por el usuario
6. **Likes**: Posts marcados como favoritos
7. **Followers**: Lista de seguidores
8. **Following**: Lista de seguidos
9. **Blocked Users**: Usuarios bloqueados
10. **Chats**: Mensajes directos
11. **Timelines de Usuario**: Timelines personalizados por usuario
12. **Búsquedas**: Búsquedas guardadas

### Acciones de Posts
- Publicar nuevo post (con imágenes, CW, idioma)
- Responder a posts
- Repostear
- Dar like
- Eliminar posts propios
- Ver conversación/hilo completo
- Copiar enlace al portapapeles
- Ver detalles del post (likes, reposts, descripción de imágenes)

### Acciones de Usuario
- Seguir/Dejar de seguir
- Silenciar/Desilenciar
- Bloquear/Desbloquear
- Ver perfil
- Ver timeline de usuario
- Ver seguidores/seguidos de usuario
- Enviar mensaje directo

### Mensajes Directos
- Lista de conversaciones
- Ver mensajes de una conversación
- Enviar mensajes

### Sistema de Actualización
- Polling periódico para notificaciones (configurable, mínimo 30 segundos)
- Publicación de eventos via pub/sub para consistencia con Mastodon

### Accesibilidad
- Lectura automática de nuevos elementos
- Indicadores de sonido para audio/video e imágenes
- Tiempos relativos actualizados al enfocar
- Soporte completo de lector de pantalla

## Formato de Visualización

El formato de posts y notificaciones se ha igualado al de Mastodon:

### Posts
```
Usuario (@handle), Texto del post, Fecha, Bluesky
```

Para reposts:
```
Reposteador (@handle), Reposted from @original: Texto, Fecha, Bluesky
```

### Notificaciones
```
Usuario (@handle), {usuario} ha añadido a favoritos: {texto}, Fecha
```

### Usuarios
```
Nombre (@handle). X seguidores, Y siguiendo, Z posts. Se unió fecha
```

## Sonidos

| Acción | Sonido |
|--------|--------|
| Nuevo post en timeline | `tweet_received.ogg` |
| Nueva notificación | `notification_received.ogg` |
| Nueva mención | `mention_received.ogg` |
| Nuevo DM | `dm_received.ogg` |
| Post enviado | `tweet_send.ogg` |
| Respuesta enviada | `reply_send.ogg` |
| Repost | `retweet_send.ogg` |
| Like | `favourite.ogg` |
| DM enviado | `dm_sent.ogg` |
| Actualización de seguidores | `update_followers.ogg` |
| Búsqueda/Conversación | `search_updated.ogg` |

## Notas Técnicas

### Diferencias con Mastodon
- Bluesky usa AT Protocol en lugar de ActivityPub
- Autenticación mediante App Password en lugar de OAuth2
- No hay "Firehose" streaming real; se usa polling
- URIs en formato `at://did:plc:xxx/app.bsky.feed.post/rkey`
- Facets para menciones y enlaces en lugar de HTML

### Manejo de Errores
- Logging consistente con `log.error()` para errores esperados
- Mensajes de error traducibles para el usuario

### Configuración
- Valores por defecto en `blueski.defaults`
- Acceso a configuración via `self.session.settings`
- Helper `get_max_items()` para obtener límite de posts

## Pruebas

Tests ubicados en `src/test/sessions/blueski/`:
- `test_blueski_session.py`: Tests de la sesión de Bluesky

## Traducciones

Todos los strings de interfaz usan la función `_()` para internacionalización:
- Títulos de buffers
- Acciones de menú
- Mensajes de confirmación
- Mensajes de error
- Formatos de notificación

## Archivos Modificados (Fuera de blueski/)

Para integrar Bluesky en TWBlue, también se modificaron:

- `src/controller/mainController.py`: Registro de handlers de sesión
- `src/sessionmanager/`: Soporte para tipo de sesión "blueski"
- `src/requirements.txt`: Dependencia atproto

## Uso

1. En TWBlue, ir a Sesión > Nueva cuenta
2. Seleccionar "Bluesky"
3. Introducir handle (ej: `usuario.bsky.social`)
4. Introducir App Password (desde Configuración > App Passwords en bsky.app)
5. Los buffers se crearán automáticamente

## Correcciones Recientes

### Orden de Conversaciones
- Las conversaciones ahora se muestran en orden cronológico correcto (más antiguo arriba, más reciente abajo)
- Se añadió método `_add_items_chronological()` en `timeline.py` para manejar el orden específico de conversaciones

### Detección de Imágenes y Sonido Indicador
- Corregido el evento de foco en paneles: cambiado de `wx.EVT_SET_FOCUS` a `wx.EVT_LIST_ITEM_FOCUSED`
- `EVT_SET_FOCUS` solo se disparaba al entrar al control, no al moverse entre elementos
- `EVT_LIST_ITEM_FOCUSED` se dispara correctamente al navegar entre posts con las flechas
- Simplificada función `is_image()` para detectar imágenes sin requerir URLs válidas

### Funcionalidad OCR
- Implementada función `ocr_image()` en `base.py` para extraer texto de imágenes
- Usa `extra.ocr.OCRSpace.OCRSpaceAPI()` para el reconocimiento
- Soporta selección de imagen cuando hay múltiples imágenes en un post
- Creada clase `text` en `controller/blueski/messages.py` como visor de resultados OCR
- Creado diálogo `viewText` en `wxUI/dialogs/blueski/postDialogs.py`
- **Independiente de Mastodon**: no hay dependencias entre módulos blueski y mastodon

### Reproducción Multimedia
- Implementada función `audio()` en `base.py` para reproducir vídeos y audio
- Usa `sound.URLPlayer` para la reproducción
- Soporta selección de URL cuando hay múltiples medios
- Función `get_media_urls()` en utils.py extrae URLs de vídeos, streams HLS y enlaces externos (YouTube, Vimeo, etc.)

### Utilidades (`sessions/blueski/utils.py`)
- `is_image(post)`: Detecta si un post tiene imágenes (simplificado, no requiere URLs válidas)
- `is_audio_or_video(post)`: Detecta contenido de audio/vídeo
- `get_image_urls(post)`: Extrae URLs de imágenes para OCR
- `get_media_urls(post)`: Extrae URLs de medios para reproducción
- `find_urls(post)`: Encuentra URLs en el contenido del post
- `_extract_images_from_embed(embed)`: Helper compartido para extracción de imágenes

## Limitaciones Conocidas

- No hay streaming en tiempo real (se usa polling)
- Las listas de Bluesky no están implementadas aún
- Los starter packs no están soportados
- La moderación de contenido es básica (solo CW)
