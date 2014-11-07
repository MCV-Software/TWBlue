% Documentation pour TW Blue 0.42

# Version 0.42 (alpha)

# Attention !

Vous lisez un document généré pour une application qui est en cours de développement. Le but de ce manuel est de clarifier quelques détails sur le fonctionnement du programme. Veuillez noter que pour être activement développé, le logiciel peut modifier une partie de cette documentation dans un avenir relativement proche, il est donc conseillé de jeter un œil de temps à autre pour ne pas perdre toute nouvelle information.

Si vous voulez voir ce qui a changé par rapport à la version précédente, [lire la liste des nouveautés ici.](changes.html)

# TW Blue

TW Blue est une application pour utiliser Twitter de manière simple, rapide et éviter dans la mesure des possibilités, consommer trop de ressources de l'ordinateur en cours d'utilisation. Avec l'application TW Blue, vous pouvez effectuer des actions sur Twitter tels que:

* Écrire, répondre, retwitter et supprimer les tweets;
* Marquer comme favori, supprimer des favoris un tweet;
* Envoyer et supprimer des messages directs (DM);
* Voir ceux qui vous suivent et ceux que vous suivez;
* Suivre, ne pas suivre, signaler comme spam ou bloquer un utilisateur;
* Ouvrir une chronologie pour un utilisateur spécifique, ce qui permet de lire tous les tweets d'un utilisateur dans une seule liste;
* Ouvrir les URLs s'il sont présente dans un tweet ou dans un message direct;
* Lire plusieurs types de fichiers ou adresses qui contiennent de l'audio;
* Et plus encore!.

# Table des matières

Pour utiliser une application comme TW Blue qui permet de gérer un compte Twitter, vous devez d'abord être inscrit dans ce réseau social. Cette documentation n'est pas destinée à expliquer la procédure pour ce faire. Nous partirons du principe où vous avez déjà un compte avec son respectifs nom d'utilisateur et mot de passe. La documentation couvrira ces sections.

