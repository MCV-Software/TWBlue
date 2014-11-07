% Documentação do TW Blue 0.42

# Versão 0.42 (alpha)

# ¡Perigro!

Você está lendo um documento gerado para uma aplicação em fase de desenvolvimento. A intenção deste manual é esclarecer alguns detalhes sobre o funcionamento do programa. Note-se que sendo desenvolvido ativamente, o software pode mudar um pouco em relação a esta documentação num futuro próximo. Por isso é aconselhável dar uma olhada de vez em quando para não se perder muito.

Si quieres ver lo que ha cambiado con respecto a la versión anterior, [lee la lista de novedades aquí.](changes.html)

# TW Blue

TW Blue é um aplicativo para utilizar o Twitter de forma simples e rápida, além de evitar tanto quanto possível consumir demasiados recursos do computador. Com ele   é possível realizar  ações do Twitter, tais como:

* Crear, responder, reenviar y eliminar Tuits,
* Marcar como favorito, eliminar de tus favoritos un tuit,
* Enviar y eliminar mensajes directos,
* Ver tus amigos y seguidores,
* Seguir, dejar de seguir, reportar como spam y bloquear a un usuario,
* Abrir una línea temporal para un usuario, lo que permite obtener todos los Tuits de ese usuario únicamente,
* Abrir direcciones URL cuando vayan en un tuit o mensaje directo,
* Reproducir varios tipos de archivos o direcciones que contengan audio.
* Y más.

# Tabla de contenidos

Para poder utilizar una aplicación como TW Blue que te permita gestionar una cuenta de Twitter, primero tienes que  estar registrado en esta red social. Esta documentación no tiene como objetivo explicar el procedimiento para hacerlo. Partiremos desde el punto que tienes una cuenta con su respectivo nombre de usuario y contraseña. La documentación cubrirá estas secciones.

