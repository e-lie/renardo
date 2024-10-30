# Tutorial 5: Referenciando atributos del jugador

# Puedes establecer variables fuera de un jugador tonos = P[0,1,2,3,4]
harmony = pitches + 2

print(pitches)
print(harmony)

p1 >> pluck(pitches)
p2 >> star(harmony)

# Si fijas la duración del segundo, puede que no tenga el efecto deseado

p1 >> pluck(pitches)
p2 >> star(harmony, dur=1/2)

# Es posible que un objeto player juegue exactamente lo que otro player.
# Para que un player siga a otro, basta con usar el método follow:
p1 >> pluck(pitches)

p2 >> star(dur=1/2).follow(p1) + 2

# También puedes hacer referencia explícita a atributos como el tono o la duración
p2 >> star(p1.pitch) + 2 # esto es lo mismo que .follow(p1)

# Funciona también para otros atributos
p1 >> pluck(pitches)
p2 >> star(dur=p1.dur).follow(p1) + 2

# Puede hacer referencia, y probar el valor actual
# El == devuelve un 1 si es verdadero y un 0 si es falso
print(p1.degree)
print(p1.degree == 2)

# Esto te permite hacer condicionales como
p1 >> pluck([0,1,2,3], amp=(p1.degree==1))

p1 >> pluck([0,1,2,3], amp=(p1.degree>1))




