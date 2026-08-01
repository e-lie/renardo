# Tutoriel 4 : Utiliser les patterns


# Les objets Player utilisent les listes Python, plus communément appelées tableaux (arrays) dans d'autres langages,
# pour se séquencer. Vous les avez déjà utilisées précédemment, mais elles ne sont pas vraiment
# flexibles pour la manipulation. Par exemple, essayez de multiplier une liste par deux comme ceci :

print([1, 2, 3] * 2)

# Le résultat est-il celui que vous attendiez ?

# Renardo utilise un type de conteneur appelé 'Pattern' pour aider à résoudre ce problème.
# Ils se comportent comme des listes normales, mais toute opération mathématique effectuée dessus est appliquée à chaque élément
# de la liste, et ce terme à terme si un second pattern est utilisé. Un pattern basique se crée
# comme vous le feriez avec une liste ou un tuple normal, mais précédé d'un 'P'.

print(P[1,2,3] * 2)

print(P[1,2,3] + 100)

# Dans cette opération, le résultat contient toutes les combinaisons des deux patterns, c'est-à-dire :
# [1+3, 2+4, 3+3, 1+4, 2+3, 3+4]
print(P[1,2,3] + [3,4])

# Vous pouvez utiliser la syntaxe de slicing de Python pour générer une série de nombres

print(P[:8])

print(P[0,1,2,3:20])

print(P[2:15:3])

# Essayez d'autres opérateurs mathématiques et observez les résultats obtenus.
print(P[1,2,3] * (1,2))

# Les objets Pattern entrelacent aussi automatiquement toute liste imbriquée.
# Comparez
# Liste normale :
for n in [0,1,2,[3,4],5]:
    print(n)

# avec
# Pattern
for n in P[0,1,2,[3,4],5]:
    print(n)

# Utilisez des PGroups si vous souhaitez éviter ce comportement. Ceux-ci peuvent être
# implicitement spécifiés sous forme de tuples dans les Patterns :
for n in P[0,1,2,(3,4)]:
    print(n)

# Ceci est un PGroup :
print(P(0,2,4) + 2)

print(type(P(0,2,4) + 2))

# En Python, vous pouvez générer une plage d'entiers avec la syntaxe range(start, stop, step).
# Par défaut, start vaut 0 et step vaut 1.
print(list(range(10))) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Vous pouvez utiliser PRange(start, stop, step) pour créer un objet Pattern avec les valeurs équivalentes :
print(PRange(10)) # P[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# P[0, 2, 2, 6, 4, 10, 6, 14, 8, 18]
# [0*1, 1*2, 2*1, 3*2, 4*1, 5*2, 6*1, 7*2, 8*1...]
print(PRange(10) * [1, 2])           # Comportement de la classe Pattern

# Ajouter une liste (ou un Pattern) à un Pattern ajoutera les valeurs des
# éléments à l'autre, là où des listes Python auraient été concaténées.
print(PRange(10) + [0,10])

# Pour concaténer des Patterns, utilisez l'opérateur pipe comme ceci :
print(PRange(10) | [0,10])
# Renardo convertit automatiquement tout objet transmis par pipe à un Pattern vers la classe Pattern de base
# afin que vous n'ayez pas à vous soucier de vérifier que tout est du bon type.

# Joue toutes les valeurs ensemble
p1 >> pluck(P(4,6,8))
p1 >> pluck(P[0,1,2,P(4,6,8),7,8])

# Répartit les valeurs sur la "dur" (durée) actuelle, par ex. si dur vaut 2 temps, chaque valeur sera jouée avec un espacement de 2/3 de temps
p1 >> pluck(P*(0,2,4), dur=1/2)
p1 >> pluck(P*(0,2,4), dur=1)
p1 >> pluck(P*(0,2,4), dur=2)
p1 >> pluck(P[0,1,2,P*(4,6,8),7,8], dur=1)

# C'est la même chose que P* mais une fois sur deux, les notes jouées sont réparties sur la valeur de dur.
p1 >> pluck(P/(0,2,4), dur=1/2)
p1 >> pluck(P/(0,2,4), dur=1)
p1 >> pluck(P/(0,2,4), dur=2)
p1 >> pluck(P[0,1,2,P/(4,6,8),7,8], dur=1)

# Répartit les valeurs sur le "sus" actuel, par ex. si dur vaut 2 temps et sus vaut 3 temps, chaque valeur sera jouée avec un espacement de 1 temps.
p1 >> pluck(P+(0,2,4), dur=2, sus=3)
p1 >> pluck(P+(0,2,4), dur=2, sus=1)
p1 >> pluck(P[0,1,2,P+(4,6,8),7,8], dur=1, sus=3)

# Répartit les premières (longueur - 1) valeurs avec un espacement égal à la dernière valeur entre chacune
# Joue 0,2,4 avec un espacement de 0.5 :
p1 >> pluck(P^(0,2,4,0.5), dur=1/2)

# Les Patterns disposent de plusieurs méthodes pour manipuler leur contenu
help(Pattern)

# Pattern standard
print(P[:8])

# Mélange le pattern en le rendant aléatoire
print(P[:8].shuffle())

# Ajoute une version inversée du pattern à la suite du pattern
print(P[:8].palindrome())

# Décale le pattern de n (par défaut 1)
print(P[:8].rotate())
print(P[:8].rotate(3))
print(P[:8].rotate(-3))

# Prend le pattern et le répète autant de fois que nécessaire pour atteindre n éléments dans le pattern
print(P[:8].stretch(12))
print(P[:8].stretch(20))

# Inverse un pattern
print(P[:8].reverse())

# Boucle un pattern n fois
print(P[:8].loop(2))

# Ajoute un décalage (offset)
print(P[:8].offadd(5))

# Ajoute un décalage multiplicatif
print(P[:8].offmul(5))

# Stutter - Répète chaque élément n fois
print(P[:8].stutter(5))

# Amen
# Fusionne et entrelace les deux premiers et les deux derniers éléments de sorte qu'un
# pattern de batterie "x-o-" devienne "(x[xo])-o([-o]-)" et imite
# le rythme du célèbre « amen break »
d1 >> play(P["x-o-"].amen())
print(P[:8].amen())

# Bubble
# Fusionne et entrelace les deux premiers et les deux derniers éléments de sorte qu'un
# pattern de batterie "x-o-" devienne "(x[xo])-o([-o]-)
d1 >> play(P["x-o-"].bubble())
print(P[:8].bubble())

