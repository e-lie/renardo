
pit2 = PointInTime()

# {Clock.now()+8}
p1 >> pluck()

# {Clock.mod(16)}
b1 >> blip()

# {pit2 - 16}
b1.fadeout(dur=16)

pit2.beat=Clock.now() + 24





########################

pit5 = PointInTime()

#{pit5} # this works
p1 >> pluck()

pit5.beat=Clock.now()+8


pit6 = PointInTime()

#{pit6 + 8} # this does not work
p1 >> pluck()

pit6.beat=Clock.now()+8