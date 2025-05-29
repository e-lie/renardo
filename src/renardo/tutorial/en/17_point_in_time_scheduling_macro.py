### New scheduling feature PointInTime

### Start in 16 beats

pit1 = PointInTime()

def whatever():
    b1 >> blip([0,2,4,5], lpf=800)
    p2 >> play("V..V*V.")

Clock.schedule(whatever, pit1)

pit1.beat=Clock.now()+16 # the music declared in function whatever will start in 16 beats when you evaluate this line

### You can also use substraction to start stuff before the point in time
# This way you can rendez vous at some point in time

def fadeinbloup():
    b1 >> blip().fadein(16)

pit2 = pit() - 16 # pit is an alias for PointInTime

Clock.schedule(fadeinbloup, pit2)

pit2.beat=Clock.mod(32)

# Using the new macro langage

## Rather than using Clock.shecule with a function which is hard and long to livecode
# and introduce a need for python indentation, renardo introduces a new macro langage
# It is comment based and compiled at evaluation time.

# The basic syntax is #{ moment/beat_number refering to the clock }

# For example the following...

# {Clock.now()+8}
p1 >> pluck()

# ...is equivalent to :

def pluck_func():
    p1 >> pluck()
Clock.schedule(pluck_func, Clock.now()+8)

## Other examples

# {Clock.mod(16)}
b1 >> blip()

## And with point in time class wich help manipulate future event more abstractly :

pit2 = PointInTime()
b1 >> blip(amplify=0)

# {pit2} # schedules the the fadein at an undefined moment later
b1.fadein(dur=16)

# Set the undefined moment triggers the fadein at the right time
pit2.beat=Clock.now() + 24
