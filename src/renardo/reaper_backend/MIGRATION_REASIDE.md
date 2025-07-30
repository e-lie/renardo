# Migration Guide: ReaperIntegrationLib → reaside

Ce document détaille les étapes précises pour migrer du système actuel `ReaperIntegrationLib` vers la nouvelle API `reaside`.

## 1. Remplacement des Imports

### Anciens imports à remplacer
```python
# À supprimer
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import ReaProject, get_reaper_object_and_param_name, set_reaper_param
from renardo.reaper_backend.ReaperIntegrationLib.ReaTrack import ReaTrack, ReaTrackType
from renardo.reaper_backend.ReaperIntegrationLib.ReaFX import ReaFX, ReaFXGroup
from renardo.reaper_backend.ReaperIntegrationLib.ReaParam import ReaParam, ReaSend
from renardo.reaper_backend.ReaperIntegrationLib.functions import split_param_name
```

### Nouveaux imports
```python
# À ajouter
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.core.project import ReaProject
from renardo.reaper_backend.reaside.core.track import ReaTrack
from renardo.reaper_backend.reaside.core.fx import ReaFX
from renardo.reaper_backend.reaside.core.param import ReaParam, ReaSend
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
```

## 2. Migration des Classes Principales

### 2.1 ReaProject

#### Ancien code
```python
class ReaProject(object):
    def __init__(self, clock, reapylib):
        self.clock = clock
        self.reapylib = reapylib
        self.tracks = {}  # Dict[str, ReaTrack]
        
    def get_track(self, track_name):
        return self.tracks.get(track_name)
        
    def init_reaproject(self):
        # Initialisation complexe avec reapy
        pass
```

#### Nouveau code
```python
# Plus besoin de classe ReaProject séparée, utiliser directement
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)
project = reaper.current_project  # ReaProject automatiquement créé

# Accès aux tracks par index au lieu de nom
track = project.get_track(0)  # Premier track
track = project.get_track_by_name("Lead Synth")  # Par nom si nécessaire
```

### 2.2 ReaTrack

#### Ancien code
```python
class ReaTrack(object):
    def __init__(self, clock, track, name: str, type: ReaTrackType, reaproject):
        self.reafxs = {}  # Dict[str, ReaFX]
        self.reaparams = {}  # Dict[str, ReaSend]
        self.firstfx = None
        
    def get_param(self, full_name):
        # Logique complexe de parsing des noms
        fx_name, param_name = split_param_name(full_name)
        return self.reafxs[fx_name].reaparams[param_name]
        
    def set_param(self, name, value):
        # Via helper functions
        set_reaper_param(self.track, name, value)
```

#### Nouveau code
```python
# ReaTrack est créé automatiquement, accès direct
track = project.get_track(0)

# FX access simplifié
fx = track.get_fx(0)  # Par index
fx = track.get_fx_by_name("ReaEQ")  # Par nom

# Paramètres track via properties
track.volume = 0.8
track.pan = -0.2
track.is_muted = True

# Paramètres FX directement
fx.set_param("frequency", 1000.0)
```

### 2.3 ReaFX

#### Ancien code
```python
class ReaFX(object):
    def __init__(self, fx, name, index, param_alias_dict={}, scan_all_params=True):
        self.reaparams: Dict[str, ReaParam] = {}
        
    def get_param(self, name):
        return self.reaparams.get(name)
        
    def set_param(self, name, value):
        if name in self.reaparams:
            self.reaparams[name].set_value(value)

# ReaFXGroup pour plusieurs instances
class ReaFXGroup(ReaFX):
    def __init__(self, fxs, name, indexes: List[int]):
        pass
```

#### Nouveau code
```python
# ReaFX créé automatiquement, pas de ReaFXGroup séparé
fx = track.get_fx(0)  # ou track.list_fx()[0]

# Paramètres via méthodes directes
param = fx.get_param("frequency")
fx.set_param("frequency", 1000.0)
value = fx.get_param_value("frequency")

# Enable/disable FX
fx.set_enabled(True)
fx.enable()
fx.disable()
is_on = fx.is_enabled()
```

### 2.4 ReaParam

#### Ancien code
```python
class ReaParam(object):
    def __init__(self, name, value, index=None, reaper_name=None, state=ReaParamState.NORMAL):
        self.state = state
        
    # Pas de méthodes set/get explicites
```

#### Nouveau code
```python
# ReaParam avec communication OSC/HTTP intégrée
param = fx.get_param("frequency")

# Méthodes explicites
value = param.get_value()
param.set_value(1000.0)

# Formatage et normalisation
formatted = param.get_formatted_value()
normalized = param.normalize_value(1000.0)
```

## 3. Migration des Fonctions Helper

### 3.1 Remplacement de `get_reaper_object_and_param_name`

