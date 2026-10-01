# Tutoriel 14 : Référence des attributs du Player
# --- TODO : ceci doit être mis à jour


# Pour voir tous les attributs :
print(Player.get_attributes())

# Vous pouvez voir quels effets sont disponibles en évaluant
print(FxList)

# Utilisons le filtre passe-haut comme exemple. Vous pouvez voir qu'il est décrit
# comme ceci :
# "<Fx 'highPassFilter' -- args: hpr, hpf>"

# Chaque effet a un argument "master" puis des arguments enfants. Ici l'argument
# maître est "hpf" (abréviation de high pass filter, filtre passe-haut) et l'argument
# enfant est "hpr" (abréviation de high pass resonance, résonance du passe-haut). L'effet n'est ajouté que lorsque
# l'argument maître est différent de zéro :
d1 >> dirt([0,4,2,1], dur=1/2, hpf=4000)

# Ceci règle le filtre passe-haut à 4000 Hz, de sorte que seules les fréquences du signal
# audio *au-dessus* de cette valeur sont réellement entendues. Changeons la valeur de résonance. Sa
# valeur par défaut est 1, alors réduisons-la
d1 >> dirt([0,4,2,1], dur=1/2, hpf=4000, hpr=0.3)


# Remarquez-vous une différence ? Nous pouvons utiliser des patterns / vars dans nos effets pour les faire
# changer dans le temps :
d1 >> dirt([0,4,2,1], dur=1/2, hpf=linvar([0,4000],8), hpr=P[1,1,0.3].stretch(8))




####################
# Référence
####################



####################
# amp - Amplitude (par défaut 1)
# Règle le volume de la note/du pattern

d1 >> play("*", dur=1/2, amp=1)

# Demi-volume
d1 >> play("*", dur=1/2, amp=.5)

# Créer un pattern avec amp
d1 >> play("*", dur=1/2, amp=[1,0,1,1,0])



####################
# amplify - Change amp, en multipliant la valeur existante (au lieu de l'écraser)

# Créer un pattern avec amp
d1 >> play("*", dur=1/2, amp=[1,0,1,1,0])
d1 >> play("*", dur=1/2, amplify=[.5,1,0])

# Met en place une "descente" (drop) dans la musique (joue à plein volume pendant 28, puis à 0 pendant 4)
p1 >> blip([0,1,2,3], amplify=var([1,0],[28,4]))



####################
# bend



####################
# benddelay - Voir bend



####################
# bits
# La profondeur de bits, en nombre de bits, à laquelle le signal est réduit ;
# c'est une valeur comprise entre 1 et 24, les autres valeurs étant ignorées.
# Utilisez crush pour régler l'ampleur de la réduction du bitrate (par défaut 8)



####################
# bitcrush - Voir bits



####################
# blur



####################
# bpf - Band Pass Filter (filtre passe-bande)



####################
# bpnoise - Voir bpf



####################
# bpr - Voir bpf



####################
# bpm



####################
# buf



####################
# channel



####################
# chop
# « Découpe » le signal en morceaux à l'aide d'une onde d'impulsions basse fréquence sur le sustain d'une note.



####################
# coarse



####################
# comb delay - Voir echo



####################
# crush



####################
# cut
# Coupe une durée
p1 >> pluck(P[:8], dur=1/2, cut=1/8)
p1 >> pluck(P[:8], dur=1/2, cut=1/4)
p1 >> pluck(P[:8], dur=1/2, cut=1/2)



####################
# cutoff



####################
# decay - Voir echo



####################
# degree - Le degree de la note, ou pitch, peut être spécifié par mot-clé (aussi le premier argument positionnel)
p1 >> blip(degree=[0,1,2,3])

# Ce qui équivaut à :
p1 >> blip([0,1,2,3])

# Ne joue que la note "root" (fondamentale) de l'accord
b1 >> bass(p1.degree[0])



####################
# delay - Une durée à attendre avant d'envoyer l'information à SuperCollider (par défaut 0)

# Retarde une note sur 3 de .1
p1 >> blip([0,1,2,3], delay=[0,0,0.1])

# Retarde une note sur 3 de .5
p1 >> blip([0,1,2,3], delay=[0,0,0.5])

# Joue la note une fois pour chaque délai différent
p1 >> blip([0,1,2,3], delay=(0,0.1))

p1 >> blip([0,1,2,3], delay=(0,0.25))

p1 >> blip([0,1,2,3], delay=(0,.1,.2,.3))



####################
# dist



