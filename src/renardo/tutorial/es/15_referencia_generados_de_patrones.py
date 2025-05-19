# Tutorial 15  Referencia generadpres de patrones

# Hay otras clases de Patrones en Renardo que te ayudan a generar matrices de números pero también se comportan
# de la misma manera que el Patrón base. Para ver que Patrones existen y probar a usarlos, ejecute
print(classes(Patterns.Sequences))

####################
# PEuclid
# PEuclid(n, k)
# Devuelve el ritmo euclidiano que reparte 'n' pulsos en 'k' pasos de la forma más uniforme posible.

# 3 pulsos sobre 8 pasos
print(PEuclid(3, 8))

####################
# PDur
# PDur(n, k, start=0, dur=0.25)
# Devuelve las duraciones reales basadas en ritmos euclidianos (ver PEuclid) donde dur es la longitud de cada paso.
# Distribuye 'n' pulsos sobre 'k' pasos tan uniformemente como sea posible.
print(PDur(3,8)) # P[0.75, 0.75, 0.5]

print(PDur(5,8))

# Dar una lista de 3 dur, appened con una lista de 5 dur 
print(PDur([3,5],8))

d1 >> play("x", dur=PDur(5,8))

####################
# PIndex
# Devuelve el índice al que se accede
print(PIndex())
print(PIndex()*4)


####################
# PSine
# PSine(n=16)
# Devuelve los valores de un ciclo de onda sinusoidal dividido en 'n' partes

# Dividido en 5 partes
print(PSine(5))

# Dividio en 10 partes
print(PSine(10))


####################
# PTri
# PTri(start, stop=None, step=None)
# Devuelve un Patrón equivalente a `Patttern(rango(inicio, parada, paso)) con su forma invertida añadida.
# Piense en ello como un ángulo "Tri".

# Hasta 5 y luego hasta 1
print(PTri(5))

# Hasta 8 y luego hasta 1
print(PTri(8))

# De 3 a 10, luego baja a 4
print(PTri(3,10))

# De 3 a 30, por 2, luego baja a 4
print(PTri(3,20,2))

# Hasta 4, luego hasta 1, luego hasta 8, luego hasta 1
print(PTri([4,8]))

p1 >> pluck(PTri(5), scale=Scale.default.pentatonic)

#  Es igual a
p1 >> pluck(PRange(5) | PRange(5,0,-1), scale=Scale.default.pentatonic)


####################
# PRand
# PRand(start, stop=None)
# Devuelve un entero aleatorio entre inicio y fin.

# Devuelve un entero aleatorio entre 0 y start.
print(PRand(8)[:5])

# Devuelve un entero aleatorio entre inicio y fin.
print(PRand(8,16)[:5])

# Si start es un tipo-contenedor devuelve un elemento aleatorio para ese contenedor.
print(PRand([1,2,3])[:5])

# Puede suministrar una semilla
print(PRand([1,2,3], seed=5)[:5])

# Sigue generando sintonía aleatoria
p1 >> pluck(PRand(8))

# Crea una lista aleatoria, e itera sobre esa misma lista
p1 >> pluck(PRand(8)[:3])

####################
# PRhythm
# PRhythm toma una lista de duraciones simples y tuplas que contienen valores que pueden ser suministrados al `PDur`.
# Lo siguiente toca el hi hat con un Ritmo Euclidiano de 3 pulsos en 8 pasos
d1 >> play("x-o-", dur=PRhythm([2,(3,8)]))

print(PRhythm([2,(3,8)]))

####################
# PSum
# PSum(n, total)
# Devuelve un Patrón de longitud 'n' cuya suma es igual a 'total'

# Devuelve un patrón de longitud 2, con elementos sumados hasta 8
print(PSum(3,8))

# Devuelve un patrón de longitud 5, con elementos sumados hasta 4
print(PSum(5,4))

####################
# PStep
# PStep(n, value, default=0)
# Devuelve un Patrón que cada n-términos es 'valor' de lo contrario 'por defecto'

# Cada 4, que sea 1, de lo contrario por defecto a 0
print(PStep(4,1))

# Cada 8, que sean 6, si no, 4
print(PStep(8,6,4))


# Cada 5, que sea 2, si no, 1
print(PStep(5,2,1))

####################
# PWalk
# PWalk(max=7, step=1, start=0)

# Por defecto, devuelve un patrón con cada elemento aleatoriamente 1 mayor o menor que el anterior
print(PWalk()[:16])

#Cambiando el paso 
print(PWalk(step=2)[:16])

#Con max
print(PWalk(max=2)[:16])

# Empieza en un número distinto de cero
print(PWalk(start=6)[:16])


####################
# PWhite
# PWhite(lo=0, hi=1)
# Devuelve valores aleatorios de coma flotante entre 'lo' y 'hi'

# Lo por defecto a 0, hi por defecto a 1
print(PWhite()[:8])

# Devuelve números aleatorios entre 1 y 5
print(PWhite(1,5)[:8])


####################
# Patrones de generador personalizados

# Se pueden hacer patrones generadores personalizados subclasificando GeneratorPattern
# y sobreescribiendo `GeneratorPattern.func`.

class CustomGeneratorPattern(GeneratorPattern):
    def func(self, index):
        return int(index / 4)

print(CustomGeneratorPattern()[:10])

# Esto se puede hacer de forma más consisa usando `GeneratorPattern.from_func`,
# pasando una función que toma un índice y devuelve algún elemento del patrón.

def some_func(index):
    return int(index / 4)

print(GeneratorPattern.from_func(some_func)[:10])

# También podemos usar lambdas 
print(GeneratorPattern.from_func(lambda index: int(index / 4))[:10])
