
# Quand vous demandez à un Player de jouer un instrument comme...
b1 >> jbass(degree=[0,5,2], dur=.75)

# ... la partie jbass est dans Renardo un objet appelé un Instrument
# Ici nous allons regarder SCInstrument, le type d'Instrument proposé par le backend SuperCollider de Renardo (ReaperInstrument sera traité assez différemment)
# Disons que nous voulons créer une nouvelle basse (une copie du jbass de FoxDot pour l'exemple).
# Nous pouvons définir directement un nouveau synthdef SuperCollider dans une chaîne multi-lignes et l'utiliser pour créer une instance de SCInstrument comme ceci :

jjbass = SCInstrument(shortname="jjbass",code="""
SynthDef.new(\\jjbass,
{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
freq=(freq / 4);
amp=(amp * 0.5);
osc=LFTri.ar(freq, mul: amp);
env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\\sin), doneAction: 0);
osc=(osc * env);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
ReplaceOut.ar(bus, osc)}).add;
""")

b1 >> jjbass(degree=[0,5,2], dur=.75)

# ...ou comme ceci :

sccode = """
SynthDef.new(\\jjbass,
{|amp=1, sus=1, pan=0, freq=0, vib=0, fmod=0, rate=0, bus=0, blur=1, beat_dur=1, atk=0.01, decay=0.01, rel=0.01, peak=1, level=0.8|
var osc, env;
sus = sus * blur;
freq = In.kr(bus, 1);
freq = [freq, freq+fmod];
freq=(freq / 4);
amp=(amp * 0.5);
osc=LFTri.ar(freq, mul: amp);
env=EnvGen.ar(Env([0, peak, level, level, 0], [atk, decay, max((atk + decay + rel), sus - (atk + decay + rel)), rel], curve:\\sin), doneAction: 0);
osc=(osc * env);
osc = Mix(osc) * 0.5;
osc = Pan2.ar(osc, pan);
ReplaceOut.ar(bus, osc)}).add;
"""
jjbass = SCInstrument(shortname="jjbass",code=sccode)

# Les SCInstruments peuvent être édités à la volée (live edit) et seront rechargés à chaque fois dans le serveur SuperCollider
# Par exemple, pendant que le Player b1 joue, changez freq=(freq / 4) en freq=(freq / 2) dans le code précédent et évaluez
# La hauteur devrait maintenant monter d'une octave

# Si cela vous semble difficile à comprendre, ne vous inquiétez pas ! Le langage SuperCollider (SCLang) n'est pas facile à aborder...
# Un vrai tutoriel pour comprendre les bases de la synthèse SuperCollider devrait bientôt arriver ici :)

# Mais regardons maintenant quelque chose de crucial pour la personnalisation de Renardo : les valeurs par défaut des arguments !
# Les objets SCInstrument ont un champ "arguments" où vous pouvez définir les valeurs par défaut utilisées par SCInstrument quand rien n'est fourni

jjbass.arguments={"dur":.5}

b1 >> jjbass(degree=[0,5,2]) # pas de dur fourni ici, donc dur=.5 sera utilisé

# Vous pouvez aussi utiliser cela pour un SCInstrument prédéfini, et c'est également valable pour les paramètres d'effets

blip.arguments={"dur":.25, "lpf":2000}
b1 >> blip()

# pour réinitialiser, vous pouvez faire
blip.arguments={}

# Vous pouvez utiliser cela dans votre fichier de démarrage pour commencer une session de live coding avec des instruments préparés/personnalisés
# ... mais idéalement, n'oubliez pas de nous montrer vos personnalisations de démarrage si vous jouez en public, pour soutenir une musique ouverte et reproductible

# Les SCInstruments sont les instruments par défaut, historiques, hérités de FoxDot où ils étaient appelés SynthDefProxies. Le mécanisme historique de FoxDot pour définir la synthèse SynthDef via un binding python/SCLang personnalisé a été supprimé au profit d'une écriture SCLang plus directe, plus facile à maintenir et à personnaliser.

# Pour aller plus loin, vous pouvez regarder le dossier sccode_library dans votre répertoire utilisateur (voir la section répertoire utilisateur des paramètres)
# Vous pouvez aussi y personnaliser les instruments et effets de Renardo, et bientôt les envoyer vers le serveur de collections communautaires https://collections.renardo.org