# Tutorial 4: Uso de patrones

# Los objetos de jugador usan listas de Python, conocidas más comúnmente como matrices en otros lenguajes,
# para secuenciarse. Ya las has usado antes, pero no son exactamente
# flexibles para la manipulación. Por ejemplo, intenta multiplicar una lista por dos de la siguiente manera:

print([1, 2, 3] * 2)

# ¿El resultado es el que esperabas?

# FoxDot usa un tipo de contenedor llamado 'Pattern' para ayudar a resolver este problema.
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
