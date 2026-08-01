# Tutoriel 2 : Manipulation algorithmique

# Le code ci-dessous joue les quatre premières notes de la gamme par défaut en boucle :
p1 >> charm([0,1,2,3])

# Il est possible de manipuler cela en ajoutant un tableau de nombres à l'objet Player
# Ceci élève la 4e note jouée de 2 degrés
p1 >> charm([0,1,2,3]) + [0,0,0,2]

# Et ceci élève chaque troisième note de 2
p1 >> charm([0,1,2,3]) + [0,0,2]

# Ces valeurs peuvent être entrelacées et groupées ensemble
p1 >> charm([0,1,2,3]) + [0,1,[0,(0,2)]]

# Ce comportement est particulièrement utile avec la méthode follow.
b1 >> bass([0,4,5,3], dur=2)
p1 >> charm().follow(b1) + [2,4,7]

# Vous pouvez programmer des actions pour les Players
# Ceci indiquera à p1 d'inverser les notes toutes les 4 temps
p1 >> charm([0,2,4,6])
p1.every(4, "reverse")

# Vous pouvez « chaîner » les méthodes en les ajoutant à la fin de
# la ligne d'origine :
p1 >> charm([0,2,4,6]).every(4, "reverse")

# Pour arrêter d'appeler "reverse", utilisez 'never' :

p1.never("reverse")

# Voici quelques autres méthodes que vous pouvez utiliser :

# Utiliser "stutter" jouera la même note 'n' fois avec différents attributs spécifiés

p1.every(4, "stutter", 4, oct=4, pan=[-1,1])

# Rotate décale toutes les valeurs d'un cran dans leur ordre
p1.every(4, "rotate")

# Pour rendre l'ordre des notes aléatoire, utilisez "shuffle"
p1.every(4, "shuffle")


