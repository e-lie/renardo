### OSC triggers: fire code from an incoming OSC message

# trig("/some/route") gives you an object that behaves exactly like the
# PointInTime you already know from the previous tutorials, except that
# instead of being defined by you (pit.beat = ...), it defines *itself*
# every time an OSC message is received on that address, from any
# software (Ableton, TouchOSC, Max/MSP, another renardo instance, a
# python-osc script...). Message arguments are ignored for now.

b1 >> blip()


def go_up():
    b1.oct = 6


Clock.schedule(go_up, trig("/octave"))

# Send an OSC message to 127.0.0.1:57430, address "/octave" (from any OSC
# capable software) and b1 will jump up an octave on the next beat.

### Same thing with the macro language

# {trig("/octave")}
b1.oct = 6

### trig() supports the same arithmetic as PointInTime

# Fire 8 beats after the OSC message instead of immediately

# {trig("/octave")+8}
b1.degree = 4

### trig() is persistent: it fires again on every subsequent message

# Every macro block or Clock.schedule call attached to a trigger stays
# attached — no need to re-evaluate anything between OSC messages.

d1 >> play("x-o-")

# {trig("/fill")}
d1.oct += 1

### Binding a PointInTime to a trigger

# `some_point.beat = trig("/route")` binds any PointInTime to a trigger:
# instead of a beat number, `some_point` gets Clock.now() every time the
# trigger fires. This is handy when you want the rendez-vous machinery
# from tutorial 17 (several points scheduled relative to one another)
# driven by an external OSC message instead of a beat number.

# A plain pit() only fires once this way (like any plain PointInTime),
# so use ppit() if you want it to be redefined on every message:

drop = ppit()


def rise():
    b1.oct += 1


def fall():
    b1.oct -= 1


Clock.schedule(rise, drop - 16)
Clock.schedule(fall, drop)

drop.beat = trig("/drop")  # every "/drop" message now redefines `drop`

### Configuring the OSC trigger server

# By default the trigger server listens on 127.0.0.1:57430. You can
# change this (e.g. to listen on all interfaces, or avoid a port clash)
# before triggering anything:

Clock.osc_trig_addr = "0.0.0.0"
Clock.osc_trig_port = 9000

# Changing either restarts the trigger server if it was already running.
