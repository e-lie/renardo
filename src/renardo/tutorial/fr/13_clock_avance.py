# Tutoriel 13 : Clock avancé (ordonnancement classique de FoxDot)

# Pour voir ce qui est programmé pour être joué.
print(Clock)

# Pour voir quelle est la latence
print(Clock.latency)

# Le Clock peut programmer tout objet possédant une méthode __call__ en utilisant
# Il prend un repère de temps absolu pour programmer une fonction
# Clock.schedule a besoin de savoir à quel temps appeler quelque chose
Clock.schedule()   # lève TypeError

# Programme un événement après une certaine durée
# Clock.future a besoin de savoir combien de temps à l'avance appeler quelque chose
Clock.future()     # lève TypeError

# Ceux-ci sont équivalents
Clock.schedule(lambda: print("hello"), Clock.now() + 4)
Clock.future(4, lambda: print("hello"))

# Pour programmer autre chose
Clock.schedule(lambda: print("hello "))

# Nous pouvons appeler quelque chose toutes les n temps
Clock.every(4, lambda: print("hello"))

# Récupère le temps actuel du Clock et ajoute 2. Utile pour la programmation.
print(Clock.now() + 2)

# Émet la commande à la prochaine mesure
nextBar(Clock.clear)

# Avec un décorateur
@nextBar
def change():
    Root.default=4
    Scale.default="minor"
    # etc etc

# Vous pouvez créer votre propre fonction, et la décorer, pour pouvoir
# l'utiliser dans un .every sur un objet Player
@PlayerMethod
def test(self):
    print(self.degree)

p1 >> pluck([0,4]).every(3, "test")

# Et l'annuler avec
p1.never("test")


