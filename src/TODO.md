
# Les Prios

- [x] finir la gestion des collections
  - [x] download les scresources banks depuis collections
  - [x] redebug from scratch

- [x] new web UI instead of TUI !!!

- redesign de l'integration reaper
  - creer les projets from scratch en programmatique
  - sauvegarder les fxchains comme des reaperResources dans le dossier renardo et les mettre dynamiquement dans le dossier Reaper
  - vol param use volume fader + new param fadeamp that is a third param special for fade like methods

- test and finish the SCLang livecoding feature (effects too)

- think about and design the meta language

- live tools in editor
  - configurable clock display
  - player playing list with attribute value display -> add a new dict like class that store the value at every param setting (__setattr__)
  - finish the bang feature (less prio)

- add collection explorer to look at the 

- documentation
  - concepts and architecture
  - every function
    - player methods
    - pattern generation functions
    - pattern methods
    - global params

- test MIDI matrix for playstrings

# Moins prio

- multiplayers as experimental feature

- pulsardo websocket
- redesign midi
  - sans reaper
  - MIDIddleware
    - virtual device based on mido
    - multiplex more than 16 channels
    - send to external hardware plus
    - handle automatic latency correction per player


# les trucs à debug

- ne pas pouvoir executer deux fois le meme code deux fois de suite du tout dans l'editeur est un bug
- spack param not working
- d1 >> play("x-o-").every(4, "stutter", 4) -> seems every is not working anymore

- fix / remove / find something else for startup file

# trucs cools pour le futur

- backend pure python avec pyo ou webaudio ?
- Multiplateform audio routing tool AUDiddleware