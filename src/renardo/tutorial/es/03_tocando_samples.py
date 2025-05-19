# Tutorial 3: Reproduciendo samples Incorporadas


# Renardo también puede ser usado para secuenciar y manipular muestras de audio.
# Para hacer esto todo lo que necesitas hacer es usar el play SynthDef especial.
# El primer argumento del play SynthDef debe ser una cadena de caracteres
# en lugar de una lista de números como lo haría para cualquier otro SynthDef.
# Cada carácter representa un archivo de audio diferente, que se almacena en un buffer en SuperCollider.

# Para ver qué carácter corresponde a cada archivo de audio, ejecute
print(DefaultSamples)

# Puedes reproducir samples de audio en los subdirectorios Renardo/snd/ utilizando el sintetizador
# sintetizador 'play' y utilizando una cadena de caracteres en lugar de una lista de notas.
bd >> play("x")

# Un carácter se refiere a un sonido y el espacio en blanco se usa para el silencio, así que
# puedes separar los sonidos en el tiempo:
bd >> play("x..x..x..")

hh >> play(".-")

# Puedes encajar patrones usando corchetes redondos
# Whick juega como: "x o xo "
d1 >> play("(x.)(.x)o.")

# Lo siguiente es lo mismo que "-------="
hh >> play("---(-=)")

# Poniendo caracteres entre corchetes se reproducirán todos en el espacio de un compás
# Y se reproducirán como un solo carácter, no simultáneamente, sino en rápida sucesión
d1 >> play("x-o[-o]")

d1 >> play("x-o[---]")

d1 >> play("x-o[-----]")

d1 >> play("x-o[--------------]")

# y se pueden poner entre corchetes como si fueran un carácter en sí mismos.
d1 >> play("x[--]o(=[-o])")

# Puedes combinar los corchetes como quieras: los siguientes patrones son idénticos
d1 >> play("x-o(-[-o])")

d1 >> play("x-o[-(o )]")

# Las llaves seleccionan un sonido de muestra al azar si desea más variedad
d1 >> play("x-o{-=[--][-o]}")

# Los corchetes angulares combinan patrones para que se reproduzcan simultáneamente
d1 >> play("<X...><-...><#...><V...>")

d1 >> play("<X...><.-..><..#.><...V>")

# Cada carácter se asigna a una carpeta de archivos de sonido y puede seleccionar diferentes
# ejemplos mediante el argumento de la palabra clave "sample"
d1 >> play("(x[--])xu[--]")

d1 >> play("(x[--])xu[--]", sample=1)

d1 >> play("(x[--])xu[--]", sample=2)

# Cambia el sample  para cada tiempo
d1 >> play("(x[--])xu[--]", sample=[1,2,3])

# Puede superponer dos patrones juntos - observe la "P", mire el tutorial 4 para obtener más información.
d1 >> play(P["x-o-"] & P[".**"])

# Y cambiar los efectos aplicados a todos los patrones en capas al mismo tiempo
d1 >> play(P["x-o-"] & P[".**"], room=0.5)

# Ejemplo del tutorial del reproductor, pero con samples en su lugar
# condicionales...
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x"))

# o cámbielo al banco de muestra 2 multiplicando
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x")*2)

# Encadenar múltiples condicionales
d1 >> play("x[--]xu[--]x", sample=(d1.degree=="x")*2 + (d1.degree=="-")*5)

# Que es lo mismo que
d1 >> play("x[--]xu[--]x", sample=d1.degree.map({"x":2, "-":5}))
