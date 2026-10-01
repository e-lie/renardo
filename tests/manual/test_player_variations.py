# Manual test: compact player-variant syntax (`param_N=value`)
#
# Feature not implemented yet at the time this file was written (see
# ignored_files/plan_player_variants.md for the dev plan). This file is a
# test bench to load in the Renardo editor once the implementation is
# done: trigger each block yourself (like the tutorials in
# src/renardo/tutorial/) and listen for the result described in the
# comments.
#
# Reminder of the principle: on any player kwarg, a "_N" suffix (N from 2
# to 9) automatically creates/updates a `<name>_N` player identical to the
# base player, except for the suffixed params which take the given value.
# Removing the "_N" kwarg by re-triggering the line stops the variant.
# Stopping the base player also stops its variants.


# --------------------------------------------------------------------------
# 1. Basic case: a single variant, a single parameter that diverges
# --------------------------------------------------------------------------

# Base octave (b1) + one octave above (b1_2), automatically:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

# You should hear BOTH octaves playing at the same time, looping, exactly
# the same rhythmic/melodic pattern.

b1.stop()


# --------------------------------------------------------------------------
# 2. Grouping several parameters on the same variant
# --------------------------------------------------------------------------

# oct_2 and dur_2 must both apply to the SAME variant b1_2:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6, dur_2=.125)

# b1: octave 5, normal tempo (dur=.25)
# b1_2: octave 6 AND twice as fast (dur=.125) -- a single extra player,
# not two.

b1.stop()  # should stop b1 AND b1_2 (see section 7 to check this in depth)


# --------------------------------------------------------------------------
# 3. Several variants at the same time
# --------------------------------------------------------------------------

# oct_2 and oct_3: two distinct variants, b1_2 AND b1_3
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6, oct_3=7)

# You should hear THREE octaves of the same pattern playing together
# (5, 6, 7).

b1.stop()


# --------------------------------------------------------------------------
# 4. degree_N: the note pattern itself can vary, not just timbre
#    parameters
# --------------------------------------------------------------------------

b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, degree_2=[0, 1, 2, 3])

# b1 plays [0,2,4,5], b1_2 plays [0,1,2,3] -- two different melodies, same
# rhythm, same timbre.

b1.stop()

# This also works if the base is written with the explicit degree= keyword
# instead of positionally:
b1 >> blip(degree=[0, 2, 4, 5], dur=.25, oct=5, degree_2=[7, 9, 11, 12])

b1.stop()


# --------------------------------------------------------------------------
# 5. Live coding: re-triggering the line updates the variant LIVE
# --------------------------------------------------------------------------

# Run this block:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

# Let it run a few seconds, then re-run this block (same line, different
# oct_2) WITHOUT stopping b1 first:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=8)

# b1_2 should change octave (6 -> 8) without interrupting the pattern or
# restarting from scratch -- just like when you change a parameter on b1
# normally.

b1.stop()


# --------------------------------------------------------------------------
# 6. Live coding: removing the "_N" param stops the variant on its own
# --------------------------------------------------------------------------

b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

# Let it run a few seconds (b1 + b1_2 audible), then re-run the line
# WITHOUT oct_2:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5)

# b1_2 should stop on its own, leaving only b1 (octave 5).

b1.stop()


# --------------------------------------------------------------------------
# 7. Cascading stop: stopping the base player stops its variants too
# --------------------------------------------------------------------------

b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6, oct_3=7)

# Let all 3 octaves run for a few seconds, then a single stop:
b1.stop()

# All THREE octaves should go silent, not just b1. If b1_2/b1_3 keep
# playing after this stop, the cascade is broken.


# --------------------------------------------------------------------------
# 8. Chained methods after >> should also apply to the variants
# --------------------------------------------------------------------------

b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6).every(4, "reverse")

# Let it run for at least 4 bars: b1 AND b1_2 should have their pattern
# reversed AT THE SAME TIME every 4 bars, not just b1.

b1.stop()

