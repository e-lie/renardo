### Nouvelle fonctionnalité de planification PointInTime

### Démarre 16 temps plus tard en définissant une valeur Point in Time

b1 >> blip()

pit1 = PointInTime()  # ou pit() pour faire plus court


def footworking():
    Clock.bpm = 160
    b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6])
    k2 >> play("v.(.x)(v*)*v.", dur=.25)
    d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


Clock.schedule(footworking, pit1)

pit1.beat = Clock.now() + 16  # la musique déclarée dans la fonction footworking démarrera dans 16 temps quand vous évaluez cette ligne

### Vous pouvez aussi utiliser la soustraction (ou une autre opération arithmétique sur un point dans le temps) pour démarrer des choses avant le point dans le temps
# Ainsi vous pouvez vous donner rendez-vous à un moment précis

def somebreak_rise():
    b1.fadein(32)  # mélodie montante pendant 32 temps avant la coupure


def somebreak():
    d2.amplify = 0  # coupure (on coupe la batterie)
    k2.amplify = 0


pit2 = pit()  # pit est un alias pour PointInTime

Clock.schedule(somebreak_rise, pit2 - 32)
Clock.schedule(somebreak, pit2)

Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)
pit2.beat = now() + 64

# On refait la même chose en utilisant le nouveau langage de macro

## Plutôt que d'utiliser Clock.schedule avec une fonction, ce qui est difficile et long à coder en live
# et introduit un besoin d'indentation Python, renardo introduit un nouveau langage de macro
# Il est basé sur des commentaires et compilé au moment de l'évaluation.

# La syntaxe de base est #{ moment/numéro_de_temps faisant référence au clock }

# Par exemple, ce qui suit...

# {Clock.now()+8} # démarre dans 8 temps
Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


# ...est équivalent à :

def footworking_func():
    Clock.bpm = 160
    b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
               amplify=0)
    k2 >> play("v.(.x)(v*)*v.", dur=.25)
    d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


Clock.schedule(footworking_func, Clock.now() + 8)

## Exemple de rendez-vous précédent avec la syntaxe macro

pit3 = pit()

Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)

# {pit3-32}
b1.fadein(32)  # mélodie montante pendant 32 temps avant la coupure
# {pit3}
d2.amplify = 0  # coupure (on coupe la batterie)
k2.amplify = 0
# {pit3+32}  # Bonus : arrêt 32 temps après la coupure
Clock.clear()

pit3.beat = now() + 64