* [Autoriser l'application](#autoriser)
* [L'interface du programme](#interface)
* [Commandes](#commandes)
* [L'Interface Graphique (GUI)](#gui)
 * [Boutons de l'application](#boutons)
* [La barre de Menus](#menus)
* [Menu Aplication](#app)
* [Menu Tweet](#tweet)
* [Menu Utilisateur](#utilisateur)
* [Menu Tampon](#tampon)
* [Menu Aide](#aide)
* [L'interface invisible](#interface_invisible)
* [Raccourcis Clavier pour l'interface graphique](#raccourcis)
* [Raccourcis Clavier pour l'interface invisible](#raccourcis_invisibles)
* [Listes](#listes)
* [Signaler une erreur depuis le Web](#signaler)
* [Contact](#contact)

## Autoriser l'application {#autoriser}

Tout d'abord, la première chose que vous devez faire est d'autoriser le programme afin que celui-ci puisse accéder à votre compte Twitter, et depuis il va réaliser se que vous lui demandez. Le processus d'autorisation est assez simple, et n'aura à aucun moment accès à vos données, telles que le nom d'utilisateur et mot de passe. Pour autoriser l'application, il suffit d'ouvrir le fichier principal du programme, appelé TW Blue.exe (dans certains PC, seulement se montre comme TW Blue).

Lors de l'exécution, Si vous n'avez pas déjà configuré le programme, il s'affichera une boîte de dialogue où il dit que vous serez amené à Twitter afin d'autoriser l'application dès que vous appuyez sur le bouton "OK". Pour commencer avec le processus d'autorisation il faut appuyez sur le seule bouton disponible de cette boîte de dialogue.

Ensuite, votre navigateur par défaut s'ouvre sur la page Twitter vous demandant d'autoriser l'application. Entrée votre nom d'utilisateur et mot de passe si vous n'êtes pas encore connecté, puis vous recherchez le bouton autoriser et appuyez sur celui-ci.

Lisez les instructions que vous obtiendrez si le processus est réussi. En résumé, vous recevrez un code numérique à plusieurs chiffres, que vous devez coller sur un champ d'édition ouvert par l'application sur une autre fenêtre.

Collez le code de vérification et appuyez sur la touche Entrée.

Si tout va bien, l'application commence à jouer un groupe de sons, pour vous signaler que vous mettez à jour vos données.

Lorsque le processus est terminé, le programme jouera un autre son, et le lecteur d'écran dira"prêt".

## L'interface du programme {#interface}

La meilleure façon de décrire l'interface graphique de l'application est la d'une fenêtre avec une barre de menus avec cinq menus (application, tweet, utilisateur, tampon et aide) ; une liste avec plusieurs éléments et, dans la plupart des cas, trois boutons: Tweet, Retweet et Répondre. Les actions disponibles pour chaque élément sont décrits ci-dessous.

Les éléments qui sont dans les listes peuvent être des tweets, des messages directs ou des utilisateurs. TW Blue crée différents onglets pour chaque liste, puis ces éléments peuvent être des Tweets envoyés, des Tweets reçus dans la chronologie principal, favoris ou les messages directs et chaque onglet contient un seul type de Tweet. Ces onglets sont appelés des listes ou des tampons.

Pour basculer entre les listes il faut Appuyez sur Contrôle+Tab pour aller en avant, et Contrôle+Maj+Tab pour revenir en arrière. A tout moment les lecteurs d'écran annoncera la liste vers la quelle se obtiendera le focus de l'application. Ici sont les listes de base de TW Blue, qui se présente si vous utiliser la configuration par défaut.

* Principal: Ici vont tous les tweets qui s'affichent dans la chronologie principal. Ceci sont les tweets provenant des utilisateurs que vous suivez.
* Mentions: Si un utilisateur (vous suit ou ne vous suit pas) vous mentionne sur Twitter, apparaîtra dans cette liste.
* Messages directs: Ici sont les messages directes (privés) que vous pouvez échanger uniquement avec les utilisateurs que vous suivez et qui vous suivent. Cette liste affiche uniquement les messages reçus.
* Envoyés: Dans cette liste il s'affiche tous les Tweets et les messages directs qui ont été envoyés depuis votre compte.
* Favoris: ici, vous pourrez voir tous les tweets que vous avez marqués comme favoris.
* Followers: Lorsque les utilisateurs suivent votre compte, vous les verrez dans cette liste, ainsi que quelques informations sur leur compte Twitter.
* Following: Même que pour la liste précédente, mais ce sont les utilisateurs que vous suivez.
* Événements: Un événement dans TW Blue est "quelque chose" qui se passe sur Twitter. Dans la chronologie des événements, vous pourrez voir enregistré les événements les plus courants (par exemple. Ont vous a commencé à suivre, ont vous a marqués ou supprimé un tweet des favoris, vous vous êtes abonné à une liste). Ils sont comme des petites notifications qui envoie Twitter et TW Blue l'organise dans une liste afin que vous ne manquez pas ce qui s'est passé avec votre compte.
* Chronologie d'un utilisateur: ce sont des listes, que vous pouvez créer. C'est une liste qui contient uniquement les tweets d'un utilisateur spécifique. Ils sont utilisés de sorte que vous pouvez voir les tweets réalisé par une seule personne et vous ne voulez pas regarder partout dans votre chronologie. Vous pouvez en créer autant que vous le souhaitez.
* Listes: Une liste ressemble à une chronologie, mais constitué des tweets de chaque utilisateur qui en fait partie. La liste est actuellement une fonctionnalité expérimentale de TW Blue. Si vous décidez de l'utiliser, veuillez S'il vous plaît nous contactez et nous signalez tout problème que vous rencontrez.
* Rechercher: Un tampon de recherche contient les résultats d'une recherche faites dans TW Blue. Les recherches peuvent être par tweets, au dans le cas que vous recherchez un terme dans le contenus des tweets pertinent de Twitter, ou par utilisateurs, où les résultats sont des noms d'utilisateurs de Twitter.
* Favoris d'un utilisateur: Il est possible de demander à TW Blue de vous afficher les tweets qu'un utilisateur a marqué comme favori.

Remarque: Uniquement pour cette version de TW Blue, la liste des following et followers peuvent mettre à jour jusq'à 400, ou autour de 400. Dans la prochaine version, nous proposons une méthode pour voir les following et followers pour éviter les erreurs causées par l'utilisation de l'API de Twitter, très fréquente entre les personnes avec plus de 600 following ou followers.

Veuillez noter que la configuration par défaut permet seulement d'afficher les 200 derniers tweets pour les listes principal, mentions, messages directs et chronologie d'un utilisateur. Vous pouvez le modifier dans la boîte de dialogue de configuration dans le menu Application sous Préférences. Pour la list envoyés il s'affichera les 200 derniers tweets et les 200 messages directs. Dans les versions futures ont vous permettra de modifier ce paramètre.

S'il y a une URL dans un tweet, TW Blue va essayer de l'ouvrir lorsque vous appuyez sur entrée sur celle-ci. S'il en existe plusieurs, il vous montrera une liste avec toutes les URLs afin que vous choisissez cellci que vous voulez ouvrir. Si vous êtes sur la boîte de dialogue de la liste des following ou followers, lorsque vous appuyez sur la touche entrée il s'affichera une fenêtre avec les détails de l'utilisateur sélectionné.

Si vous appuyez sur Contrôle+Entrée, TW Blue va lire un audio si disponible à partir du tweet ayants le focus système, tant qu'il existe une URL. Si le tweet a le hashtag #audio, vous entendrez un son lorsque vous passer sur lui en vous faisant alerter que se tweet contient un audio et vous pouvez essayer de le jouer. Toutefois, dans un tweet il peut manquer le hashtag mais TW Blue sera toujours capable de le jouer, tant qu'il comporte une URL avec l'audio.

## Commandes {#commandes}

À partir de la version 0.36, il existe un support pour une interface qui ne nécessite pas d'une fenêtre visible. Celle-ci peut être activé en appuyant sur Contrôle+m, ou en sélectionnant dans le menu Application l'option "Masquer la fenêtre". Cette interface est gérée complètement avec des raccourcis clavier. Ces raccourcis sont différentes de celles utilisées par l'interface graphique. chaqu'une d'entre elles peuvent utiliser uniquement les raccourcis qui lui corresponde, ce qui signifie que vous ne pourrai pas utiliser les raccourcis de l'interface invisible si vous avez activé l'interface graphique. Dans cette section il vous sera détailler tantôt l'interface graphique comme l'interface invisible.

### L'Interface Graphique (GUI) {#gui}

Voici ci-dessous une liste divisée en deux parties. D'une part, les boutons qui sont accessibles en appuyant sur Tab ou Maj + tab dans l'interface du programme et d'autre part, les différents éléments qui existent dans la barre de menus.

#### Boutons de l'application {#boutons}

* Tweet: Ce bouton ouvre la boîte de dialogue pour écrire un tweet. Le message ne doit pas dépasser au-delà de 140 caractères. Lorsque vous écrivez le caractère numéro 141, un son sera joués pour vous avertir que vous avez dépassé la limite permise par Twitter. Vous pouvez réduire ou élargir une URL si celle-ci est incluse dans votre tweet afin de gagner plus d'espace, afin que vous puissiez continuer à écrire. Pour cela, ils existes ces boutons avec ces noms. Appuyez sur entrée pour envoyer le tweet. Si tout s'est bien passé, le message sera envoyé et vous entendrez un son de confirmation. Dans le cas contraire, le lecteur d'écran indiquera un message d'erreur en anglais décrivant le problème.
* Retweet: Ce bouton s'occupe de retwitter le tweet que vous lisez. En appuyant sur ce bouton une fenêtre s'ouvre et ont vous demandera si Vous souhaitez ajouter un commentaire à ce tweet original (mentionner) ou simplement l'envoyer comme il a été écrit sans ajouter quoi que ce soit d'autre.
* Répondre: Lorsque vous visualiser un Tweet, vous pouvez répondre à l'utilisateur qui l'a écrit en cliquant sur ce bouton. Il s'ouvre la même boîte de dialogue que pour le bouton Tweet, mais avec le nom de l'utilisateur (par exemple: @utilisateur), donc il suffit d'écrire le message que vous souhaitez répondre. Si dans le tweet il y a plus d'un utilisateur mentionné, appuyez sur Maj+Tab et cliquez sur le bouton "Mentionner à tous". Lorsque vous êtes dans la liste des following ou followers, ce bouton s'appellera "Mention" à la place.
* Message direct: Exactement pareil que pour envoyer un tweet, mais c'es un message privé qui verra seulement l'utilisateur auquel vous l'envoyez. Appuyez sur Maj+Tab pour voir le destinataire de votre message. Si dans le tweet où vous étiez pour envoyer le message,il y a plus d'un utilisateur mentionné, vous pouvez naviguer avec les flèches haut et bas pour sélectionner un destinataire différent, ou écrivez manuellement le nom de l'utilisateur (sans le signe arobase).

Veuillez noter que les boutons s'affichent selon les actions qui peuvent être effectuées dans la liste où que vous soyez. Par exemple, dans la chronologie principal, mentions, envoyés, favoris et la chronologie de l'utilisateur vous verrez quatre boutons ; alors que dans la liste des messages directs seulement sera disponible le bouton "Message Direct" et "Tweet", et dans les listes following et followers, s'affichera le bouton "Tweet" et celle du "Message direct" à côté de "Mention".

#### La barre de Menus {#menus}

En haut de la fenêtre du programme, vous trouverez une barre de menus qui a les mêmes fonctions et un peu plus, d'où vous pouvez exécuter plusieurs actions dont celles mentionnées ci-dessus. La barre de menu est accessibles en appuyant sur la touche ALT, et actuellement compte avec quatre menus pour différentes actions: Application, Tweet, Utilisateur et Aide. Ci-dessous, nous décrivons les actions pour chaque menu.

##### Menu Application {#app}

* Mettre à jour le profil: Il ouvre une boîte de dialogue où vous pouvez mettre à jour une partie de vos informations sur Twitter. Nom, Localisation, URL et Description. Si vous avez déjà un de ces champs dans le profil ils sont automatiquement préremplis avec les informations existantes dans votre configuration personnelle sur Twitter. Vous pouvez également charger une photo à votre profil.
* Masquer la fenêtre: Il va désactiver l'interface graphique. Lire le paragraphe sur l'interface invisible pour plus de détails sur cette fonctionnalité.
* Rechercher: Affiche une boîte de dialogue où vous pouvez rechercher par tweets ou par utilisateurs sur Twitter.
* Gestionnaire de listes: Afin d'utiliser les listes de Twitter, vous devez d'abord les créer. Cette boîte de dialogue vous permet de voir vos listes, les modifiez, les créez, les supprimez. Éventuellement les listes seront afficher dans les tampons comme vous le feriez avec les chronologies.
* Tutoriel de sons: Ouvre une boîte de dialogue où vous verrez une liste avec les différents sons de TW blue, ainsi vous pouvez les apprendre afin de vous aider à vous familiariser avec eux et vous faciliter l'utilisation de TW Blue.
* Préférences: Ouvre une boîte de dialogue de configuration où vous pouvez contrôler certains aspects du programme. Les options ne nécessitent pas d'explication.
* Sortir: Ouvre une boîte de dialogue pour confirmer si vous souhaitez fermer le programme. Si la réponse est oui, l'application s'arrête.

##### Menu Tweet {#tweet}

* Les premiers éléments du menu sont tweet, répondre et retweet, qui correspondent aux boutons du même nom. 
* Ajouter aux favoris: marque le tweet que vous visualisez comme favori.
* Supprimer des favoris: Supprime un tweet de vos favoris. Cela ne signifie pas qui sont supprimés à partir de Twitter, mais n'apparaîtra plus dans votre liste de favoris.
* Voirr tweet: Il ouvre une boîte de dialogue où vous pouvez voir le tweet, message direct, folowing ou follower sur le quelle se trouve le focus de l'application. Vous pouvez lire le texte avec les flèches. C'est la même boîte de dialogue utilisée pour écrire des tweets.
* Supprimer Tweet: Supprime le tweet ou message direct sur le quelle vous êtes, il va être supprimer définitivement de Twitter et il va être supprimer de vos listes. Veuillez noter que dans le cas des Tweets, Twitter permet uniquement de supprimer les tweets que vous avez écrit vous-même.

##### Menu Utilisateur {#utilisateur}

Veuillez noter que les six premier éléments de ce menu ouvrent la même boîte de dialogue. Cette boîte de dialogue comporte une zone d'édition où vous pouvez sélectionner l'utilisateur sur lequel vous voulez agir, bien en utilisant les flèches haut et bas ou en écrivant vous-même le nom. Puis ensuite, vous trouverez un groupe de boutons radio pour suivre, ne pas suivre, muet, désactiver muet, signaler comme spam et bloquer. Si vous choisissez l'élément Suivre dans le menu, le bouton radio Suivre dans la boîte de dialogue sera coché, et il en va de même pour les bboutons radio Ne pas suivre, Signaler comme spam et Bloquer. Appuyez sur le bouton OK pour que le programme essaye d'exécuter l'action. Si le programme ne réussit pas, vous entendrez le message d'erreur en anglais.

Les autres éléments du menu sont décrits ci-dessous:

* Message direct: La même action que le bouton.
* Ajouter à la liste: Afin de voir les tweets d'un utilisateur dans vos listes, vous devez les ajouter tout d'abord. Cette option ouvrira une boîte de dialogue où vous pouvez sélectionner l'utilisateur que vous souhaitez ajouter, ensuite il s'ouvre une autre fenêtre où vous pouvez sélectionner la liste à laquelle vous souhaitez ajouter cet utilisateur. Une fois cela fait, la liste contiendra un nouveau utilisateur et vous verrez ces tweets.
* Voir le profil de l'utilisateur: Il ouvre une boîte de dialogue qui vous permet de sélectionner l'utilisateur auquel vous souhaitez voir le profil.
* Chronologie: Il ouvre une boîte de dialogue où vous pouvez sélectionner l'utilisateur pour lequel la chronologie sera créée. En appuyant sur entrée, il sera créé. Si vous faite une chronologie pour un utilisateur qui n'a aucun Tweets, le programme échouera. Si vous créez une chronologie qui existe déjà le programme vous avertira et il ne vous permettra pas de la créer à nouveau.
* Voir les favoris: Il s'ouvre un tampon où vous pouvez voir quels tweets ont été marquer comme favori par un utilisateur spécifique.

##### Menu Tampon {#tampon}

* Muet: Rend complètement muet le tampon, afin que vous n'entendrez aucun son lorsque les nouveaux tweets arrivent.
* Lecture automatique des tweets pour ce tampon: Cette option active ou désactive la lecture automatique des Tweets. Si cell-ci est activé, le lecteur d'écran ou la voix Sapi5 (si celle-ci est activé) lit automatiquement les nouveau tweet quand ils arrivent au tampon sélectionné. 
* Effacer le tampon: Il va vider tous Les éléments afficher dans ce tampon.
* Supprimer le tampon: Efface la liste sur laquelle vous êtes actuellement focalisé.

##### Menu Aide {#aide}

* Documentation: Ouvre ce fichier, où vous pouvez lire quelques concepts intéressants du programme.
* Quoi de neuf dans cette version ?: Ouvre un document avec la liste des changements de la version actuelle, jusqu'à la première version existante.
* Vérifier les mises à jour: Chaque fois que vous ouvrez le programme il recherche automatiquement les nouvelles versions. S'il y a une, il vous demandera si vous voulez la télécharger ; si vous acceptez, TW Blue va télécharger la nouvelle version puis va l'installer et il vous demandera de redémarrer le programme ; (c'est quelque chose qui fait automatiquement). Cette option vérifie les nouvelles mises à jour sans avoir à redémarrer l'application.
* Site Web de TW Blue: Accédez à notre [page d'accueil](http://twblue.com.mx) où vous pouvez trouver toutes les informations pertinentes et téléchargements pour TW Blue, et devenir une partie de la communauté.
* Signaler une erreur: Ouvre une boîte de dialogue pour signaler une erreur en remplissant deux champs d'édition. Le titre et une brève description de ce qui s'est passé. En appuyant sur le bouton "Envoyer le rapport" le rapport d'erreur sera envoyé. Si l'opération ne réussit pas, le programme affichera un message d'avertissement.
* A propos de TW Blue: Affiche les informations de version et les crédits du programme.

### Interface invisible {#interface_invisible}

Si vous appuyez sur Contrôle+M, ou si dans le menu Application vous sélectionnez "Masquer la fenêtre", vous êtes entrain d'activez une interface qui ne peut pas être utilisée de la manière habituelle, parce qu'il est invisible.

Chaque action sur l'interface invisible se fait grâce à des raccourcis clavier, même pour parcourir les listes. Finalement, on peut ouvrir les boîtes de dialogue et ceux-ci seront visibles, mais pas la fenêtre principale de l'application. Lire la section sur les raccourcis clavier de l'interface invisible pour savoir quels sont ceux que vous pouvez utiliser actuellement.

### Raccourcis clavier pour l'interface graphique {#raccourcis}

Au lieu d'utiliser les menus et les boutons, la plupart des actions peuvent être effectuées en appuyant sur une combinaison de touches. Ceux disponibles à l'heure actuelle sont décrits ci-dessous:

* Entrée: Ouvrir une URL. S'il y a plus d'une, vous obtiendrez une liste qui vous permettra de choisir celle que vous voulez. Si vous êtes sur la liste des following ou followers, il affichera les détails de l'utilisateur sélectionné.
* Contrôle+Entrée: Lire un audio si disponible si dans le Tweet il y a une URL contenant de l'audio. 
* F5: Diminue de 5% le volume des sons. Ceci affecte les sons joués par le programme ainsi que l'audio que vous pouvez entendre à travers de lui.
* F6: Augmente de 5% le volume des sons de l'application.
* Contrôle+N: Ouvre la boîte de dialogue pour écrire un nouveau Tweet.
* Contrôle+M: Masque la fenêtre.
* Contrôle+Q: Ferme l'application.
* Contrôle+R: Ouvre la boîte de dialogue pour répondre un Tweet.
* Contrôle+Maj+R: Équivalent à l'action de Retweet.
* Contrôle+D: Envoyer un message direct.
* Contrôle+F: Marquer comme favori.
* Contrôle+Maj+F: Supprimer des favoris.
* Contrôle+Maj+V: Voir Tweet.
* Contrôle+S: Suivre un utilisateur.
* Contrôle+Maj+S: Ne pas suivre un utilisateur.
* Contrôle+K: Bloquer un utilisateur.
* Contrôle+Maj+K: Signaler comme spam.
* Contrôle+I: Ouvrir une chronologie d'un utilisateur.
* Contrôle+Maj+I: Supprimer une chronologie d'un utilisateur.
* Contrôle+p: Modifier le profil.
* Supprimer: Supprimer un tweet ou un message direct.
* Maj+supprimer: Vider le tampon en retirant tous les éléments. Cela ne les supprime pas de Twitter.

### Raccourcis clavier pour l'interface invisible {#raccourcis_invisibles}

Voici les raccourcis clavier que vous pouvez utiliser à partir de l'interface invisible. Veuillez noter que lorsque l'affichage de l'interface graphique est activé aucun d'entre eux peut être utilisé. Lorsque ont parle de "Windows", nous nous référons à la touche Windows de gauche.

* Contrôle+Windows+Flèche Haut: Parcourir la liste actuelle vers le haut.
* Contrôle+Windows+Flèche bas: Parcourir la liste actuelle vers le bas.
* Contrôle+Windows+Flèche Gauche: Aller à l'onglet précédent.
* Contrôle+Windows+Flèche Droite: Aller à l'onglet suivant.
* Contrôle+Windows+Origine: Aller au premier élément de la liste.
* Contrôle+Windows+Fin: Aller au dernier élément de la liste.
* Contrôle+Windows+Page Suivante: Sauter de 20 éléments vers le bas dans la liste actuelle.
* Contrôle+Windows+Page Précédente: Sauter de 20 éléments vers le haut dans la liste actuelle.
* Contrôle+Windows+Alt+Flèche Haut: Augmenter le volume de 5%.
* Contrôle+Windows+Alt+Flèche Bas: Diminuer le volume de 5%.
* Contrôle+Windows+Entrée: Ouvrir l'URL dans le tweet actuel, ou voir les détails d'un utilisateur si vous êtes dans la liste following ou follower.
* Contrôle+Windows+Alt+Entrée: Lire un audio si disponible.
* Contrôle+Windows+M: Affiche l'interface graphique, en désactivant l'interface invisible.
* Contrôle+Windows+N: Nouveau tweet.
* Contrôle+Windows+R: Répondre à un tweet.
* Contrôle+Windows+Maj+R: Retweet.
* Contrôle+Windows+D: Envoyer un message direct.
* Contrôle+Windows+Supprimer: Supprimer un tweet ou un message direct.
* Contrôle+Windows+Maj+Supprimer: Vider le tampon en retirant tous les éléments. Cela ne les supprime pas de Twitter.
* Windows+Alt+F: Marquer comme favori.
* Windows+Alt+Maj+F: Supprimer des favoris.
* Contrôle+Windows+S: Suivre un utilisateur.
* Contrôle+Windows+Maj+S: Ne pas suivre un utilisateur.
* Contrôle+Windows+Alt+N: Voir les détails d'un utilisateur.
* Contrôle+Windows+V: Voir le tweet dans une zone d'édition.
* Contrôle+Windows+I: Ouvrir une chronologie d'un utilisateur.
* Contrôle+Windows+Maj+I: Supprimer une chronologie d'un utilisateur.
* Alt+Windows+P: Modifier le profil.
* Contrôle+Windows+Espace: Voir le tweet actuel.
* Contrôle+Windows+c: Copier dans le Presse-papiers le tweet sélectionné.
* Contrôle+Windows+a: Ajouter un utilisateur à une liste.
* Contrôle+Maj+Windows+a: Supprimer l'utilisateur de la liste.
* Contrôle+Windows+Maj+M: Activer / désactiver les sons pour le tampon actuel.
* Contrôle+Windows+E: Activer ou désactiver la lecture automatique pour les tweets entrants dans le tampon actuel.
* Contrôle+Windows+Maj+Flèche Haut: Aller au tweet précédent dans la conversation.
* Contrôle+Windows+Maj+Flèche Bas: Aller au tweet suivant dans la conversation.
* Windows+Alt+M: Activer / désactiver tous les sons pour TW Blue.
* Contrôle+Windows+- (tiret): Rechercher sur Twitter.
* Contrôle+Windows+F4: Sortir du programme.

## Listes {#listes}

Une des caractéristiques plus intéressantes de Twitter sont les listes, car ils sont un moyen pour rester à jour sans avoir à lire les tweets de tous les utilisateurs que vous suivez. Avec une liste de Twitter seulement vous verrez les tweets de ces membres (ceux qui sont sur la liste). Il est similaire à une chronologie, mais pour beaucoup plus d'utilisateurs.

Dans TW blue Nous avons commencé à fournir un support pour cette fonctionnalité. Pour le moment nous allons lentement, mais il est possible d'utiliser cette fonction. Ont va vous expliquer étape par étape comment faire pour ouvrir une liste avec TW Blue.

* Tout d'abord, vous devrez aller dans le menu Application, sélectionnez "Gestionnaire de listes".
* Dans la boîte de dialogue "Gestionnaire de listes", vous verrez toutes les listes auxquelles vous êtes inscrit, à commencer par ceux que vous avez créée. Si vous ne voyez aucune liste dans cette boîte de dialogue, cela signifie que vous n'avez pas créé ou que vous n'êtes pas un membre d'une liste. C'est bien.
* Vous verrez un groupe de bouton: "Créer une nouvelle liste", "Modifier", "Effacer "et "Ouvrir dans un tampon". Le dernier d'entre eux est peut-être un peu moins explicite, c'est-à-dire il ouvrira la liste dans un nouveau tampon pour que TW Blue actualise la liste des Tweets de la même manière comme pour une chronologie.

Une fois que vous avez créé une nouvelle liste, la prochaine étape sera d'ajouter des utilisateurs à cette liste. Si vous deviez ouvrir dès maintenant une liste dans un tampon, elle sera vide et aucun tweets ne seraient présent dans cette liste. C'est pour cela que vous ne devez pas ouvrir celle-ci dans un tampon. En tout cas pas immédiatement, parce que vous n'avez pas aucun membre dans cette liste et cela signifie que lorsque les tweets sont chargés pour commencer à actualiser la liste vous ne verrez rien. Il est recommandé tout d'abord d'ajouter des utilisateurs à la liste, donc pour cela procédez comme suit:

* Lorsque vous avez fermé la boîte de dialogue "Gestionnaire de listes", et que vous naviguez entre les Tweets des utilisateurs, rechercher l'utilisateur auquel vous souhaitez ajouter à la liste.
* Une fois trouvé, cliquez sur le raccourci Windows+Contrôle+A ; ou allez dans le menu Utilisateur et sélectionnez l'option "Ajouter à la liste".
* La prochaine chose que vous verrez est une boîte de dialogue qui vous permet de sélectionner l'utilisateur, assurez-vous que c'est l'utilisateur qui est par défaut et si c'est celui-ci que vous voulez, ou changez si nécessaire. Le nom de l'utilisateur contenant le tweet que vous venez de sélectionner devrait déjà être dans la zone. Il suffit de confirmer qu'il est correcte et appuyez sur le bouton "OK".
* Une autre boîte de dialogue s'affiche, mais ici sont toutes vos listes. Sélectionner une liste. Flèche sur celle que vous voulez et appuyez sur le bouton "Ajouter".
* Pour supprimer un utilisateur d'une liste répètez la même procédure, mais appuyez sur Contrôle+Windows+Maj+A ; ou allez dans le menu Utilisateur et sélectionnez l'option "Supprimer de la liste", et, dans la boîte de dialogue qui apparaît, Choisissez la liste dont vous souhaitez supprimer l'utilisateur sélectionné et appuyez sur le bouton "Effacer".

## Signaler une erreur depuis le Web {#signaler}

Remarque: Si vous utilisez également le programme vous pouvez signaler une erreur depuis le même, en utilisant l'option dans le menu Aide. Cette procédure seulement vous demande de remplir les deux zones d'édition, et il gère le reste. Ces étapes sont rédigés pour ceux qui ne peut pas ouvrir le programme, ne l'ont pas en cours d'utilisation actuellement ou tout simplement il souhaite le signaler depuis le Web au lieu du système intégré de rapports d'erreurs.

Les choses de ce monde (oui, y compris le logiciel) sont loin de être parfait, si souvent, que vous rencontrerez des erreurs inattendues dans l'application. Mais l'intention est toujours d'améliorer, vous êtes libre (il serait formidable si vous le fassiez) de signaler les erreurs que vous vous allez y trouver dans le programme afin qu'ils puissent être réviser et éventuellement être corriger.

Pour accéder à la page Web qui est en espagnol réservée au rapport d'incidents, suivez [Ce lien.](http://twblue.com.mx/errores/bug_report_page.php) C'est une page Web qui est en espagnol avec un formulaire où vous devrez remplir plusieurs champs. Seulement trois d'entre eux sont vraiment obligatoires (ceux qui sont marqué d'un astérisque), mais entre plus de champs que vous pourriez remplir, ce sera mieux.

A titre d'information!:  J'ai fait la traduction de la page en espagnol vers le français contenant les différents champs du formulaire et ce que vous devez entrer, vous le trouverez ci-dessous. Les champs marqués d'un * (astérisque) sont obligatoire!.

Voici les différents champs du formulaire et ce que vous devez entrer dans chaqu'un d'entre eux. N'oubliez pas que seulement les champs marqués d'un astérisque (*) sont obligatoires.

* Catégorie: Cette zone de liste déroulante permet de choisir à quelle catégorie est assigner l'erreur. Il peut être dans la catégorie Générale, si c'est une erreur du programme, ou de documentation, si vous avez trouvé une erreur dans ce fichier ou dans la liste des changements. Ce champ est obligatoire.
* Reproductibilité: Ici, vous devez indiquer combien il est facile ou il est difficile de reproduire l'erreur. Les options disponibles sont Inconnus, Non reproductibles, Pas essayé (par défaut), aléatoire, parfois ou toujours. Selon la question de savoir si vous pouvez reproduire l'erreur ou non, vous devez choisir le plus près à votre situation. Si vous faites une demande de fonctionnalité, ce champ n'est pas pertinent.
* Gravité: Ici vous choisissez combien elle affecte le programme. Les options disponibles sont fonctionnalités (choisissez cette option pour une demande de fonctionnalité), Trivial, Texte, Réglage, Mineur, Majeur, Incident ou Blocage. Remarquez que les options augmentent de niveau. Choisissez celui qui correspond le mieux a la situation. Si vous ne savez pas lequel choisir vous pouvez le laisser tel qu'il est.
* Priorité: Dans cette zone de liste déroulante il faut choisir en fonction de l'importance de l'erreur ou fonctionnalité demandée. Les options disponibles sont Aucun, Faible, Normale, Haute, Urgent et Immédiat.
* Sélectionner Profil: ici vous pouvez choisir la configuration d'architecture (32 ou 64 bits), et le système d'exploitation (Windows 7 pour l'instant). Si non, vous pouvez remplir les trois champs d'édition qui se trouvent dans le tableau ci-dessous avec vos informations spécifiques.
* Version du produit: Choisissez la version du programme que vous utilisez pour être en mesure de savoir où l'erreur a été générée. Dans cette zone de liste déroulante vous aurez la liste des versions dans l'ordre. Bien qu'il n'est pas obligatoire, cela aiderait beaucoup à résoudre plus rapidement l'erreur.
* Résumé: Un titre pour l'erreur, expliquant en quelques mots En quoi consiste le problème. C'est un champ d'édition obligatoire.
* Description: Ce champ est obligatoire Il vous demande de décrire plus en détail ce qui s'est passé avec le programme.
* Étapes pour reproduire: Ce champ est utilisé si vous savez comment l'application a pu générer l'erreur. Il n'est pas nécessaire, mais cela aiderait beaucoup de savoir comment le programme arrive à l'erreur afin de mieux le traquer.
* Information supplémentaire: Si vous avez un commentaire ou une remarque à ajouter, il peut aller ici. Il n'est pas obligatoire. 
* Charger un fichier: Ici vous pouvez charger le fichier TW Blue.exe.log qui a été créé contenant l'erreur génèré par le programme. Il n'est pas obligatoire.
* Visibilité: Choisissez si vous voulez que l'erreur soit public ou soit privé. Par défaut il est public, et il est recommandé de le garder de cette façon.
* Envoyer le rapport: Appuyez sur le bouton figurant sur la page pour envoyer le rapport d'erreur et attendre que celui-ci soit pris en charge.

Merci beaucoup pour votre participation à signaler des erreurs et d'essayer de nouvelles fonctionnalités.

## Contact {#contact}

Si ce qui est exposé dans le présent document n'est pas suffisant, si vous voulez contribuer d'une autre manière, ou si vous voulez tout simplement entrer en contact avec le développeur de l'applications, suivez le compte Twitter, [@tw_blue2](https://twitter.com/tw_blue2) ou [@manuelcortez00.](https://twitter.com/manuelcortez00) Vous pouvez également visiter notre [Site Web à](http://twblue.com.mx)

---
Copyright © 2013-2014. Manuel Cortéz.