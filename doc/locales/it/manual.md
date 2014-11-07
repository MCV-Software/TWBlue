% Guida utente TW Blue

# Versione 0.42 (alfa)

# Attenzione!

Questo manuale fa riferimento a una versione in sviluppo. L'intento del manuale è dare alcuni dettagli sul funzionamento del programma. Considerare che il programma è continuamente in sviluppo, alcune funzioni del software possono non corrispondere, è consigliabile seguire lo sviluppo per non perdere nuove informazioni.

Per leggere le novità rispetto alle precedenti versioni, [Leggi le novità quì.](changes.html)

# TW Blue

TW Blue è un'applicazione che consente di utilizzare Twitter in modo semplice, rapido, con l'utilizzo di poche risorse del computer in uso. Di seguito le azioni che puoi eseguire in Twitter attraverso TWBlue:

* Scrivere, rispondere, Ritwittare e eliminare Tweet;
* Segnare come favorito, eliminare dai favoriti un tweet;
* Inviare ed eliminare messaggi diretti (DM);
*Visualizzare i tuoi seguitori e chi stai seguendo;
* •Seguire, non seguire, riportare come spam o bloccare un utente;
* Aprire una linea temporale specifica per un utente, che permette di leggere i tweet dell'utente scelto in un unico elenco;
* Aprire collegamenti a pagine web se presenti in un tweet o nei messaggi;
* Riprodurre file o collegamenti che contengono audio;
* E ancora di più!.

# Tabella dei contenuti

Per utilizzare un client come TW Blue che permette di gestire un account Twitter, occorre esser registrati al social network. Questa documentazione non ha l'intento di spiegare la procedura per iscriversi a Twitter. Per iniziare ti occorre il tuo nome utente e password che usi per accedere al tuo account. La documentazione riguarderà queste sezioni.

