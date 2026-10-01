# Tutorial 5: Referencing Player Attributes

# You can set variables outside a player
pitches = P[0,1,2,3,4]
harmony = pitches + 2

print(pitches)
print(harmony)

p1 >> pluck(pitches)
p2 >> star(harmony)

# If you set the duration of the second, it might not have the desired effect
p1 >> pluck(pitches)
p2 >> star(harmony, dur=1/2)

# It is possible for one player object to play exactly what another player is.
# To have one player follow another, just use the follow method:
p1 >> pluck(pitches)

p2 >> star(dur=1/2).follow(p1) + 2

# You can explicitly reference attributes such as pitch or duration too:

p2 >> star(p1.pitch) + 2  # this is the same as .follow(p1)

# Works for other attributes too
p1 >> pluck(pitches)
p2 >> star(dur=p1.dur).follow(p1) + 2

# You can reference, and test for the current value
# The == returns a 1 if true and a 0 if false
print(p1.degree)
print(p1.degree == 2)

# This allows you to do conditionals like
p1 >> pluck([0,1,2,3], amp=(p1.degree==1))

p1 >> pluck([0,1,2,3], amp=(p1.degree>1))

# Or change it to a different amp by multiplying by 4
p1 >> pluck([0,1,2,3], amp=(p1.degree==1)*4)

# Chain multiple conditionals
p1 >> pluck([0,1,2,3], amp=(p1.degree==1)*4 + (p1.degree==2)*1)

# Which is the same as
p1 >> pluck([0,1,2,3], amp=p1.degree.map({1:4, 2:1}))

# O cámbialo por otro amplificador multiplicando por 4
p1 >> pluck([0,1,2,3], amp=(p1.degree==1))

p1 >> pluck([0,1,2,3], amp=(p1.degree>1))

# --------------------------------------------------------------------------
# Global defaults and "stickiness"
# --------------------------------------------------------------------------

# Just like Scale and Root (see Tutorial 8), the common attributes oct, dur,
# sus, pan, rate and sample each have a global `.default` you can change:

Oct.default = 6
Dur.default = 1
Sus.default = 1
Pan.default = 0
Rate.default = 1
Sample.default = 0

# Any player that has NOT set that attribute itself will pick up the new
# value on its very next event -- you don't need to retrigger it with '>>':
p1 >> pluck(pitches)
Oct.default = 5  # p1 jumps down an octave immediately, still playing

# But as soon as you set an attribute explicitly on a player, it "sticks":
# the player keeps that value even if you change the global default
# afterwards.
p1 >> pluck(pitches, oct=4)
Oct.default = 7
# p1 is still at oct=4 here

# If you'd rather have attributes behave exactly like scale/root -- always
# reverting to the current global default whenever you retrigger the player
# without that keyword, even if you gave it an explicit value before -- flip
# this switch:
PlayerDefaults.sticky_override = False

p1 >> pluck(pitches)  # no 'oct' keyword here, so it picks up Oct.default (7)
Oct.default = 5

# Set it back to the default ("sticky") behaviour:
PlayerDefaults.sticky_override = True