# Same check with an amp/chop-style effect instead of .every, to make sure
# this isn't specific to .every:
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6).amp(0.6)

b1.stop()


# --------------------------------------------------------------------------
# 9. Edge case to verify: must NOT collide with real effect parameters
#    that already end with a digit glued to the name (room2, mix2, damp2,
#    fdistcfreq1..4, fx1/fx2...). That's why the convention uses an
#    UNDERSCORE before the digit (room_2), never just "room2".
# --------------------------------------------------------------------------

# room_2 (with underscore) = variant: b1_2 should exist with room=0.8
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, room=0.3, room_2=0.8)

# b1: light reverb (room=0.3). b1_2: stronger reverb (room=0.8), same
# note, same octave.

b1.stop()

# room2 (WITHOUT underscore) is a real, distinct effect parameter (second
# reverb stage), NOT a variant marker. No "b3_2" player should appear
# here, room2 should just apply normally to b3:
b3 >> blip([0, 2, 4, 5], dur=.25, oct=5, room2=0.5)

# You should hear ONE SINGLE player (b3), with a reverb effect applied. If
# a phantom "b3_2" starts playing too, that's a bug in the feature.

b3.stop()


# --------------------------------------------------------------------------
# 10. Valid suffix range: only _2 to _9. _0, _1 and _10+ are NEVER treated
#     as variant markers (1 = the base player itself, not a separate
#     variant).
# --------------------------------------------------------------------------

b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_1=99, oct_0=99, oct_10=99)

# No b1_1, b1_0 or b1_10 should appear. You should hear b1 alone, at
# octave 5 (oct_1/oct_0/oct_10 are ignored as markers -- depending on the
# implementation they may either be silently ignored or raise an error;
# check against the choice made in the plan).

b1.stop()


# --------------------------------------------------------------------------
# 11. Silent overwrite: if a "b1_2" player already exists for some
#     unrelated reason, the variant should take its place cleanly --
#     without leaving the old sound running in the background ("ghost
#     sound").
#
#     Unlike b1, b2, p1... "b1_2" is NOT one of the pre-declared 2-character
#     player names, so it doesn't exist yet and you have to create it
#     yourself. Do it through FoxDotCode.namespace (not a plain
#     `b1_2 = Player()`): the variant-overwrite logic looks names up in
#     FoxDotCode.namespace, and depending on how you're running this file
#     (the Renardo editor vs. a plain Python/IPython shell), a bare
#     top-level assignment may or may not end up in that same dict. Going
#     through FoxDotCode.namespace directly reproduces the collision
#     reliably either way.
# --------------------------------------------------------------------------

# We deliberately occupy the name b1_2 with an unrelated player:
b1_2 = Player("b1_2")
FoxDotCode.namespace["b1_2"] = b1_2
b1_2 >> pluck([7], dur=1)

# You should hear a low pluck alone here. Let it run a bit.

# Now trigger a variant that will want to reuse "b1_2":
b1 >> blip([0, 2, 4, 5], dur=.25, oct=5, oct_2=6)

# The low pluck should disappear completely, replaced by the blip at
# octave 6. If you still hear the pluck together with the blip, that's a
# ghost sound -- a bug to fix (the old player must be stopped before being
# replaced). Check FoxDotCode.namespace["b1_2"] if you want to confirm in
# code rather than by ear -- it should now be the blip variant, not the
# pluck.

b1.stop()


# --------------------------------------------------------------------------
# 12. Also works for sample players, not just melodic synths
# --------------------------------------------------------------------------

p1 >> play("x-x-", sample=2, room_2=0.5)

# p1: "dry" sample pattern. p1_2: same pattern, same sample, but with more
# reverb (room=0.5).

p1.stop()

# Combine with a sample-pattern change on the variant, via a named
# parameter (no need for degree_N here, "sample" already acts as the
# standard named parameter for play()):
p1 >> play("x-x-", sample=2, sample_2=4)

# p1 and p1_2 should play the same "x-x-" rhythm but with two different
# sample sounds (sample=2 vs sample=4).

p1.stop()
