# Tutorial 14: Referencia de atributos del player
# --- TODO: esto necesita actualizarse

# Para ver todos los atributos:
print(Player.get_attributes())

# Puedes ver los efectos disponibles evaluando
print(FxList)

# Usemos el filtro de paso alto como ejemplo. Puedes ver que se describe
# así:
# «<Fx “highPassFilter” -- args: hpr, hpf>"

# Cada efecto tiene un argumento "master" y luego argumentos hijos. Aquí el
# argumento maestro es «hpf» (abreviatura de filtro de paso alto) y el argumento hijo
# es «hpr» (abreviatura de resonancia de paso alto). El efecto sólo se añade cuando
# argumento maestro es distinto de cero:
d1 >> dirt([0,4,2,1], dur=1/2, hpf=4000)

# Esto establece el filtro de paso alto a 4000 Hz por lo que sólo las frecuencias en el audio
# se escuchen realmente. Cambiemos el valor de resonancia. Su
# valor por defecto es 1, así que vamos a hacerlo más pequeño
d1 >> dirt([0,4,2,1], dur=1/2, hpf=4000, hpr=0.3)

# ¿Notas alguna diferencia? Podemos usar patrones / vars en nuestros efectos para hacerlos
# cambien con el tiempo:
d1 >> dirt([0,4,2,1], dur=1/2, hpf=linvar([0,4000],8), hpr=P[1,1,0.3].stretch(8))



####################
# Referencia
####################

####################
# amp - Amplitud (por defecto 1)
# Establece el volumen de la nota/patrón
d1 >> play("*", dur=1/2, amp=1)

# medio volumen
d1 >> play("*", dur=1/2, amp=.5)

# Crear un patrón con amp
d1 >> play("*", dur=1/2, amp=[1,0,1,1,0])


####################
# amplify - Cambia el amperaje, multiplicando contra el valor existente (en lugar de sobrescribir)

# Crear un patrón con amp
d1 >> play("*", dur=1/2, amp=[1,0,1,1,0])
d1 >> play("*", dur=1/2, amplify=[.5,1,0])

# Establece una "drop" en la música (Reproduce a todo volumen durante 28, luego 0 durante 4)
p1 >> blip([0,1,2,3], amplify=var([1,0],[28,4]))

####################
# bend



####################
# benddelay - See bend


##################
# bits
# La profundidad de bits, en número de bits, a la que se reduce la señal;
# este es un valor entre 1 y 24 donde otros valores son ignorados.
# Utilice crush para establecer la cantidad de reducción a la tasa de bits (por defecto es 8).


####################
# bitcrush - ver bits

####################
# blur



####################
# bpf - Band Pass Filter



####################
# bpnoise - ver bpf



####################
# bpr - ver bpf

####################
# bpm



####################
# buf



####################
# channel

####################
# chop
# 'chops' la señal en trozos utilizando una onda de pulsos de baja frecuencia sobre el sustain de una nota.


####################
# coarse



####################
# comb delay - ver echo



####################
# crush

####################
# cut
# corta la duración 
p1 >> pluck(P[:8], dur=1/2, cut=1/8)
p1 >> pluck(P[:8], dur=1/2, cut=1/4)
p1 >> pluck(P[:8], dur=1/2, cut=1/2)

####################
# cutoff



####################
# decay - ver echo


# degree - El degree o grado  de la nota, o afinación, se puede especificar por palabra clave (también la primera posicional)
p1 >> blip(degree=[0,1,2,3])

# Que es lo mismo que:
p1 >> blip([0,1,2,3])

# Sólo toca la nota "root" del acorde
b1 >> bass(p1.degree[0])

####################
# delay - Tiempo de espera antes de enviar la información a SuperCollider (por defecto 0)

# Retrasa cada 3 notas en .1
p1 >> blip([0,1,2,3], delay=[0,0,0.1])

# Retrasa cada 3 notas en .5
p1 >> blip([0,1,2,3], delay=[0,0,0.5])

# Toca la nota una vez por cada retardo diferente
p1 >> blip([0,1,2,3], delay=(0,0.1))

p1 >> blip([0,1,2,3], delay=(0,0.25))

p1 >> blip([0,1,2,3], delay=(0,.1,.2,.3))


####################
# dist