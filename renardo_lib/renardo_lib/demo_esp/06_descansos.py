# Tutorial 6: Descansos


# Se pueden añadir silencios utilizando un objeto rest en el array dur
# El silencio silencia la nota que se hubiera tocado.

# Sin descanso, 5 notas (sí, un dur=1 funcionaría, pero seamos explícitos para contrapunto del siguiente ejemplo)
p1 >> charm([0,1,2,3,4], dur=[1,1,1,1,1])

# Con un silencio ... 4 notas y un silencio, la nota «4» se silencia durante 4 tiempos
p1 >> charm([0,1,2,3,4], dur=[1,1,1,1,rest(4)])
