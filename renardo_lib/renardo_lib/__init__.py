import logging

from renardo_lib.Code import *
from renardo_gatherer.samples_download import SPackManager

FoxDotCode.namespace = globals()

spack_manager = SPackManager()

from renardo_lib.TempoClock import *
from renardo_lib.Buffers import *
from renardo_lib.Players import *
from renardo_lib.PlayerMethods import *
from renardo_lib.Groups import *
from renardo_lib.Patterns import *
from renardo_lib.Effects import *
from renardo_lib.TimeVar import *
from renardo_lib.Constants import *
from renardo_lib.Midi import *
from renardo_lib.Settings import *
from renardo_lib.SCLang._SynthDefs import *
from renardo_lib.ServerManager import *
from renardo_lib.SCLang import SynthDefs, Env, SynthDef, CompiledSynthDef
from renardo_lib.Root import Root
from renardo_lib.Scale import Scale, Tuning

@PatternMethod
def __getitem__(self, key):
    """ Overrides the Pattern.__getitem__ to allow indexing
        by TimeVar and PlayerKey instances. """
    if isinstance(key, PlayerKey):
        # Create a player key whose calculation is get_item
        return key.index(self)
    elif isinstance(key, TimeVar):
        # Create a TimeVar of a PGroup that can then be indexed by the key
        item = TimeVar(tuple(self.data))
        item.dependency = key
        item.evaluate = fetch(Get)
        return item
    else:
        return self.getitem(key)

def _futureBarDecorator(n, multiplier=1):
    if callable(n):
        def switch(*args, **kwargs):
            Clock.now_flag = True
            output = n()
            Clock.now_flag = False
            return output
        Clock.schedule(switch, Clock.next_bar())
        return switch
    def wrapper(f):
        Clock.schedule(f, Clock.next_bar() + (n * multiplier))
        return f
    return wrapper

def next_bar(n=0):
    ''' Schedule functions when you define them with @nextBar
    Functions will run n beats into the next bar.

    >>> nextBar(v1.solo)
    or
    >>> @nextBar
    ... def dostuff():
    ...     v1.solo()
    '''
    return _futureBarDecorator(n)

nextBar = next_bar # temporary alias

def futureBar(n=0):
    ''' Schedule functions when you define them with @futureBar
    Functions will run n bars in the future (0 is the next bar)

    >>> futureBar(v1.solo)
    or
    >>> @futureBar(4)
    ... def dostuff():
    ...     v1.solo()
    '''
    return _futureBarDecorator(n, Clock.bar_length())

def update_foxdot_clock(clock):
    """ Tells the TimeVar, Player, and MidiIn classes to use
        a new instance of TempoClock. """

    assert isinstance(clock, TempoClock)

    for item in (TimeVar, Player, MidiIn):

        item.set_clock(clock)

    clock.add_method(_convert_json_bpm)

    return

def update_foxdot_server(serv):
    """ Tells the `Effect` and`TempoClock`classes to send OSC messages to
        a new ServerManager instance.
    """

    assert isinstance(serv, ServerManager)

    TempoClock.set_server(serv)
    SynthDefs.set_server(serv)

    return

def instantiate_player_objects():
    """ Instantiates all two-character variable Player Objects """
    alphabet = list('abcdefghijklmnopqrstuvwxyz')
    numbers  = list('0123456789')

    for char1 in alphabet:

        group = []

        for char2 in alphabet + numbers:

            arg = char1 + char2

            FoxDotCode.namespace[arg] = EmptyPlayer(arg)

            group.append(arg)

        FoxDotCode.namespace[char1 + "_all"] = Group(*[FoxDotCode.namespace[char1+str(n)] for n in range(10)])

    return

def _reload_synths():
    """ Resends all the synth / sample info to SuperCollider. Useful for times
        when starting FoxDot before running `FoxDot.start` in SuperCollider. """
    from renardo_lib import SCLang
    from renardo_lib import Effects
    reload(SCLang._SynthDefs)
    reload(Effects)
    Samples._reset_buffers()
    return

def foxdot_reload():
    Server.reset()
    SynthDefs.reload()
    FxList.reload()
    Samples.reset()
    return

def _convert_json_bpm(clock, data):
    """ Returns a TimeVar object that has been sent across a network using JSON """
    if isinstance(data, list):
        cls = data[0]
        val = data[1]
        dur = data[2]
        return FoxDotCode.namespace[cls](val, dur)
    else:
        return data

def Master():
    """ Returns a `Group` containing all the players currently active in the Clock """
    return Group(*Clock.playing)

def Ramp(t=32, ramp_time=4):
    """ Returns a `linvar` that goes from 0 to 1 over the course of the last
        `ramp_time` bars of every `t` length cycle. """
    return linvar([0,0,1,0],[t-ramp_time, ramp_time, 0, 0])

def allow_connections(valid = True, *args, **kwargs):
    """ Starts a new instance of ServerManager.TempoServer and connects it with the clock. Default port is 57999 """
    if valid:
        Clock.start_tempo_server(TempoServer, **kwargs)
        print("Listening for connections on {}".format(Clock.tempo_server))
    else:
        Clock.kill_tempo_server()
        print("Closed connections")
    return

def Go():
    """ Function to be called at the end of Python files with FoxDot code in to keep
        the TempoClock thread alive. """
    try:
        import time
        while 1:
            time.sleep(100)
    except KeyboardInterrupt:
        return

# Util class

class _util:
    def __repr__(self):
        return "Renardo ver. 1.0.0.dev2"
    def reload(self):
        Server.reset()
        SynthDefs.reload()
        FxList.reload()
        Samples.reset()
        return
    def reassign_clock(self):
        FoxDotCode.namespace['Clock'] = _Clock
        return

FoxDot = _util()

# Create a clock and define functions

_ = None

logging.basicConfig(level=logging.ERROR)
when.set_namespace(FoxDotCode) # experimental

_Clock = Clock = TempoClock()

update_foxdot_server(Server)
update_foxdot_clock(Clock)
instantiate_player_objects()

# Create a "now" time variable
now = var([0]).transform(lambda a: Clock.now())
nextbar = var([0]).transform(lambda a: Clock.next_bar())

Attributes = Player.get_attributes()
PatternMethods = Pattern.get_methods()
PatternTypes = functions(Patterns.Sequences)

# Start

Clock.start()
