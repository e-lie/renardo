# Tutoriel 5 : Référencer les attributs du Player

# Vous pouvez définir des variables en dehors d'un Player
pitches = P[0,1,2,3,4]
harmony = pitches + 2

print(pitches)
print(harmony)

p1 >> pluck(pitches)
p2 >> star(harmony)

# Si vous fixez la durée du second, cela pourrait ne pas avoir l'effet escompté
p1 >> pluck(pitches)
p2 >> star(harmony, dur=1/2)

# Il est possible qu'un objet Player joue exactement ce qu'un autre Player joue.
# Pour qu'un Player en suive un autre, utilisez simplement la méthode follow :
p1 >> pluck(pitches)

p2 >> star(dur=1/2).follow(p1) + 2

# Vous pouvez aussi référencer explicitement des attributs comme le pitch ou la durée :

p2 >> star(p1.pitch) + 2  # ceci équivaut à .follow(p1)

# Fonctionne aussi pour d'autres attributs
p1 >> pluck(pitches)
p2 >> star(dur=p1.dur).follow(p1) + 2

# Vous pouvez référencer, et tester, la valeur actuelle
# Le == renvoie 1 si vrai et 0 si faux
print(p1.degree)
print(p1.degree == 2)

# Cela vous permet de faire des conditions comme
p1 >> pluck([0,1,2,3], amp=(p1.degree==1))

p1 >> pluck([0,1,2,3], amp=(p1.degree>1))

# Ou changez-le pour un autre amp en multipliant par 4
p1 >> pluck([0,1,2,3], amp=(p1.degree==1)*4)

# Enchaînez plusieurs conditions
p1 >> pluck([0,1,2,3], amp=(p1.degree==1)*4 + (p1.degree==2)*1)

# Ce qui est équivalent à
p1 >> pluck([0,1,2,3], amp=p1.degree.map({1:4, 2:1}))

# Ou changez-le pour un autre amp en multipliant par 4
p1 >> pluck([0,1,2,3], amp=(p1.degree==1))

p1 >> pluck([0,1,2,3], amp=(p1.degree>1))

# --------------------------------------------------------------------------
# Valeurs par défaut globales et « stickiness » (persistance)
# --------------------------------------------------------------------------

# Tout comme Scale et Root (voir le Tutoriel 8), les attributs communs oct, dur,
# sus, pan, rate et sample possèdent chacun un `.default` global modifiable :

Oct.default = 6
Dur.default = 1
Sus.default = 1
Pan.default = 0
Rate.default = 1
Sample.default = 0

# Tout Player qui n'a PAS défini cet attribut lui-même récupérera la nouvelle
# valeur dès son prochain événement -- inutile de le relancer avec '>>' :
p1 >> pluck(pitches)
Oct.default = 5  # p1 descend immédiatement d'une octave, tout en continuant à jouer

# Mais dès que vous définissez un attribut explicitement sur un Player, celui-ci
# « colle » (sticky) : le Player conserve cette valeur même si vous changez
# ensuite la valeur par défaut globale.
p1 >> pluck(pitches, oct=4)
Oct.default = 7
# p1 est toujours à oct=4 ici

# Si vous préférez que les attributs se comportent exactement comme scale/root --
# c'est-à-dire qu'ils reviennent toujours à la valeur par défaut globale en vigueur
# chaque fois que vous relancez le Player sans ce mot-clé, même si vous lui aviez
# donné une valeur explicite auparavant -- activez cet interrupteur :
PlayerDefaults.sticky_override = False

p1 >> pluck(pitches)  # pas de mot-clé 'oct' ici, donc récupère Oct.default (7)
Oct.default = 5

# Rétablissez le comportement par défaut ("sticky") :
PlayerDefaults.sticky_override = True
