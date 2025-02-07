import pytest
from pathlib import Path
import json
import time
from renardo_sc_backend.osc_proxy import OSCProxy
#from renardo import RenardoInterpreter  # Adapt to your implementation

# Constants and Configuration
from renardo_lib.runtime import (
    ADDRESS, ALPHA_VALUE, AUTO_COMPLETE_BRACKETS, BOOT_ON_STARTUP, CHECK_FOR_UPDATE,
    CLOCK_LATENCY, COLOR_THEME, COLOURS, CONSOLE_ON_STARTUP, CPU_USAGE, EFFECTS_DIR,
    ENVELOPE_DIR, FONT, FORWARD_ADDRESS, FORWARD_PORT, FOXDOT_CONFIG_FILE,
    FOXDOT_EDITOR_ROOT, FOXDOT_EDITOR_THEMES, FOXDOT_EFFECTS_FILE, FOXDOT_HELLO,
    FOXDOT_ICON, FOXDOT_ICON_GIF, FOXDOT_LOOP, FOXDOT_ROOT, FOXDOT_SETTINGS,
    FOXDOT_SND, FOXDOT_STARTUP, FOXDOT_STARTUP_PATH, GET_SC_INFO,
    LINENUMBERS_ON_STARTUP, LINE_NUMBER_MARKER_OFFSET, MAX_CHANNELS, MENU_ON_STARTUP,
    PORT, PORT2, PATTERN_METHODS, RECORDING_DIR, RECOVER_WORK, SAMPLES_DIR,
    SAMPLES_PACK_NUMBER, SC3_PLUGINS, SUPERCOLLIDER, SYNTHDEF_DIR, TEXT_COLORS,
    TMP_EFFECTS_DIR, TMP_SYNTHDEF_DIR, TRANSPARENT_ON_STARTUP, TREEVIEW_ON_STARTUP,
    TUTORIAL_DIR, USE_ALPHA
)

# Core Classes
from renardo_lib.runtime import (
    Buffer, BufferManager, BufferManagement, Code, CodeString, CodeType, Dict,
    Effect, EffectManager, Effects, FoxDot, FoxDotCode, FunctionType, LiveObject,
    Optional, Path, PatternMethods, PatternTypes, Server, SynthDefManagement,
    TimeVar, TypeType, WarningMsg
)

# Audio and Synthesis Classes
from renardo_lib.runtime import (
    AudioIn, BPF, Blip, BufChannels, BufDur, BufFrames, BufGrain, BufRateScale,
    BufSampleRate, ClipNoise, CombC, CombL, CombN, Crackle, CrossoverDistortion,
    Decimator, DelayC, DelayL, DelayN, Disintegrator, Dust, Env, FileSynthDef,
    Formant, Formlet, FreeVerb, GVerb, Gendy1, Gendy2, Gendy3, Gendy4, Gendy5,
    GranularPygenSynthDef, HPF, Impulse, In, K2A, Klank, LFCub, LFNoise0, LFNoise1,
    LFNoise2, LFPar, LFPulse, LFSaw, LFTri, LPF, Lag, Limiter, Line,
    LiveSynthDef, LoopPygenSynthDef, Master, MdaPiano, Out, PMOsc, Pan2,
    PinkNoise, PlayBuf, Pulse, PygenEffectSynthDefs, PygenSynthDef, RHPF, RLPF,
    Ramp, Resonz, Ringz, Saw, SinOsc, SinOscFB, SmoothDecimator, Squiz,
    StretchPygenSynthDef, VarSaw, Vibrato, XLine
)

# Pattern System Classes
from renardo_lib.runtime import (
    Add, Bang, CalculateDelaysFromDur, CalculateEuclideanDelay, ChildPvar,
    ChildTimeVar, ClassPatternMethod, Convert, Cycle, DefaultPygenSynthDef, Div,
    DominantPattern, EmptyItem, EmptyPlayer, EuclidsAlgorithm, FloorDiv, Format,
    GeneratorPattern, Generators, Get, Group, GroupAttr, History, LCM, LoopPlayer,
    MAX_SIZE, Main, MIDIDeviceNotFound, MethodCall, MethodType, MidiIn, Mod, Mul,
    Nil, NumberKey, Operations, Or
)

