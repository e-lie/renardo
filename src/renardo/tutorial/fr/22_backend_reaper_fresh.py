# Tutoriel 22 : Utiliser le backend REAPER (Fresh / extension OSC)

# Ce tutoriel utilise le nouveau backend REAPER basé sur une extension OSC native en Rust.
# Il ne nécessite PAS reapy ni l'ancien pont Lua ReaScript.

# ── Étape 1 : Installer REAPER ──────────────────────────────────────────────────
# Installez une version récente de REAPER (https://www.reaper.fm)
# Lancez-le au moins une fois pour qu'il crée son répertoire de configuration.

# ── Étape 2 : Installer l'extension REAPER de Renardo ──────────────────────────
# Ceci télécharge l'extension Rust précompilée depuis la release GitHub de Renardo
# et l'installe dans le répertoire UserPlugins de REAPER.
# Exécutez ceci une fois (ou à nouveau avec force=True pour mettre à jour) :

setup_reaper_fresh()

# Si le téléchargement échoue, vous pouvez indiquer un tag de release spécifique :
# setup_reaper_fresh(tag="v0.8.0")
# Réinstallation forcée :
# setup_reaper_fresh(force=True)

# Après l'installation, REDÉMARREZ REAPER pour charger l'extension.

# ── Étape 3 : Activer le backend REAPER dans Renardo ────────────────────────────
# Dans le webclient de Renardo, allez dans l'onglet "Audio Backends" et activez REAPER,
# ou réglez REAPER_BACKEND_ENABLED = true dans votre settings.toml.

# ── Étape 4 : Préparer votre projet REAPER ──────────────────────────────────────
# Ouvrez REAPER et créez des pistes pour vos instruments.
# Les pistes MIDI seront pilotées par Renardo via MIDI.
# Les pistes audio (sans entrée MIDI) peuvent aussi être scannées mais ne recevront pas de MIDI.
#
# Exemples de pistes que vous pourriez créer :
#   "Bass Synth"  → charger un instrument VST de basse
#   "Lead"        → charger un instrument VST de lead
#   "Drums"       → charger un instrument VST de batterie
#   "Pad"         → charger un instrument VST de nappe (pad)

# ── Étape 5 : Scanner le projet et créer les façades d'instrument ───────────────
# Avec REAPER lancé et l'extension chargée, exécutez :

reaper_instruments = create_reaper_instruments(max_midi_tracks=16, scan_audio_tracks=True)

# Ceci scanne toutes les pistes et renvoie un dict {nom_piste_en_snake_case: façade, '_project': project}
# La piste "Bass Synth" devient reaper_instruments["bass_synth"]
# La piste "Lead"       devient reaper_instruments["lead"]
# La piste "Drums"      devient reaper_instruments["drums"]

# Vous pouvez aussi créer des façades manuellement pour une piste spécifique :
# from renardo.reaper_backend_fresh import ReaperFreshInstrumentFacade
# bass = ReaperFreshInstrumentFacade(reaper_instruments["_project"], "Bass Synth", midi_channel=1)

# ── Étape 6 : Jouer ───────────────────────────────────────────────────────────
# Utilisez l'attribut .out de chaque façade comme SynthDef pour un Player :

b1 >> reaper_instruments["bass303"].out([0, 3, 5, 7], dur=0.25, cutoff=linvar([0,1]), sus=.24, reso=linvar([0,1], 5))

b2 >> blip([0,3,5,7], oct=7, amp=2)

b1 >> reaper_instruments["bass_synth"].out([0, 3, 5], dur=[0.75, 0.75, 0.5])

p1 >> reaper_instruments["lead"].out([0, 2, 4, 7], dur=1/4)

d1 >> reaper_instruments["drums"].out([0, 2, 4], dur=1)

# Volume (fader linéaire, 0.0–1.5, où ~0.716 ≈ 0 dB) :
b1 >> reaper_instruments["bass_synth"].out([0, 3, 5], vol=0.6)

# ── Étape 7 : Gestion de la latence ─────────────────────────────────────────────
# REAPER introduit une latence MIDI par rapport au backend SuperCollider.
# Ajustez Clock.latency et Clock.midi_nudge pour aligner les deux backends :

Clock.latency = 0.5      # ajoute de la latence aux notes SuperCollider
Clock.midi_nudge = -0.16 # avance les notes MIDI

# Testez l'alignement en lançant en parallèle un instrument SC et un instrument REAPER :
b1 >> blip()
b2 >> reaper_instruments["bass_synth"].out([0, 3, 5])

# ── Nettoyage ────────────────────────────────────────────────────────────────
Clock.clear()
