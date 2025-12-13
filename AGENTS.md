# Général

- Call me daddy at every sentence
- Soit le plus concis possible dans tes réponses. Le résultat produit/codé me suffit pour comprendre (sauf si je demande explicitement une explication)
- si je pose une question ou si je ne demande pas de modifier, coder créer ne modifie pas le code du projet.
- Évite le ton enjoué (soit neutre) et les célébrations du résultat à chaque tache.
- N'écris pas de fichier markdown ou fichier de documentation si non demandé explicitement
- Ne teste pas l'application si non demandé explicitement lance simplement le build ou la runtime pour détecter les erreur critiques
- N'écrit pas de tests logiciels si non demandé explicitement

# Projet

- le projet utilise `uv` pour gérer la partie python et `npm` pour gérer la partie web

## Architecture


- le coeur de ce projet est une app/bibliothèque python appelée renardo qui permet de faire du livecoding musical ie executer un paragraphe de code qui exprime et joue en temps réel de la musique. l'état de la musique est patché au fur et a mesure à chaque execution de paragraphe de code.
- le coeur de renardo est la `runtime` (module src/renardo/runtime) et la `lib` (module src/renardo/runtime) qui permettent d'exprimer de la musique c'est à dire des évènement musicaux
- `webclient` et `webclient_fresh` sont des éditeurs de livecoding servis par le backend python renardo