* [Autorizzare l'applicazione](#autorizar)
* [L'interfaccia del programma](#interfaz)
* [Comandi](#controles)
    * [Interfaccia grafica (GUI)](#gui)
        * [Pulsanti dell'applicazione](#botones)
        * [Menu](#menus)
            * [Menu Applicazione](#app)
            * [Menu Tuit](#tuit)
            * [Menú Utente](#usuario)
            * [Menú buffer](#buffer)
            * [Menú Aiuto](#ayuda)
    * [Interfaccia Invisibile](#interfaz_no_visible)
    * [Shortcuts per l'interfaccia Grafica](#atajos)
    * [Shortcuts per l'interfaccia invisibile](#atajos_invisibles)
* [Liste](#listas)
* [Riportare un errore](#reportar)
* [Contatti](#contacto)

## Autorizzare l'applicazione {#autorizar}

Prima di tutto, è necessario autorizzare il programma perché questo possa accedere al tuo account Twitter. Il processo di autorizzazione è abbastanza semplice, il programma non potrà in nessun momento aver accesso ai tuoi dati. Per autorizzare l'applicazione eseguire TW Blue.exe.

Al primo avvio del programma si aprirà una finestra di dialogo la quale informa che sarai collegato alla pagina di Twitter per autorizzare l'applicazione. Premere il pulsante "Accetto" per iniziare il processo di autorizzazione.

Una pagina si aprirà nel browser con la richiesta di autorizzazione. inserisci i tuoi dati di accesso, e premi il pulsante Autorizza.

Se il processo di login ha avuto esito positivo, si apre una pagina con le istruzioni proposte da Twitter. Viene visualizzato un codice alfa-numerico che si dovrà copiare e inserire nell'apposita finestra del programma.

Premi invio per accettare il codice di autorizzazione.

Se tutto è andato a buon fine, l'applicazione riproduce un set di suoni che confermano che si stanno aggiornando i tuoi dati.

Al termine, si udirà un altro suono di avvio e lo Screen Reader annuncerà "Pronto!".


## Interfaccia del programma {#interfaz}

Il modo più semplice per descrivere l'interfaccia grafica è quella di una finestra con una barra che contiene cinque menu (Applicazione, Tweet, Utente, Buffer ed Aiuto). Un elenco nel riquadro principale e, nella maggior parte dei casi, tre pulsanti; Tweet, retweet e Rispondi. Le azioni per ciascuno di questi elementi saranno descritti di seguito.

Gli elementi presenti nell'elenco possono esser Tweet, messaggi diretti o utenti. TW Blue visualizza diverse schede per vari elenchi, quindi questi elementi possono esser Tuits inviati, Tweet ricevuti nella linea temporale principale, favoriti, o messaggi diretti. Ogni scheda contiene un solo tipo di questi elementi, queste schede sono chiamate buffers.

Per selezionare i buffer premere Control+Tab o Control+Shift+Tab per retrocedere. Ogni qual volta si cambia buffer il lettore di schermo annuncia il riquadro focalizzato. Di seguito i buffer presenti in TW Blue.

* Linea Temporale: quì verranno visualizzati i Tweet nella linea temporale principale. Sono i Tweet degli utenti che stiamo seguendo attualmente.
* Menzioni: Se un utente (seguitore o meno) ti menziona in Twitter, verrà visualizzato in questo buffer il tweet.
* Messaggi Diretti: visualizza i messaggi diretti (DM privati) che puoi scambiare solo con gli utenti che segui e che ti seguono. Questo elenco visualizza solo i messaggi ricevuti.
* Inviati: visualizza i Tweet e i messaggi diretti inviati dal tuo account.
* •Favoriti: l'elenco dei tweet segnalati come favoriti.
* Followers: elenco degli utenti che ti stanno seguendo, con alcune informazioni riguardo il loro account Twitter.
* Following: elenco degli utenti che stai seguendo.
* Notifiche: alcuni eventi vengono registrati come notifiche in Twitter. In questo buffer verranno visualizzate le notifiche più comuni (per esempio qualcuno ha iniziato a seguirti, hanno segnalato o rimosso un tuo tweet come favorito, ti sei iscritto a una lista). Sono tutte le notifiche che invia twitter e TW Blue organizza in un elenco per non perderti ciò che accade al tuo account.
* Linea Temporale di un utente: è possibile creare linee temporali per specifici utenti. In questo elenco appariranno solo i tweet di uno specifico utente. Utile per cercare i tweet di una determinata persona, senza dover scorrere tutta la Linea Temporale principale. Si possono creare più linee temporali specifiche per ogni utente, a seconda delle necessità.
* Lista: Una lista È simile a una linea temporale, ma visualizza solo i tweets degli utenti che ne fanno parte. Attualmente questa caratteristica è sperimentale in TW Blue. In caso si verificano problemi con questa caratteristica, si prega di contattarci e segnalare l'errore.
* Ricerca: Un buffer contenente i risultati della ricerca con TW Blue. Le ricerche possono essere per tweets, nel caso si cerca un termine contenuto in tweet, o per utenti, dove i risultati sono i nomi utente di Twitter.
* Favoriti di un utente: è possibile visualizzare in TW Blue i tweet che un utente ha contrassegnato come preferito.

Nota: Solo per questa versione di TW Blue, l'elenco degli utenti che segui e che ti seguono si aggiorna a 400, o circa 400. Ci proponiamo per le prossime versioni un metodo per evitare gli errori della API di Twitter, segnalato da persone con più di 600 utenti che segue o che stanno seguendo.

Di default vengono visualizzati 200 tweet nel buffer principale, menzioni, messaggi diretti e linee temporali specifiche. Dal menu preferenze è possibile cambiare questa impostazione. Per gli elementi inviati verranno visualizzati gli ultimi 200 Tuits e 200 messaggi diretti. Le versioni future vi permetteranno di impostare anche questo parametro.

Se è presente un link nei tweet, TW Blue tenterà di aprirla premendo Invio. Se son presenti più collegamenti, si aprirà una finestra di dialogo per selezionare il link che si desidera aprire. Nell'elenco dei follower o following, premendo Invio verrà mostrata una finestra con i dettagli dell'utente.

Premendo Control+Invio, TW Blue riproduce l'audio inserito nel tweet selezionato, se è presente un collegamento audio. Se il tweet contiene l'etichetta #audio, verrai avisato da un suono che è possibile riprodurre l'audio. Può comunque accadere che non appare nessuna etichetta, ma TW Blue può riprodurre ugualmente l'audio, sempre che ci sia un collegamento.

## Comandi da tastiera {#controles}

Dalla versione 0.36, Vi è il supporto per un'interfaccia che non richiede una finestra visibile. Questa può esser attivata premendo Control+m, o dal menu Applicazione selezionando "Nascondi la finestra". Questa interfaccia è completamente gestita con le scorciatoie da tastiera. Queste scorciatoie sono diverse da quelle utilizzate per l'interfaccia grafica. Ogni interfaccia ha i suoi comandi specifici, ciò significa che non si possono usare i comandi dell'interfaccia grafica se è attiva l'interfaccia invisibile. Vediamo in dettaglio i comandi per l'interfaccia grafica e l'interfaccia invisibile.

### Interfaccia grafica (GUI) {#gui}

Di seguito un elenco diviso in due parti. Da una parte i pulsanti che si raggiungono premendo Tab o Shift+Tab nell'interfaccia del programma, e in secondo luogo, i diversi elementi della barra dei menu.

#### Pulsanti dell'applicazione {#botones}

* Twit: Questo pulsante apre una finestra di dialogo per digitare un tweet. Il limite è 140 caratteri, Quando si scrive il numero di carattere 141, verrà riprodotto un suono per avvisarti che hai superato il limite consentito da Twitter. È possibile accorciare o espandere un link, se vuoi includerlo,per guadagnare più spazio. Premere Invio per inviare il tweet. Se tutto è andato a buon fine, il messaggio viene inviato e si sente un suono di conferma. In caso contrario verrai avisato da un messaggio del mancato invio.
* Retweet: Reinvìa il tweet selezionato. È possibile aggiungere un commento al tweet originale (citandolo) o semplicemente inviarlo senza modifiche.
* Rispondi: È possibile rispondere al tweet selezionato premendo questo pulsante. Si apre una finestra di dialogo uguale a quella per i Tweet, con l'aggiunta del l'utente menzionato (per esempio @nomeutente). Se nel tweet ci son più utenti menzionati, premere Shift+Tab e premere il pulsante "Menziona a tutti". Nell'elenco follower e following, Questo pulsante è chiamato Menziona.
* Messaggio Diretto: come per la finestra per inviare Tweet, ma è un messaggio privato che può visualizzare solo l'utente a cui si invia. Premendo Shift+Tab si legge il destinatario del messaggio. Se nel tweet usato per richiamare il messaggio diretto sono presenti più utenti menzionati, si può navigare con le freccie per scegliere un destinatario diverso, o digitare manualmente il nome utente (senza il simbolo chiocciola).

Si noti che i pulsanti appariranno a seconda delle azioni che possono essere eseguite nel buffer focalizzato. Per esempio, nella linea temporale principale e specifica, menzioni, inviati, e preferiti verranno visualizzati i quattro pulsanti comuni. Invece nella scheda messaggi Diretti saranno presenti i pulsanti "Messaggio Diretto" e "tweet", mentre negli elenchi dei follower o following appare il pulsante "Twit" e "Messaggio Diretto" con quello "Menziona".

#### Barra del Menu {#menus}

Nella parte superiore della finestra del programma troverete una barra dei menu dal quale è possibile eseguire vari comandi compresi quegli sopra citati. Si accede al menu con il tasto Alt, attualmente sono presenti quattro menu per diverse azioni: Applicazione, Tweet, Utente e Aiuto. Di seguito si descrivono le azioni per ciascun menu.

##### Menú applicazione {#app}

* Aggiorna il profilo: apre una finestra dal quale è possibile modificare informazioni del tuo profilo in Twitter. Nome, localizzazione, indirizzo web e una descrizione. Inizialmente verranno visualizzati i dati attualmente inseriti nella tua configurazione personale di Twitter. È anche possibile inserire una foto al profilo.
* Nascondi la finestra: Disattiva l'interfaccia grafica. Leggere la sezione relativa all'interfaccia invisibile per maggiori dettagli su questa caratteristica.
* Ricerca: apre una finestra di dialogo per effettuare una ricerca per tweet o per utente in twitter.
* Gestione liste: Per utilizzare le liste di Twitter, è necessario prima crearle. Questa finestra di dialogo permette di visualizzare le tue liste, modificarle, crearne nuove, eliminarla. Le liste verranno visualizzate nell'area buffer così come sono le linee temporali.
* Tutorial dei suoni: Apre una finestra di dialogo con l'elenco dei suoni usati da TW blue, per aiutarti a famigliarizzare e facilitare l'utilizzo di TW Blue.
* Preferenze: Apre una finestra di configurazione dove è possibile controllare alcuni aspetti del programma.
* Esci: apre una finestra di dialogo per la conferma in caso si vuol uscire dal programma.


##### Menú Tweet {#tuit}

* I primi elementi del menu sono:Tweet, Rispondi e retweet, che corrispondono ai pulsanti con lo stesso nome.
* Aggiungi ai preferiti: segna il tweet selezionato come preferito.
* Rimuovi dai preferiti: Elimina un tweet dai preferiti. Questo non significa che vengono cancellati da Twitter, ma non verrà più visualizzato nell'elenco preferiti.
* Visualizza tweet: Apre una finestra per visualizzare un Tweet, un messaggio diretto selezionato . Permette di leggere il testo usando il cursore, molto simile alla finestra per scrivere Tweet.
* Elimina tweet: elimina il tweet o il messaggio diretto selezionato, rimuovendolo da Twitter e togliendolo dall'elenco. Si noti che nel caso di Tweets, Twitter consente di eliminare solo i tweet che hai scritto.

##### Menú Utente {#usuario}

Le prime sei opzioni di questo menu aprono la stessa finestra. Nel campo editazione è possibile indicare l'utente sulla quale si intende agire. Le varie azioni sono selezionabili con dei pulsanti radio. Se dal menu si sceglie Segui, nella finestra apparirà selezionato lo stesso pulsante radio, così per le altre azioni come unmute, non seguire, blocca ecc... Per accettare ed eseguire l'azione premere Invio. In caso l'azione scelta non può esser eseguita, verrai avvisato da un messaggio.

Di seguito le altre opzioni del menu Utente:

* Messaggio Diretto: la stessa azione del pulsante.
* Aggiungi alla lista: Per visualizzare i tweet di un utente nella tua lista, occorre prima aggiungerlo. Questa opzione apre una finestra di dialogo da cui è possibile selezionare l'utente che si desidera aggiungere, quindi apre un'altra finestra dove è possibile selezionare la lista a cui aggiungere l'utente. Una volta fatto, la lista conterrà un nuovo utente e visualizzerà i suoi tweet.
* Visualizza il profilo utente: Apre una finestra di dialogo in cui è possibile selezionare l'utente che si desidera vedere il profilo.
* Linea temporale: Apre una finestra da cui è possibile selezionare l'utente per il quale verrà creata una linea temporale specifica. Premendo Invio verrà creata. Se si tenta di creare una linea temporale di un utente che non ha nessun Tweet, il programma avrà esito negativo. Se una linea temporale per l'utente è già esistente verrai avvisato da un messaggio, non si possono creare linee temporali già esistenti.
* Visualizza preferiti: Apre un buffer per visualizzare i favoriti di un utente specifico

##### Menú Buffer {#buffer}

* Mute: silenzia il buffer, non verrà riprodotto nessun suono al verificarsi di nuovi eventi per questo buffer.
* Leggi automaticamente tweet per questo buffer: Questa opzione abilita o disabilita la lettura automatica di tweet. Se attivato, il lettore di schermo o SAPI5 vocale (se abilitato) leggerà i nuovi tweet quando arrivano al buffer selezionato.
* Ripulisci l'elenco: svuota gli elementi visualizzati nel buffer.
* Elimina elenco: elimina il buffer attualmente focalizzato.

##### Menú Aiuto {#ayuda}

* Documentazione: Apre questa guida per apprendere le caratteristiche e funzioni del programma.
* Cosa c'è di nuovo in questa versione?: apre un documento con l'elenco delle modifiche della versione attuale, rispetto alla prima versione.
* Ricerca di aggiornamenti: questa opzione controlla la disponibilità di aggiornamenti senza dover riavviare l'applicazione. Ogni volta che TW Blue si avvia, questo controlla automaticamente se ci sono nuove versioni. In caso di aggiornamenti verrai avisato ed apparirà una richiesta di conferma per scaricare; se si accetta, TW Blue scaricherà la nuova versione, quindi installa e riavvia il programma in automatico.
* Sito web di TW Blue: vai alla nostra Home page dove si possono trovare tutte le informazioni e download relative a TW Blue, e partecipare alla comunità.
* Riporta un errore: apre una finestra per segnalare eventuali errori compilando due campi editazione. Il titolo e una breve descrizione di ciò che è accaduto. Premendo il pulsante "Invia", il rapporto di errore verrà inviato. In caso di mancato invio, verrai avvisato da un messaggio.
* Informazioni su TW Blue: Mostra informazioni sulla versione e credits del programma.

### Interfaccia invisibile {#interfaz_no_visible}

Premendo Control+M, o dal menu Applicazione selezioni Nascondi Finestra, si attiva un'interfaccia per la quale non si usano i comandi convenzionali, è l'interfaccia invisibile.

Nell'interfaccia invisibile si possono eseguire solo comandi da tastiera, incluso quelli per scorrere gli elenchi. Potranno apparire messaggi di dialogo visibili, ma l'interfaccia principale sarà non visibile. Vai alla sezione scorciatoie da tastiera per l'interfaccia invisibile per conoscere i comandi attualmente disponibili.

### Scorciatoie da tastiera per l'interfaccia grafica {#atajos}

Oltre ai pulsanti e menu, La maggior parte delle azioni possono essere eseguite premendo una combinazione di tasti. Di seguito le shortcuts disponibili:

* Invio: Permette di aprire un link. Se in un tweet ci son più link, verrà visualizzato un elenco dei link che potrai aprire. Nell'elenco dei follower o following, visualizza dettagli dell'utente selezionato.
* Control+Invio: Riproduce l'audio contenuto nel tweet.
* F5: Diminuisce il volume (5%). Riguarda sia il volume dei suoni che dell'audio riprodotto con il programma.
* F6: aumenta il volume (5%) dei suoni dell'applicazione.
* Control+N: Apre una finestra per scrivere un nuovo Tweet.
* Control+M: Nasconde la finestra.
* Control+Q: esce dall'applicazione.
* Control+R: apre la finestra per rispondere a un tweet.
* Control+Shift+R: Equivalente all'azione Retweet.
* Control+D: Invia un messaggio diretto.
* Control+F: segna come preferito.
* Control+Shift+F: cancella dai preferiti.
* Control+Shift+V: visualizza tweet.
* Control+S: segui un utente.
* Control+Shift+S: non seguire più.
* Control+K: blocca utente.
* Control+Shift+K: riportare come Spam.
* Control+I: apre una linea temporale specifica.
* Control+Shift+I: elimina la linea temporale in uso.
* Control+p: modifica profilo.
* Delete: elimina il tweet o il messaggio diretto selezionato.
* Shift+Delete: svuota il buffer, rimuovendo tutti gli elementi ricevuti. Gli elementi non verranno rimossi da Twitter.

### Tasti di scelta rapida per l'interfaccia invisibile {#atajos_invisibles}

Queste sono le scorciatoie da tastiera che è possibile utilizzare nell'interfaccia invisibile. Si noti che quando l'interfaccia grafica è attivata nessuno di questi può essere utilizzato. Con il tasto "windows", ci riferiamo al tasto Windows di sinistra.

* Control+Windows+Freccia sù: Scorre l'elenco verso l'alto.
* Control+Windows+Freccia giù: Scorre l'elenco verso il basso.
* Control+Windows+Freccia sinistra: Passa alla scheda di sinistra.
* Control+Windows+Freccia destra: Passa alla scheda a destra.
* Control+Windows+Home: Vai alla prima voce dell'elenco.
* Control+Windows+Fine: Vai all'ultima voce dell'elenco.
* Control+Windows+pagina giù: salta 20 voci dell'elenco verso il basso.
* Control+Windows+Pagina sù: salta 20 voci dell'elenco verso l'alto.
* Control+Windows+Alt+Freccia sù: aumenta il volume del 5%.
* Control+Windows+Alt+Freccia giù: abbassa il volume del 5%.
* Control+Windows+Invio: apre un link nel tweet, apre i dettagli di un utente se ti trovi nell'elenco follower o following.
* Control+Windows+Alt+Invio: riproduce audio se disponibile.
* Control+Windows+M: visualizza l'interfaccia grafica, disattivando l'interfaccia invisibile.
* Control+Windows+N: nuovo tweet.
* Control+Windows+R: rispondi a un tweet.
* Control+Windows+Shift+R: retweet.
* Control+Windows+D: invia un messaggio diretto.
* Control+Windows+Delete: elimina un tweet o un messaggio diretto.
* Control+win+Shift+Delete: svuota buffer, rimuovendo tutte le voci fino a questo momento. Le voci non vengono eliminate da Twitter.
* Windows+Alt+F: segna come preferito.
* Windows+Alt+Shift+F: rimuovi dai preferiti.
* Control+Windows+S: segui.
* Control+Windows+Shift+S: non seguire più.
* Control+Windows+Alt+N: Visualizza i dettagli di un utente.
* Control+Windows+V: visualizza tweet.
* Control+Windows+I: Apri una linea temporale.
* Control+Windows+Shift+I: elimina una linea temporale specifica.
* Alt+Windows+P: Modifica il tuo profilo.
* Control+win+Spazio: visualizza il tweet attuale.
* Control+win+c: copia negli appunti il tweet selezionato.
* Control+windows+a: Aggiungere un utente ad una lista.
* Control+shift+windows+a: rimuovi dalla lista.
* Control+Windows+Shift+freccia sù: vai al tweet precedente nella conversazione.
* Control+Windows+freccia giù: vai al tweet successivo nella conversazione.
* Control+Windows+Shift+M: Attivare o disattivare i suoni per il buffer attuale.
* Windows+Alt+M: abilita o disabilita tutti i suoni per TW Blue.
* Control+Windows+E: attiva o disattiva la lettura automatica dei tweet nel buffer attuale.
* Control+windows+-(trattino): ricerca in Twitter.
* Control+Windows+F4: Chiude il programma.

## Le liste {#listas}

Una delle caratteristiche più interessanti di Twitter sono le liste, un modo comodo per rimanere aggiornati su alcuni argomenti specifici senza dover leggere tutti i tweet degli utenti che segui. Con una lista di Twitter vedrete soltanto i tweet dei suoi membri. Simile alla linea temporale specifica, ma può includere più utenti.

In TW blue Abbiamo cominciato a dare supporto per questa funzionalità. Lo sviluppo procede man mano, è però possibile sfruttare questa caratteristica. Spieghiamo passo passo come aprire una lista con TW Blue.

* Dal menù Aplicazione seleziona Gestione Liste.
* nel gestore Liste vengono visualizzate tutte le liste a cui sei iscritto, a partire da quelle che hai creato. Se non si vede alcun elenco in questa finestra di dialogo, significa che non ne hai creato, o non sei membro di nessuna lista.
* Vengono visualizzati alcuni pulsanti che non hanno bisogno di spiegazione: Crea nuova lista, Modifica, Elimina, apri in un buffer (apre un nuovo buffer in modo che TW Blue aggiorna l'elenco dei tweet allo stesso modo delle linee temporali).

Appena creata una nuova lista, non si dovrebbe aprire in un buffer. Non immediatamente, In quanto al principio non ci sono membri e quindi non verranno caricati tweet. Si consiglia di aggiungere persone alla lista, così come spiegato:

* Creata la lista e chiuso il Gestore Liste, cerca l'utente che desideri aggiungere alla tua lista.
* Una volta trovato, premi Control+Win+A, o dal menù Utente selezionare l'opzione "Aggiungi alla Lista".
* Appare una finestra che ti permette di selezionare l'utente da aggiungere, assicurati che quello selezionato sia quello che hai scelto, o modìficalo se necessario e premi Invio per accettare;
* Si apre un'altra finestra di dialogo dove son visualizzate tutte le tue liste. Seleziona quella al quale vuoi aggiungere l'utente e premi il pulsante Aggiungi;
* Per rimuovere un utente da una lista, si ripete lo stesso procedimento, premendo però Control+Win+Shift+A, o selezionando "Rimuovi dalla lista", e nella finestra delle liste premere "Rimuovi".

## Riportare un errore {#reportar}

Nota: Se si sta utilizzando il programma è anche possibile segnalare un errore attraverso l'apposito menu Aiuto. Questo processo richiede la semplice compilazione di due campi di editazione. Per chi vuole segnalare via Web oltre al sistema di segnalazione integrato a TW Blue, è disponibile una pagina dedicata.

Tutte le cose del mondo (sí sì, inclusi i software) son molto lontani dalla perfezione, è facile incontrare quindi imprevisti che causano errori. La buona intezione è sempre quella di migliorare, sentiti libero (o meglio, sarebbe ottimo se lo facessi) di riportare eventuali errori che incontri nel programma in modo da poterli correggere.

Per entrare nella pagina riservata alla segnalazione errori, vai a [questo link.](http://twblue.com.mx/errores/bug_report_page.php) 

La pagina è in spagnolo e contiene un form da compilare. I campi contrassegnati da un * (asterisco) sono obbligatori, più campi vengono compilati meglio si può valutare l'errore.

Grazie per la partecipazione riportando errori e provando le nuove funzioni di TW Blue.

## Contatti: {#contacto}

Se ciò che viene presentato in questo documento non è sufficiente, se vuoi collaborare in altri modi, o se volete semplicemente tenervi in contatto con chi sviluppa questa applicazione segui [@tw_blue2](https://twitter.com/tw_blue2) oppure [@manuelcortez00.](https://twitter.com/manuelcortez00) Potete anche visitare il nostro [sito Web.](http://twblue.com.mx)

---

Copyright © 2013-2014. Manuel Cortéz.
