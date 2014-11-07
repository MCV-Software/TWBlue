% Lista de Cambios

#¡Peligro!

Antes de continuar con la prueba del programa, considera que es una versión en desarrollo. Específicamente la versión 0.42. Esto quiere decir que no solo es posible que encuentres errores, sino que los vas a encontrar. La idea es reportar lo más que salga, para que se puedan resolver para las próximas alphas.

Aquí la lista de cambios del programa. Si quieres leer como usarlo, [mira este documento.](manual.html) Si ves un enlace con un signo de número (#) y un código que empieza por varios números, estás viendo un error que se ha reportado en el Sistema de seguimiento de incidencias. Siéntete libre de publicar tus propios errores y peticiones de mejoras y nuevas características a través de esta herramienta, disponible desde el menú ayuda en TW Blue.

## Cambios introducidos en esta nueva versión

* Se arregla un error que no permitía mostrar en buffer listas con acentos o caracteres especiales.
* Ahora TW blue no debería dejar de actualizar los tuits repentinamente.
* Ahora TW blue soporta la opción "mute" de Twitter. Cuando silencias a un usuario, no podrás ver sus tuits ni sus menciones, pero no lo dejarás de seguir, con lo que podrás seguir teniendo contacto con él a través de mensaje directo. A diferencia del bloqueo o de dejar de seguirlo, con esta opción el usuario no se dará cuenta que lo tienes silenciado. Busca esto desde el diálogo de acciónes de usuario, o desde el menú de usuario.
* Se añade una nueva página de sonido en el diálogo de configuración que permite seleccionar los dispositivos de entrada y salida, ajustar el volumen y silenciar globalmente TW Blue. Algunas otras opciones se han movido desde la página "general" hacia "sonido".
* Se ha rediseñado el fichero de configuración. La mayoría de las opciones se deberán reconfigurar de nuevo.
* Es posible desactivar Sapi5 para que no intervenga si no hay ningún lector de pantalla soportado en ejecución.
* Dentro de la pestaña General, se puede cambiar manualmente de idioma. Tw Blue reqiere reiniciarse.
* Se incluye un diálogo nuevo que ayuda a entender los sonidos de TW Blue.
* es posible desactivar el sonido y notificaciones de un buffer. El resto del cliente funcionará correctamente. Pulsa Control+win+shift+m(interfaz no visible) o selecciónalo desde el menú buffer para conmutar entre esta característica.
*Ahora puedes realizar búsquedas por usuarios y tuits. Las búsquedas de tuits quedarán guardadas en la configuración mientras que las de usuarios se eliminarán al salir. Pulsa Ctrl+Shift+guion o selecciónalo desde el menú aplicación.
* puedes abrir buffer para ver los favoritos de un usuario desde el menú "usuario".
* Con control+win+shift arriba y abajo en la interfaz no visible, y control arriba y abajo en la interfaz gráfica, puedes ir hacia el anterior o siguiente tweet en la conversación. Para que esto funcione deben estar los tweets de la conversación en la línea principal.
* Durante la grabación de un audio para adjuntar, puedes pausar y reanudar la grabación para omitir partes que puedan generar un audio muy grande.
* Es posible subir audios a Dropbox. Para ello configura el servicio en la pestaña "servicios de audio" en el diálogo de configuración.
* ahora que se pueden subir audios a Dropbox, en el diálogo de adjuntar un audio podrás seleccionar al servicio que deseas subir.
* se incluye un diálogo de corrección ortográfica para los tuits o mensajes. Por ahora los idiomas disponibles son Español, inglés, portugués, ruso y polaco. El idioma será seleccionado automáticamente de acuerdo con la configuración de TW Blue.
* Se ha introducido la  lectura automática de los tuits para un buffer. Activando esta característica se puede hacer que TW Blue lea automáticamente los tuits que lleguen a los buffers que tengan activada esta opción. Pulsando control+Win+e conmutarás esta característica.
* En el diálogo de configuración ahora puedes especificar si deseas que TW Blue inicie con la interfaz oculta.
* Las URL se muestran en su versión original. Únicamente las fotos de Twitter se siguen mostrando como acortadas, y las que hayan sido acortadas manualmente antes de enviarlas en un tuit.

## Cambios introducidos en la versión 0.40

* Se puede cambiar entre diferentes paquetes de sonidos y crear los propios. Cada paquete debe ir en un directorio por separado dentro de la carpeta sounds. Para cambiar el paquete de sonido se puede seleccionar desde el diálogo de configuración.
* Los archivos de sonido van en formato OGG.
* Ahora TW Blue debe ser capaz de cerrar correctamente.
* La hora está escrita teniendo en cuenta el formato de 12 horas.
* La hora se escribe de acuerdo con la zona horaria de Twitter establecida en tu cuenta.
* Añadidas nuevas traducciones al portugués, polaco y ruso. Gracias chicos!
* TW Blue elimina de la configuración líneas temporales de usuarios que han cambiado su nombre o borrado su cuenta.
* ahora se maneja la gran mayoría de los eventos en Twitter con el buffer de eventos.
* Ya se puede ver el texto de los eventos, con Control+shift+V (GUI) y control+win+V (interfaz no visible).
* Manejo de listas: Se puede crear, editar, borrar, ver una lista como buffer en TW Blue, añadir y borrar miembros de una lista.
* Ahora si durante el inicio TW Blue intenta cargar una línea temporal que no existe, automáticamente la elimina de la configuración y continúa la carga normalmente.
* Solo se cargará hasta los 400 amigos y seguidores para evitar problemas con la API. Se corregirá en próximas versiones.
* Para el modo no visible, Se incluyen atajos para escuchar nuevamente el tweet sobre el que se está situado (control+win+espacio) y para copiar el mensaje al portapapeles (control+win+c).

## Cambios introducidos en la versión 0.38

* Se ha corregido un fallo que impedía cerrarse al darle la orden.
* Ahora los tweets no terminan en un punto obligatoriamente. Si el programa detecta que el tweet termina en una letra o número, coloca un punto automáticamente. Si no es así, deja el texto tal y como está.
* Ya se pueden subir imágenes a los tweets y respuestas. Ten en cuenta que el tamaño de las imágenes es establecido por twitter.
* Al desplazarte hacia la izquierda y derecha usando el modo no visible, ahora solo se anuncia información de la posición en la lista de elementos.
* TW Blue ya debería funcionar para Windows XP al momento de autorizar la aplicación.
* Se ha añadido una nueva opción en el diálogo de configuración que permite revertir los buffers. Esto significa que puedes escojer si quieres ver los tweets como hasta ahora, o que los más nuevos se coloquen arriba y los viejos debajo.
* Se pueden subir fotos al perfil de Twitter, disponible desde el diálogo para actualizar tu perfil.
* Se ha añadido un buffer de eventos, donde se guardan por ahora algunos eventos que ocurren en twitter, como seguir o hacer que alguien te siga, marcar un favorito, que un tweet tuyo sea marcado como favorito, etc. Se puede activar y desactivar este buffer desde el diálogo de configuración.
* Ahora se pueden eliminar líneas temporales ya creadas que no contengan tweets, y no se permitirá crear líneas temporales de usuarios sin tweets.
* La interfaz de la aplicación es traducible. Ahora cualquier usuario puede hacer sus propias traducciones a diferentes idiomas.

## Cambios introducidos en la versión 0.36

* Los usuarios brasileños podrán ver algunos mensajes en portugués. (Usuários brasileiros poderão ver algumas mensagens em Português).
* Se ha arreglado un fallo que hacía que algunos sonidos se escucharan y otros no. Ahora deberían escucharse todos.
* La reconexión también ha recivido un arreglo, pues en ocasiones se efectuaba de forma incorrecta y había que volver a abrir la aplicación.
* Ahora TW Blue permite eliminar únicamente líneas temporales con el comando correspondiente. Antes se mostraba el diálogo sin importar en qué buffer se estaba.
* Se vuelve a poder ver los detalles de los usuarios con Enter estando en el buffer para amigos o seguidores.
* A partir de esta versión no hay soporte para bases de datos.
* Escucharás una notificación por voz cuando alguien marque como favorito uno de tus tweets.
* Los amigos y seguidores ya se actualizan.
* Cuando sigues a alguien, ya no arroja ningún error si no se muestran los amigos. Pasa lo mismo con los seguidores.
* Puedes limpiar un buffer pulsando Shift suprimir en la ventana visible, y Control+win+Shift+Suprimir en la ventana no visible. Esto vaciará todos los tweets en el buffer actual.

## cambios introducidos en la versión 0.35

* Existe un sitio web oficial para el programa, ve a [twblue.com.mx.](http://twblue.com.mx) Desde este espacio encontrarás el sistema de seguimiento de errores, el blog con las noticias recientes, y la última versión disponible.
* TW Blue anuncia cuando eres mencionado, y cuando te llega un mensaje directo.
* Jaws ya no habla el atajo de teclado que se presiona en el modo oculto. [#11](http://twblue.a12x.net/errores/view.php?id=11)
* En el modo no visible, los comandos Control+Win+inicio, control+Win+Fin, control+win+avance de página y control+win+retroceso de página van al principio de la lista, al final, 20 elementos hacia abajo y 20 elementos hacia arriba respectivamente. [#10,](http://twblue.a12x.net/errores/view.php?id=10) [#21,](http://twblue.a12x.net/errores/view.php?id=21) [#22](http://twblue.a12x.net/errores/view.php?id=22) 
* Ahora se pueden reproducir audios de Audioboo.
* Ahora el Stream debería poder conectarse luego de que la máquina regresa de una suspensión.
* Es posible grabar audios o subir archivos a SndUp.net. Si estás registrado en esta página, podrás poner en la configuración tu API Key para que los archivos se suban a tu nombre. Puedes subir archivos Wav, OGG y MP3. Los archivos wav se recodificarán a OGG.
* Si no estás usando ningún lector de pantalla, algunas acciones de TW blue usarán la síntesis de voz Sapi 5.
* Hay disponible una versión para arquitecturas de 64 Bits. Gracias a [@jmdaweb](https://twitter.com/jmdaweb) por tomarse el trabajo de hacer funcionar la aplicación en esta arquitectura y prepararla para su distribución.
* Cambio en los sonidos del cliente. Gracias a [@guilevi_es](https://twitter.com/guilevi_es) por la colaboración con el pack de sonidos.
* Algunos mensajes del programa se pueden traducir. En futuras versiones será internacionalizada la totalidad de su interfaz.
* Y Corrección de algunos cuantos errores más ([#5,](http://twblue.com.mx/errores/view.php?id=5) [#7,](http://twblue.com.mx/errores/view.php?id=7) [#8,](http://twblue.com.mx/errores/view.php?id=8) [#9,](http://twblue.com.mx/errores/view.php?id=9) [#12,](http://twblue.com.mx/errores/view.php?id=12))

## Cambios introducidos en la versión 0.3

* Ya se puede actualizar tu perfil desde TW Blue. [#19](http://twblue.a12x.net/issues/view.php?id=19)
* Ahora se pueden crear nuevamente las líneas temporales y no dan problemas. [#24](http://twblue.a12x.net/issues/view.php?id=24)
* Ahora los archivos de errores se guardarán en el directorio "logs".
* Cuando crees una línea temporal, se actualizará en tiempo real desde el principio en lugar de actualizar cada 2 minutos.
* Ya puedes solicitar más llamadas a la API que funcionarán para obtener 200 tweets cada una. Una llamada equivale a 200 elementos de la lista principal, menciones, mensajes directos, favoritos y líneas temporales. En el archivo de configuración se puede editar la opción en [twitter]/max_api_calls. Es recomendable no pedirle a Twitter más de 2 llamadas a la API, o de lo contrario llegará al límite de llamadas permitidas muy pronto y la aplicación fallará.
* Cuando respondes a un Tweet, este se envía como respuesta al mismo y no como si fuera un tweet nuevo.
* El antiguo sistema de reporte de errores tuvo que ser cambiado. A partir de esta versión, podrás reportar los errores directamente desde la aplicación. La opción Reportar un Error abrirá un diálogo que te preguntará detalles sobre tu error y enviará el reporte automáticamente.
* Ya se borran los amigos cuando dejas de seguir a un usuario.
* También los favoritos, al momento de quitar un tweet como favorito, realizan el cambio.
* Se añade un diálogo de configuración que permite controlar el número de llamadas a la API a realizar, si usar o no bases de datos, y ocultar y mostrar las listas de amigos, seguidores y favoritos.
* Al citar tweets, las comillas que cierran el mensaje ahora están separadas por un espacio de la última letra. Esto es así porque antes, cuando había una URL, causaba que las comillas hicieran parte de la dirección enviando a sitios inexistentes.
* Mejoras con algunas líneas temporales. Ahora puede guardar sin problemas cualquier línea temporal. No debería dar errores.
* Ahora los audios se reproducirán únicamente con Control+Intro, mientras que las URL se abrirán con Intro.
* El stream se intentará reconectar al fallar la conexión a internet.
* Ahora desde los seguidores y amigos se puede mencionar a un usuario.
* Ahora se proporciona un modo "invisible". Bajo el menú aplicación, la opción "Esconder ventana" o pulsando Control+M. Para mostrar la ventana de nuevo se pulsa Control+Win+M.

## Cambios introducidos en la versión 0.025

Ten en cuenta que cuando un usuario te deja de seguir o tú dejas de seguir a alguien más, no se actualizará en la lista de amigos o seguidores por ahora. Al reiniciar el programa sí aparecerá la información correcta.

* Corregido un error que impedía cerrar la aplicación hasta que el programa anunciara que estaba listo. [#17](http://twblue.a12x.net/issues/view.php?id=17) y [#18](http://twblue.a12x.net/issues/view.php?id=18)
* Cambiado el modo de organizar las líneas temporales en la configuración. Es necesario volver a crearlas.
* Ahora puede enviarse un mensaje directo a los amigos y seguidores usando el botón. Esto no funcionaba en las versiones 0.02 y 0.021.
* Se puede subir y bajar el volumen desde la lista de seguidores y amigos.
* En el diálogo para escribir un tweet, se puede ahora traducir el mensaje usando Google Traductor. Aparecerá un diálogo para preguntar por los idiomas de origen y destino.
* El menú archivo tiene la opción salir.
* A partir de esta versión solo se reproducirán archivos de audio pulsando enter si estos llevan la etiqueta #audio.
* Puedes intentar reproducir una URL cualquiera sin que lleve la etiqueta #audio pulsando Control Enter. Este comando intentará reproducir la primer URL encontrada.
* Se ha mejorado el buscador de URLS, haciendo más rápida la función y ahora debería ser capaz de detectar todas las URLS. [#21](http://twblue.a12x.net/issues/view.php?id=21)
* Ahora el diálogo que se muestra para seleccionar el usuario del que se desea ver detalles permite además de seleccionarlo de una lista, escribir el nombre de usuario que desees.

## Cambios introducidos en versión 0.02 y 0.021

* El mensaje que se reproducía al seguir un usuario ahora dice "ahora sigues a x usuario" en lugar de "ahora no sigues a x usuario". [#5](http://twblue.a12x.net/issues/view.php?id=5)
* Al salir un diálogo te preguntará si deseas hacerlo. Ahora se sale de una forma mucho más limpia del programa, evitando varios errores durante el cierre.
* Cambio de los sonidos para los dm entrante y saliente. Gracias a [@marcedsosa](https://twitter.com/marcedsosa) por los nuevos sonidos.
* El nombre de usuario de twitter se lee en el título de la ventana.
* Los sonidos del programa también leen el volumen desde la configuración. El módulo de sonido debería tomar menos tiempo en reproducir varios de los sonidos de la aplicación.
* Las acciones de subir y bajar volumen reproducen un sonido que indica que tan fuerte suena.
* Ya no se muestran las menciones de personas que no te siguen en tu línea principal. [#1](http://twblue.a12x.net/issues/view.php?id=1)
 * Ahora puedes eliminar tweets y mensajes directos. Solo podrás eliminar los tweets que tú hayas escrito.
* Arreglado un error que impedía cargar correctamente las diferentes listas si en alguna de ellas no había ningún tweet, usuario o mensaje directo. Esto afectaba especialmente a cuentas con 0 favoritos, 0 tweets, 0 enviados o 0 mensajes directos. [#2](http://twblue.a12x.net/issues/view.php?id=2)
* Ahora cada que se publique una nueva versión, se te notificará de ello. Si accedes a descargarla, el programa la descargará y copiará todo lo necesario.
* Ya se puede obtener la lista completa de amigos y seguidores.
* Se añade la fecha del último tweet de los seguidores y amigos.
* Se actualizan ahora los amigos y seguidores a tiempo real. (ToDo: Los amigos y seguidores no muestran la fecha de su último tweet cuando se actualizan a tiempo real. Lo hacen al recargarse una vez reiniciada la aplicación).
* El orden de las pestañas se ha cambiado. Ahora se ordenan comenzando por el principal, menciones, mensajes directos y enviados.
* Ahora se muestran los mensajes directos en la lista de tweets enviados cuando se carga el stream por primera vez. Esto no pasaba y si el usuario enviaba un DM desde otro cliente cuando Tw Blue no estaba abierto, al abrir la aplicación no mostraba dicho DM. [#8](http://twblue.a12x.net/issues/view.php?id=8)
* Con Control+A, se puede seleccionar todo el texto de un mensaje. Funciona con Jaws y NVDA.
* Hay atajos de teclado (detallados en la [Documentación)](leeme.html) para muchas de las acciones que puede hacer el programa.
* Ahora TW Blue detecta más audios en URLS que vienen en retweets, y audios compartidos desde Dropbox. [#3](http://twblue.a12x.net/issues/view.php?id=3)
* Se incluye documentación para la aplicación y créditos.
* Si la conexión a internet deja de funcionar, el stream intentará reconectarse por 30 minutos.
* Se ha escrito un documento que detalla como usar el programa.
* Se ha abierto el [Sistema de seguimiento de incidencias](http://twblue.a12x.net/issues/) donde los usuarios podrán reportar los errores y si lo desean, aportar nuevas ideas para el desarrollo de la aplicación. Hay disponible un acceso directo al formulario de reporte desde el menú ayuda.
* Ahora hay créditos de la versión actual.
* Se añade en el menú usuario la opción para ver los detalles. También funciona si se presiona intro sobre un amigo o seguidor.

## Cambios introducidos en la versión Prealpha1

Ten en cuenta que en esta versión los amigos y seguidores no se actualizan automáticamente. Esto será añadido en  otra versión. Tampoco se puede borrar ningún tweet, o DM. Todos los tweets, mensajes directos, menciones, favoritos, seguidores y amigos se actualizarán descargando un máximo de 200. Pronto se podrán añadir más a la cantidad de actualizaciones. Aquí los cambios desde la primer versión.

* La fecha se ve bien, de acuerdo con la zona horaria del usuario.
* Ahora el cursor se pone al principio cuando se va a responder o hacer un retweet.
* Si se pulsa Control+E en los cuadros de texto, se seleccionará todo el mensaje.
* Algunas correcciones para el manejo de las líneas temporales (necesito hacer mejoras en la manera de administrar esto).
* Los favoritos se actualizan en tiempo real.
* Escucharás un sonido cuando pasas por un tweet que podría contener un audio reproducible.
* Se soporta reproducción de audio con la etiqueta #audio y una URL. Pulsa enter para escuchar la canción. Pulsa F5 para bajar el volumen un 5%, o f6 para subirlo un 5%. Si quieres detener la reproducción, ve hacia donde haya un audio, y pulsa intro. Si el programa es incapaz de reproducir algo, te avisará. El volumen de la música (no de los sonidos del programa por ahora) quedará guardado en la configuración, y el programa lo recordará la próxima vez que reproduzcas algo.
* Puedes ver los primeros 200 amigos y seguidores con sus nombres de usuario, nombre real y algo de información útil. En futuras versiones podrás ver todos si tienes más de 200. Ten en cuenta que hay acciones que no podrás hacer con estos usuarios en la lista (por ejemplo, responder o retwittear, porque no son tweets, son usuarios), pero sí podrás seguirlos, dejarlos de seguir, y hacer casi todo (menos enviar DM por ahora) lo que podrías hacer desde el menú de usuario.

Ahora hay que usar y probar, y cuando encuentres un error, por favor mira en la carpeta de la aplicación, pues se ha de generar un archivo con el nombre del ejecutable pero con un .log al final. Bien, ese es vital para que yo pueda saber dónde se ha roto el programa, y te agradecería me lo enviaras junto con una descripción de qué era más o menos lo que estabas haciendo, cuando la aplicación no hizo lo que tenía que hacer. Por ejemplo, "intenté enviarme un DM, pero el cuadro de diálogo de mensaje directo nunca se abrió". Si puedes subirlo a un servidor de almacenamiento (como [Dropbox,](https://www.dropbox.com) por ejemplo), y enviármelo ya sea mencionando a [@tw_blue2](https://twitter.com/tw_blue2) o a [@manuelcortez00,](https://twitter.com/manuelcortez00) sería genial.

¡Infinitas gracias por probar!

## Novedades de la versión prealpha 0

* Hacer tweets, responder a los tweets de los demás, mencionando a todos los usuarios cuando haya más de uno en el tweet,  retwittear lo que te agrada, añadiendo o no un comentario al retweet y eliminarlos.
* Añadir y quitar de favoritos un tweet.
* Acortar y desacortar direcciones URL cuando escribes un tweet o dm (puedes seleccionar cual deseas acortar o desacortar desde una lista cuando sean más de una).
* Abrir un navegador web con la dirección URL que viene en el tweet, pulsando enter. Cuando haya más de una dirección, verás una lista donde te preguntará por la que desees.
* Usuarios: puedes seguir, dejar de seguir, reportar como spam, bloquear y enviar un mensaje directo a los usuarios.
* Puedes abrir y eliminar líneas temporales individuales para cada usuario.
* También verás tus favoritos.
* y por ahora, a menos que se me esté pasando algo, es todo.

---
Copyright © 2013-2014, Manuel Cortéz