# Pattern Classes
from renardo_lib.runtime import (
    P, P10, PAdd, PAlt, PBeat, PBern, PChain, PDelay, PDelta, PDiv, PDiv2, PDur,
    PEq, PEuclid, PEuclid2, PFibMod, PFloor, PFloor2, PGet, PGroup, PGroupAnd,
    PGroupDiv, PGroupMod, PGroupOr, PGroupPlus, PGroupPow, PGroupPrime, PGroupStar,
    PGroupXor, PGroups, PIndex, PJoin, PMod, PMod2, PMul, PNe, POperand, PPairs,
    PPow, PPow2, PQuicken, PRand, PRange, PRhythm, PShuf, PSine, PSq, PSquare,
    PStep, PStretch, PStrum, PStutter, PSub, PSub2, PSum, PTree, PTri, PWalk,
    PWhite, PZ12, PZip, PZip2, Parse, ParseError, ParsePlayString, Pattern,
    PatternContainer, PatternFormat, PatternInput, PatternMethod, PlayerMethod,
    Pow, PulsesToDurations, Pvar, PvarGenerator, PvarGeneratorEx, PwRand, PxRand
)

# Player System
from renardo_lib.runtime import (
    MidiInputHandler, MidiOut, Player, PlayerKey, PlayerKeyException, Queue,
    QueueBlock, QueueObj, RequestTimeout, Root, SamplePlayer, Scale, ScheduleError,
    Sequences, ServerManager, SoloPlayer, StaticPatternMethod, SynthDefProxy,
    SynthDefs, TempoClient, TempoClock, TempoServer, Utils, Wrapper, Xor
)

# Utility Functions and Constants
from renardo_lib.runtime import (
    allow_connections, arrow_zip, asPattern, asStream, bar_type, br_pairs,
    braces_type, bubble, choice, clean, conf, convert_nested_data, convert_to_int,
    copy, debug_stdout, dots, equal_values, error_stack, execute, expvar, feed,
    fetch, force_pattern_args, format_args, foxdot_func_cmp, foxdot_live_function,
    foxdot_reload, foxdot_when_statement, fromString, functools, futureBar,
    get_avg_if, get_expanded_len, get_first_item, get_freq_and_midi, get_input,
    get_inverse_op, get_now, get_pypi_version, get_samples_dir_path,
    get_synthdefs_dir_path, get_tutorial_files, group_modi, handle_stdin, heapq,
    inf, inspect, instance, instances, isiterable,
    itertools, json, linvar, livefunction, load_startup_file, loop_pattern_func,
    loop_pattern_method, main_lib, mapvar, math, metaPGroupPrime, metaPattern,
    nextBar, next_bar, nextbar, now, offadd, offlayer, offmul, pattern_depth,
    patternclass, play, recursive_any, reload, rest, rtMidiNotFound, sinvar,
    sliceToRange, socket_timeout, square_type, sum_delays, synthdefs_initialisation,
    threading, update_foxdot_clock, update_foxdot_server, urlopen, var,
    write_to_file, Clock
)
# instantiate_player_functions,

