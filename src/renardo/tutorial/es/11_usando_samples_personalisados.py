# Tutorial 11: Reproducción de samples personalizadas

# Puede utilizar sus propias samples simplemente soltando archivos de audio en los directorios de muestras existentes de Renardo.
# Estos se encuentran en el directorio 'snd' en la root de la instalación de Renardo
# (por ejemplo, 'C:\Python27\Lib\site-packages\Renardo\snd').

# Viste antes cómo trabajar con samples usando play(). También puede reproducir samples con loop().

s1 >> loop('foxdot')

# Puedes notar que esto es sólo reproducir la primera parte del sample una y otra vez.
# Puedes ajustar el comportamiento con muchos de los argumentos que hemos visto hasta ahora para controlar otros sintetizadores. dur es un buen lugar para empezar.
s1 >> loop('foxdot', dur=4)

# Si tienes una carpeta llena de samples que te gustaría usar en Renardo, puedes llamar a loop() con la ruta completa al sample.
s1 >> loop('/path/to/samples/quack.wav')

# Si le das a loop la ruta a una carpeta, reproducirá el primer sample que encuentre. Puedes cambiar el sample que reproduce con el argumento sample=.

# Reproducir el primer sample de mi colección
s1 >> loop('/path/to/samples')

# reproducir el segundo sample de la colección
s1 >> loop('/path/to/samples', sample=1)

# Si va a utilizar muchas muestras de una carpeta, puede añadirla a la ruta de búsqueda de muestras. Renardo buscará en todas sus rutas de búsqueda una muestra que coincida cuando le des un nombre.
Samples.addPath('/path/to/samples')
s1 >> loop('quack')

# Una vez que tenga una ruta de búsqueda, puede utilizar la concordancia de patrones para buscar muestras.

# Toca el tercer sample en el directorio 'snare
s1 >> loop('snare/*', sample=2)

# También puedes usar * en los nombres de directorio
s1 >> loop('*_120bpm/drum*/kick*')

# ** significa «todos los subdirectorios recursivos». Esto reproducirá el primer sample
# anidada bajo 'percussion' (por ejemplo, 'percussion/kicks/classic/808.wav')
s1 >> loop('percussion/**/*')