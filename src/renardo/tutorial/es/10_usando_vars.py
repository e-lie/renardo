# Tutorial 10: Usando Vars

# Una TimeVar es una abreviatura de «Time Dependent Variable» y es una característica clave de Renardo.
# Una TimeVar tiene una serie de valores entre los que cambia después de un número predefinido de pulsaciones
# y se crea usando un objeto var con la sintaxis var([lista_de_valores],[lista_de_duraciones]).

# Genera los valores: 0,0,0,0,3,3,3,3...
a = var([0,3],4)            # La duración puede ser un valor único
print(int(Clock.now()), a)  # 'a' tiene inicialmente el valor 0
# >>> 0, 0                  # El primer valor puede diferir...


print(int(Clock.now()), a)   # Después de 4 pulsaciones, el valor cambia a 3

print(int(Clock.now()), a)  # Después de otras 4 pulsaciones, el valor cambia a 0

# La duración también puede ser una lista
a = var([0,3],[4,2])
print(int(Clock.now()), a)

# Cuando una TimeVar se utiliza en una operación matemática, los valores a los que afecta también se convierten en TimeVars
# que cambian de estado cuando la TimeVar original cambia de estado - esto se puede utilizar incluso con patrones:
a = var([0,3], 4)
print(int(Clock.now()), a + 5) # Cuando beat es 0, a es 5
# >>> 5


print(int(Clock.now()), a + 5) # When beat is 4, a is 8
# >>> 8

b = PRange(4) + a
print(int(Clock.now()), b)  # Después de 8 beats, el valor cambia a 0
# >>> P[0, 1, 2, 3]

b = PRange(4) + a
print(int(Clock.now()), b) # Después de 12 beats, el valor cambia a 3
# >>> P[3, 4, 5, 6]

# Usa 'var' con tus objetos player para crear progresiones de acordes.
a = var([0,4,5,3], 4)
b1 >> bass(a, dur=PDur(3,8))
p1 >> charm(a + (0,2), dur=PDur(7,16))

# Puedes añadir un 'var' a un objeto player o a un var.
b1 >> bass(a, dur=PDur(3,8)) + var([0,1],[3,1])

b = a + var([0,10],8)

print(int(Clock.now()), (a, b))

# Actualizar los valores de una 'var' los actualizará en todas las demás
a.update([1,4], 8)

print(int(Clock.now()), (a, b))

# Vars pueden ser nombrados ...
var.chords = var([0,4,5,4],4)

# y usado después
b1 >> pluck(var.chords)

## Se actualizarán todos los players que utilicen el var nombrado
var.chords = var([0,1,5,3],4)

# También puedes usar una 'linvar' que cambie sus valores gradualmente en el tiempo
# Cambia el valor de 0 a 1 en 16 beats
c = linvar([0,1],16)

# Ejecutar esto varias veces para ver los cambios que se producen
print(int(Clock.now()), c)

# Cambia el amplificador basado en ese linvar
p1 >> charm(a, amp=c)

# un 'Pvar' es una 'var' que puede almacenar patrones (a diferencia de, digamos, números enteros)
d = Pvar([P[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], P[0, 1, 2, 3, 4, 5, 4, 3, 2, 1]], 8)

print(int(Clock.now()), d)

p1 >> charm(a, amp=c, dur=1/4) + d

# Cambia la escala cada 16 tiempos
Scale.default = Pvar([Scale.major, Scale.minor],16)

# Incluso configuras el valor para que dure para siempre una vez que se alcanza usando un valor especial llamado "inf"
x = var([0, 1, 2, 3], [4, 4, 4, inf])

print(x) # Siga presionando - eventualmente se detendrá en 3

###################### 
# Otros tipos de "var" # Hay varias sub-clases de "var" que devuelven valores entre ellos
# los números especificados. Por ejemplo, un "linvar" cambia gradualmente
# valores de forma lineal:

print(linvar([0,1],8)) # sigue corriendo para ver el cambio de valor entre 0 y 1

# Ejemplo: aumentar el corte del filtro pasa-altos sobre 32 beats
p1 >> play("x-o-", hpf=linvar([0,4000],[32,0]))

# Otros tipos incluyen «sinvar» y «expvar»
print("Linear:", linvar([0, 1], 8))
print("Sinusoidal:", sinvar([0, 1], 8))
print("Exponential:", expvar([0, 1], 8))

#################

# Patrón TimeVar

# A veces podemos querer almacenar patrones enteros dentro de una var pero
# si intentamos hacerlo, se encadenan automáticamente:

pattern1 = P[0, 1, 2, 3]
pattern2 = P[4, 5, 6, 7]

print(var([pattern1, pattern2], 4))

# Para almacenar patrones enteros, necesitas usar un «Pvar» que no
# no encaje los valores, sino que almacene los patrones en su lugar

print(Pvar([pattern1, pattern2], 4))

p1 >> pluck(Pvar([pattern1, pattern2], 4), dur=1/4)


###########################
# Offsetting the start time

# Otro truco útil es desplazar la hora de inicio de la var. Por
# por defecto es cuando el tiempo del Reloj es 0 pero puedes especificar un valor
# valor diferente usando la palabra clave "start"

print(linvar([0, 1], 8))
print(linvar([0, 1], 8, start=2))

# Esto puede combinarse con Clock.mod() para iniciar una rampa al comienzo del#
# siguiente ciclo de 32 beat:
d1 >> play("x-o-", hpf=linvar([0,4000],[32,inf], start=Clock.mod(32)))

