### New scheduling feature PointInTime

### Start 16 beats later when defining Point in time value

b1 >> blip()

pit1 = PointInTime()  # or pit() to be shorter


def footworking():
    Clock.bpm = 160
    b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6])
    k2 >> play("v.(.x)(v*)*v.", dur=.25)
    d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


Clock.schedule(footworking, pit1)

pit1.beat = Clock.now() + 16  # the music declared in function footworking will start in 16 beats when you evaluate this line

### You can also use substraction (or other point in time arithmetic) to start stuff before the point in time
# This way you can rendez vous at some point in time

def somebreak_rise():
    b1.fadein(32)  # rising melody for 32 beats before break


def somebreak():
    d2.amplify = 0  # break (cutting the drum)
    k2.amplify = 0


pit2 = pit()  # pit is an alias for PointInTime

Clock.schedule(somebreak_rise, pit2 - 32)
Clock.schedule(somebreak, pit2)

Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)
pit2.beat = now() + 64

# Doing the same using the new macro langage

## Rather than using Clock.shecule with a function which is hard and long to livecode
# and introduce a need for python indentation, renardo introduces a new macro langage
# It is comment based and compiled at evaluation time.

# The basic syntax is #{ moment/beat_number refering to the clock }

# For example the following...

# {Clock.now()+8} # starting in 8 beats
Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


# ...is equivalent to :

def footworking_func():
    Clock.bpm = 160
    b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
               amplify=0)
    k2 >> play("v.(.x)(v*)*v.", dur=.25)
    d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)


Clock.schedule(footworking_func, Clock.now() + 8)

## Preceding rendez vous example with macro syntax

pit3 = pit()

Clock.bpm = 160
b1 >> blip([0, 1, 5, [2, [_, 1]]], dur=var([.5, .25], 8), sus=1, amp=1.5 * P[.4, .7, 1, .7], lpf=800, oct=[4, 5, 6],
           amplify=0)
k2 >> play("v.(.x)(v*)*v.", dur=.25)
d2 >> play("{cccc.}", dur=var([2, 2 / 3], [12, 4]), rate=(1.2, 2.4), lpf=800)

# {pit3-32}
b1.fadein(32)  # rising melody for 32 beats before break
# {pit3}
d2.amplify = 0  # break (cutting the drum)
k2.amplify = 0
# {pit3+32}  # Bonus stopping 32 beat after the break
Clock.clear()

pit3.beat = now() + 64