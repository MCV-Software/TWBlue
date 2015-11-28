% Liste des Changements

#Attention ! 

Avant de poursuivre l'essai du programme, il est considéré que c'est une version de développement. Plus précisément, la version 0.42. Cela signifie qu'il n'est pas seulement possible de trouver des erreurs, mais que vous les trouverez. L'idée est de signaler le plus  d'erreurs possibles afin qu'ils puisse être résolus pour les prochaines alphas.

Voici la liste des changements dans le programme. Si vous voulez lire comment l'utiliser, [voir ce document.](manual.html) Si vous voyez un lien avec un signe dièse (#) et un code qui commence par plusieurs numéro, vous voyez une erreur qui a été  signalé dans le Système de suivi d'incidences. N'hésitez pas à publier vos propres erreurs et demandes d'améliorations et nouvelles fonctionnalités à travers de cet outils, disponible dans le menu Aide de TW Blue.

## Changements ajouter dans cette nouvelle version

* Correction d'une erreur qu'elle ne permettait pas d'afficher les listes avec des accents ou des caractères spéciaux dans un tampon.
* Maintenant TW blue ne devrait pas actualiser les Tweets soudainement.
* Maintenant TW blue supporte l'option "muet" de Twitter. Lorsque cette option est activée pour un utilisateur, vous ne pouvez pas voir  ces tweets ni ces mentions, mais vous le suivez toujours, et vous serez en mesure de être en contact avec lui à travers de message direct. Ceci est différent de la fonction Bloquer ou Ne pas suivre, avec cette option l'utilisateur sera pas au courant que vous avez activée l'option muet. sette option  se trouvent  dans la boîte de dialogue des actions utilisateur de  l'interface invisible, ou dans le menu  Utilisateur de  l'interface graphique.
* Un onglet "Audio" a été ajoutée dans la boîte de dialogue de configuration qui vous permet de sélectionner les périphériques d'entrée et de sortie, régler le volume et activer/ désactiver tous les sons pour TW Blue. D'autres options ont été déplacées  depuis l'onglet "Général" vers l'onglet "Audio".
* Le fichier de configuration a été repensé. La plupart des options devront être reconfigurés à nouveau.
* Vous pouvez maintenant désactiver SAPI5 afin qu'il n'intervienne pas s'il n'y a aucun lecteur d'écran supporté en cours d'exécution.
* Dans l'onglet Général, Vous pouvez modifier manuellement la langue. Tw Blue reqiere redémarré.
* Maintenant il y a une nouvelle boîte de dialogue où vous pouvez apprendre les différents sons de TW Blue.
* Il est possible maintenant de désactiver le son et notification d'un tampon. Le reste du client fonctionnera correctement. Appuyez sur Contrôle+Windows+Maj+m (interface invisible) ou le sélectionnez depuis le menu "Tampon" (interface visible) pour basculer entre cette fonctionnalité.
* Vous pouvez maintenant rechercher par utilisateur et par tweets. Les recherches de tweets sont sauvegardées dans la configuration, tandis que ceux des utilisateurs seront supprimer lors de la fermeture. Appuyez sur Ctrl+Windows+- (tiret) (interface invisible) ou le sélectionnez depuis le menu "Application" (interface visible).
* Vous pouvez ouvrir le tampon pour voir les favoris d'un utilisateur dans le menu "Utilisateur".
* Maintenant avec Contrôle+Windows+Maj+Flèche Haut / Bas (dans l'interface graphique) et Contrôle+Windows+Flèche Haut / Bas (dans l'interface invisible), vous pouvez aller au tweet précédent ou suivant dans la conversation. Pour que cela fonctionne les tweets de la conversation doivent être dans  la chronologie principale.
* Au cours d'un enregistrement audio pour ajouter, maintenant vous pouvez mettre en pause ou reprendre l'enregistrement pour sauter des parties qui peuvent générer un audio très long.
* Il est maintenant possible de charger de l'audio vers Dropbox. Pour configurer le service aller dans l'onglet "Services audio" dans la boîte de dialogue de Configuration.
* Maintenant que vous pouvez charger de l'audio vers Dropbox, dans la boîte de dialogue pour ajouter un audio vous pouvez sélectionner le service auquelle vous souhaitez charger.
* Maintenant il comprend une boîte de dialogue pour la correction orthographique pour les tweets ou messages. Les langues actuellement disponibles sont: Espagnol, Anglais, Portugais, Russe et Polonais. La langue sera sélectionnée automatiquement selon la configuration de TW Blue.
* Ajouter la lecture automatique des Tweets pour un tampon. L'activation de cette fonctionnalité peut faire que TW Blue lit automatiquement les tweets lors  de l'arrivée dans les tampons qui ont cette option activée. Appuyez sur Contrôle+Windows+e pour basculer entre cette fonction.
* Dans la boîte de dialogue de Configuration maintenant vous pouvez spécifiez si vous voulez que TW Blue démarre avec l'interface invisible.
* Les URLs s'affiche dans leur version originale. Uniquement les photos de Twitter ils apparaissent toujours comme réduites, et celles qui ont été réduites manuellement avant de les envoyer dans un tweet.

