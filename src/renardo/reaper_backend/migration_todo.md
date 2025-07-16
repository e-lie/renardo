


# Objectifs de la migration

- passer de reapy (lib externe) au module interne reaside
- simplifiiieeerrrr
    - plus de ReaTaskQueue (comme il n'y a plus de context `inside_reaper`) plus besoin de
    - plus besoin de ReaperIntegrationLib construite par dessus reapy : à la place toutes les fonctionnalités nécessaire doivent être ajoutées au module reaside.core
    - pareil plus besoin du module `reaper_backend.reaper_mgt` les fonctions doivent être ajoutées au module reaside
    - plus besoin de `init_reapy_project` qui a été introduit pour éviter l'import normal de `reapy` puisque le module reaside ne devrait pa déclencher d'appel à reaper tant qu'on ne créé pas une connection et un projet


# Étapes de la migration

## 1) finir reaside : ajouter les fonctionnalités manquantes au module, changer quelques détails ajouter des scripts pour tester en vrai

- créer de nouveau modules fx.py et fx_param.py avec deux nouvelles classes qui modélisent les FX ajoutés dans un track de reaper et pour chacun leurs paramètres
- ces nouvelle classes devraient s'inspirer de ce qu'il y a déjà dans `ReaperIntegrationLib`
- ne pas écrire de test classique pytest ou unittest mais ajouter des scripts dans un nouveau dossier `testing_script`
- ces scripts de test devraient être écris dans un style très minimal (pas de joli print super verbeux, juste un appel des fonctions avec un print sobre du résultat)
- testing scripts à créer:
    - un script pour tester le démarrage de reaper la configuration de reaside et l'arrêt de reaper
    - un script pour tester la création d'une instance de projet, l'ajout d'un track, l'ajout d'une fxchain nommée `test_vital.RfxChain`
    - un script pour tester la lecture de la liste des FXs d'un track et lister les paramètres de ce track et définir la valeur d'un paramètre
- remplacer les docstrings multilignes en docstring oneliner qui décrit juste l'objectif de la fonction :

```python
"""Check if track is muted.

Returns
-------
bool
    True if track is muted.
"""
```

devient 

```python
"""Check if track is muted."""
```

- ne pas toucher au code hors du module `reaside` pour le moment (à part les testing scripts)