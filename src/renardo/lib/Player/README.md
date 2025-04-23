FoxDot generates music by creating instances of `Player` and giving them instructions
to follow. At startup FoxDot creates many instances of `Player` and assigns them to
any valid two character variable. This is so that when you start playing you don't
have to worry about typing `myPlayer = Player()` and `myPlayer_2 = Player()` every
time you want to do something new. Of course there is nothing stopping you from
doing that if yo so wish.

Instances of `Player` are given instructions to generate music using the `>>` syntax,
overriding the bitshift operator, and should be given an instance of `SynthDefProxy`.
A `SynthDefProxy` is created when calling an instance of `SynthDef` - these are the
"instruments" used by player objects and are written in SuperCollider code. You can
see more information about these in the `SynthDefManagement` module. Below describes how to assign
a `SynthDefProxy` of the `SynthDef` `pads` to a `Player` instance called `p1`: ::

    # Calling pads as if it were a function returns a
    # pads SynthDefProxy object which is assigned to p1
    p1 >> pads()

    # You could store several instances and assign them at different times
    proxy_1 = pads([0,1,2,3], dur=1/2)
    proxy_2 = pads([4,5,6,7], dur=1)

    p1 >> proxy_1 # Assign the first to p1
    p1 >> proxy_2 # This replaces the instructions being followed by p1