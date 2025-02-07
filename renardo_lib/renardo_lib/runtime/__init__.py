import logging

#base = set(dir())
#from renardo_lib.runtime import *
#new_symbols = set(dir()) - base
#symbols_str = f"import {', '.join(sorted(new_symbols))}"
#print(symbols_str)


from renardo_lib.Settings import (
    ADDRESS, ALPHA_VALUE, AUTO_COMPLETE_BRACKETS, BOOT_ON_STARTUP, CHECK_FOR_UPDATE,
    CLOCK_LATENCY, COLOR_THEME, COLOURS, CONSOLE_ON_STARTUP, CPU_USAGE,
    EFFECTS_DIR, ENVELOPE_DIR, FONT, FORWARD_ADDRESS, FORWARD_PORT,
    FOXDOT_CONFIG_FILE, FOXDOT_EDITOR_ROOT, FOXDOT_EDITOR_THEMES, FOXDOT_EFFECTS_FILE,
    FOXDOT_HELLO, FOXDOT_ICON, FOXDOT_ICON_GIF, FOXDOT_LOOP, FOXDOT_ROOT,
    FOXDOT_SETTINGS, FOXDOT_SND, FOXDOT_STARTUP_PATH,
    GET_SC_INFO, LINENUMBERS_ON_STARTUP, LINE_NUMBER_MARKER_OFFSET,
    MAX_CHANNELS, MENU_ON_STARTUP, PORT, PORT2, RECORDING_DIR,
    RECOVER_WORK, SAMPLES_DIR, SAMPLES_PACK_NUMBER, SC3_PLUGINS, SUPERCOLLIDER,
    SYNTHDEF_DIR, TEXT_COLORS, TMP_EFFECTS_DIR, TMP_SYNTHDEF_DIR,
    TRANSPARENT_ON_STARTUP, TREEVIEW_ON_STARTUP, TUTORIAL_DIR, USE_ALPHA,
    conf,
    get_samples_dir_path, get_synthdefs_dir_path,
    get_tutorial_files,
    reload,
)
from renardo_lib.Code import (
    CodeString,
    CodeType,
    FunctionType,
    LiveObject,
    TypeType,
    WarningMsg, classes, clean, debug_stdout, error_stack, execute,
    foxdot_func_cmp, foxdot_live_function, foxdot_when_statement,
    get_input, get_now,
    handle_stdin, instances, livefunction, load_startup_file,
    main_lib, modi, re_player, when,
    write_to_file, FoxDotCode, functions, FOXDOT_STARTUP
)

FoxDotCode.namespace = globals()

from renardo_sc_backend import buffer_manager, DefaultSamples, Samples
from renardo_lib.runtime import synthdefs_initialisation

from renardo_lib.TempoClock import (
    Code, History, MIDIDeviceNotFound, MethodCall, MethodType, MidiIn, Player,
    Queue, QueueBlock, QueueObj, RequestTimeout, ScheduleError, ServerManager,
    SoloPlayer, TempoClient, TempoClock, TimeVar, Wrapper, asStream, inspect,
    threading
)

