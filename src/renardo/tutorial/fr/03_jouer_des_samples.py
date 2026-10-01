# Tutoriel 3 : Jouer des samples intégrés


# Renardo peut aussi être utilisé pour séquencer et manipuler des samples audio.
# Pour cela, il suffit d'utiliser le SynthDef spécial play.
# Le premier argument du SynthDef play doit être une chaîne de caractères
# au lieu d'une liste de nombres comme vous le feriez pour tout autre SynthDef.
# Chaque caractère représente un fichier audio différent, stocké dans un buffer dans SuperCollider.

# Pour voir quel caractère correspond à quel fichier audio, exécutez
print(DefaultSamples)

# Vous pouvez jouer des samples audio dans les sous-répertoires Renardo/snd/ en utilisant le
# Synth 'play' et en utilisant une chaîne de caractères au lieu d'une liste de notes.
bd >> play("x")

# Un caractère représente un son, et un espace blanc sert de silence, ainsi
# vous pouvez espacer les sons dans le temps :
bd >> play("x..x..x..")

hh >> play(".-")

# Vous pouvez entrelacer des patterns en utilisant des parenthèses
# Ce qui joue comme : "x o  xo "
d1 >> play("(x.)(.x)o.")

# Ce qui suit équivaut à "-------="
hh >> play("---(-=)")

# Mettre des caractères entre crochets les jouera tous dans l'espace d'un temps
# Et ils seront joués comme un seul caractère, pas simultanément, mais en succession rapide
d1 >> play("x-o[-o]")

d1 >> play("x-o[---]")

d1 >> play("x-o[-----]")

d1 >> play("x-o[--------------]")

# et peuvent être placés entre parenthèses comme s'ils étaient eux-mêmes un seul caractère.
d1 >> play("x[--]o(=[-o])")

# Vous pouvez combiner les crochets et parenthèses comme vous voulez : les patterns suivants sont identiques
d1 >> play("x-o(-[-o])")

d1 >> play("x-o[-(o )]")

# Les accolades sélectionnent un son de sample au hasard si vous voulez plus de variété
d1 >> play("x-o{-=[--][-o]}")

# Les chevrons combinent des patterns pour qu'ils soient joués simultanément
d1 >> play("<X...><-...><#...><V...>")

d1 >> play("<X...><.-..><..#.><...V>")

# Chaque caractère est associé à un dossier de fichiers sonores et vous pouvez sélectionner différents
# samples en utilisant l'argument nommé "sample"
d1 >> play("(x[--])xu[--]")

d1 >> play("(x[--])xu[--]", sample=1)

d1 >> play("(x[--])xu[--]", sample=2)

# Change le sample à chaque temps
d1 >> play("(x[--])xu[--]", sample=[1,2,3])

# Vous pouvez superposer deux patterns ensemble - notez le "P", voir le tutoriel 4 pour plus d'informations.
d1 >> play(P["x-o-"] & P[".**"])

# Et changer les effets appliqués à tous les patterns superposés en même temps
d1 >> play(P["x-o-"] & P[".**"], room=0.5)

# Exemple tiré du tutoriel sur le Player, mais avec des samples cette fois
# Conditions...
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x"))

# Ou changez-le pour la banque de samples 2 en multipliant
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x")*2)

# Enchaînez plusieurs conditions
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x")*2 + (d1.degree=="-")*5)

# Ce qui est équivalent à
d1 >> play("x[--]xu[--]x", sample=d1.degree.map({"x":2, "-":5}))
