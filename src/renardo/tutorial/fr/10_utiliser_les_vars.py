# Tutoriel 10 : Utiliser les vars


# Une TimeVar est une abréviation de « Time Dependent Variable » (variable dépendante du temps) et est une fonctionnalité clé de Renardo.
# Une TimeVar possède une série de valeurs entre lesquelles elle change après un nombre prédéfini de temps
# et se crée en utilisant un objet var avec la syntaxe var([liste_de_valeurs],[liste_de_durées]).

# Génère les valeurs : 0,0,0,0,3,3,3,3...
a = var([0,3],4)            # La durée peut être une seule valeur
print(int(Clock.now()), a)  # 'a' a initialement la valeur 0
# >>> 0, 0                  # La première valeur peut différer...

print(int(Clock.now()), a)   # Après 4 temps, la valeur passe à 3
# >>> 4, 3

print(int(Clock.now()), a)   # Après 4 temps de plus, la valeur repasse à 0
# >>> 8, 0

# La durée peut aussi être une liste
a = var([0,3],[4,2])
print(int(Clock.now()), a)

# Quand une TimeVar est utilisée dans une opération mathématique, les valeurs qu'elle affecte deviennent elles aussi des TimeVars
# qui changent d'état lorsque la TimeVar d'origine change d'état -- cela fonctionne même avec les patterns :
a = var([0,3], 4)
print(int(Clock.now()), a + 5)   # Quand le temps est 0, a vaut 5
# >>> 5

print(int(Clock.now()), a + 5)   # Quand le temps est 4, a vaut 8
# >>> 8

b = PRange(4) + a
print(int(Clock.now()), b)   # Après 8 temps, la valeur passe à 0
# >>> P[0, 1, 2, 3]

print(int(Clock.now()), b)   # Après 12 temps, la valeur passe à 3
# >>> P[3, 4, 5, 6]

# Utilisez 'var' avec vos objets Player pour créer des progressions d'accords.
a = var([0,4,5,3], 4)
b1 >> bass(a, dur=PDur(3,8))
p1 >> charm(a + (0,2), dur=PDur(7,16))

# Vous pouvez ajouter une 'var' à un objet Player ou à une var.
b1 >> bass(a, dur=PDur(3,8)) + var([0,1],[3,1])

b = a + var([0,10],8)

print(int(Clock.now()), (a, b))

# Mettre à jour les valeurs d'une 'var' la mettra à jour partout ailleurs
a.update([1,4], 8)

print(int(Clock.now()), (a, b))

# Les vars peuvent être nommées ...
var.chords = var([0,4,5,4],4)

# Et utilisées plus tard
b1 >> pluck(var.chords)

# Tout Player utilisant la var nommée sera mis à jour
var.chords = var([0,1,5,3],4)

# Vous pouvez aussi utiliser une 'linvar' qui change ses valeurs progressivement dans le temps
# Change la valeur de 0 à 1 sur 16 temps
c = linvar([0,1],16)

# Exécutez ceci plusieurs fois pour voir les changements se produire
print(int(Clock.now()), c)

# Change l'amp en fonction de cette linvar
p1 >> charm(a, amp=c)

# une 'Pvar' est une 'var' qui peut stocker des patterns (contrairement, par exemple, à des entiers)
d = Pvar([P[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], P[0, 1, 2, 3, 4, 5, 4, 3, 2, 1]], 8)

print(int(Clock.now()), d)

p1 >> charm(a, amp=c, dur=1/4) + d

# Change la gamme toutes les 16 temps
Scale.default = Pvar([Scale.major, Scale.minor],16)

# Vous pouvez même faire en sorte qu'une valeur dure éternellement une fois atteinte, en utilisant une valeur spéciale appelée "inf"

x = var([0, 1, 2, 3], [4, 4, 4, inf])

print(x) # Continuez à exécuter -- la valeur finira par se stabiliser à 3

######################
# Autres types de "var"

# Il existe plusieurs sous-classes de "var" qui renvoient des valeurs comprises entre
# les nombres spécifiés. Par exemple, une "linvar" change
# progressivement de valeur de façon linéaire :

print(linvar([0,1],8)) # continuez à exécuter pour voir la valeur changer entre 0 et 1

# Exemple : augmenter la fréquence de coupure du filtre passe-haut sur 32 temps

p1 >> play("x-o-", hpf=linvar([0,4000],[32,0]))

# D'autres types incluent "sinvar" et "expvar"

print("Linear:", linvar([0, 1], 8))
print("Sinusoidal:", sinvar([0, 1], 8))
print("Exponential:", expvar([0, 1], 8))

#################
# TimeVar de Pattern

# Parfois, on peut vouloir stocker des patterns entiers dans une var, mais
# si on essaie de le faire, ils sont automatiquement entrelacés :

pattern1 = P[0, 1, 2, 3]
pattern2 = P[4, 5, 6, 7]

print(var([pattern1, pattern2], 4))

# Pour stocker des patterns entiers, il faut utiliser une "Pvar" qui
# n'entrelace pas les valeurs, mais stocke les patterns à la place

print(Pvar([pattern1, pattern2], 4))

p1 >> pluck(Pvar([pattern1, pattern2], 4), dur=1/4)



###########################
# Décaler l'heure de départ

# Une autre astuce utile consiste à décaler l'heure de départ de la var. Par
# défaut, c'est lorsque le temps du Clock est 0, mais vous pouvez spécifier une
# valeur différente en utilisant le mot-clé "start"

print(linvar([0, 1], 8))
print(linvar([0, 1], 8, start=2))

# Cela peut être combiné avec Clock.mod() pour démarrer une rampe au début du#
# prochain cycle de 32 temps :

d1 >> play("x-o-", hpf=linvar([0,4000],[32,inf], start=Clock.mod(32)))




