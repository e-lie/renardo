from renardo.lib.SynthDefManagement.SimpleSynthDefs import SimpleSynthDef, LiveSynthDef, FileSynthDef

from .python_defined_effect_synthdefs import (
    Effect, EffectManager, Effects, In, Out, Server, TMP_EFFECTS_DIR, effect_manager, fx
)

# from .special_synthdefs import (
    # AudioIn, BPF, Blip, BufChannels, BufDur, BufFrames, BufGrain, BufRateScale, BufSampleRate, ClipNoise, CombC, CombL, CombN, Crackle,
    # CrossoverDistortion, Decimator, DelayC, DelayL, DelayN, Disintegrator, Dust, Env, Formant, Formlet, FreeVerb,
    # GVerb, Gendy1, Gendy2, Gendy3, Gendy4, Gendy5, HPF, Impulse, K2A, Klank, LFCub, LFNoise0, LFNoise1, LFNoise2,
    # LFPar, LFPulse, LFSaw, LFTri, LPF, Lag, Limiter, Line, MdaPiano, Out, PMOsc, Pan2, PinkNoise, PlayBuf, Pulse,
    #  RHPF, RLPF, Resonz, Ringz, SamplePygenSynthDefs, Saw, SinOsc, SinOscFB, SmoothDecimator, Squiz,
    # VarSaw, Vibrato, XLine, audioin, cls, core, dup, format_args, stutter,

    #PygenSynthDef, DefaultPygenSynthDef, GranularPygenSynthDef, LoopPygenSynthDef, StretchPygenSynthDef, PygenEffectSynthDefs,

    #granular, loop, stretch,
# )

from .python_defined_synthdefs import (
    arpy, bell, blip, bug, charm, creep, crunch, dab, dirt, donk, dub, feel, freq, fuzz, glass, gong, growl, instance,
    jbass, karp, klank, lazer, marimba, noise, nylon, orient, pluck, pulse, quin, rave, razz, ripple, saw, scatter, scratch, sitar,
    snick, soft, soprano, spark, squish, star, swell, twang, varsaw, zap
)

from .sclang_file_synthdefs import (

    play,
    loop,
    stretch,
    granular,

    abass, acidbass, alva, ambi, angel, angst, bass, bassguitar, bbass, bchaos, bellmod, benoit, birdy, blips, bnoise,
    borgan, bounce, bphase, brass, brown, chimebell, chipsy, click, clip, cluster, combs, cs80lead, dafbass, dbass, dblbass, dirt, donkysub,
    donorgan, dopple, drone, dustv, ebass, ecello, eeri, eoboe, epiano, faim, faim2, fbass, filthysaw, flute, fm, fmbass, fmrhodes, garfield,
    glitchbass, glitcher, grat, gray, gsynth, harp, hnoise, hoover, hydra, kalimba, keys, ladder, lapin, laserbeam, latoo, lazer, lfnoise,
    linesaw, longsaw, mhpad, mhping, moogbass, moogpluck, moogpluck2, mpluck, noisynth, noquarter, organ, organ2, pads, pasha, pbass, phazer,
    pianovel, pink, pmcrotal, ppad, prayerbell, prof, prophet, radio, rhodes, rhpiano, risseto, rissetobell, rlead, rsaw, rsin, sawbass,
    scatter, shore, sillyvoice, sine, sinepad, siren, sos, sosbell, space, spacesaw, spick, sputter, square, ssaw, steeldrum, strings, subbass,
    subbass2, supersaw, tb303, total, tremsynth, tribell, tritri, triwave, tubularbell, tworgan, tworgan2, tworgan3, tworgan4, varicelle, vibass,
    video, vinsine, viola, virus, waves, windmaker, wobble, wobblebass, wsaw, wsawbass, xylophone
)


