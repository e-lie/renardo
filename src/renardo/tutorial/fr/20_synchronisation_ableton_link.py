# Tutoriel 20 : Synchronisation Ableton Link

# Ableton Link est un protocole qui permet de synchroniser le tempo et la phase
# entre plusieurs applications et appareils musicaux sur le même réseau.

# Active la synchronisation Ableton Link
Clock.sync_to_link(enabled=True)

# Désactive Ableton Link
Clock.sync_to_link(enabled=False)

# Vérifie l'état de Link (affiche le tempo, le temps, la phase, les pairs connectés, etc.)
Clock.link_status()

# Exemple
Clock.sync_to_link(enabled=True)
Clock.bpm = 140
Clock.meter = (4, 4)

d1 >> play("x-o-", dur=1)
b1 >> bass([0, 0, 3, 5], dur=0.5)
p1 >> pluck(P[0, 2, 4, 7].amen(), dur=1/4)

# Si vos temps sont légèrement décalés par rapport aux temps de Link, ajustez le décalage de phase
# La valeur par défaut est 0.5, mais vous devrez peut-être l'ajuster selon votre configuration
Clock.link_phase_offset = 0.5   # Un demi-temps en avant
Clock.link_phase_offset = 0.0   # Pas de décalage
Clock.link_phase_offset = -0.5  # Un demi-temps en arrière

# Ajuste le BPM (ceci sera synchronisé sur toutes les applications compatibles Link)
Clock.bpm = 120

# Change la signature rythmique (affecte l'alignement du quantum)
# Pour une mesure en 3/4 :
Clock.meter = (3, 4)

# Pour arrêter la synchronisation Link
Clock.sync_to_link(enabled=False)

# Vous pouvez aussi définir manuellement le quantum si besoin :
Clock.link_quantum = 4  # Force un alignement sur 4 temps quel que soit le meter

# Pour revenir à un quantum automatique basé sur le meter :
Clock.link_quantum = None



# Contrôle la fréquence de resynchronisation avec Link (en temps)
# Valeurs plus basses = synchronisation plus serrée mais plus de CPU, valeurs plus hautes = plus lâche mais plus efficace
Clock.link_sync_interval = 1   # Resynchronise à chaque temps (par défaut)
Clock.link_sync_interval = 4   # Resynchronise toutes les 4 temps (une mesure en 4/4)

# === EXEMPLE PRATIQUE ===

# 1. Démarrez Ableton Live (ou toute application compatible Link)
# 2. Activez Link dans cette application
# 3. Activez Link dans Renardo
Clock.sync_to_link(enabled=True)

# 4. Vérifiez l'état pour voir si la connexion est établie
Clock.link_status()
# Vous devriez voir "Peers: 1" (ou plus si plusieurs applications sont connectées)

# 5. Jouez quelque chose
p1 >> pluck([0, 2, 4, 7], dur=1)

# 6. Le tempo sera synchronisé avec Ableton Live
# Essayez de changer le tempo dans l'une ou l'autre application - elles restent synchronisées !

# 7. Lancez des clips dans Ableton - ils seront en phase avec Renardo

# === DÉPANNAGE ===

# Si les temps ne sont pas alignés :
# - Vérifiez Clock.link_status() pour voir la phase actuelle
# - Ajustez Clock.link_phase_offset par incréments de 0.25
# - Valeurs courantes : -0.5, 0.0, 0.5, 1.0

# Si le tempo dérive :
# - Diminuez Clock.link_sync_interval pour une synchronisation plus serrée
# - Vérifiez que les deux applications sont sur le même réseau

# Si aucun pair n'est détecté :
# - Assurez-vous que Link est activé dans les autres applications
# - Vérifiez les paramètres du pare-feu (Link utilise le port UDP 20808)
# - Assurez-vous que tous les appareils sont sur le même réseau local

# === UTILISATION AVANCÉE ===

# Link fonctionne très bien avec des configurations de performance live :
# - Synchronisez Renardo avec Ableton Live pour des performances hybrides
# - Connectez plusieurs instances de Renardo sur différents ordinateurs
# - Synchronisez avec des applications iOS comme Audiobus, AUM, etc.

# La synchronisation Link se fait en temps réel avec une très faible latence
# L'architecture d'horloge à double thread assure une temporisation précise


