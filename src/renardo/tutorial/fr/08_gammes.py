# Tutoriel 8 : Gammes


# Par défaut, les objets Player utilisent la gamme de Do Majeur.
# Cela peut être changé en utilisant les arguments nommés 'scale' et 'root'.
# Les gammes peuvent être définies comme un tableau de demi-tons, tel que la gamme Majeure est [0,2,4,5,7,9,11]
# ou l'une des gammes prédéfinies du module Scale, par ex. Scale.minor.
# Root fait référence à la fondamentale de la gamme ; 0 étant Do, 1 est Do#, 2 est Ré, et ainsi de suite.

# La gamme par défaut peut être changée de sorte que tout Player n'utilisant pas de gamme spécifique sera mis à jour.
# Cela se fait avec la syntaxe ci-dessous (chaque ligne est techniquement équivalente) :

Scale.default.set("major")
Scale.default.set(Scale.major)
Scale.default.set([0,2,4,5,7,9,11])

# Ou la même chose, mais en mineur :
Scale.default.set("minor")
Scale.default.set(Scale.minor)
Scale.default.set([0,2,3,5,7,10])

# Pour gagner du temps, vous pouvez aussi faire
Scale.default = "minor"

# C'est la même chose pour la fondamentale (root) :
Root.default.set(1)
Root.default.set("C#")

# Ou :
Root.default.set(2)
Root.default.set("D")

# Pour voir la liste de toutes les gammes, utilisez
print(Scale.names())

# Vous pouvez changer la gamme utilisée par un Player avec le mot-clé 'scale'
p1 >> charm([0,1,2], scale=Scale.minor)

# De la même façon, vous pouvez changer la fondamentale utilisée par les Players avec le mot-clé root
# et l'objet Root.default
p1 >> charm([0,1,2], scale=Scale.minor, root=2)