#### Ancien code
```python
def get_reaper_object_and_param_name(track, param_fullname):
    # Logique complexe de parsing
    fx_name, param_name = split_param_name(param_fullname)
    if fx_name in track.reafxs:
        return track.reafxs[fx_name], param_name
    return None, None

# Usage
rea_object, param_name = get_reaper_object_and_param_name(track, "eq.frequency")
```

#### Nouveau code
```python
# Plus de fonction helper nécessaire, accès direct
fx = track.get_fx_by_name("eq")
param = fx.get_param("frequency")

# Ou en une ligne
param = track.get_fx_by_name("eq").get_param("frequency")
```

### 3.2 Remplacement de `set_reaper_param`

#### Ancien code
```python
def set_reaper_param(track, param_fullname, value, update_freq=.02):
    # Logique complexe avec task queue
    rea_object, param_name = get_reaper_object_and_param_name(track, param_fullname)
    if rea_object:
        rea_object.set_param(param_name, value)

# Usage
set_reaper_param(track, "eq.frequency", 1000.0)
```

#### Nouveau code
```python
# Méthode directe avec OSC intégré
track.get_fx_by_name("eq").set_param("frequency", 1000.0)

# Ou via param object
param = track.get_fx_by_name("eq").get_param("frequency")
param.set_value(1000.0)
```

## 4. Migration de `reaper_music_resource.py`

### 4.1 Classe ReaperEffect

#### Ancien code
```python
class ReaperEffect(Effect):
    def apply_to_track(self, track_name: str, **params):
        # Via ReaperIntegrationLib
        track = self.get_track(track_name)
        for param_name, value in params.items():
            set_reaper_param(track, f"{self.shortname}.{param_name}", value)
```

#### Nouveau code
```python
class ReaperEffect(Effect):
    def apply_to_track(self, track_index: int, **params):
        # Via reaside
        track = project.get_track(track_index)
        fx = track.get_fx_by_name(self.shortname)
        if not fx:
            track.add_fx(self.shortname)
            fx = track.get_fx_by_name(self.shortname)
            
        for param_name, value in params.items():
            fx.set_param(param_name, value)
```

### 4.2 Classe ReaperInstrument

#### Ancien code
```python
class ReaperInstrument(Instrument):
    def setup_track(self, track_name: str):
        # Via ReaperIntegrationLib
        track = reaproject.get_track(track_name)
        track.create_reafxs_for_chain(self.fxchain_relative_path)
```

#### Nouveau code
```python
class ReaperInstrument(Instrument):
    def setup_track(self, track_index: int):
        # Via reaside
        track = project.get_track(track_index)
        track.add_fxchain(self.fxchain_relative_path)
```

## 5. Points d'Attention pour la Migration

### 5.1 Accès aux Tracks
- **Ancien**: Par nom de string `track.get_track("Lead")`
- **Nouveau**: Par index numérique `project.get_track(0)` ou `project.get_track_by_name("Lead")`

### 5.2 Task Queue
- **Ancien**: Utilise `ReaTaskQueue` pour les opérations asynchrones
- **Nouveau**: Communication directe OSC/HTTP, pas de queue nécessaire

### 5.3 Context Management
- **Ancien**: Require `with reapylib.inside_reaper():`
- **Nouveau**: Communication directe, pas de context manager

### 5.4 Parameter States (TimeVar)
- **Ancien**: Gestion des états VAR1, VAR2 pour TimeVar
- **Nouveau**: À implémenter au niveau application si nécessaire

### 5.5 FX Groups
- **Ancien**: Classe `ReaFXGroup` séparée
- **Nouveau**: Gérer au niveau logique application

## 6. Checklist de Migration

### Phase 1: Setup de base
- [ ] Remplacer tous les imports `ReaperIntegrationLib` par `reaside`
- [ ] Créer `ReaperClient` et `Reaper` au lieu de `ReaProject`
- [ ] Migrer l'accès aux tracks (index vs nom)

### Phase 2: Migration des FX
- [ ] Remplacer `track.reafxs[name]` par `track.get_fx_by_name(name)`
- [ ] Migrer `fx.reaparams[name]` vers `fx.get_param(name)`
- [ ] Ajouter appels `fx.set_enabled()` pour enable/disable

### Phase 3: Migration des paramètres
- [ ] Remplacer `set_reaper_param()` par `param.set_value()`
- [ ] Migrer `get_reaper_object_and_param_name()` vers accès direct
- [ ] Utiliser properties pour volume/pan/mute/solo des tracks

### Phase 4: Nettoyage
- [ ] Supprimer les imports `ReaperIntegrationLib`
- [ ] Supprimer les fonctions helper obsolètes
- [ ] Supprimer les task queue references
- [ ] Tester la communication OSC

## 7. Avantages après Migration

- **Performance**: Communication OSC temps-réel
- **Simplicité**: API plus directe et intuitive
- **Type Safety**: Meilleure annotations de types
- **Maintenance**: Code plus moderne et structuré
- **Features**: Enable/disable FX, properties track, etc.

Cette migration remplace un système complexe basé sur reapy par une API moderne avec communication OSC/HTTP directe.