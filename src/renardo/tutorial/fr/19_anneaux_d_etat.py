
### Les Rings comme une sorte de méta-Patterns

# Les Rings sont des cycles de valeurs qui passent à la valeur suivante à chaque fois que l'expression est évaluée

b1 >> blip(R[2,3,P[2,3], var([2,1,4])]) # Reste sur la note/degree 2, puis en réévaluant reste sur 3, puis sur le Pattern [2,3] etc

# Les Rings peuvent contenir n'importe quel objet ou valeur

## Les Rings sont censés être utilisés avec des points dans le temps récurrents ou persistants (ne fonctionne pas pour l'instant)

rpit1 = rpit(16)
ppit1 = ppit()

rpit1.beat = now()

#{ppit1}
b1 >> blip(R[0,5,10]).stop(1.5)

ppit1.beat = now() + 16

ppit1.beat = now() + 32

