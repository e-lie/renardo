# Tutorial 9: Grupos

# Los atributos de los players, como el grado o la escala, también pueden modificarse asignándole directamente valores tales que
p1 >> charm([0,2,4,2], scale=Scale.majorPentatonic)

# es equivaklente a
p1 >> charm()
p1.degree = [0,2,4,2]
p1.scale = Scale.majorPentatonic

# Esto es útil si quieres asignar los mismos valores a múltiples objetos player simultáneamente, así:
p1 >> charm([0,2,4,2])
p2 >> charm([2,1,0,4])
p3 >> charm([2,3])
p1.dur=p2.dur=p3.dur=[1,1/2,1/4,1/4]

p1.stop()
p2.stop()
p3.stop()

# Puede hacer referencia a todos los miembros con nombres similares
p_all.dur = [1/2,1/4] # Ejecutar esto mientras p1, p2, etc están sonando!

# o
p_all.amplify = 1

# O...
p_all.stop()

# O...
p_all.solo()

# Para reducir la cantidad de escritura, los objetos player pueden ser agrupados y sus atributos modificados de una manera más simple:
p1 >> charm([0,2,4,2])
p2 >> charm([2,1,0,4])
p3 >> charm([2,3])
g1 = Group(p1, p2, p3)
g1.dur=[1,1/2,1/4,1/4]

# Puedes agrupar will _all grupos
g1 = Group(p_all, d_all, b1, b2)

# Activa el volumen durante 4 tiempos, luego lo desactiva durante 4
# Esto anula las amplitudes existentes en el objeto player
g1.amp=var([1,0],4)

g1.stop()

# Puedes usar funciones para agrupar cosas. Para ejecutar use CTRL+ENTER, no ALT+ENTER.

def tune():
    b1 >> bass([0,3], dur=4)
    p1 >> pluck([0,4], dur=1/2)
    d1 >> play("x--x--x-")
tune()

# o programar el reloj para llamar a otras funciones agrupadas
def verse():
    b1 >> bass([0,3], dur=4)
    p1 >> pluck([0,4], dur=1/2)
    d1 >> play("x--x--x-")
    Clock.future(16, chorus)
def chorus():
    b1 >> bass([0,4,5,3], dur=4)
    p1 >> pluck([0,4,7,9], dur=1/4)
    d1 >> play("x-o-")
    Clock.future(16, verse)
verse()

