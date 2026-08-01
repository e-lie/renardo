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

# --------------------------------------------------------------------------
# Valores por defecto globales y "stickiness" (persistencia)
# --------------------------------------------------------------------------

# Igual que Scale y Root (ver Tutorial 8), los atributos comunes oct, dur,
# sus, pan, rate y sample tienen cada uno un `.default` global que puedes
# cambiar:

Oct.default = 6
Dur.default = 1
Sus.default = 1
Pan.default = 0
Rate.default = 1
Sample.default = 0

# Cualquier player que NO haya fijado ese atributo por sí mismo recogerá el
# nuevo valor en su próximo evento -- no hace falta relanzarlo con '>>':
p1 >> pluck(pitches)
Oct.default = 5  # p1 baja de octava inmediatamente, sin dejar de sonar

# Pero en cuanto fijas un atributo explícitamente en un player, este "se
# pega" (sticky): el player conserva ese valor aunque cambies después el
# valor por defecto global.
p1 >> pluck(pitches, oct=4)
Oct.default = 7
# p1 sigue en oct=4 aquí

# Si prefieres que los atributos se comporten exactamente como scale/root --
# volviendo siempre al valor por defecto global vigente cada vez que
# relanzas el player sin esa palabra clave, incluso si le habías dado un
# valor explícito antes -- activa este interruptor:
PlayerDefaults.sticky_override = False

p1 >> pluck(pitches)  # sin 'oct' aquí, así que recoge Oct.default (7)
Oct.default = 5

# Vuelve al comportamiento por defecto ("sticky"):
PlayerDefaults.sticky_override = True