# Built-in Instruments
from renardo_lib.runtime import (
    acidbass, ambi, amen, angel, angst, arpy, audioin, bass, bassguitar, bchaos,
    bell, bellmod, benoit, birdy, blip, blips, bnoise, borgan, bounce, bphase,
    brass, brown, bug, charm, chimebell, chipsy, click, clip, cluster, combs, creep,
    crunch, cs80lead, dab, dafbass, dbass, dblbass, dirt, donk, donkysub, donorgan,
    dopple, drone, dub, dup, dustv, ebass, ecello, eeri, eoboe, epiano, faim,
    faim2, fbass, feel, filthysaw, flute, fmbass, fmrhodes, freq, fuzz, garfield,
    glass, glitchbass, glitcher, gong, granular, grat, gray, growl, gsynth, harp,
    hnoise, hoover, hydra, jbass, kalimba, karp, keys, klank, ladder, lapin,
    laserbeam, latoo, lazer, lfnoise, linesaw, longsaw, marimba, mhpad, mhping,
    moogbass, moogpluck, moogpluck2, mpluck, noise, noisynth, noquarter, nylon,
    organ, organ2, orient, pads, pasha, pbass, phazer, pianovel, pink, pluck,
    pmcrotal, ppad, prayerbell, prof, prophet, pulse, quin, radio, rave, razz,
    rhodes, rhpiano, ripple, risseto, rissetobell, rlead, rsaw, rsin, sawbass,
    scatter, scratch, shore, sillyvoice, sine, sinepad, siren, sitar, snick, soft,
    soprano, sos, sosbell, space, spacesaw, spark, spick, sputter, square, squish,
    ssaw, star, steeldrum, stretch, strings, stutter, subbass, subbass2, supersaw,
    swell, tb303, tremsynth, tribell, tritri, triwave, tubularbell, twang, tworgan,
    tworgan2, tworgan3, tworgan4, varicelle, varsaw, vibass, video, vinsine, viola,
    virus, waves, windmaker, wobble, wobblebass, wsaw, wsawbass, xylophone, zap
)

# All single letter variables (a-z, A-Z, 0-9 suffixes)
#from renardo_lib.runtime import (
#    a0, a1, a2, a3, a4, a5, a6, a7, a8, a9, a_all, aa, ab, ac, ad, ae, af, ag, ah,
#    ai, aj, ak, al, am, an, ao, ap, aq, ar, as_, at, au, av, aw, ax, ay, az,
#    b0, b1, b2, b3, b4, b5, b6, b7, b8, b9, b_all, ba, bb, bc, bd, be, bf, bg, bh,
#    bi, bj, bk, bl, bm, bn, bo, bp, bq, br, bs, bt, bu, bv, bw, bx, by, bz
#)


@pytest.fixture
def osc_proxy():
    """Fixture that provides a configured OSC proxy for testing."""
    proxy = OSCProxy(listen_port=57120, forward_port=57110)
    proxy.start()
    yield proxy
    proxy.stop()


@pytest.fixture
def event_signatures():
    """Load the expected event signatures."""
    signatures_path = Path("test_data/signatures.json")
    with open(signatures_path) as f:
        return json.load(f)


def assert_osc_sequence(actual_events, expected_events, timing_tolerance=0.1):
    """
    Verify that a sequence of OSC events matches the expected signature.

    Args:
        actual_events: Captured OSC events
        expected_events: Expected event signature
        timing_tolerance: Timing tolerance in seconds
    """
    assert len(actual_events) == len(expected_events), \
        f"Incorrect number of events. Expected: {len(expected_events)}, Got: {len(actual_events)}"

    for actual, expected in zip(actual_events, expected_events):
        # Check OSC address
        assert actual.address == expected["address"], \
            f"Incorrect OSC address. Expected: {expected['address']}, Got: {actual.address}"

        # Check arguments
        assert actual.args == expected["args"], \
            f"Incorrect arguments. Expected: {expected['args']}, Got: {actual.args}"

        # Check timing (with tolerance)
        assert abs(actual.timestamp - expected["timestamp"]) <= timing_tolerance, \
            f"Incorrect timing. Expected: {expected['timestamp']}, Got: {actual.timestamp}"

def test_blip_1(osc_proxy, event_signatures):
    time.sleep(3)
    b1 = Player()
    b1 >> blip([0,2,4,5,6])
    Clock.set_time(0)
    time.sleep(3)
    Clock.clear()