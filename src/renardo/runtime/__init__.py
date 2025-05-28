import logging

#base = set(dir())
#from renardo.lib.runtime import *
#new_symbols = set(dir()) - base
#symbols_str = f"import {', '.join(sorted(new_symbols))}"
#print(symbols_str)

from renardo.settings_manager import conf, get_tutorial_files

from renardo.lib.Code import (
    CodeString,
    CodeType,
    FunctionType,
    LiveObject,
    TypeType,
    WarningMsg, classes, clean, debug_stdout, error_stack, execute,
    foxdot_func_cmp, foxdot_live_function, foxdot_when_statement,
    get_input, get_now,
    handle_stdin, instances, livefunction,
    main_lib, modulo_index, re_player, when,
    write_to_file, FoxDotCode, functions
)

# Import and initialize startup files system
from .startup_files import STARTUP_FILE, create_startup_directory, load_startup_file
create_startup_directory()  # Ensure startup directory exists

# Replace the stub with our real startup file
main_lib.FOXDOT_STARTUP = STARTUP_FILE

# Set up the namespace
FoxDotCode.namespace = globals()
FoxDotCode.namespace['FOXDOT_STARTUP'] = STARTUP_FILE

from renardo.runtime.managers_instanciation import (
    settings, Server, sample_pack_library, sample_packs,
    DefaultSamples, buffer_manager, effect_manager, Effects,
    scresource_library, SynthDefs
)

from renardo.sc_backend.sc_music_resource import SCInstrument
SCInstrument.set_instrument_dict(SynthDefs)
SCInstrument.set_buffer_manager(buffer_manager)
SCInstrument.set_server(Server)

import renardo.runtime.synthdefs_initialisation

# import renardo.runtime.python_defined_effect_synthdefs

from renardo.sc_backend.PygenEffectSynthDefs import In, Out, PygenEffect
PygenEffect.set_server(Server)
# In()
# Out()
PygenEffect.server.setFx(effect_manager)



from renardo.lib.Player import Player

Player.set_effect_manager(effect_manager)
Player.set_synth_dict(SynthDefs)
Player.set_buffer_manager(buffer_manager)

from renardo.lib.TempoClock import (
    History,
    SchedulingQueue, QueueBlock, QueueObj, ScheduleError,
    SoloPlayer, TempoClock, Wrapper, PointInTime, PersistentPointInTime, RecurringPointInTime
)

from renardo.sc_backend import TempoClient, ServerManager, RequestTimeout

from renardo.sc_backend.Midi import MidiIn, MIDIDeviceNotFound

from renardo.lib.Patterns import (
    Add, CalculateDelaysFromDur, CalculateEuclideanDelay, ClassPatternMethod,
    Convert, Cycle, Div, DominantPattern, EmptyItem,
    EuclidsAlgorithm, FloorDiv, Format, GeneratorPattern, Generators,
    LCM, MAX_SIZE, Main, Mod, Mul, Nil,
    Operations, Or, P, P10, PAdd, PAlt, PBeat, PBern, PChain, PDelay,
    PDelta, PDiv, PDiv2, PDur, PEq, PEuclid, PEuclid2, PFibMod, PFloor, PFloor2,
    PGet, PGroup, PGroupAnd, PGroupDiv, PGroupMod, PGroupOr, PGroupPlus, PGroupPow,
    PGroupPrime, PGroupStar, PGroupXor, PGroups, PIndex, PJoin, PMod, PMod2, PMul,
    PNe, POperand, PPairs, PPow, PPow2, PQuicken, PRand, PRange, PRhythm, PShuf,
    PSine, PSq, PSquare, PStep, PStretch, PStrum, PStutter, PSub, PSub2, PSum,
    PTree, PTri, PWalk, PWhite, PZ12, PZip, PZip2, Parse, ParseError,
    ParsePlayString, Pattern, PatternContainer, PatternFormat, PatternInput,
    PatternMethod, PatternType, PlayString, Pow,
    PulsesToDurations, PwRand, PxRand, RandomGenerator,
    Sequences, StaticPatternMethod, Sub,
    Utils, Xor, amen, arrow_zip, asPattern, bar_type, br_pairs,
    braces_type, bubble, choice, convert_nested_data, convert_to_int, dots,
    equal_values, feed, force_pattern_args, fromString, functools,
    get_avg_if, group_modulo_index, itertools,
    loop_pattern_func, loop_pattern_method, math, metaPGroupPrime,
    metaPattern, offadd, offlayer, offmul, pattern_depth, patternclass, rAdd, rDiv,
    rFloorDiv, rGet, rMod, rMul, rOr, rPow, rSub, rXor, random, re_arrow,
    re_chars, re_curly, re_nests, re_square, shuffle, sliceToRange,
    square_type, sum_delays, as_pattern
)

from renardo.lib.ring import Ring, R

from renardo.lib.Player import (
    Bang,
    EmptyPlayer,
    Group, GroupAttr, LoopPlayer,
    NumberKey,
    PGroup,
    Pattern,
    PlayerKey, PlayerKeyException,
    Repeatable, Root,
    SamplePlayer, Scale,
    copy,
    get_first_item, get_freq_and_midi, inf,
    rest,
)
from renardo.lib.InstrumentProxy import InstrumentProxy

