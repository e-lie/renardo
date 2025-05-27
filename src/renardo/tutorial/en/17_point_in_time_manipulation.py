### Start in 16 beats

pit1 = PointInTime()

def haha():
    b1 >> blip()
    p2 >> play("ziuhf")

Clock.schedule(haha, pit1)

pit1.beat=Clock.now()+16


### Start 16 beats before RDV

def fadeinbloup():
    b1 >> blip().fadein(16)

pit2 = PointInTime() - 16

Clock.schedule(fadeinbloup, pit2)

pit2.beat=Clock.mod(32)