from renardo_lib.Players import (
    Add, Bang, CalculateDelaysFromDur, CalculateEuclideanDelay, ClassPatternMethod,
    Convert, Cycle, DefaultPygenSynthDef, Div, DominantPattern, EmptyItem,
    EmptyPlayer, EuclidsAlgorithm, FloorDiv, Format, GeneratorPattern, Generators,
    Get, Group, GroupAttr, LCM, LoopPlayer, MAX_SIZE, Main, Mod, Mul, Nil,
    NumberKey, Operations, Or, P, P10, PAdd, PAlt, PBeat, PBern, PChain, PDelay,
    PDelta, PDiv, PDiv2, PDur, PEq, PEuclid, PEuclid2, PFibMod, PFloor, PFloor2,
    PGet, PGroup, PGroupAnd, PGroupDiv, PGroupMod, PGroupOr, PGroupPlus, PGroupPow,
    PGroupPrime, PGroupStar, PGroupXor, PGroups, PIndex, PJoin, PMod, PMod2, PMul,
    PNe, POperand, PPairs, PPow, PPow2, PQuicken, PRand, PRange, PRhythm, PShuf,
    PSine, PSq, PSquare, PStep, PStretch, PStrum, PStutter, PSub, PSub2, PSum,
    PTree, PTri, PWalk, PWhite, PZ12, PZip, PZip2, Parse, ParseError,
    ParsePlayString, Pattern, PatternContainer, PatternFormat, PatternInput,
    PatternMethod, PatternType, PlayString, PlayerKey, PlayerKeyException, Pow,
    PulsesToDurations, PwRand, PxRand, RandomGenerator, Repeatable, Root,
    SamplePlayer, Scale, Sequences, StaticPatternMethod, Sub, SynthDefProxy,
    SynthDefs, Utils, Xor, amen, arrow_zip, asPattern, bar_type, br_pairs,
    braces_type, bubble, choice, convert_nested_data, convert_to_int, copy, dots,
    effect_manager, equal_values, feed, force_pattern_args, fromString, functools,
    get_avg_if, get_first_item, get_freq_and_midi, group_modi, inf, itertools,
    linvar, loop_pattern_func, loop_pattern_method, mapvar, math, metaPGroupPrime,
    metaPattern, offadd, offlayer, offmul, pattern_depth, patternclass, rAdd, rDiv,
    rFloorDiv, rGet, rMod, rMul, rOr, rPow, rSub, rXor, random, re_arrow,
    re_chars, re_curly, re_nests, re_square, rest, shuffle, sliceToRange,
    square_type, sum_delays, var
)

from renardo_lib.TimeVar import (
    ChildPvar, ChildTimeVar, PATTERN_METHODS, Pvar, PvarGenerator, PvarGeneratorEx,
    URLError, expvar, fetch, get_expanded_len, get_inverse_op, get_pypi_version,
    isiterable, json, max_length, recursive_any, sinvar, socket_timeout, urlopen
)

from renardo_lib.Constants import NoneConst, const
from renardo_lib.Midi import MidiInputHandler, MidiOut, midi, rtMidiNotFound

from renardo_sc_backend import (
    Buffer, BufferManagement, BufferManager, DESCRIPTIONS, Dict, Optional, Path,
    Server, SynthDefManagement, TempoServer, alpha, closing, custom_osc_lib, heapq,
    nil, sample_pack_library, settings_manager, supercollider_settings, wave
)

from renardo_lib.SynthDefManagement.SynthDict import SynthDefs


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
    serv.update_synthdef_dict(SynthDefs)

    return

def _reload_synths():
    """ Resends all the synth / sample info to SuperCollider. Useful for times
        when starting FoxDot before running `FoxDot.start` in SuperCollider. """
    from renardo_lib import SynthDefManagement
    reload(SynthDefManagement._SynthDefs)
    reload(Effects)
    buffer_manager.reset()
    return

def foxdot_reload():
    Server.init_connection()
    SynthDefs.reload()
    effect_manager.reload()
    buffer_manager.reset()
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


def allow_connections(valid = True, *args, **kwargs):
    """ Starts a new instance of ServerManager.TempoServer and connects it with the clock. Default port is 57999 """
    if valid:
        Clock.start_tempo_server(TempoServer, **kwargs)
        print("Listening for connections on {}".format(Clock.tempo_server))
    else:
        Clock.kill_tempo_server()
        print("Closed connections")
    return


#########################################
### Initialize base Player instances
#########################################

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


#########################################
### Initialize base synthdefs
#########################################

from renardo_lib.runtime.synthdefs_initialisation import *


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
        buffer_manager.reset()
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
PatternTypes = functions(Sequences)

# Start

Clock.start()
