### Point dans le temps persistant

# Un point dans le temps que vous pouvez réactiver plusieurs fois (plus utile qu'un PointInTime à usage unique)

# Crée un point persistant pour les sections de refrain (chorus)
somebreak = ppit() # ou PersistentPointInTime()

# Démarre une boucle musicale
Clock.bpm=160
b1 >> blip([0,1,5,[2,[_,1]]], dur=var([.5,.25],8), sus=1, amp=1.5*P[.4,.7,1,.7], lpf=800, oct=[4,5,6])
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2,2/3],[12,4]), rate=(1.2,2.4), lpf=800)

# un petit métronome pour le fun
p7 >> pluck([4,0,0,0], oct=6, lpf=2000)

# Programme ce qui se passe pendant la coupure

# {somebreak} coupe la batterie pendant 16 temps
d2.amplify=0 # coupure (on coupe la batterie)
k2.amplify=0
# {somebreak+16} # Remet la batterie 16 temps plus tard
d2.amplify=1
k2.amplify=1

# Vous pouvez maintenant déclencher la coupure plusieurs fois !

# Première coupure 16 temps après la fin de la mesure (mesure en 4/4)
somebreak.beat = mod(4) + 16

# Attendez un peu, puis déclenchez une deuxième coupure plus tard
somebreak.beat = mod(4) + 32


# Chaque déclenchement exécute le même pattern musical !

### Point dans le temps récurrent (réexécute le code périodiquement)

# Crée un point récurrent pour des patterns de hi-hat toutes les 4 temps
hihat_pattern = RecurringPointInTime(period=16)
print(f"Déclencheur de hi-hat récurrent créé : {hihat_pattern}")

# Programme le pattern de hi-hat
# {hihat_pattern}
hh >> play("--[--]-", dur=1/4, amp=0.4).stop(2)

# Démarre le pattern récurrent
hihat_pattern.beat = now() + 4
print(f"Le pattern de hi-hat se répétera toutes les 4 temps à partir de {Clock.now() + 4}")


#### Double rpit

rpit1 = rpit(16)
rpit2 = rpit(12)

b1 >> blip(dur=.25, sus=[1,.75,.25], lpf=800, amp=[.3,.7,1,.6])

#{rpit1}
b1.oct=[5,5,3,7]
#{rpit2}
b1.oct=[6,4]

rpit1.beat=now()+4
rpit2.beat=now()+4








# Crée un pattern récurrent plus long pour des chutes de basse (bass drops)
drop_cycle = RecurringPointInTime(period=16)

# {drop_cycle}
# Grosse chute de basse toutes les 16 temps
b2 >> bass([0], dur=4, amp=1.5, lpf=400)
d2 >> play("X-------X-------", amp=1.8)

drop_cycle.beat = Clock.now() + 16
print(f"La chute de basse se répétera toutes les 16 temps")

# Crée un pattern de montée (build-up) qui se produit entre les chutes de basse
# {drop_cycle + 8}
# Montée 8 temps après chaque chute
p2 >> pluck([0, 2, 4, 7], dur=1/4, amp=var([0.5, 1], 4))
d3 >> play("x-x-x-x-", dur=1/2, amp=0.6)

### Effacer pour annuler des événements programmés

# Toutes les classes PointInTime ont une méthode clear() pour supprimer les opérations programmées

# Arrête un pattern récurrent
reccurent_start_of_drum = rpit(period=8)

# {drum_pattern_to_stop}
d4 >> play("X-o-", dur=1/2)

# Démarre le pattern
reccurent_start_of_drum.beat = now() + 4

# Plus tard, arrête-le complètement
reccurent_start_of_drum.clear()
print("Le pattern de batterie ne redémarrera plus avec clean()")
