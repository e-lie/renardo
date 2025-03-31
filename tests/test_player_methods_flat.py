b2 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).every(4, "stutter", 3)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).often("reverse")

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).rarely("reverse")

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=PRand([.25,1,2,4,.5])).sometimes("reverse")

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).stutter(3)


b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).strum(.25)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).offbeat()

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).changeSynth(["pluck", "charm"])

b1.degrade(amount=.25)

b1.multiply(2)

# b1.bang() # what is that ?

l1 >> loop("foxdot").reload()

l1.stop()

b1.solo()

b1.solo(0)

b1.only()

b2 >> blip([0,3,0,4], dur=[1,.25,.75, .5,.5], sus=1)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).follow(b2)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).accompany(b2)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).spread()

b2 >> blip([0,1,2,3], dur=1, oct=3)

b1 >> blip([0,1,2,3], dur=1, sus=1).rshift() # shift played event of one note to the right

b1 >> blip([0,1,2,3], dur=1, sus=1).lshift() # shift played event of one note to the left

b2.stop()

b1 >> blip([0,1,2,3], dur=1, sus=1).penta() # switch to pentatonic mode of the current default scale

b1 >> blip([0,1,2,3], dur=1, sus=1).slider()

b1 >> blip([0,1,2,3], dur=1, sus=1).alt_dur(linvar([.1,1],16)) # switch dur to 1 and use bpm to change dur for use with linvar

b1.reverse()

b1.shuffle()

b1.rotate() # rotate degree pattern of one note

# p1 >> pads().map(b1, {0: {oct=[4,5], dur=PDur(3,8)}, 2: oct})

# smap

# attrmap


b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).spread()

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).unison()

b1.seconds() # mesure dur in second (<=> bpm=60)

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1).versus(b2) # Bug :/

b1.pause() # Bug :/

b1.play()

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1)

b1.stop()

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1)

b1.kill()

b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1)

# b1.addFx # Not implemented

b1.fade(fvol=.5)

b1.fadeout(autostop=False)

b1.fadein(dur=16)

b3 >> blip([0,3,0,4], dur=[1], sus=2, oct=4)

b1.solofade(fvol=.5) # Bug ?

b1.solofadein() # ?

b1.eclipse(4, 16, 2)

b2.eclipse(8, 16, 6)




# To debug :

# b1 >> blip([0,2,0,5], dur=[1,.25,.75, .5,.5], sus=1)

# p1 >> pads(dur=.25).map(b1, {0: oct=[4,5], 2: oct=6})   

# p1 >> pads(dur=.25).attrmap(b1, "degree", "dur")

# p1 >> pads(dur=.25).smap({"degree": {4: 0, 5: 1}})

