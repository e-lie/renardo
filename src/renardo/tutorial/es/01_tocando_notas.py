# Tutorial 1: Tocando Notas

# En Renardo, todos los nombres de variables de dos caracteres están reservados para objetos reproductores, como 'p1'
# Creando un objeto reproductor sin argumentos tocará una sola nota en Do central, por defecto, repetidamente hasta que se detenga.
# Usa >> para dar uno de estos a un objeto reproductor así:

p1 >> pluck()

# Para detener un objeto jugador individual, basta con ejecutar

p1.stop()

# Además de las variables de 2 caracteres que están pre-reservadas, puedes crear
# con variables tus propios nombres

foo = Player()
foo >> pluck()

# El >> en Python está normalmente reservado para un tipo de operación, como + o -, pero no es el caso en Renardo.
# Si un usuario re-ejecuta el código, Renardo actualizará p1 en lugar de crear un PlayerObject,
# lo que significa que puedes hacer cambios en tu música usando sólo una línea de código.

# Si ahora le das a tu objeto reproductor algunos argumentos, puedes cambiar las notas que se reproducen.
# El primer argumento debe ser el grado de la nota a reproducir
# (por defecto es la nota más grave de la octava 5 de la escala mayor) y no necesita ser especificado por nombre.

# Python, como la mayoría de los lenguajes de programación, utiliza la indexación a cero cuando accede a los valores de un array,
# lo que significa que 0 se refiere a la primera nota de la escala.
# Dale a tu objeto reproductor instrucciones para hacer música con su Sintetizador.
# El primer argumento es la nota de la escala a tocar. El siguiente código
# reproduce las tres primeras notas de la escala por defecto (mayor) en repetición.

# Para una sola nota
p1 >> pluck(0)

# O una lista de notas
p1 >> pluck([0,1,2])

# Pero tendrás que especificar cualquier otra cosa que quieras cambiar...

# Tales como duraciones de nota, o la longitud de cada nota
p1 >> pluck([0,0,0], dur=[1,2,3])

# o amplitud, el «volumen» de cada nota
p1 >> pluck([0,0,0], amp=[1,2,3])

# Si la segunda lista, el amplificador en este ejemplo, es demasiado larga, entonces la primera lista (el degree) sólo hace un bucle, y se emparejan con los elementos restantes de la segunda lista (la amplitud).
p1 >> pluck([0,2,4], amp=[1,2,3,1,5])

# En general, se recorren todas las listas independientemente de su longitud.
p1 >> pluck([0,2,4], dur=[1,2], amp=[1,2,3,1,5])

# Los argumentos pueden ser enteros, puntos flotantes, fracciones, listas,
#  tuplas, o una mezcla

p1 >> pluck([0,0,0], dur=2)

p1 >> pluck([0,0,0], dur=1.743)

p1 >> pluck([0,0,0], dur=[0.25,0.5,0.75])

p1 >> pluck([0,0,0], dur=[1/4,1/2,3/4])

p1 >> pluck([0,0,0], dur=[1/4,0.25,3])

# Las listas de valores se repiten a medida que el reproductor reproduce las notas.
# La siguiente duración equivale a:  1,2,3,1,4,3
# Si aún no entiendes esto, no te preocupes, más sobre patrones en el tutorial de patrones
p1 >> pluck([0,0,0], dur=[1,[2,4],3])

# Los valores de las tuplas se usan simultáneamente, es decir, p1 tocará 3 notas individuales y luego un acorde de 3 juntas al mismo tiempo.
p1 >> pluck([0,2,4,(0,2,4)])

# También puedes asignar valores a los atributos de los objetos jugador directamente
p1.oct = 5

# Para ver todos los nombres de los atributos de los jugadores, basta con ejecutar
print(Player.get_attributes())

# Más sobre esto más adelante en el tutorial de atributos de jugador

# Podrías almacenar varias instancias de jugador y asignarlas en diferentes momentos
proxy_1 = charm([0,1,2,3], dur=1/2)
proxy_2 = charm([4,5,6,7], dur=1)

p1 >> proxy_1 # Asigna el primero a p1

p1 >> proxy_2 # Esto reemplaza las instrucciones que sigue p1

# Para reproducir varias secuencias a la vez, basta con hacer lo mismo con otro
# objeto reproductor:

p1 >> pluck([0, 2, 3, 4], dur=1/2)

p2 >> charm([(0, 2, 4), (3, 5, 7)], dur=8)

# Toca sólo este reproductor, silenciando los demás
p1.solo() # El valor por defecto es 1 (solo activado)

# Y desactiva el solo
p1.solo(0)

# Detener (no sólo silenciar) a los otros jugadores
p1.solo()

# Usa Ctrl+. para borrar todo para el reloj de programación o ejecución
Clock.clear()
