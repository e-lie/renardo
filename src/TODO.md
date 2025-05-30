
# Les Prios

- [x] finir la gestion des collections
  - [x] download les scresources banks depuis collections
  - [x] redebug from scratch

- [x] new web UI instead of TUI !!!

- redesign de l'integration reaper
  - [x] creer les projets from scratch en programmatique
  - [x] sauvegarder les fxchains comme des reaperResources dans le dossier renardo et les mettre dynamiquement dans le dossier Reaper
  - [ ] vol param use volume fader + new param fadeamp that is a third param special for fade like methods
  - Clock.bpm= should do the stuff from change_bpm
  - [ ] create a detailed documentation page

- [x] test and finish the SCLang livecoding feature

- think about and design the meta language
  - [x] create the meeting point schedule feature
  - [x] create the comment based macros to program clock schedule without python indented blocks
  - [ ] create the state machine cycle like list class
  - [ ] explore and debug


- [ ] add a close all buffers button with a warning (Did you save the session)
- [ ] add configure other editors with multiple tabs and a button that give you configuration for pulsardo


- live tools in editor
  - [x] custom editor fonts + jgs
  - [ ] configurable clock display

- documentation
  - concepts and architecture
  - every function
    - player methods
    - pattern generation functions
    - pattern methods
    - global params

# Moins prio

- live tools in editor
  - player playing list with attribute value display -> add a new dict like class that store the value at every param setting (__setattr__) (less prio)
  - displaying state of the ppit and rpit (less prio)
  - finish the bang feature (less prio)

- add collection explorer to look at the 

- test MIDI matrix for playstrings

- multiplayers as experimental feature

- share to activitypub feature
- share with the community as potential example (do a new repo per year on the long term ?)

- test livecoding effects

- pulsardo websocket
- redesign midi
  - sans reaper
  - MIDIddleware
    - virtual device based on mido
    - multiplex more than 16 channels
    - send to external hardware plus
    - handle automatic latency correction per player

# les trucs à debug

- [ ] debug effects with renardo community sclang bank
- [ ] when opening same tutorial file or music example it opens multiple tabs

- [ ] debug supercollider startup
- [ ] debug la bonne execution des startup files
- [x] Clock.bpm =  is broken ?? from which commit on ?

- [ ] editor color scheme = dropdown bugs on reload if not default color scheme (dracula for now)

- [ ] configure the ouput with verbosity parameter => create a renardo logger to replace print ?

- [ ] make every output of the renardo backend be displayed to the renardo console even delayed output using the logger (Clock.every(4, lambda: print("hello")))

- [ ] ne pas pouvoir executer deux fois le même code deux fois de suite du tout dans l'editeur est un bug
- [ ] spack param not working
- [ ] d1 >> play("x-o-").every(4, "stutter", 4) -> seems every is not working anymore

- [x] fix / remove / find something else for startup file
- [ ] open reaper directory, open user dir does nothing on linux !
- [x] when opened through renardo scide is closed when closing renardo

# trucs cools pour le futur

- backend pure python avec pyo ou webaudio ?
- Multiplateform audio routing tool AUDiddleware
