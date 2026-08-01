# Tutoriel 15 : Référence des générateurs de patterns


# Il existe plusieurs autres classes de Pattern dans Renardo qui vous aident à générer des tableaux de nombres, mais qui se comportent
# aussi de la même façon que le Pattern de base. Pour voir quels Patterns existent et essayer de les utiliser, exécutez
print(classes(Patterns.Sequences))



####################
# PEuclid
# PEuclid(n, k)
# Renvoie le rythme euclidien qui répartit 'n' impulsions sur 'k' pas de la manière la plus régulière possible.

# 3 impulsions sur 8 pas
print(PEuclid(3, 8))



####################
# PDur
# PDur(n, k, start=0, dur=0.25)
# Renvoie les durées réelles basées sur des rythmes euclidiens (voir PEuclid), où dur est la longueur de chaque pas.
# Répartit 'n' impulsions sur 'k' pas de la manière la plus régulière possible

print(PDur(3,8)) # P[0.75, 0.75, 0.5]

print(PDur(5,8))

# Donne une liste de 3 dur, suivie d'une liste de 5 dur
print(PDur([3,5],8))

d1 >> play("x", dur=PDur(5,8))



####################
# PIndex
# Renvoie l'index en cours d'accès

print(PIndex())
print(PIndex()*4)



####################
# PSine
# PSine(n=16)
# Renvoie les valeurs d'un cycle d'onde sinusoïdale divisé en 'n' parties

# Divisé en 5 parties
print(PSine(5))

# Divisé en 10
print(PSine(10))



####################
# PTri
# PTri(start, stop=None, step=None)
# Renvoie un Pattern équivalent à `Pattern(range(start, stop, step)) avec sa forme inversée ajoutée à la suite.
# Pensez-y comme à un "Tri"angle.

# Monte jusqu'à 5 puis redescend jusqu'à 1
print(PTri(5))

# Monte jusqu'à 8 puis redescend jusqu'à 1
print(PTri(8))

# De 3 à 10, puis redescend jusqu'à 4
print(PTri(3,10))

# De 3 à 30, par pas de 2, puis redescend jusqu'à 4
print(PTri(3,20,2))

# Monte jusqu'à 4, puis redescend jusqu'à 1, puis monte jusqu'à 8, puis redescend jusqu'à 1
print(PTri([4,8]))

p1 >> pluck(PTri(5), scale=Scale.default.pentatonic)

# Identique à
p1 >> pluck(PRange(5) | PRange(5,0,-1), scale=Scale.default.pentatonic)



####################
# PRand
# PRand(start, stop=None)
# Renvoie un entier aléatoire entre start et stop.

# Renvoie un entier aléatoire entre 0 et start.
print(PRand(8)[:5])

# Renvoie un entier aléatoire entre start et stop.
print(PRand(8,16)[:5])

# Si start est un type conteneur, renvoie un élément aléatoire de ce conteneur.
print(PRand([1,2,3])[:5])

# Vous pouvez fournir une graine (seed)
print(PRand([1,2,3], seed=5)[:5])

# Ou définir une graine par défaut globale au lieu de passer seed= à chaque fois.
# Elle s'applique à tout générateur aléatoire (PRand, PWhite, etc.) créé
# par la suite -- les générateurs déjà existants conservent l'aléatoire qu'ils avaient déjà.
Seed.default = 5

print(PRand([1,2,3])[:5])
print(PWhite()[:5])

# Un seed= explicite sur un générateur spécifique continue de prendre le pas sur la valeur par défaut globale
print(PRand([1,2,3], seed=99)[:5])

# Remettez-la à None pour restaurer un aléatoire normal, sans graine
Seed.default = None

# Continue à générer une mélodie aléatoire
p1 >> pluck(PRand(8))

# Crée une liste aléatoire, et itère sur cette même liste
p1 >> pluck(PRand(8)[:3])



####################
# PRhythm
# PRhythm prend une liste de durées simples et de tuples contenant des valeurs qui peuvent être fournies à `PDur`

# Ce qui suit joue le hi-hat avec un rythme euclidien de 3 impulsions sur 8 pas
d1 >> play("x-o-", dur=PRhythm([2,(3,8)]))

print(PRhythm([2,(3,8)]))



####################
# PSum
# PSum(n, total)
# Renvoie un Pattern de longueur 'n' dont la somme est égale à 'total'

# Renvoie un pattern de longueur 2, dont les éléments somment à 8
print(PSum(3,8))

# Renvoie un pattern de longueur 5, dont les éléments somment à 4
print(PSum(5,4))



####################
# PStep
# PStep(n, value, default=0)
# Renvoie un Pattern dont chaque n-ième terme vaut 'value', sinon 'default'

# Tous les 4, met 1, sinon la valeur par défaut 0
print(PStep(4,1))

# Tous les 8, met 6, sinon 4
print(PStep(8,6,4))

# Tous les 5, met 2, sinon 1
print(PStep(5,2,1))



####################
# PWalk
# PWalk(max=7, step=1, start=0)

# Par défaut, renvoie un pattern dont chaque élément est aléatoirement 1 de plus ou 1 de moins que le précédent
print(PWalk()[:16])

# En changeant step
print(PWalk(step=2)[:16])

# Avec max
print(PWalk(max=2)[:16])

# Commence à un nombre non nul
print(PWalk(start=6)[:16])



####################
# PWhite
# PWhite(lo=0, hi=1)
# Renvoie des valeurs aléatoires à virgule flottante entre 'lo' et 'hi'

# Lo vaut 0 par défaut, hi vaut 1 par défaut
print(PWhite()[:8])

# Renvoie des nombres aléatoires entre 1 et 5
print(PWhite(1,5)[:8])



####################
# Patterns générateurs personnalisés

# Des patterns générateurs personnalisés peuvent être créés en sous-classant GeneratorPattern
# et en redéfinissant `GeneratorPattern.func`

class CustomGeneratorPattern(GeneratorPattern):
    def func(self, index):
        return int(index / 4)

print(CustomGeneratorPattern()[:10])

# Cela peut être fait de façon plus concise en utilisant `GeneratorPattern.from_func`,
# en passant une fonction qui prend un index et renvoie un élément de pattern.

def some_func(index):
    return int(index / 4)

print(GeneratorPattern.from_func(some_func)[:10])

# On peut aussi utiliser des lambdas
print(GeneratorPattern.from_func(lambda index: int(index / 4))[:10])

