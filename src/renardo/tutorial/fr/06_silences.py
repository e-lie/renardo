# Tutoriel 6 : Silences


# Des silences peuvent être ajoutés en utilisant un objet rest dans le tableau dur
# Le silence coupe le son de la note qui aurait dû être jouée.

# Sans silence, 5 notes (oui, un dur=1 fonctionnerait, mais soyons explicites pour faire contrepoint avec l'exemple suivant)
p1 >> charm([0,1,2,3,4], dur=[1,1,1,1,1])

# Avec un silence ... 4 notes et un silence, la note "4" est coupée pendant 4 temps
p1 >> charm([0,1,2,3,4], dur=[1,1,1,1,rest(4)])
