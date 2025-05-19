# Tutorial 13:  Clock Avanzado

# Para ver lo que está previsto que se reproduzca.
print(Clock)

# Para ver cuál es la latencia
print(Clock.latency)

# El clock puede programar cualquier cosa con un método __call__ usando
# Se necesita una pista de tiempo absoluta para programar una función
# Clock.schedule necesita saber el beat para llamar algo en
Clock.schedule()   # raises TypeError

# Programar un evento después de una cierta duración
# Clock.future necesita saber cuantos beats adelante para llamar algo
Clock.future() 

# Estos son equivalentes
Clock.schedule(lambda: print("hello"), Clock.now() + 4)
Clock.future(4, lambda: print("hello"))

# Para programar otra cosa
Clock.schedule(lambda: print("hello "))

# Podemos llamar a algo cada n beats
Clock.every(4, lambda: print("hello"))


# Obtén el clock actual y súmale 2. Útil para programar.
print(Clock.now() + 2)

# Emitir orden en la siguiente barra
nextBar(Clock.clear)

# Con un decorador
@nextBar
def change():
    Root.default=4
    Scale.default="minor"

# Puedes crear tu propia función, y decorarla, para poder
# utilizarla en un .every sobre un objeto player
@PlayerMethod
def test(self):
    print(self.degree)

p1 >> pluck([0,4]).every(3, "test")

# Y cancélalo con
p1.never("test")
