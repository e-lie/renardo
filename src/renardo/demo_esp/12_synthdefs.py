# Tutoral 12: SynthDefs

# FoxDot crea música dando a los objetos player un 'instrumento digital'
# para tocar, que se llaman 'SynthDefs'. Usted puede ver la lista de pre-instalados
print(SynthDefs)

# Cada uno de estos representa un `SynthDef` *objeto*. Estos objetos son entonces
# entregados a los players para que los toquen - como dar un instrumento a alguien de tu orquesta.

# Escribiendo tus propias Definiciones de Sintetizador

# Esto es un poco más avanzado, pero si ya has escrito SynthDefs en
# Supercollider entonces puede que te sientas como en casa.  Si no, vuelve a esta sección  más adelante.

# FoxDot puede acceder a cualquier SynthDef almacenado en el servidor SuperCollider,
# pero necesita saber que está ahí. Si ya has escrito un SynthDef
# en SuperCollider y lo has llamado \mySynth entonces sólo tienes que crear un SynthDef  # usando FoxDot así:

mySynth = SynthDef("mySynth")

# Usar el mismo nombre de variable en FoxDot que en SuperCollider para tu SynthDef
# es una buena idea para evitar confusiones. Si quieres escribir (o editar) tu propio
# SynthDef durante el tiempo de ejecución en FoxDot puede utilizar una API SuperCollider por  # importando el módulo SynthDefManagement. Todos los objetos SynthDef de FoxDot heredan el comportamiento # de la clase base.
# el comportamiento de la clase base, como los filtros de paso alto y bajo y el vibrato,
# pero estos pueden ser anulados o actualizados fácilmente. Si quieres saber más
# sobre el procesamiento digital de sonido y la creación de SynthDef, consulte la
# documentación de SuperCollider. A continuación se muestra un ejemplo de la creación de uno en FoxDot:

# Importar módulo para escribir código SynthDefManagement desde Python
from SCLang import *

# Crea un SynthDef llamado 'ejemplo' (usar el mismo nombre de variable que el nombre del SynthDef es una buena idea)
example = SynthDef("example")

# Crea el oscilador (osc) usando una onda sinusoidal
example.osc = SinOsc.ar(ex.freq)

# Y darle una envolvente de sonido percusivo (env)
example.env = Env.perc()

# Finalmente, ¡almacénalo!
example.add()

# Cómo crear un SynthDef

with SynthDef("charm") as charm:
	charm.osc = SinOsc.ar(charm.freq)
	charm.env = Env.perc()

#Es equivalente a 

charm = SynthDef("charm")
charm.osc = SinOsc.ar(charm.freq)
charm.env = Env.perc()
charm.add()
