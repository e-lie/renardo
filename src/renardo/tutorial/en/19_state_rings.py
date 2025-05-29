
### Rings as kinda meta Patterns

# Rings are cycles of values that switch to next value each time the expression is evaluated

b1 >> blip(R[2,3,P[2,3], var([2,1,4])]) # Will stay on note/degree 2, then when reevaluated stays on 3, then on Pattern [2,3] etc

# Rings can contain any objects or values

## Rings are meant to be used with recurrent or persistent points in time (not working for now)

rpit1 = rpit(16)
ppit1 = ppit()

rpit1.beat = now()

#{ppit1}
b1 >> blip(R[0,5,10]).stop(1.5)

ppit1.beat = now() + 16

ppit1.beat = now() + 32

