# Tutorial 8: Escalas

# Por defecto, los objetos player utilizan la escala de Do Mayor.
# Esto puede cambiarse usando los argumentos de palabra clave 'scale' y 'root'.
# Las escalas pueden ser definidas como un arreglo de semitonos, tal que la escala Mayor es [0,2,4,5,7,9,11]
# o una de las escalas predefinidas del módulo Scale, por ejemplo Scale.minor.
# Root se refiere a la tónica de la escala; siendo 0 Do, 1 es Do#, 2 es Re y así sucesivamente.

# La escala por defecto puede ser cambiada de tal manera que cualquier player que no use una escala específica será actualizado.
# Esto se hace utilizando la sintaxis siguiente (cada línea es técnicamente equivalente):

Scale.default.set("major")
Scale.default.set(Scale.major)
Scale.default.set([0,2,4,5,7,9,11])


# Or lo mismo, pero en minor:
Scale.default.set("minor")
Scale.default.set(Scale.minor)
Scale.default.set([0,2,3,5,7,10])

# Para ahorrar algo de tiempo también puedes hacer
Scale.default = "minor"

#Esto es lo mismo para la root:
Root.default.set(1)
Root.default.set("C#")

# o

Root.default.set(2)
Root.default.set("D")

# Para ver una lista de todas las escalas, utilice
print(Scale.names())


# Puedes cambiar la escala utilizada por un player utilizando la palabra clave 'scale'.
p1 >> charm([0,1,2], scale=Scale.minor)


# De forma similar, puedes cambiar los players de las notas root usando la palabra clave root
# y el objeto Root.default
p1 >> charm([0,1,2], scale=Scale.minor, root=2)
