# Tutoriel 21 : Utiliser le backend Ableton Live

# 1. Installez Ableton Live 11 ou supérieur
# 2. Installez les dépendances pylive (devraient être installées avec Renardo)
# 3. Installez le Remote Script AbletonOSC dans Ableton Live
#    Téléchargez depuis : https://github.com/ideoforms/AbletonOSC

# Pour installer le Remote Script AbletonOSC (voir le README github de pylive et d'abletonOSC pour des informations à jour)
# 1. Téléchargez et extrayez le dépôt sous forme de fichier zip
# 2. Renommez le dossier "AbletonOSC-master" en "AbletonOSC"
# 3. Copiez le dossier dans le répertoire Remote Scripts :
#    - Windows : C:\Users\[username]\Documents\Ableton\User Library\Remote Scripts
#    - macOS : /Users/[username]/Music/Ableton/User Library/Remote Scripts
# 4. Redémarrez Ableton Live
# 5. Dans Ableton : Preferences > Link / Tempo / MIDI
#    - Sélectionnez "AbletonOSC" dans le menu déroulant Control Surface
# 6. Vous devriez voir : "AbletonOSC: Listening for OSC on port 11000"

# Active le backend Ableton
# ABLETON_BACKEND_ENABLED=true dans le fichier toml de settings ou via l'interface du client web

# Assurez-vous qu'Ableton Live est lancé avec le device AbletonOSC chargé
# Puis créez les instruments Ableton dans Renardo

# Ceci va :
# - Se connecter à Ableton Live via OSC
# - Scanner toutes les pistes, devices et paramètres
# - Créer des façades d'instrument pour chacune des 16 premières pistes, pour un accès facile

ableton_instruments = create_ableton_instruments(max_midi_tracks=16, scan_audio_tracks=True)


# Exemple : si vous avez une piste nommée "Bass Synth" dans Ableton :
b1 >> mybass([0, 3, 5, 7], dur=0.5) # mybass est le nom de la piste dans ableton, en snake_case

# Si vous avez une piste nommée "Lead" :
p1 >> thelead([0, 2, 4, 7], dur=1/4)

# Si vous avez une piste nommée "Drums" :
d1 >> drumkiit([0,2,4], dur=1)

b1 >> mybass([0, 3, 5], cutoff=2000)

b1 >> bass_synth([0, 3, 5], cutoff=linvar([500, 4000], 8))

b1 >> bass_synth([0, 3, 5], vol=0.8)

b1 >> bass_synth([0, 3, 5], pan=0.5)

# Ces paramètres ableton NE fonctionnent PAS avec des patterns, seulement avec des timevars
# (pour des raisons structurelles, les patterns ne sont possibles que via SuperCollider)

# Clock.bpm change le bpm d'ableton et le bpm de l'horloge link (voir la synchronisation ableton link)

# Synchro de la tonalite : tant que le backend Ableton est actif, la gamme
# (Scale.default) et la tonique (Root.default) de Renardo sont repercutees dans
# la vue "Scale Awareness" de Live (synchro unidirectionnelle Renardo -> Live,
# changements dynamiques Pvar/var inclus).
#   Root.default = "F#"
#   Scale.default = "phrygian"
# Prerequis : AbletonOSC doit etre a jour (>= la version exposant root_note /
# scale_name sur le Song). Desactivable via ABLETON_SYNC_SCALE_ROOT=false.

Clock.clear()