## Changements ajouter dans la version 0.40

* Vous pouvez changer entre les différents paquets de sons  utilisé par TW Blue et de créer vos propres sons. Chaque paquet doit être dans un  répertoire par séparé dans le dossier sounds. Pour modifier le  paquet de sons vous pouvez le sélectionner dans la boîte de dialogue de configuration.
* Les fichiers audio doivent être au format OGG.
* TW Blue doit être maintenant en mesure de fermer correctement.
* L'heure est écrit tenant en compte  le format 12 heures (AM /P M).
* L'heure est écrit d'accord au fuseau horaire que vous avez défini dans votre compte Twitter.
* Ajout de nouvelles traductions en Portugais, Polonais et Russe. Merci les gars !
* TW Blue supprime de la configuration la chronologie de l'utilisateur qui ont changé leur noms ou supprimer leurs comptes Twitter.
* Maintenant est gérés la grande majorité des événements dans Twitter avec le tampon des événements.
* Il est maintenant possible de voir le texte des événements avec Contrôle+Maj+V (GUI) ou Contrôle+Windows+V (interface invisible).
* Gestionnaire de listes: Vous pouvez créer, modifier, supprimer, afficher une liste  comme tampon dans TW Blue, ajouter et supprimer des membres d'une liste.
* Maintenant, si au démarrage de TW Blue il tente de charger une chronologie qui n'existe pas, automatiquement il la supprime de la configuration et il continue à charger normalement.
* Seuls seront chargées jusqu'à 400 following et followers pour éviter les problèmes avec l'API. Elle sera corrigée dans les versions futures.
* Pour le mode invisible, il inclus des raccourcis pour réentendre le tweet sur lequel vous êtes (Contrôle+Windows+espace) et pour copier le message dans le presse-papiers (Contrôle+Windows+c).

## Changements ajouter dans la version 0.38

* Correction d'une erreur qui empêchait en donnant l'ordre de fermer.
* Maintenant les tweets ne finissent pas par un point obligatoirement. Si le programme détecte que le tweet se termine par une lettre ou un chiffre, il va placez un point automatiquement. Si ce n'est pas le cas, il va laisser le texte tel qu'il est.
* Il est maintenant possible  de charger des images  aux tweets et réponses. Veuillez noter que la taille des images est mis en place par twitter.
* Pour se déplacer vers la gauche ou vers la droite en utilisant le mode invisible, maintenant il s'annonce uniquement des informations de la position   dans la liste d'éléments.
* TW Blue devrait maintenant fonctionner pour Windows XP au moment de la demande d'autorisation pour l'application.
* Ajouté une nouvelle option dans la boîte de dialogue de configuration qui vous permet de revenir à vos tampons. Cela signifie que vous pouvez choisir si vous voulez voir les tweets comme jusqu'à maintenant, ou que les plus nouveaux soit  placés  vers le haut  et les anciens vers le bas.
* Maintenant les photos peuvent être chargées aux profil de Twitter, disponible à partir de la boîte de dialogue Mettre à jour votre profil.
* Ajouté  un tampon d'événements, où ils sont stockés pour le moment quelques  événements qui se déroulent dans Twitter, comme suivre ou faire que quelqu'un vous suivent, marquer  un favori, que un de vos tweet  soit  marqué comme favoris, Etc. Vous pouvez activer et désactiver ce tampon de la boîte de dialogue de configuration.
* Maintenant, vous pouvez supprimer des chronologies déjà créé qui ne contiennent pas des tweets, et il ne sera  pas permit de créer des chronologies pour les utilisateurs sans tweets.
* L'interface de l'application est traduisible. Maintenant, n'importe quel utilisateur peut faire leurs propres traductions en différentes langues.

