## Tempo Clock design

Clock management for scheduling notes and functions. Anything 'callable', such as a function
or instance with a `__call__` method, can be scheduled. An instance of `TempoClock` is created
when FoxDot started up called `Clock`, which is used by `Player` instances to schedule musical
events. 

The `TempoClock` is also responsible for sending the osc messages to SuperCollider. It contains
a queue of event blocks, instances of the `QueueBlock` class, which themselves contain queue
items, instances of the `QueueObj` class, which themseles contain the actual object or function
to be called. The `TempoClock` is continually running and checks if any queue block should 
be activated. A queue block has a "beat" value for which its contents should be activated. To make
sure that events happen on time, the `TempoClock` will begin processing the contents 0.25
seconds before it is *actually* meant to happen in case there is a large amount to process.  When 
a queue block is activated, a new thread is created to process all of the callable objects it
contains. If it calls a `Player` object, the queue block keeps track of the OSC messages generated 
until all `Player` objects in the block have been called. At this point the thread is told to
sleep until the remainder of the 0.25 seconds has passed. This value is stored in `Clock.latency`
and is adjustable. If you find that there is a noticeable jitter between events, i.e. irregular
beat lengths, you can increase the latency by simply evaluating the following in FoxDot:

    Clock.latency = 0.5

To stop the clock from scheduling further events, use the `Clock.clear()` method, which is
bound to the shortcut key, `Ctrl+.`. You can schedule non-player objects in the clock by
using `Clock.schedule(func, beat, args, kwargs)`. By default `beat` is set to the next
bar in the clock, but you use `Clock.now() + n` or `Clock.next_bar() + n` to schedule a function
in the future at a specific time. 

To change the tempo of the clock, just set the bpm attribute using `Clock.bpm=val`. The change
in tempo will occur at the start of the next bar so be careful if you schedule this action within
a function like this:

    def myFunc():
        print("bpm change!")
        Clock.bpm+=50

This will print the string `"bpm change"` at the next bar and change the bpm value at the
start of the *following* bar. The reason for this is to make it easier for calculating
currently clock times when using a `TimeVar` instance (See docs on TimeVar.py) as a tempo.

You can change the clock's time signature as you would change the tempo by setting the
`meter` attribute to a tuple with two values. So for 3/4 time you would use the follwing
code:

    Clock.meter = (3,4)