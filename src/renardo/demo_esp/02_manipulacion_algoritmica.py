# Tutorial 2: Manipulación Algorítmica

# El código siguiente reproduce las cuatro primeras notas de la escala por defecto en repetición:
p1 >> charm([0,1,2,3])

# Es posible manipular esto añadiendo un array de números al objeto Player
# Esto eleva la 4ª nota tocada en 2 degrees
p1 >> charm([0,1,2,3]) + [0,0,0,2]

# Y esto eleva cada tercera nota en 2
p1 >> charm([0,1,2,3]) + [0,0,2]

# Estos valores se pueden encadenar y agrupar
p1 >> charm([0,1,2,3]) + [0,1,[0,(0,2)]

# Este comportamiento es particularmente útil cuando se utiliza el método follow.
b1 >> bajo([0,4,5,3], dur=2)
p1 >> charm().follow(b1) + [2,4,7]

# Puedes programar los reproductores para que hagan cosas
# Esto le dirá a p1 que invierta las notas cada 4 tiempos
p1 >> charm([0,2,4,6])
p1.every(4, «reverse»)

# Se pueden «encadenar» métodos añadiéndolos al final de
# la línea original:
p1 >> charm([0,2,4,6]).every(4, «reverse»)

# Para dejar de llamar a «reverse», usa 'never':

p1.never(«reverse»)

# Aquí tienes otros métodos que puedes usar:

# Usando «stutter» tocarás la misma nota 'n' número de veces con diferentes atributos especificados

p1.every(4, "stutter", 4, oct=4, pan=[-1,1])

# Rotar desplazará todos los valores en 1 en su orden
p1.every(4, "rotate"))

# Para cambiar aleatoriamente el orden de las notas, utiliza «shuffle».
p1.every(4, "shuffle")