## Changements ajouter dans la version 0.36

* Les utilisateurs brésiliens pourront voir quelques messages en Portugais. (Usuários brasileiros poderão ver algumas mensagens em Português).
* Correction d'une erreur qui fait que quelques sons ils peuvent s'entendre et d'autres non. Maintenant, ils devraient  s'entendre tous.
* La réconnexion aussi a reçu une correction, parce que parfois, il s'effectué de façon incorrecte et il devait s'ouvrir à nouveau l'application.
* Maintenant TW Blue permet de supprimer uniquement les chronologies avec la commande correspondante. Avant il s'affichées la boîte de dialogue  peu importe dans quel tampon  vous  aviez été.
* Vous êtes en mesure à nouveau de  voir les détails des  utilisateurs avec la touche Entrée étant dans le tampon pour les following  ou followers.
* À partir de cette version, il n'y a pas de support pour les bases de données.
* Vous entendrez une notification vocale lorsque quelqu'un marque comme favori  un de vos tweets.
* Les following et followers  sont déjà mis à jour.
* lorsque vous suivez quelqu'un, il ne se produit        aucune erreur Si ne sont pas affichées les following. C'est la même chose avec les followers.
* Vous pouvez effacer un tampon en appuyant sur Maj+Supprimer dans la fenêtre visible, et Contrôle+Windows+Maj+Supprimer dans la fenêtre invisible. Ceci va vider tous les tweets dans le tampon courant.

## Changements ajouter dans la version 0.35