####################
# dur - Durées (par défaut 1, et 1/2 pour le Sample Player)



####################
# echo
# Mot-clé de titre : echo, mot-clé(s) d'attribut : decay
# Règle le temps de decay de tout effet d'écho en temps, fonctionne mieux sur le Sample Player (par défaut 0)
# Multiplié par la valeur de sustain
d1 >> play("x-o-", echo=0.1)

d1 >> play("x-o-", echo=0.5)

p1 >> pluck(P[:8], echo=.25)

p1 >> pluck(P[:8], echo=.5)

p1 >> pluck(P[:8], echo=.5, decay=.5)



####################
# env



####################
# fmod



####################
# formant



####################
# freq



####################
# hpf - High Pass Filter (filtre passe-haut)
# Filtre toutes les fréquences en dessous de la valeur donnée, en supprimant les fréquences basses

# 4000 hertz
p1 >> pluck(P[:8], dur=1/2, hpf=4000)

# HPF vaut 0 pendant 4 temps, puis 4000 pendant 4 temps
p1 >> pluck(P[:8], dur=1/2, hpf=var([0,4000],[4,4]))

# Changement linéaire du hpf, met 4 temps pour passer de 0 à 4000, puis 4 temps pour revenir à 0
p1 >> pluck(P[:8], dur=1/2, hpf=linvar([0,4000],[4,4]))

# Changement linéaire du hpf, met 8 temps pour passer de 0 à 4000, puis revient directement à 0
p1 >> pluck(P[:8], dur=1/2, hpf=linvar([0,4000],[8,0]))

# Avec un changement de résonance (par défaut 1)
p1 >> pluck(P[:8], dur=1/2, hpf=linvar([0,4000],[8,0]), hpr=.5)

# Avec un changement de résonance sous forme de linvar
p1 >> pluck(P[:8], dur=1/2, hpf=linvar([0,4000],[8,0]), hpr=linvar([0.1,1],12))



####################
# hpr - Voir hpf



####################
# lpf - Low Pass Filter (filtre passe-bas)
# Filtre toutes les fréquences au-dessus de la valeur donnée, en supprimant les fréquences hautes

# 4000 hertz
p1 >> pluck(P[:8], dur=1/2, lpf=400)

# Avec un changement de résonance sous forme de linvar
p1 >> pluck(P[:8], dur=1/2, lpf=linvar([500,4000],[8,0]), lpr=linvar([0.1,1],12))



####################
# lpr - Voir lpf



####################
# midinote



####################
# pan
# Panoramique, où -1 est tout à gauche, 1 est tout à droite (par défaut 0)



####################
# pitch - Voir degree



####################
# pshift



####################
# oct



####################
# rate
# Mot-clé variable utilisé pour divers changements sur un signal. Par ex. la vitesse de lecture du Sample Player (par défaut 1)



####################
# room
# Mot-clé de titre : room, mot-clé(s) d'attribut : mix

# L'argument room spécifie la taille de la pièce (room)
d1 >> play("x-o-", room=0.5)

# Mix est le mélange dry/wet de la réverbération, c'est-à-dire la proportion de réverbération mélangée à la source. 1 est tout réverbération, 0 pas de réverbération du tout. (Par défaut 0.1)
d1 >> play("x-o-", room=0.5, mix=.5)



####################
# Reveb
# Voir Room



####################
# sample
# Mot-clé spécial pour les Sample Players ; sélectionne un autre fichier audio dans la banque de samples pour un caractère de sample.



####################
# scale



####################
# shape



####################
# slide - Slide To
# « Glisse » la valeur de fréquence d'un signal vers freq * (slide+1) sur la durée d'une note (par défaut 0)

p1 >> pluck(P[:8], dur=1/2, slide=1)

p1 >> pluck(P[:8], dur=1/2, slide=12)

p1 >> pluck(P[:8], dur=1/2, slide=var([0,-1],[12,4]))



####################
# slidedelay



####################
# slidefrom



####################
# slider



####################
# spread



####################
# spin



####################
# striate



####################
# stutter



####################
# sus - Sustain (par défaut `dur`)



####################
# swell



####################
# vib - Vibrato
# Vibrato - Mot-clé de titre : vib, mot-clé(s) d'attribut : Vibrato (par défaut 0)

p1 >> pluck(P[:8], dur=1/2, vib=12)

# Avec l'attribut enfant vibdepth (par défaut 0.2)
p1 >> pluck(P[:8], dur=1/2, vib=12, vibdepth=0.5)



####################
# vibdepth - Voir vib