* [Autorizar la aplicación](#autorizar)
* [La interfaz del programa](#interfaz)
* [Controles](#controles)
    * [La interfaz gráfica (GUI)](#gui)
        * [Botones de la aplicación](#botones)
        * [Menús](#menus)
            * [Menú aplicación](#app)
            * [Menú Tuit](#tuit)
            * [Menú Usuario](#usuario)
            * [Menú buffer](#buffer)
            * [Menú ayuda](#ayuda)
    * [La interfaz No Visible](#interfaz_no_visible)
    * [Atajos de Teclado para la Interfaz Gráfica](#atajos)
    * [Atajos de Teclado para la Interfaz no Visible](#atajos_invisibles)
* [Listas](#listas)
* [Reportando Errores desde la web](#reportar)
* [Contacto](#contacto)

## Autorizando la aplicación {#autorizar}

Antes de nada, lo primero que se necesita es autorizar al programa para que este pueda acceder a tu cuenta de Twitter, y desde ella realizar lo que le pidas. El proceso de autorización es bastante sencillo, y en ningún momento el programa podrá tener acceso a tus datos como usuario y contraseña. Para autorizar la aplicación, solo tienes que abrir el archivo principal del programa, llamado TW Blue.exe (en algunos PC, solo se muestra como TW Blue).

Al hacerlo, si no has configurado ninguna vez el programa, se mostrará un cuadro de diálogo donde te informa que serás llevado a Twitter para autorizar la aplicación una vez pulses sobre "aceptar". Para empezar con el proceso de autorización presiona sobre el único botón de ese diálogo.

A continuación, tu navegador predeterminado se abrirá con la página de Twitter solicitándote autorizar la aplicación. Escribe, si no estás autenticado ya, tu nombre de usuario y contraseña, luego busca el botón autorizar, y presiónalo.

De la página a la que serás redirigido (si el proceso ha tenido éxito), busca las instrucciones que te proporciona Twitter. En resumen, te dará un código numérico de varios dígitos que deberás pegar en un cuadro de texto que la aplicación ha abierto en otra ventana.

Pega el código de verificación, y pulsa la tecla Intro.

Si todo ha salido bien, la aplicación empezará a reproducir un grupo de sonidos en señal que se están actualizando tus datos.

Cuando termine, el programa reproducirá otro sonido, y el lector de pantalla dirá "listo".

## La interfaz del programa {#interfaz}

La forma más simple de describir la interfaz gráfica de la aplicación es la de una ventana con una barra de menú con cinco menús (aplicación, tuit, usuario, buffer y ayuda); una lista de varios elementos y en la mayoría de los casos tres botones. Tuit, retuit y responder. Las acciones para cada uno de estos elementos serán descritas más adelante.

Los elementos que hay en las listas pueden ser Tuits, mensajes directos o usuarios. TW Blue crea diferentes pestañas para cada lista, pues estos elementos pueden ser Tuits enviados, Tuits recividos en la línea principal, favoritos, o mensajes directos, y cada pestaña tiene un solo tipo de Tuit. Estas pestañas se llaman listas o buffers.

Para cambiar entre las listas se hace presionando Control+Tab si se desea avanzar, y Control+Shift+Tab para retroceder. En todo momento los lectores de pantalla anunciarán la lista hacia la que se cambie el foco de la aplicación. Aquí están las listas básicas de TW Blue, que aparecen si se usa la configuración por defecto.

* Principal: Aquí van todos los Tuits que se muestran en la línea principal. Estos son los Tuits de los usuarios a los que sigues.
* Menciones: Si un usuario (lo sigas o no) te menciona en Twitter, lo verás en esta lista.
* Mensajes directos: Aquí están los mensajes directos (privados) que intercambias con los usuarios que sigues y te siguen. Esta lista solo muestra los mensajes recividos.
* Enviados: En esta lista se muestran todos los Tuits y mensajes directos que se han enviado desde tu cuenta.
* Favoritos: Aquí verás los Tuits que has marcado como favoritos.
* Seguidores: Cuando los usuarios sigan tu cuenta, podrás verlos en esta lista, junto con un poco de información de la cuenta.
* Amigos: Igual que la lista anterior, pero estos usuarios son a los que tú sigues.
* Eventos: Un evento en TW Blue es "algo" que pase en Twitter. En la línea de eventos, podrás ver registrados los eventos más comunes (p. Ej. Te han comenzado a seguir, han marcado o removido un tweet tuyo de los favoritos, te has suscrito a una lista). Son como pequeñas notificaciones que envía Twitter y TW Blue organiza para que no te pierdas lo que ha pasado con tu cuenta.
* Línea temporal de un usuario: Estas son listas que tú deberás crear. Es una lista que contiene únicamente los Tuits de un usuario. Se usan si algún día necesitas o quieres ver los Tuits que ha realizado solo una persona y no deseas buscar por todo tu timeline. Puedes crear tantas como usuarios necesites.
* Lista: Una lista es parecida a una línea temporal, pero compuesta por los tweets de cada usuario que forme parte de ella. De momento las listas son una característica experimental de TW Blue. Si experimentas problemas con ellas, por favor escríbenos para contárnoslo.
* Búsqueda: Un buffer de búsqueda contiene los resultados de una búsqueda hecha en TW Blue. Las búsquedas pueden ser por tuits, en cuyo caso buscas un término en los tuits relevantes de Twitter, o por usuarios, donde los resultados son nombres de usuario de Twitter.
* Favoritos de un usuario: Es posible pedirle a TW Blue que te muestre los tuits que un usuario ha marcado como favoritos.

Nota: Únicamente para esta versión de TW Blue, los amigos y seguidores actualizarán hasta 400, o cerca a los 400. En la próxima versión proporcionaremos un método para ver los amigos y seguidores sin exponerse tanto a los errores causados por el uso de la API de Twitter, muy frecuente entre personas con más de 600 amigos o seguidores.

Ten en cuenta que por defecto la configuración solo permite obtener los 200 últimos Tuits para las listas principal, menciones, mensajes directos y líneas temporales. Esto puedes cambiarlo desde el diálogo de configuración. Para los enviados se obtendrán los últimos 200 Tuits y 200 mensajes directos. En versiones futuras se permitirá ajustar este parámetro.

Si hay una dirección URL en algún tuit, TW Blue intentará abrirla cuando presiones Intro sobre ella. Si hay más de una, te mostrará una lista con todas para que selecciones la que quieras abrir. Si estás en el cuadro de diálogo de los amigos o seguidores,  la tecla intro te mostrará detalles del mismo.

Si pulsas Control+Intro, TW Blue intentará reproducir el audio que tenga el tuit sobre el que está el foco del sistema, siempre que tenga una URL. Si el tuit lleva la etiqueta #audio, un sonido al pasar por él te alertará que es un audio y puedes intentar reproducirlo. No obstante, también puede que no esté etiquetado y que TW Blue pueda reproducirlo, siempre que lleve a una dirección URL donde exista audio.

## Controles {#controles}

A partir de la versión 0.36, existe soporte para una interfaz que no requiere de una ventana visible. Esta puede ser activada pulsando Control+m, o seleccionando desde el menú aplicación la opción "Esconder ventana". Esta interfaz se maneja completamente con atajos de teclado. Estos atajos son diferentes a los que se utilizan para la interfaz gráfica. Cada una de ellas podrá utilizar solo los atajos que le correspondan, lo que quiere decir que no se permitirá utilizar los atajos de la interfaz no visible si se tiene activada la interfaz gráfica. En esta sección se detallará tanto la interfaz gráfica como la no visible.

### Interfaz gráfica (GUI) {#gui}

Aquí una lista dividida en dos partes. Por un lado, los botones que encontrarás si presionas Tab o Shift+Tab en la interfaz del programa, y por otro, los diferentes elementos que hay en la barra de menú.

#### Botones de la aplicación {#botones}

* Twit: Este botón abre el diálogo para escribir un tuit. El mensaje solo debe tener 140 caracteres. Al escribir el caracter número 141, un sonido será reproducido para indicarte que te has pasado del límite permitido por Twitter. Puedes querer acortar o desacortar una URL si la incluye tu tuit a fin de ganar más espacio donde escribir, para eso están los botones con esos nombres. Pulsa Intro para enviar el tuit. Si todo sale bien, el mensaje se enviará y tú escucharás un sonido que te lo confirme, si no, el lector de pantalla te responderá con un error en inglés, que indica por qué no se ha podido enviar el mensaje.
* Retuit: Este botón se encarga de reenviar el tuit sobre el que estás leyendo. Al presionarlo se te preguntará si deseas añadirle un comentario al tuit original (citándolo) o simplemente enviarlo como se ha escrito sin añadir nada más.
* Responder: Cuando estés visualizando un Tuit, puedes responderle al usuario que lo escribió pulsando sobre este botón. Se abrirá el mismo diálogo de Tuit, pero con el nombre del usuario (por ejemplo @usuario) en el, para que solo escribas el mensaje que quieres responderle. Si en el tuit hay más de un usuario mencionado, pulsa Shift+Tab y pulsa el botón "Mencionar a todos los usuarios". Cuando estés en la lista de amigos o seguidores, este botón se llamará mencionar.
* mensaje directo: Exactamente igual que enviar un Tuit, pero es un mensaje privado que solo podrá ver el usuario al que se lo envías. Pulsa Shift+Tab para ver el destinatario de tu mensaje. Si en el Tuit donde estabas para enviar el mensaje había más de un usuario mencionado, puedes navegar con las flechas de arriba y abajo para seleccionar otro, o escribir tú mismo el usuario (sin el signo de arroba).

Ten en cuenta que los botones aparecerán según las acciones que se puedan hacer en la lista donde estés. Por ejemplo, en la línea principal, menciones, enviados, favoritos y las líneas temporales de los usuarios podrás ver los cuatro botones; mientras que en la lista de mensajes directos solo estará disponible el botón de "Mensaje Directo" y "tuit", y en las listas de amigos y seguidores, se verá el botón para "Twit" y el de "Mensaje directo" junto a "mencionar".

#### Menús {#menus}

En la parte superior de la ventana del programa podrás encontrar una barra de menú que hace las mismas cosas, y algunas cuantas más. A la barra de menú se accede presionando la tecla ALT, y cuenta en este momento con cuatro menús para diferentes acciones: Aplicación, Tuit, usuario y Ayuda. En esta sección se describen las acciones para cada uno de ellos.

##### Menú aplicación {#app}

* Actualizar Perfil: Abre un diálogo desde donde se podrá actualizar parte de tu información en Twitter. Nombre, ubicación, dirección URL y descripción. Si ya tienes alguno de estos campos actualmente en el perfil se llenarán automáticamente con lo que tiene tu configuración de Twitter. También podrás subir una foto a tu perfil.
* Esconder Ventana: Desactiva la interfaz gráfica. Lee el apartado sobre la interfaz no visible para más detalles sobre este comportamiento.
* Búsqueda: Muestra un cuadro de diálogo desde donde puedes buscar por tuits o por usuarios en twitter.
* Gestor de listas: Para poder utilizar las listas de Twitter, primero necesitarás crearlas. Este diálogo permite ver tus listas, editarlas, crearlas, borrarlas y, opcionalmente, verlas en buffers tal como lo harías con las líneas temporales.
* Tutorial de sonidos: Abre un diálogo donde verás una lista de los sonidos de TW blue, para que puedas aprenderlos y no te cueste trabajo familiarizarte con TW Blue.
* Preferencias: Abre un diálogo de configuración desde donde se pueden controlar algunos aspectos del programa. Las opciones no necesitan de explicación.
* Salir: pregunta si quieres salir o no del programa. Si la respuesta es que sí, cierra la aplicación.

##### Menú Tuit {#tuit}

* Las primeras opciones del menú son Twit, responder y retuit, que corresponden a los botones del mismo nombre.
* Marcar como favorito: Marca el tuit que estés viendo como favorito.
* Quitar tuit de favoritos: Elimina el tuit de tus favoritos. Esto no significa que se borra de Twitter, solo deja de estar en tu lista de favoritos.
* Ver Tuit: Abre un diálogo donde puedes ver el Tuit, mensaje directo, amigo o seguidor sobre el que esté el foco de la aplicación. Puedes leer el texto con los cursores. El diálogo es el mismo que el que se usa para escribir un Tuit.
* Eliminar: Elimina el Tuit o mensaje directo sobre el que estés, borrándolo definitivamente de Twitter y qitándolo de tus listas. Ten en cuenta que en el caso de los Tuits, Twitter solo permite borrar los que tú mismo has escrito.

##### Menú usuario {#usuario}

Ten en cuenta que las primeras seis opciones de este menú abren un mismo diálogo. Este diálogo tiene un cuadro de edición donde puedes seleccionar el usuario sobre el que deseas actuar, bien con los cursores arriba y abajo o escribiendo tú mismo el nombre. Después, hay un grupo de botones de radio para seguir, dejar de seguir, silenciar, des-silenciar, reportar como Spam y bloquear. Si seleccionas desde el menú la opción seguir, el botón del cuadro de diálogo estará marcado con esa opción, así como sucederá respectivamente con dejar de seguir, reportar como Spam y bloquear. Pulsa el botón Aceptar para que el programa trate de hacer lo que le pides. Si no se ha podido, escucharás el error en inglés.

A continuación se describen las opciones restantes para este menú:

* Mensaje Directo: La misma acción que el botón.
* Añadir a lista: Para que puedas ver los tweets de un usuario en tus listas, primero hay que añadirlo. Esta opción abrirá un diálogo desde donde puedes seleccionar al usuario que deseas añadir, para después abrir otra ventana donde puedes seleccionar la lista a la cual añadir a ese usuario. Una vez hecho esto, la lista contendrá un nuevo usuario y podrás ver sus tweets.
* Ver Perfil del usuario: Abre un diálogo desde donde te permite seleccionar el usuario al que quieres ver el perfil.
* Línea temporal: Abre un diálogo desde donde puedes seleccionar el usuario para el que se creará la línea temporal. Al presionar intro, se creará. Si se hace una línea temporal de un usuario que no tenga Tuits, el programa fallará. Si se crea una línea que ya existe el programa te avisará y no permitirá crearla de nuevo.
* Ver favoritos: Abre un buffer para seguir los favoritos que marca el usuario seleccionado.

##### Menú Buffer {#buffer}

* Silenciar: Silencia completamente el buffer, con lo que no escucharás sonido alguno cuando nuevos elementos aparezcan.
* Leer automáticamente tuits para este buffer: Esta opción activa o desactiva la lectura automática de tuits. Si está activada, el lector de pantalla o la voz Sapi5 (si está activada una) leerá automáticamente los nuevos tuits conforme estos vayan llegando al buffer.
* Limpiar Buffer: Vacía los elementos de este buffer.
* Eliminar buffer: Borra la lista sobre la que te encuentras actualmente.

##### Menú Ayuda {#ayuda}

* Documentación: Abre este archivo, donde puedes leer algunos conceptos interesantes del programa.
* ¿Qué hay de nuevo en esta versión?: Abre un documento con la lista de cambios desde la versión actual, hasta la primera en existencia.
* Buscar actualizaciones: Cada que se abre el programa él mismo busca automáticamente si hay una nueva versión. Si lo hay, te preguntará si quieres descargarla; si aceptas, TW Blue descargará la actualización, la instalará y te pedirá reiniciarla (algo que hace automáticamente). Esta opción comprueba si hay actualizaciones sin tener que reiniciar la aplicación.
* Sitio web de TW Blue. Ve a  nuestra [página principal](http://twblue.com.mx) donde podrás encontrar toda la información y descargas relativas a TW Blue, así como participar de la comunidad.
* Reportar un error: Lanza un diálogo desde donde puedes reportar un error solo llenando un par de campos. El título y una pequeña descripción de lo que pasó. Al pulsar en "enviar" el error se reportará. Si no se ha podido el programa te mostrará un mensaje informándolo.
* Sobre TW Blue: Muestra información de créditos del programa.

### Interfaz no visible {#interfaz_no_visible}

Si presionas Control+M, o si desde el menú aplicación seleccionas esconder ventana, estarás activando una interfaz a la que no se podrá acceder por la manera convencional, porque no se ve. 

En la interfaz no visible todo lo que hagas será mediante atajos de teclado, incluso para recorrer las listas. Eventualmente se abrirán diálogos y estos sí serán visibles, pero la ventana principal de la aplicación no. Ve a la sección de atajos de teclado de la interfaz no visible para saber cuales puedes usar de momento.

### Atajos de teclado para la Interfaz Gráfica {#atajos}

Además de los botones y menús, la mayoría de las acciones pueden hacerse presionando una combinación de teclado. Aquí están las existentes en este momento:

* Intro: Abrir una dirección URL. Si hay más de una podrás ver una lista que te permitirá seleccionar la que quieras. Si estás en la lista de amigos o seguidores, mostrará detalles del seleccionado.
* Control+Intro: Intenta reproducir un audio si en el Tuit hay una dirección URL. 
* F5: Baja un 5% el volumen de los sonidos. Esto afecta a los sonidos que reproduce el programa y al audio que puedas escuchar a través de él.
* F6: Sube un 5% el volumen de los sonidos de la aplicación.
* Control+N: Abre el diálogo para escribir un nuevo Tuit.
* Control+M: Oculta la ventana.
* Control+Q: Sale de la aplicación.
* Control+R: Abre el diálogo para responder.
* Control+Shift+R: Equivalente a la acción Retuit.
* Control+D: Enviar mensaje directo.
* Control+F: Marcar como favorito.
* Control+Shift+F: Quitar de favoritos.
* Control+Shift+V: Ver Tuit.
* Control+S: Seguir a un usuario.
* Control+Shift+S: Dejar de seguir a un usuario.
* Control+K: Bloquear a un usuario.
* Control+Shift+K: Reportar como Spam.
* Control+I: Abrir línea temporal a un usuario.
* Control+Shift+I: Eliminar línea temporal.
* Control+p: Editar tu perfil.
* Suprimir: Eliminar tuit o mensaje directo.
* Shift+suprimir: vacía el buffer, quitando todos los elementos hasta ese entonces. Esto ocurre sin borrar nada de Twitter.

### Atajos de teclado para la Interfaz no Visible {#atajos_invisibles}

Estos son los atajos de teclado que puedes usar desde la interfaz no visible. Ten en cuenta que cuando la vista de la interfaz gráfica esté activada ninguno de ellos podrá usarse. Al decir "windows", nos estamos refiriendo a la tecla de Windows izquierda.

* Control+Windows+Flecha Arriba: Va arriba en la lista actual.
* Control+Windows+Flecha abajo: Va hacia abajo en la lista actual.
* Control+Windows+Izquierda: Se desplaza a la pestaña de la izquierda.
* Control+Windows+Derecha: Se desplaza hacia la pestaña de la derecha.
* Control+Windows+Inicio: Ir al primer elemento de la lista.
* Control+Windows+Fin: Ir al final de la lista.
* Control+Windows+Avance de página: Ir 20 elementos hacia abajo en la lista actual.
* Control+Windows+Retroceso de página: ir 20 elementos hacia arriba en la lista actual.
* Control+Windows+Alt+Flecha Arriba: Subir volumen un 5%.
* Control+Windows+Alt+Flecha Abajo: Bajar volumen un 5%.
* Control+Windows+Intro: Abrir URL en el tuit, o ver detalles del usuario si estás en la lista de amigos o seguidores.
* Control+Windows+Alt+Intro: Intentar reproducir un audio.
* Control+Windows+M: Muestra la interfaz gráfica, desactivando la no visible.
* Control+Windows+N: Hacer un nuevo Tuit.
* Control+Windows+R: Responder a un tuit.
* Control+Windows+Shift+R: Hacer un retuit.
* Control+Windows+D: Enviar un mensaje directo.
* Control+Windows+Suprimir: Eliminar un tuit o mensaje directo.
* control+win+Shift+suprimir: vacía el buffer, quitando todos los elementos hasta ese entonces. Esto ocurre sin borrar nada de Twitter.
* Windows+Alt+F: Marcar como favorito.
* Windows+Alt+Shift+F: Quitar de favoritos.
* Control+Windows+S: Seguir a un usuario.
* Control+Windows+Shift+S: Dejar de seguir a alguien.
* Control+Windows+Alt+N: Ver detalles de un usuario,
* Control+Windows+V: Ver tuit en un cuadro de texto.
* Control+Windows+I: Abrir línea temporal.
* Control+Windows+Shift+I: Eliminar línea temporal de un usuario.
* Alt+Windows+P: Editar tu perfil.
* Control+win+espacio: ver tweet actual.
* Control+win+c: Copiar tweet al portapapeles.
* Control+windows+a: Añadir a un usuario a la lista.
* Control+shift+windows+a: qitar de la lista.
* Control+Windows+Shift+Flecha arriba: Ir un tuit hacia arriba en la conversación.
* Control+Windows+Flecha Abajo: Ir un tuit hacia abajo en la conversación.
* Control+Windows+Shift+M: Activar o desactivar el sonido para el buffer actual.
* Windows+Alt+M: Activar o desactivar el silencio global de TW Blue.
* Control+Windows+E: Activar o desactivar la lectura automática de los tuits en el buffer actual.
* Control+windows+Guion: buscar en Twitter.
* Control+Windows+F4: Cerrar el programa.

## Listas {#listas}

Una de las características más interesantes de Twitter son las listas, ya que son una manera de mantenerse actualizado sin tener que leer los tweets de todos los usuarios a los que sigues. Con una lista de Twitter solo verás los tweets de sus miembros (la gente que está dentro de la lista). Es parecido a una línea temporal, pero para muchos más usuarios.

En TW blue hemos empezado a dar soporte para esta característica. De momento vamos poco a poco, pero ya es posible usar esta función. Te presentamos los pasos que hay que dar para poder tener una lista abierta en TW Blue.

* Primero necesitarás ir al gestor de listas, ubicado bajo el menú aplicación.
* en el gestor de listas podrás ver todas las listas a las que estás unido, empezando por las que tú has creado. Si no ves ninguna lista en este diálogo, significa que no has creado ni te has unido a ninguna lista. Está bien.
* Verás un grupo de botones que se explican por sí solos: Crear nueva lista, editar, eliminar, abrir en buffer (este quizá es el menos claro, se refiere a abrir un nuevo buffer para que TW Blue actualice los tweets de la lista, como cuando pasa con las líneas temporales).

Una vez que hayas creado una nueva lista, no deberías abrirla en buffer. Al menos no de inmediato, porque en este momento no tiene miembro alguno y eso significa que cuando se carguen los tweets para empezar a actualizarla no verás nada. Es recomendable primero añadir a gente a la lista, tal como sigue:

* Cuando hayas cerrado el gestor de listas y estés navegando por entre los tweets de los usuarios, busca el usuario al que quieres añadir a la lista.
* Una vez encontrado, presiona el atajo Ctrl+Win+A o ve al menú usuario y selecciona la opción "Añadir a lista".
* Lo siguiente que verás es un diálogo que te permitirá seleccionar el usuario, asegúrate que el que está como predeterminado es el que deseas, o cámbialo si es necesario, y presiona Aceptar.
* Ahora verás otro diálogo, pero aquí están todas tus listas. Selecciona una (simplemente lleva el cursor hacia ella), y presiona el botón añadir.
* Para qitar a un usuario de una lista repite el mismo proceso, pero presiona Control+Win+Shift+A o selecciona la opción "Quitar de lista", y en el diálogo de las listas presiona sobre el botón "remover".

## Reportando Errores Desde la Web {#reportar}

Nota: Si estás usando el programa también puedes reportar un error desde el mismo, usando para ello la opción del menú ayuda. Este proceso solo te pide llenar dos cuadros de edición, y se encarga del resto. Estos pasos están escritos para quienes no pueden abrir el programa, no lo tienen en uso en este momento o sencillamente quieran reportar desde la web en lugar del sistema integrado de reporte de errores.

Las cosas en este mundo (sí, incluidos los programas informáticos) están muy lejos de ser perfectas, con lo que a menudo te encontrarás con errores no previstos en la aplicación. Pero como la intención es siempre mejorar, eres libre (es más, sería genial que lo hicieras) de reportar los errores que vayas encontrando del programa para que se puedan revisar y eventualmente corregir.

Para entrar a la web de reporte de incidencias, sigue [Este enlace.](http://twblue.com.mx/errores/bug_report_page.php) Es una web con un formulario donde tienes que llenar varios campos. Solo tres de ellos son realmente obligatorios (los que tienen marcado un asterisco), pero entre más campos puedas llenar, será mejor.

Aquí están los diferentes campos del formulario y lo que deberías introducir en cada uno de ellos. Recuerda que son obligatorios solamente los campos marcados con un asterisco (*):

* Categoría: Este cuadro combinado permite seleccionar a qué categoría asignar el error. Puede ser a la categoría General, si es un error del programa, o a documentación, si has encontrado un error en este archivo o en la lista de cambios. Este campo es obligatorio.
* Reproducibilidad: Aquí deberías indicar qué tan fácil o no es de reproducir el error. Las opciones disponibles son Desconocido, No reproducible, No se ha intentado (por defecto), aleatorio, a veces o siempre. Dependiendo de si se puede reproducir el error o no, deberías indicar lo que se parezca más a tu caso. Si estás solicitando una nueva funcionalidad, no importa este cuadro combinado.
* Severidad: Aquí se selecciona que tanto afecta esto al programa. Las opciones disponibles son funcionalidad (selecciona esto para solicitar una nueva funcionalidad), Trivial, Texto, Ajuste, Menor, Mayor, fallo o bloqueo. Nota que las opciones aumentan de nivel. Selecciona lo que más creas. Si no estás seguro de que seleccionar puedes dejarlo como está.
* Prioridad: En este cuadro se selecciona la opción de acuerdo con la importancia del error o funcionalidad solicitada. Las opciones disponibles son Ninguna, baja, normal, alta, hurgente e inmediata.
* Seleccionar Perfil: Aquí puedes escojer entre la configuración de arquitectura (32 o 64 bits), y el sistema operativo (Windows siete de momento). Si no, puedes llenar los tres cuadros de edición que están en la siguiente tabla con tus datos en específico.
* Versión del producto: Selecciona la versión del programa que estás utilizando para poder averiguar donde se ha generado el error. Este cuadro combinado tendrá la lista de las versiones en orden. Si bien no es obligatorio, ayudaría mucho a resolver más rápidamente el error.
* Resumen: Un título para el error, que explique en pocas palabras qué ocurre. Es un cuadro de texto obligatorio.
* Descripción: Este campo también obligatorio, te pide que describas con más detalles qué fue lo que ha ocurrido con el programa.
* Pasos para reproducir: Este campo de texto te sirve si sabes como hacer que la aplicación genere el error. Esto no es obligatorio, pero ayudaría mucho conocer como hacer que el programa tenga este error para rastrearlo mejor.
* Información adicional: Si tienes un comentario o nota que añadir, aquí puede ir. No es obligatorio.
* Subir archivo: Puedes subir aquí el archivo TW Blue.exe.log que se creó con el error que el programa tuvo. No es obligatorio.
* Visibilidad: Selecciona si quieres que el error sea público o privado. Por defecto es público, y es recomendable que así continúe.
* Enviar reporte. Presiona aquí para publicar el error y que este sea atendido.

Muchas gracias por participar reportando errores y probando las funciones nuevas.

## Contacto {#contacto}

Si lo que se expone en este documento no es suficiente, si deseas colaborar de alguna otra forma o si simplemente deseas mantenerte en contacto con quien hace esta aplicación, sigue a la cuenta [@tw_blue2](https://twitter.com/tw_blue2) o a [@manuelcortez00.](https://twitter.com/manuelcortez00) También puedes visitar nuestro [Sitio web](http://twblue.com.mx)

---
Copyright © 2013-2014. Manuel Cortéz.