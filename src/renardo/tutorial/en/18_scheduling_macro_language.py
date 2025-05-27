
pit2 = PointInTime()

# {Clock.now()+8}
p1 >> pluck

# {Clock.mod(16)}
b1 >> blip()

# {pit2 - 16}
b1.fadein(dur=16)

pit2.beat=Clock.now()