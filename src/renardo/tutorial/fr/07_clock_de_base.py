# Tutoriel 7 : Bases du Clock


# Pour arrêter tous les objets Player, vous pouvez appuyer sur Ctrl+.  (Maintenez Ctrl et appuyez sur le point)
# Ce qui est un raccourci pour la commande :
Clock.clear()

# Change le tempo (cela prend effet à la prochaine mesure) La valeur par défaut est 120.
Clock.bpm = 144

# Pour voir ce qui est programmé pour être joué.
print(Clock)

# Pour voir quelle est la latence
print(Clock.latency)

# Parfois vous voulez savoir quand commence le prochain cycle de X temps. Pour
# faire cela on utilise la méthode 'mod'. Par exemple si nous voulons voir quand
# commence le prochain cycle de 32 temps, nous pouvons faire
print(Clock.mod(32))

# Parfois vous voulez savoir quand commence le prochain cycle de X temps. Pour
# faire cela on utilise la méthode 'mod'. Par exemple si nous voulons voir quand
# commence le prochain cycle de 32 temps, nous pouvons faire
print(Clock.latency)
