# Partie un - Installer et configurer Reaper

# Installez d'abord une version récente du DAW Reaper (utilisez la version normale, pas la version portable)

# Nous devons configurer la connexion Python à Reaper avec la bibliothèque reapy.
# Cette première partie relève encore un peu de la magie noire et est parfois capricieuse, car REAPER ne collabore pas très bien avec le contrôle externe... stabilisation en cours

# Dans renardo, allez dans l'onglet "Audio Backends" REAPER et cliquez sur "Initialize REAPER Integration"
# Lisez et suivez attentivement les étapes (attendez que Reaper démarre ou se ferme avant de cliquer sur continuer).
# Si vous manquez une étape, fermez Reaper et redémarrez le processus en cliquant sur le bouton.

# Pour tester que l'intégration fonctionne, exécutez dans l'éditeur de code

import reapy
print(reapy.Project()) # la sortie devrait ressembler à : Project("(ReaProject*)0x0000000005FD88A0")

# Voir "troubleshooting Reaper Integration / reapy" dans la documentation, si vous n'arrivez pas à faire fonctionner cela simplement.

# Partie deux - Installer les plugins open source de base (configuration classique des plugins)

# Installez la version VST3 de vital synth (https://vital.audio) et de Surge XT (https://surge-synthesizer.github.io/)
#
# Vérifiez dans Reaper la section Preferences > VST. Si le scan des plugins ne détecte pas vos plugins :
# sur Windows et MacOS, l'installation par défaut des plugins devrait fonctionner directement,
# sur Linux, attention, les plugins peuvent être installés dans /usr/lib/vst3, ce qui n'est pas scanné par REAPER par défaut
# => vous pouvez lancer la commande suivante pour vous en assurer : ln -s /usr/lib/vst3 ~/.vst3/global
# En général, vous devriez ajuster la liste des "VST plugins Paths" pour que REAPER trouve les vst3 dans le bon répertoire

# Partie trois - Configurer la connexion MIDI

# Reaper doit être préparé avec 16 pistes MIDI (une par canal) avant de créer les instruments. Exécutez ce qui suit une fois que Reaper est complètement chargé :
# ensure_16_midi_tracks() # Les pistes MIDI devraient apparaître dans l'interface de Reaper. TODO mettre à jour avec le nouveau contrôle reaper

# Activez une entrée MIDI dans Reaper dans Preference > MIDI Inputs

# Lancez le backend SuperCollider de Renardo avec MIDI, soit automatiquement
# avec les fonctionnalités Audio Backends > SuperCollider de Renardo, soit manuellement dans SuperCollider.

# Selon votre OS, vous devez configurer la connexion MIDI entre SuperCollider et REAPER (tutoriel à venir bientôt à ce sujet :)
# Vous pouvez ensuite tester la connexion en ajoutant un plugin instrument sur la piste "chan1" et en exécutant :

m1 >> MidiOut(channel=0)

# Partie quatre - Utiliser l'intégration avec Reaper Instrument

# Vous devez maintenant choisir 16 instruments reaper maximum (pour l'instant) dans la bibliothèque reaper
# Pour lister les instruments actuellement sélectionnés, exécutez :
list_selected_reaper_instruments()

# Pour voir tous les instruments de la bibliothèque :
list_all_reaper_instruments()

# Sélectionnez des noms d'instruments dans une liste avec
set_selected_instruments(["bass303", "lonesine", "gone", "solar2", "pluckbass"])

# Pour créer et ajouter à reaper les instruments sélectionnés, exécutez
create_selected_instruments()

# testez un instrument
b1 >> pluckbass([0,0,0,2], dur=[.75,.75,.5])

# en cas de problème si cela ne fonctionne pas
# Assurez-vous que Renardo.midi est démarré, que les messages MIDI sont correctement envoyés de SuperCollider vers Reaper
# Recherchez les erreurs dans le journal du terminal de Renardo
# Page de documentation de dépannage (travail en cours)

# Partie cinq - Gestion de la latence

# Pour synchroniser les notes entre les backends SuperCollider et Reaper...
# Nous pouvons ajouter de la latence au backend SuperCollider avec

Clock.latency = 0.5

# Puis nous pouvons ajuster un décalage (nudge) MIDI négatif avec

Clock.midi_nudge = -0.16

# Lancez deux instruments, Reaper et SuperCollider, pour ajuster la valeur pour votre machine

b1 >> blip()

b2 >> pluckbass()