from renardo.lib.TimeVar import (
    ChildPvar, ChildTimeVar, PATTERN_METHODS, Pvar, PvarGenerator, PvarGeneratorEx,
    URLError, expvar, fetch, get_expanded_len, get_inverse_op, get_pypi_version,
    isiterable, json, max_length, recursive_any, sinvar, socket_timeout, urlopen, Get,
    TimeVar, linvar, expvar, var, xvar, yvar, mapvar
)

from renardo.lib.Constants import NoneConst, const
from renardo.sc_backend.Midi import MidiInputHandler, MidiOut, MidiInstrumentProxy, midi, rtMidiNotFound

from renardo.sc_backend import (
    Buffer, buffer_management, BufferManager, Dict, Optional, Path,
    TempoServer, closing, custom_osc_lib, heapq,
    nil, wave, PygenEffect
)



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

def player_method(f):
    """ Decorator for assigning functions as Player methods.

    >>> @player_method
    ... def test(self):
    ...    print(self.degree)

    >>> p1.test()
    """
    setattr(Player, f.__name__, f)
    return getattr(Player, f.__name__)

PlayerMethod = player_method # Temporary alias


#########################################
### Scheduling utils
#########################################

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

#########################################
### Reset clock and OSC server
#########################################



# TODO redesign this with new synthdef loading
# def _reload_synths():
#     """ Resends all the synth / sample info to SuperCollider. Useful for times
#         when starting FoxDot before running `FoxDot.start` in SuperCollider. """
#     from renardo.lib import SynthDefManagement
#     reload(SynthDefManagement._SynthDefs)
#     reload(Effects)
#     buffer_manager.reallocate_buffers()
#     return

def foxdot_reload():
    Server.init_connection()
    SynthDefs.reload()
    effect_manager.reload()
    buffer_manager.reallocate_buffers()
    return

# def _convert_json_bpm(clock, data):
#     """ Returns a TimeVar object that has been sent across a network using JSON """
#     if isinstance(data, list):
#         cls = data[0]
#         val = data[1]
#         dur = data[2]
#         return FoxDotCode.namespace[cls](val, dur)
#     else:
#         return data


# def allow_connections(valid = True, *args, **kwargs):
#     """ Starts a new instance of ServerManager.TempoServer and connects it with the clock. Default port is 57999 """
#     if valid:
#         Clock.start_tempo_server(TempoServer, **kwargs)
#         print("Listening for connections on {}".format(Clock.tempo_server))
#     else:
#         Clock.kill_tempo_server()
#         print("Closed connections")
#     return


#########################################
### Initialize base synthdefs
#########################################

from renardo.runtime.synthdefs_initialisation import *

Clock = TempoClock()

_Clock = Clock

#########################################
### Define some practical functions
#########################################

def Master():
    """ Returns a `Group` containing all the players currently active in the Clock """
    return Group(*Clock.playing)

def Ramp(t=32, ramp_time=4):
    """ Returns a `linvar` that goes from 0 to 1 over the course of the last
        `ramp_time` bars of every `t` length cycle. """
    return linvar([0,0,1,0],[t-ramp_time, ramp_time, 0, 0])

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
        return "Renardo ver. 0.9.13"
    def reload(self):
        Server.init_connection()
        SynthDefs.reload()
        effect_manager.reload()
        buffer_manager.reallocate_buffers()
        return
    def reassign_clock(self):
        FoxDotCode.namespace['Clock'] = _Clock
        return

FoxDot = _util()

# None is used for Rest/Silence in Pattern for Players
# Define _ as a shorthand alias
_ = None

logging.basicConfig(level=logging.ERROR)
when.set_namespace(FoxDotCode) # experimental



def set_main_clock(clock):
    """ Tells the TimeVar, Player, and MidiIn classes to use
        a new instance of TempoClock. """
    assert isinstance(clock, TempoClock)
    for item in (TimeVar, Player, MidiIn):
        item.set_clock(clock)
    # clock.add_method(_convert_json_bpm)
    return

def set_server_manager(serv):
    """ Tells the `Effect` and`TempoClock`classes to send OSC messages to
        a new ServerManager instance.
    """
    assert isinstance(serv, ServerManager)
    TempoClock.set_server(serv)
    serv.update_synthdef_dict(SynthDefs)

    return

set_server_manager(Server)

set_main_clock(Clock)


if settings.get("core.INSTANCIATE_FOXDOT_PLAYERS"):
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

    instantiate_player_objects()

# Create a "now" time variable
now = var([0]).transform(lambda a: Clock.now())
nextbar = var([0]).transform(lambda a: Clock.next_bar())

Attributes = Player.get_attributes()
PatternMethods = Pattern.get_methods()
PatternTypes = functions(Sequences)

## Conditionnal init of reaper backend
if settings.get("reaper_backend.REAPER_BACKEND_ENABLED"):
    from renardo.runtime.managers_instanciation import reaper_resource_library
    from renardo.reaper_backend import ReaperInstrument, init_reapy_project
    reaproject = init_reapy_project(Clock)
    ReaperInstrument.set_class_attributes(
        presets={},
        project=reaproject,
        resource_library=reaper_resource_library
    )
    from .reaper_backend_init import *
    create_selected_instruments = ReaperInstrumentFactory(FoxDotCode) # then we can call create_selected_instruments as a function


schedule = Clock.schedule
now = Clock.now
mod = Clock.mod
pit = PointInTime
ppit = PersistentPointInTime
rpit = RecurringPointInTime


# Start !!!
Clock.start()