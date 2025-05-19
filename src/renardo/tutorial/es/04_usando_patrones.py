# Tutorial 4: Uso de patrones

# Los objetos de jugador usan listas de Python, conocidas más comúnmente como matrices en otros lenguajes,
# para secuenciarse. Ya las has usado antes, pero no son exactamente
# flexibles para la manipulación. Por ejemplo, intenta multiplicar una lista por dos de la siguiente manera:

print([1, 2, 3] * 2)

# ¿El resultado es el que esperabas?

# Renardo usa un tipo de contenedor llamado 'Pattern' para ayudar a resolver este problema.
# Actúan como listas normales, pero cualquier operación matemática que se realice en ellas se aplica a cada elemento
# de la lista y se hace de a pares si se usa un segundo patrón. Se crea un patrón básico como
# lo harías con una lista o tupla normal, pero con una 'P' precediéndolo.

print(P[1,2,3] * 2)

print(P[1,2,3] + 100)

# En esta operación, la salida consta de todas las combinaciones de los dos patrones, es decir,
# [1+3, 2+4, 3+3, 1+4, 2+3, 3+4]
print(P[1,2,3] + [3,4])

# Puedes usar la sintaxis de slicing de Python para generar una serie de números

print(P[:8])

print(P[0,1,2,3:20])

print(P[2:15:3])

# Pruebe otros operadores matemáticos y vea qué resultados obtiene.
print(P[1,2,3] * (1,2))

# Los objetos patrón también entrelazan automáticamente en cualquier lista anidada.
# Comparar
# Lista normal:
for n in [0,1,2,[3,4],5]:
    print(n)


# con
# Patrón
for n in P[0,1,2,[3,4],5]:
    print(n)

# Utilice PGroups si desea evitar este comportamiento. Estos pueden ser implícitamente
# especificados como tuplas en Patrones:
for n in P[0,1,2,(3,4)]:
    print(n)

#esto es un grupo 
print(P(0,2,4) + 2)

print(type(P(0,2,4) + 2))

# En Python, puedes generar un rango de enteros con la sintaxis range(start, stop, step).
# Por defecto, inicio es 0 y paso es 1.
print(list(range(10))) # [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# Puedes usar PRange(start, stop, step) para crear un objeto Patrón con los valores equivalentes:
print(PRange(10)) # P[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

# P[0, 2, 2, 6, 4, 10, 6, 14, 8, 18]
# [0*1, 1*2, 2*1, 3*2, 4*1, 5*2, 6*1, 7*2, 8*1...]
print(PRange(10) * [1, 2])           # Pattern class behaviour

# Añadir una lista (o Patrón) a un Patrón añadirá los valores de los
# elementos al otro donde las listas de Python se concatenarían.
print(PRange(10) + [0,10])

# Para concatenar patrones, usa el operador pipe así:
print(PRange(10) | [0,10])

# Renardo convierte automáticamente cualquier objeto que se canaliza a un Patrón a la clase Patrón base.
# para que no tengas que preocuparte de asegurarte de que todo es del tipo correcto.

# ejecuta todos los valores juntos
p1 >> pluck(P(4,6,8))
p1 >> pluck(P[0,1,2,P(4,6,8),7,8])

# Distribuye los valores a lo largo de la duración actual, por ejemplo, si la duración es de 2 tiempos, cada valor se reproducirá con una separación de 2/3 tiempos.
p1 >> pluck(P*(0,2,4), dur=1/2)
p1 >> pluck(P*(0,2,4), dur=1)
p1 >> pluck(P*(0,2,4), dur=2)
p1 >> pluck(P[0,1,2,P*(4,6,8),7,8], dur=1)

# Es lo mismo que P* pero cada vez que se tocan las notas se extienden sobre el valor dur.
p1 >> pluck(P/(0,2,4), dur=1/2)
p1 >> pluck(P/(0,2,4), dur=1)
p1 >> pluck(P/(0,2,4), dur=2)
p1 >> pluck(P[0,1,2,P/(4,6,8),7,8], dur=1)


# Por ejemplo, si la duración es de 2 tiempos y la duración es de 3 tiempos, cada valor se reproducirá con 1 tiempo de diferencia.
p1 >> pluck(P+(0,2,4), dur=2, sus=3)
p1 >> pluck(P+(0,2,4), dur=2, sus=1)
p1 >> pluck(P[0,1,2,P+(4,6,8),7,8], dur=1, sus=3)

# Distribuye los primeros (longitud - 1) valores con un espacio del último valor entre cada uno
# Distribuye 0,2,4 con un espacio de 0,5:
p1 >> pluck(P^(0,2,4,0.5), dur=1/2)

# Los patrones vienen con varios métodos para manipular el contenido
help(Pattern)

# Patrón estándar
print(P[:8])

# Patrón aleatorio
print(P[:8].shuffle())

# Añade un patrón invertido al patrón
print(P[:8].palindrome())

# Desplaza el patrón en n (por defecto 1)
print(P[:8].rotate())
print(P[:8].rotate(3))
print(P[:8].rotate(-3))

# Toma el patrón y lo añade tantas veces como sea necesario para alcanzar n número de elementos en el patrón
print(P[:8].stretch(12))
print(P[:8].stretch(20))

# reversa el patron 
print(P[:8].reverse())

#loopea un patron n numero de veces
print(P[:8].loop(2))

# Añadir un offset
print(P[:8].offadd(5))

#añade multiples offset
print(P[:8].offmul(5))

# Stutter - Repite cada elemento n veces
print(P[:8].stutter(5))

# Amen
# Fusiona y encaja los dos primeros y últimos elementos de tal manera que un patrón de batería «x-o-» se convertiría en "(x[xo])-o([-o]-)" e imita
# el ritmo del famoso «amen break»
d1 >> play(P["x-o-"].amen())
print(P[:8].amen())

# Bubble
# Fusiona y encaja los dos primeros y últimos elementos de tal manera que un # patrón de tambor «x-o-» se convertiría en "(x[xo])-o([-o]-)"
d1 >> play(P["x-o-"].bubble())
print(P[:8].bubble())



