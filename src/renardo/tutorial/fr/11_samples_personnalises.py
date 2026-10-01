# Tutoriel 11 : Jouer des samples personnalisés

# Vous pouvez utiliser vos propres samples en déposant simplement des fichiers audio dans les répertoires de samples existants de Renardo.
# Ceux-ci se trouvent dans le répertoire 'snd' à la racine de l'installation de Renardo
# (par ex., 'C:\Python27\Lib\site-packages\Renardo\snd').

# Vous avez vu plus tôt comment travailler avec des samples en utilisant play(). Vous pouvez aussi jouer des samples avec loop().
s1 >> loop('foxdot')

# Vous remarquerez peut-être que cela ne fait que jouer en boucle la première partie du sample.
# Vous pouvez ajuster ce comportement avec bon nombre des arguments que nous avons déjà vus pour contrôler d'autres synthés. dur est un bon point de départ.
s1 >> loop('foxdot', dur=4)

# Si vous avez un dossier plein de samples que vous voulez utiliser dans Renardo, vous pouvez appeler loop() avec le chemin complet vers le sample.
s1 >> loop('/path/to/samples/quack.wav')

# Si vous donnez à loop le chemin d'un dossier, il jouera le premier sample qu'il trouve. Vous pouvez changer le sample joué avec l'argument sample=.

# Joue le premier sample de ma collection
s1 >> loop('/path/to/samples')

# Joue le deuxième sample de ma collection
s1 >> loop('/path/to/samples', sample=1)

# Si vous comptez utiliser beaucoup de samples d'un dossier, vous pouvez l'ajouter au chemin de recherche des samples. Renardo cherchera dans tous ses chemins de recherche un sample correspondant lorsque vous lui donnez un nom.
Samples.addPath('/path/to/samples')
s1 >> loop('quack')

# Une fois que vous avez un chemin de recherche, vous pouvez utiliser la correspondance de motifs (pattern matching) pour rechercher des samples.

# Joue le 3e sample dans le dossier 'snare'
s1 >> loop('snare/*', sample=2)

# Vous pouvez aussi utiliser * dans les noms de répertoires
s1 >> loop('*_120bpm/drum*/kick*')

# ** signifie "tous les sous-répertoires de manière récursive". Ceci jouera le premier sample
# trouvé sous 'percussion' (par ex. 'percussion/kicks/classic/808.wav')
s1 >> loop('percussion/**/*')
