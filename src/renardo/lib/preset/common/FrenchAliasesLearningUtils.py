from renardo.lib.runtime import Player, Group, play, Clock, Scale, blip, bbass

joueur1 = Player()
joueur2 = Player()
joueur3 = Player()
joueur4 = Player()
joueur5 = Player()
joueur6 = Player()
joueur7 = Player()
joueur8 = Player()
joueur9 = Player()
joueur10 = Player()


joueurs = Group(joueur1, joueur2, joueur3, joueur4, joueur5, joueur6, joueur7, joueur8, joueur9, joueur10)


def arrêter():
    joueurs.generic_fadeout(8)
    def stopp():
        Clock.clear()
    Clock.schedule(stopp, beat=Clock.next_bar()+8)


batterie = play

Gamme = Scale

mineur = Scale.minor
majeur = Scale.major
pentatonique = Scale.majorPentatonic
pentatoniqueMineur = Scale.minor
egyptien = Scale.egyptian


def basse(*args, **kwargs):
    if 'oct' not in kwargs.keys():
        kwargs['oct'] = 3
    return bbass(*args, **kwargs)


def blup(*args, **kwargs):
    if 'oct' not in kwargs.keys():
        kwargs['oct'] = 6
    return blip(*args, **kwargs)


# bass, blup, piano, harpe, laser(click), space, alva

# blip, click, space, epiano, bbass, harp, noisynth

# elec: space, blip, click, vibass, sinepad, laserbeam, virus, sillyvoice
# lead: noisynth, epiano, square, faim2
# mallets: tubularbell, rissetobell
# borgan, harp,
# pads: drone
# Basses: tb303, acidbass, bbass, filthysaw, mhping, noquarter
# melodic noise: spick, alva
# Noise: bnoise, hnoise, glitcher, shore




