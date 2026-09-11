### Déclencheurs OSC : lancer du code depuis un message OSC entrant

# trig("/une/route") vous donne un objet qui se comporte exactement comme
# les PointInTime vus dans les tutoriels précédents, à ceci près qu'au
# lieu d'être défini par vous (pit.beat = ...), il se définit *lui-même*
# à chaque fois qu'un message OSC est reçu sur cette adresse, depuis
# n'importe quel logiciel (Ableton, TouchOSC, Max/MSP, une autre instance
# de renardo, un script python-osc...). Les arguments du message sont
# ignorés pour l'instant.

b1 >> blip()


def monte():
    b1.oct = 6


Clock.schedule(monte, trig("/octave"))

# Envoyez un message OSC vers 127.0.0.1:57430, adresse "/octave" (depuis
# n'importe quel logiciel capable d'émettre de l'OSC) et b1 montera d'une
# octave au prochain temps.

### La même chose avec le langage de macro

# {trig("/octave")}
b1.oct = 6

### trig() supporte la même arithmétique que PointInTime

# Se déclenche 8 temps après le message OSC au lieu d'immédiatement

# {trig("/octave")+8}
b1.degree = 4

### trig() est persistant : il se redéclenche à chaque nouveau message

# Chaque bloc macro ou appel à Clock.schedule attaché à un déclencheur
# reste attaché — pas besoin de réévaluer quoi que ce soit entre deux
# messages OSC.

d1 >> play("x-o-")

# {trig("/fill")}
d1.oct += 1

### Lier un PointInTime à un déclencheur

# `mon_point.beat = trig("/route")` lie n'importe quel PointInTime à un
# déclencheur : au lieu d'un numéro de temps, `mon_point` reçoit
# Clock.now() à chaque déclenchement. C'est pratique quand vous voulez
# piloter le mécanisme de rendez-vous du tutoriel 17 (plusieurs points
# programmés les uns par rapport aux autres) depuis un message OSC
# externe plutôt qu'un numéro de temps.

# Un pit() classique ne se déclenche qu'une seule fois de cette façon
# (comme n'importe quel PointInTime simple) : utilisez ppit() si vous
# voulez qu'il soit redéfini à chaque message :

drop = ppit()


def monte_octave():
    b1.oct += 1


def descend_octave():
    b1.oct -= 1


Clock.schedule(monte_octave, drop - 16)
Clock.schedule(descend_octave, drop)

drop.beat = trig("/drop")  # chaque message "/drop" redéfinit maintenant `drop`

### Configurer le serveur de déclencheurs OSC

# Par défaut, le serveur de déclencheurs écoute sur 127.0.0.1:57430.
# Vous pouvez changer cela (par exemple pour écouter sur toutes les
# interfaces, ou éviter un conflit de port) avant de déclencher quoi que
# ce soit :

Clock.osc_trig_addr = "0.0.0.0"
Clock.osc_trig_port = 9000

# Changer l'une ou l'autre valeur redémarre le serveur de déclencheurs
# s'il était déjà en cours d'exécution.
