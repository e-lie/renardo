# Tutoriel 1 : Jouer des notes

# Dans Renardo, tous les noms de variables à deux caractères sont réservés aux objets Player, comme 'p1'
# Créer un objet Player sans argument jouera une seule note en do central, par défaut, en boucle jusqu'à l'arrêt.
# Utilisez >> pour donner l'une de ces instructions à un objet Player, comme ceci :

p1 >> pluck()

# Pour arrêter un objet Player individuel, exécutez simplement

p1.stop()

# En plus des variables à 2 caractères pré-réservées, vous pouvez créer les
# vôtres avec vos propres noms

foo = Player()
foo >> pluck()

# En Python, >> est habituellement réservé à un type d'opération, comme + ou -, mais ce n'est pas le cas dans Renardo.
# Si un utilisateur ré-exécute le code, Renardo mettra à jour p1 au lieu de créer un nouvel objet Player,
# ce qui signifie que vous pouvez modifier votre musique en utilisant une seule ligne de code.

# Si vous donnez maintenant des arguments à votre objet Player, vous pouvez changer les notes jouées.
# Le premier argument doit être le degré de la note à jouer
# (par défaut, la note la plus basse de l'octave 5 de la gamme majeure) et n'a pas besoin d'être nommé.

# Python, comme la plupart des langages de programmation, utilise l'indexation à partir de zéro pour accéder aux valeurs d'un tableau,
# ce qui signifie que 0 fait référence à la première note de la gamme.
# Donnez à votre objet Player des instructions pour faire de la musique avec son Synth.
# Le premier argument est la note de la gamme à jouer. Le code suivant
# joue les trois premières notes de la gamme par défaut (majeure) en boucle.

# Pour une seule note
p1 >> pluck(0)

# Ou une liste de notes
p1 >> pluck([0,1,2])

# Mais vous devrez préciser tout ce que vous voulez changer d'autre...

# Comme la durée des notes, ou la longueur de chaque note
p1 >> pluck([0,0,0], dur=[1,2,3])

# Ou l'amplitude, le « volume » de chaque note
p1 >> pluck([0,0,0], amp=[1,2,3])

# Si la deuxième liste, l'amp dans cet exemple, est trop longue, alors la première liste (le degree) boucle simplement, et ses éléments sont associés aux éléments restants de la deuxième liste (l'amplitude).
p1 >> pluck([0,2,4], amp=[1,2,3,1,5])

# Plus généralement, toutes les listes sont parcourues quelle que soit leur longueur.
p1 >> pluck([0,2,4], dur=[1,2], amp=[1,2,3,1,5])

# Les arguments peuvent être des entiers, des nombres à virgule flottante, des fractions, des listes,
# des tuples, ou un mélange de tout cela

p1 >> pluck([0,0,0], dur=2)

p1 >> pluck([0,0,0], dur=1.743)

p1 >> pluck([0,0,0], dur=[0.25,0.5,0.75])

p1 >> pluck([0,0,0], dur=[1/4,1/2,3/4])

p1 >> pluck([0,0,0], dur=[1/4,0.25,3])

# Les listes de valeurs sont parcourues au fur et à mesure que le Player joue les notes
# La durée suivante équivaut à : 1,2,3,1,4,3
# Si vous ne comprenez pas encore cela, ne vous inquiétez pas, on parlera davantage des patterns dans le tutoriel dédié
p1 >> pluck([0,0,0], dur=[1,[2,4],3])

# Les valeurs dans des tuples sont utilisées simultanément, c'est-à-dire que p1 jouera 3 notes individuelles, puis un accord des 3 notes ensemble en même temps.
p1 >> pluck([0,2,4,(0,2,4)])

# Vous pouvez aussi assigner des valeurs aux attributs des objets Player directement
p1.oct = 5

# Pour voir tous les noms des attributs des Players, exécutez simplement
print(Player.get_attributes())

# Plus de détails à ce sujet plus tard dans le tutoriel sur les attributs des Players

# Vous pouvez stocker plusieurs instances de Player et les assigner à des moments différents
proxy_1 = charm([0,1,2,3], dur=1/2)
proxy_2 = charm([4,5,6,7], dur=1)

p1 >> proxy_1 # Assigne la première à p1

p1 >> proxy_2 # Ceci remplace les instructions suivies par p1

# Pour jouer plusieurs séquences à la fois, faites simplement la même chose avec un autre
# objet Player :

p1 >> pluck([0, 2, 3, 4], dur=1/2)

p2 >> charm([(0, 2, 4), (3, 5, 7)], dur=8)

# Ne joue que ce Player, en coupant le son des autres
p1.solo() # la valeur par défaut est 1 (solo activé)

# Et désactive le solo
p1.solo(0)

# Arrête (pas seulement coupe le son) les autres Players
p1.only()

# Utilisez Ctrl+. pour tout effacer dans l'horloge de programmation (Clock)
Clock.clear()
