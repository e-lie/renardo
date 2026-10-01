# Tutoriel 9 : Groupes


# Les attributs des Players, comme degree ou scale, peuvent aussi être changés en leur assignant directement des valeurs, tel que
p1 >> charm([0,2,4,2], scale=Scale.majorPentatonic)

# est équivalent à
p1 >> charm()
p1.degree = [0,2,4,2]
p1.scale = Scale.majorPentatonic

# Ceci est utile si vous voulez assigner les mêmes valeurs à plusieurs objets Player simultanément, comme ceci :
p1 >> charm([0,2,4,2])
p2 >> charm([2,1,0,4])
p3 >> charm([2,3])
p1.dur=p2.dur=p3.dur=[1,1/2,1/4,1/4]

p1.stop()
p2.stop()
p3.stop()

# Vous pouvez référencer tous les membres portant des noms similaires
p_all.dur = [1/2,1/4] # Exécutez ceci pendant que p1, p2, etc. jouent !

# ou
p_all.amplify = 1

# Ou...
p_all.stop()

# Ou...
p_all.solo()

# Pour réduire la quantité de code à écrire, les objets Player peuvent être regroupés et leurs attributs modifiés plus simplement :
p1 >> charm([0,2,4,2])
p2 >> charm([2,1,0,4])
p3 >> charm([2,3])
g1 = Group(p1, p2, p3)
g1.dur=[1,1/2,1/4,1/4]

# Vous pouvez grouper avec _all les groupes
g1 = Group(p_all, d_all, b1, b2)

# Active le volume pendant 4 temps, puis le coupe pendant 4
# Ceci écrase les amplitudes déjà définies dans l'objet Player
g1.amp=var([1,0],4)

g1.stop()

# Vous pouvez utiliser des fonctions pour grouper des éléments ensemble. Pour exécuter, utilisez CTRL+Entrée, pas ALT+Entrée.
def tune():
    b1 >> bass([0,3], dur=4)
    p1 >> pluck([0,4], dur=1/2)
    d1 >> play("x--x--x-")
tune()

# ou programmez le Clock pour appeler d'autres fonctions groupées
def verse():
    b1 >> bass([0,3], dur=4)
    p1 >> pluck([0,4], dur=1/2)
    d1 >> play("x--x--x-")
    Clock.future(16, chorus)
def chorus():
    b1 >> bass([0,4,5,3], dur=4)
    p1 >> pluck([0,4,7,9], dur=1/4)
    d1 >> play("x-o-")
    Clock.future(16, verse)
verse()