* Il existe un site Web officiel pour le programme, aller sur [twblue.com.mx.](http://twblue.com.mx) Dans cet espace, vous trouverez le système de suivi d'erreurs, le blog avec les dernières nouvelles, et la dernière version disponible.
* TW Blue il annonce lorsque vous êtes mentionné, et lorsque vous obtenez un message direct.
* Jaws il ne   dit pas le raccourci clavier  qui est appuyé dans le mode invisible. [#11](http://twblue.a12x.net/errores/view.php?id=11)
* Dans le mode invisible, les commandes Contrôle+Windows+Origine, Contrôle+Windows+Fin, Contrôle+Windows+Page Suivante et Contrôle+Windows+Page Précédente va aller vers le haut de la liste, vers la fin, 20 éléments vers le bas et 20 éléments vers le haut respectivement. [#10,](http://twblue.a12x.net/errores/view.php?id=10) [#21,](http://twblue.a12x.net/errores/view.php?id=21) [#22](http://twblue.a12x.net/errores/view.php?id=22) 
* Maintenant vous pouvez lire l'audios d'Audiobook.
* Maintenant, le flux doit être connecté une fois que la machine revient d'une suspension.
* Il est possible d'enregistrer de l'audio ou charger fichiers sur SndUp.net. Si vous êtes inscrit  dans cette page, vous pouvez mettre dans la configuration votre API Key pour que les fichiers se charge sur votre nom. Vous pouvez charger des fichiers Wav, OGG et MP3. Les fichiers wav ils seront récodifier en OGG.
* Si vous n'utilisez  aucun lecteur d'écran, quelques actions de TW blue utilisent la synthèse vocale SAPI5.
* Il existe une version pour les architectures de 64 Bits. Merci à [@jmdaweb](https://twitter.com/jmdaweb) pour prendre le travail de faire fonctionner l'application dans cette architecture et la préparez pour sa distribution.
* Changement dans les sons du client. Merci à [@guilevi_es](https://twitter.com/guilevi_es) pour la collaboration avec le paquet de sons.
* Quelques messages du programme peuvent être traduits. Dans des futures versions la totalité de l'interface sera internationalisé.
* Et quelques correction d'erreur en plus ([#5,](http://twblue.com.mx/errores/view.php?id=5) [#7,](http://twblue.com.mx/errores/view.php?id=7) [#8,](http://twblue.com.mx/errores/view.php?id=8) [#9,](http://twblue.com.mx/errores/view.php?id=9) [#12,](http://twblue.com.mx/errores/view.php?id=12))

## Changements ajouter dans la version 0.3

* Maintenant vous pouvez mettre à jour votre profil à partir de TW Blue. [#19](http://twblue.a12x.net/issues/view.php?id=19)
* Maintenant vous pouvez créer les chronologies à nouveau et ils ne donne pas de problèmes. [#24](http://twblue.a12x.net/issues/view.php?id=24)
* Maintenant les fichiers d'erreur sont enregistrés dans le répertoire "logs".
* Lorsque vous créez une chronologie, il sera mis à jour en temps réel dès le début au lieu de le mettre à jour toutes les 2 minutes.
* Vous pouvez maintenant demander davantage d'appels  à l'API qui fonctionnera pour obtenir 200 tweets chaqu'une. Un appel est équivalent à 200 éléments de la liste principal, mentions, messages directs, favoris et chronologies. Dans le fichier de configuration Vous pouvez modifier l'option dans [twitter]/max_api_calls. Il est recommandé de ne pas demander  à Twitter plus de 2 appels à l'API, ou sinon vous arriverez bientôt à la limite des appels autorisés et l'application échouera.
* Lorsque vous répondez à un Tweet, c'est envoyé comme réponse au même et pas comme s'il s'agissait d'un nouveau tweet.
* L'ancien  système de   rapport d'erreurs il a dû être changée. À partir de cette version, vous pouvez signaler des erreurs, directement depuis l'application. L'option Signaler une erreur ouvrira une boîte de dialogue qui vous demande des détails sur votre erreur et il va envoyer le rapport automatiquement.
* Ils sont déjà supprimées les following lorsque ils ne suivent pas un utilisateur.
* Aussi les favoris, au moment de retirer un tweet comme favori, il exécutent le changement.
* Ajouté une boîte de dialogue de configuration qui permet de contrôler le nombre d'appels à l'API à exécuter, si oui ou non utiliser des bases de données, et masquer ou afficher les listes de following, followers et favoris.
* En mentionnant les tweets, les guillemets qui entourent le message maintenant sont séparés par un espace de la dernière lettre. Il en est ainsi parce qu'avant, lorsque il y avait une URL, il causé  que les guillemets facent partie de l'URL en envoyant vers des sites inexistants.
* Améliorations avec quelques chronologies. Vous pouvez maintenant enregistrer une chronologie sans problèmes. Il ne devrait pas faire des erreurs.
* Maintenant, l'audio est joué seulement avec Contrôle+Entrée, tandis que l'URL s'ouvrira avec la touche Entrée.
* Le flux tentera de se reconnecter à l'échec de la connexion internet.
* Maintenant depuis les followers et following on peut mentionner un utilisateur.
* Maintenant il est fournit un mode "invisible". Sous le menu "Application", dans l'option "Masquer la fenêtre" ou en appuyant sur Contrôle+M. Pour afficher la fenêtre à nouveau appuyez sur Contrôle+Windows+M.

## Changements ajouter dans la version 0.025

Veuillez noter que lorsque un utilisateur vous ne sui pas ou vous ne suivez pas   quelqu'un d'autre, la liste des following ou des followers il ne sera pas mis à jour pour le moment. Lorsque vous redémarrez le programme, si les informations son correctes ils seront afficher.

* Correction d'une erreur qui rendait impossible de fermer l'application jusqu'à ce que le programme a annoncé qu'elle était prête. [#17](http://twblue.a12x.net/issues/view.php?id=17) y [#18](http://twblue.a12x.net/issues/view.php?id=18)
* Changé la façon d'organiser les chronologies dans la configuration. Il est nécessaire de les recréer.
* Maintenant, vous pouvez envoyer un message direct aux following et followers en utilisant le bouton. Cela ne fonctionnait pas dans la version 0.02 et 0.021.
* Vous pouvez augmenter et diminuer le volume depuis la liste des followers et following.
* Dans la boîte de dialogue pour écrire un tweet peut être maintenant traduit le message  à l'aide de Google Traductor. Une boîte de dialogue s'affiche pour  demander les langues source et destination.
* Le menu fichier contient l'option Sortir.
* À partir de cette version ils se jouera uniquement les fichiers de'audio en appuyant sur Entrée s'ils contienne le hashtag #audio.
* Vous pouvez essayer de jouer une URL quelconque sans qui comporte  le hashtag #audio en appuyant sur Contrôle+Entrée. Cette commande va tenter de reproduire la première URL trouvée.
* A été amélioré le moteur de recherche d'URLS, en rendant plus rapide la fonction et maintenant, devrait être capable de détecter toutes les URLS. [#21](http://twblue.a12x.net/issues/view.php?id=21)
* Maintenant, la boîte de dialogue qui s'affiche pour sélectionner l'utilisateur que vous souhaitez afficher les détails permet en plus de le sélectionner dans une liste, écrire le nom de l'utilisateur que vous souhaitez.

## Changements ajouter dans la version 0.02 et 0.021

* Le message qui se reproduicé lorsque vous suivez un utilisateur maintenant dit "maintenant vous suivez à x utilisateur" en lieu de "maintenant vous ne suivez pas à x utilisateur". [#5](http://twblue.a12x.net/issues/view.php?id=5)
* Lorsque vous sorter une boîte de dialogue vous demandera si vous voulez le faire. Maintenant vous sorter d'une façon beaucoup plus proprement du programme, empêchant plusieurs erreurs pendant la fermeture.
* Changement des  sons pour les dm entrant et sortant. Merci à [@marcedsosa](https://twitter.com/marcedsosa) pour les nouveaux sons.
* Le Nom d'utilisateur de twitter il se lit dans le titre de la fenêtre.
* Les sons du programme aussi peuvent  lire le volume depuis  la configuration. Le module de sons devrait prendre moins de temps pour reproduire plusieurs des sons de l'application.
* Les actions d'augmenter et de diminuer le volume ils reproduisent un son indiquant que tant forts ça sonne.
* Il n'affichent plus les mentions de personnes qui ne vous suivent pas dans  votre chronologie principal. [#1](http://twblue.a12x.net/issues/view.php?id=1)
 * Vous pouvez maintenant supprimer les tweets et les messages directs. Vous ne pouvez supprimer que les tweets que vous avez écrit.
* Correction d'une erreur qui empêchait de charger correctement les différentes listes si dans quelques une d'elles ils n'y avait aucun tweet, utilisateur ou message direct. Ceci affectant surtout les comptes avec 0 favoris, 0 tweets, 0 envoyés ou 0 messages directes. [#2](http://twblue.a12x.net/issues/view.php?id=2)
* Maintenant  à chaque fois  qu'une  nouvelle version est disponible, vous serez informé de cela. Si vous avez accès pour le télécharger, le programme va télécharger et copier tout ce dont vous avez besoin.
* Maintenant, vous pouvez obtenir la liste complète des following et followers.
* Ajouter la date du dernier tweet des followers et following.
* Les following et followers sont maintenant mis à jour en temps réel. (ToDo: Les following et followers ils ne montrent pas la date de ces dernier tweet lorsque  une mise à jour est faite en temps réel. Ils le font lors du rechargement une fois redémarrée l'application).
* L'ordre des onglets il a changé. Maintenant ils sont classés en commençant par Principal, Mentions, Messages directs et Envoyés.
* Maintenant dans la liste de tweets envoyés les messages directs sont affichés lorsque le flux est chargé pour la première fois. Ceci ne était pas le cas et si l'utilisateur envoyés  un DM à partir d'un autre client lorsque Tw Blue n'était pas ouvert, lors de l'ouverture de l'application il ne   montré pas la dite DM. [#8](http://twblue.a12x.net/issues/view.php?id=8)
* Con Control+A, se puede seleccionar todo el texto de un mensaje. Funciona con Jaws y NVDA.
* Il y a des raccourcis clavier (détaillés dans la [Documentation)](leeme.html) pour un grand nombre d'actions qui peut faire le programme.
* Maintenant TW Blue détecte plus d'audio dans les URLS qui vienne dans les retweets, et des audio partagé à partir de Dropbox. [#3](http://twblue.a12x.net/issues/view.php?id=3)
* Inclut la documentation pour  l'application et les crédits.
* Si la connexion internet s'arrête de fonctionner, le flux va essayer de se reconnecter pendant 30 minutes.
* On a écrit un document qui détaille comment utiliser le programme.
* Il a été ouvert le [Système de suivi d'incidents](http://twblue.a12x.net/issues/) où les utilisateurs peuvent signaler des erreurs et si vous le souhaitez, vous pouvez apporter de nouvelles idées pour le développement de l'application. Il existe un accès direct au formulaire réservée au rapport d'incidents dans le menu Aide.
* Il y a maintenant des crédits à partir de la version actuelle.
* Ajout d'une option dans menu Utilisateur pour afficher les détails. Cela fonctionne également si vous appuyez sur entrer sur un following ou follower.

## Changements ajouter dans la version Prealpha1

Veuillez noter que dans cette version les following et les followers ne sont pas mis à jour automatiquement. Cela s'ajoutera à une autre version. Vous ne pouvez pas également supprimer des tweet, ou DM. Tous les tweets, messages directs, mentions, favoris, followers et following lors de la mise à jour seront télécharger un maximum de 200. Bientôt ils s'ajouteront plus à la quantité lors des mises à jour. Ici les changements  à partir de la première version.

* La date il s'affiche bien, selon le fuseau horaire de l'utilisateur.
* Maintenant, le curseur est placé au début lorsque vous allez à répondre ou faire un retweet.
* Si vous appuyez sur contrôle + E dans les zones d'édition, l'intégralité du message sera sélectionné.
* Quelques corrections pour la gestion des chronologies (j'ai besoin d'apporter des améliorations dans la façon de gérer cela).
* Les favoris sont mises à jour en temps réel.
* Vous entendrez un son lorsque vous passez par un tweet qui pourrait contenir un audio jouable.
* Supporte la lecture audio avec le hashtag #audio et une URL. Appuyez sur Entrée pour entendre la chanson. Appuyez sur F5 pour diminuer le  volume de 5%, ou f6 pour augmenter d'un 5%. Si vous souhaitez arrêter la lecture, aller où il y a une audio, puis appuyez sur Entrée. Si le programme est incapable de reproduire quelque chose, il vous avertira. Le volume de la musique (pas  pour les sons du programme pour l'instant) est enregistré dans la configuration, et le programme va le mémorisé pour la prochaine fois que vous jouez quelque chose.
* Vous pouvez voir les 200 premiers following et followers avec leurs noms d'utilisateur, nom réel et un peu d'informations utiles. Dans des futures versions  vous pourrez tout voir si vous avez plus de 200. Veuillez noter que il y a des actions que vous ne pouvez pas faire avec ces utilisateurs dans la liste (par exemple, répondre ou retweet, parce qu'ils ne sont pas des tweets, sont utilisateurs), Mais oui, vous pouvez les suivre, ne pas les suivre, et faire presque tout (moins envoyer DM pour l'instant) ce que vous pourriez faire dans le menu Utilisateur.

Maintenant, il faut l'utiliser et le tester et lorsque vous trouvez une erreur, s'il vous plaît veuillez regarder dans le dossier de l'application, puis il doit générer un fichier avec le nom du fichier exécutable, mais avec une extension .log à la fin. Eh bien, c'est vital pour moi de savoir où le programme a été cassé, et vous devriez être reconnaissant si vous me l'envoyer ainsi qu'une description de ce qui était plus ou moins ce qu'ils faisaient quand l'application fait ce qu'il avait à faire. Par exemple, « j'ai essayé de m'envoyer un DM, mais la boîte de dialogue de message direct jamais elle a été ouverte". Si vous pouvez le charger vers un serveur de stockage  (comme Dropbox,](https://www.dropbox.com) par exemple), et me l'envoyer soit en mentionnant à [@tw_blue2](https://twitter.com/tw_blue2) ou à [@manuelcortez00,](https://twitter.com/manuelcortez00) ce serait formidable.

Merci infiniment de l'essayer !

## Nouveautés  dans la version prealpha 0

* Faire des tweets, répondre aux tweets des autres, mentionner tous les utilisateurs, lorsque il y a plus d'un dans le tweet, retweet ce qui vous plaît, ajouter ou non un commentaire au retweet et les supprimez.
* Ajouter ou supprimer des favoris un tweet.
* Réduire  et élargir une URL lorsque vous écrivez un tweet ou dm (vous pouvez sélectionner quelle URL vous souhaitez réduire  et élargir à partir d'une liste lorsque ils sont plus d'une).
* Ouvrir un navigateur Web avec l'URL venant dans le tweet, en appuyant sur Entrée. Lorsque il y a plusieurs  URLs, vous verrez une liste  où on vous demandera la quelles  vous voulez.
* Utilisateurs: Vous pouvez Suivre, Ne pas suivre, Signaler comme spam, Bloquer et Envoyer un message direct aux utilisateurs.
* Vous pouvez ouvrir et supprimer des chronologies individuels pour chaque utilisateur.
* Vous pourrez aussi voir vos favoris.
* Et pour l'instant, à moins qu'il m'arrive d'oublier quelque chose, c'est tout.

---
Copyright © 2013-2014, Manuel Cortéz